import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(Invite(bot))


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        """あなたの友達を一人招待できます"""
        role = discord.utils.get(ctx.author.guild.roles, name="招待権使用済み")
        if role is None:
            await ctx.message.channel.send(":warning: `招待権使用済み`という権限を作成してください")
        elif role in ctx.author.roles:
            await ctx.message.channel.send(":warning: すでに使用済みです")
        else:
            await ctx.author.add_roles(role)
            invite = await ctx.message.channel.create_invite(max_uses=1, max_age=18000, unique=True)
            await ctx.message.channel.send(":white_check_mark: DMに一度限り使用できる招待リンクを送信しました")
            await ctx.author.send(invite)
