import asyncio
from contextlib import redirect_stdout
import copy
import inspect
import io
import subprocess
import textwrap
import traceback
from typing import Any, List

from discord.ext import commands
import discord
import import_expression

EMPTY_STR = ""
INDENT = " " * 4


def codeblock(py_object: Any, language: str = "") -> str:
    if py_object == EMPTY_STR:
        return EMPTY_STR

    return f"```{language}\n{py_object}\n```"


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.last_result = None
        self.sessions = set()

    async def run_process(self, command: str) -> List[str]:
        """Run command in async subprocess, returning results."""
        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            result = await process.communicate()

        except NotImplementedError:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    def cleanup_code(self, content: str) -> str:
        """Automatically removes code blocks from the code."""
        if content.startswith("```py") and content.endswith("```"):
            content = "\n".join(content.splitlines()[1:])

        content = content.strip("` \n")

        return content

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Check if ctx.author is owner of the bot."""
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, error: SyntaxError) -> str:
        """Generate message in case of syntax error."""
        if error.text is None:  # no text -> show normal message
            return codeblock(f"{error.__class__.__name__}: {error}", "py")

        return codeblock(
            f"{error.text}{'^':>{error.offset}}\n{error.__class__.__name__}: {error}", "py"
        )

    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, *, module: str) -> None:
        """Loads a module."""
        try:
            self.bot.load_extension(module)

        except commands.ExtensionError as error:
            await ctx.send(codeblock(f"{error.__class__.__name__}: {error}", "py"))

        else:
            await ctx.send(codeblock(f"Extension loaded: {module!r}."))

    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, *, module: str) -> None:
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)

        except commands.ExtensionError as error:
            await ctx.send(codeblock(f"{error.__class__.__name__}: {error}", "py"))

        else:
            await ctx.send(codeblock(f"Extension unloaded: {module!r}."))

    async def send_or_file(self, ctx: commands.Context, string: str, limit: int = 2000) -> None:
        if len(string) < limit:
            await ctx.send(string)
        else:
            file = io.BytesIO(self.cleanup_code(string).encode("utf-8"))
            await ctx.send(file=discord.File(file, "result.txt"))

    @commands.command(hidden=True, name="eval")
    async def eval_command(self, ctx: commands.Context, *, body: str) -> None:
        """Evaluates some code."""

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self.last_result,
        }

        env.update(globals())

        stdout = io.StringIO()
        body = self.cleanup_code(body)
        indented = textwrap.indent(body, INDENT)

        to_compile = f"async def function():\n{indented}"

        try:
            import_expression.exec(to_compile, env)
        except Exception as error:
            await ctx.send(codeblock(f"{error.__class__.__name__}: {error}", "py"))
            return

        function = env["function"]

        try:
            with redirect_stdout(stdout):
                result = await function()

        except Exception:
            value = stdout.getvalue()
            result_format = codeblock(value) + "\n" + codeblock(traceback.format_exc(), "py")

        else:
            value = stdout.getvalue()

            if result is None:
                if value:
                    result_format = codeblock(value)
                else:
                    result_format = codeblock("[No output]")
            else:
                self.last_result = result
                result_format = codeblock(value) + "\n" + codeblock(repr(result), "py")

        await self.send_or_file(ctx, result_format)

    @commands.command(hidden=True)
    async def repl(self, ctx: commands.Context) -> None:
        """Launches an interactive REPL session."""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send(codeblock(f"Already running a REPL session in this channel."))
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send(
            codeblock("Enter code to execute or evaluate. To exit, enter `exit` or `quit`.")
        )

        def check(message: discord.Message) -> bool:
            return (
                message.content.startswith("`")
                and message.author.id == ctx.author.id
                and message.channel.id == ctx.channel.id
            )

        while True:
            try:
                response = await self.bot.wait_for("message", check=check, timeout=600)

            except asyncio.TimeoutError:
                await ctx.send(codeblock("Exiting REPL session."))
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in {"quit", "exit", "quit()", "exit()"}:
                await ctx.send(codeblock("Exiting REPL session."))
                self.sessions.remove(ctx.channel.id)
                return

            try:
                code = import_expression.compile(cleaned, "<repl>", "eval")
                executor = import_expression.eval

            except SyntaxError:
                try:
                    code = import_expression.compile(cleaned, "<repl>", "exec")
                    executor = import_expression.exec

                except SyntaxError as error:
                    await ctx.send(self.get_syntax_error(error))
                    continue

            env.update(message=response)
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, env)
                    if inspect.isawaitable(result):
                        result = await result

            except Exception:
                value = stdout.getvalue()
                result_format = codeblock(value) + "\n" + codeblock(traceback.format_exc(), "py")

            else:
                value = stdout.getvalue()

                if result is None:
                    if value:
                        result_format = codeblock(value)
                    else:
                        result_format = codeblock("[No output]")

                else:
                    env["_"] = result
                    result_format = codeblock(value) + "\n" + codeblock(repr(result), "py")

            await self.send_or_file(ctx, result_format)

    @commands.command(hidden=True)
    async def sh(self, ctx: commands.Context, *, command: str) -> None:
        async with ctx.typing():
            stdout, stderr = await self.run_process(command)

        if stderr:
            text = "\n".join(("stdout:", stdout, "stderr:", stderr))
        else:
            text = stdout

        await self.send_or_file(ctx, codeblock(text))

    @commands.command(hidden=True)
    async def sudo(self, ctx: commands.Context, user: discord.User, *, command: str) -> None:
        """Run a command as another user."""
        message = copy.copy(ctx.message)
        message.channel = ctx.channel
        message.author = ctx.guild.get_member(user.id) or user
        message.content = ctx.prefix + command

        new_ctx = await self.bot.get_context(message, cls=type(ctx))

        await self.bot.invoke(new_ctx)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Admin(bot))
