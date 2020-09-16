from typing import Optional

from discord.ext import commands
import discord


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self, ctx: commands.Context, amount: int, member: Optional[discord.Member] = None
    ) -> None:
        def message_check(message: discord.Message) -> bool:
            if member:
                return message.author.id == member.id
            return True

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, check=message_check)

        await ctx.send(
            embed=discord.Embed(title=f"Deleted {len(deleted)}/{amount} messages.", color=0x77FF77),
            delete_after=10,
        )

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None
    ) -> None:
        await member.ban(reason=reason)
        await ctx.send(embed=discord.Embed(title=f"Banned {member.display_name}.", color=0x77FF77))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(
        self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None
    ) -> None:
        await member.kick(reason=reason)
        await ctx.send(embed=discord.Embed(title=f"Kicked {member.display_name}.", color=0x77FF77))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
