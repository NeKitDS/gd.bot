from discord.ext import commands
import discord

HIGH_PING = 1000  # ms


class Meta(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx: commands.Context) -> None:
        delta = ctx.message.created_at - self.bot.uptime

        minutes, seconds = divmod(delta.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days = delta.days

        await ctx.send(
            embed=discord.Embed(title=f"{days}d {hours}h {minutes}m {seconds}s", color=0x7289DA)
        )

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        message = await ctx.send(embed=discord.Embed(title="Checking...", color=0x7289DA))

        ms = (message.created_at - ctx.message.created_at).total_seconds() * 1000

        color = 0x77FF77 if ms < HIGH_PING else 0xFF7777

        await message.edit(embed=discord.Embed(title=f"Ping: {ms:.2f}ms", color=color))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Meta(bot))
