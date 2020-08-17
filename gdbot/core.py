import asyncio
import datetime
from pathlib import Path
import traceback
from typing import Optional

import aiohttp
from discord.ext import commands
import discord

import gd

__all__ = ("GDBot", "run_bot", "run_bot_sync")

assets = Path(__file__).parent / "assets"

cogs = ["gdbot.cogs.admin", "gdbot.cogs.meta", "gdbot.cogs.mod"]

description = """
Discord Bot that can interact with servers of Geometry Dash, and much more!
""".strip()

get_prefix = commands.when_mentioned_or("n?", "gd!")


class GDBot(commands.AutoShardedBot):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        super().__init__(
            command_prefix=get_prefix,
            description=description,
            help_attrs=dict(hidden=True),
            loop=loop,
            pm_help=None,
        )

        self.session = aiohttp.ClientSession(loop=loop)
        self.load_cogs()

    def load_asset(self, name: str) -> discord.File:
        return discord.File(assets / name, name)

    def load_cogs(self) -> None:
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception:
                print(f"Exception occured on cog loading: {cog}.")
                traceback.print_exc()

    async def on_ready(self) -> None:
        if not hasattr(self, "uptime"):
            self.uptime = datetime.datetime.utcnow()

        print(f"Ready: {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        await self.process_commands(message)

    async def close(self) -> None:
        await super().close()
        await self.session.close()


async def run_bot(
    token: str,
    gd_user: Optional[str] = None,
    gd_password: Optional[str] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> None:
    if loop is None:
        loop = gd.utils.acquire_loop()

    bot = GDBot(loop=loop)

    client = gd.Client(loop=loop)

    if gd_user and gd_password:
        try:
            await client.login(gd_user, gd_password)
        except Exception:
            print("Exception caught on logging into GD account.")
            traceback.print_exc()

    bot.client = client

    try:
        await bot.start(token)

    finally:
        await bot.close()


def run_bot_sync(
    token: str, gd_user: Optional[str] = None, gd_password: Optional[str] = None
) -> None:
    loop = gd.utils.acquire_loop()
    loop.run_until_complete(run_bot(token, gd_user, gd_password, loop))
