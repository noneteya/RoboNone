import discord
from discord.ext import commands
from . import discord_db
import typing
import asyncio


def setup(bot):
    bot.add_cog(Approval(bot))


def hasnt_any_roles(ctx):
    return len(ctx.message.author.roles) == 1


class Approval:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        pass

    async def on_reaction_add(self, reaction, user):
        if len(reaction.message.author.roles) != 1:
            return
        if user == self.bot.user:
            return
        if user == reaction.message.author:
            await reaction.remove(user)
            return

        if reaction.emoji == "✅":
            if reaction.count > 3:
                role = discord.utils.find(lambda m: m.name == 'player', user.guild.roles)
                reaction.message.author.add_roles(role)
                await reaction.message.channel.send(f"{reaction.message.author.mention} あなたは承認されました！")
                await reaction.message.delete()
            else:
                m = await reaction.message.channel.send(f"{user.mention} 申請を承認しました")
                await asyncio.sleep(5)
                await m.delete()

        elif reaction.emoji == "❎":
            if reaction.count > 3:
                await reaction.message.channel.send(f"{reaction.message.author.mention} 申請が否認されました")
                await reaction.message.delete()
            else:
                m = await reaction.message.channel.send(f"{user.mention} 申請を否認しました")
                await asyncio.sleep(5)
                await m.delete()

        else:
            await reaction.remove(user)

    @commands.command()
    @commands.check(hasnt_any_roles)
    async def agree(self, ctx):
        """承認待ちができます"""
        role = discord.utils.find(lambda m: m.name == 'prospect', ctx.guild.roles)
        await ctx.author.add_roles(role)
        await ctx.message.add_reaction("✅")
        await ctx.message.add_reaction("❎")
        m = await ctx.send(f"{ctx.author.mention} 承認待ちユーザーになりました！")
        await asyncio.sleep(5)
        await m.delete()
