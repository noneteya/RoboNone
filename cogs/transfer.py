import discord
from discord.ext import commands
import typing
import asyncio


def setup(bot):
    bot.add_cog(Transfer(bot))


class Transfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trans(self, ctx, user :discord.Member):
        """権限を移行できます"""
        role = discord.utils.find(lambda m: m.name == '権限担当のひと', ctx.guild.roles)

        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await user.add_roles(role)

            m = await ctx.send(f"{ctx.author.mention} 権限を移行しました")
            await asyncio.sleep(5)
            await m.delete()
        else:
            m = await ctx.send(f"{ctx.author.mention} あなたは権限を持っていません")
            await asyncio.sleep(5)
            await m.delete()
