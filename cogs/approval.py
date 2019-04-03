import discord
from discord.ext import commands
import typing
import asyncio


def setup(bot):
    bot.add_cog(Approval(bot))


def has_no_roles(ctx):
    return len(ctx.message.author.roles) == 1


class Approval:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        pass

    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.get_message(payload.message_id)
        if message.guild:
            user = message.guild.get_member(payload.user_id)
        else:
            user = self.bot.get_user(payload.user_id)

        has_prospect = False
        for role in message.author.roles:

            if role.name == "prospect":
                has_prospect = True
        if not has_prospect:
            return

        if user == self.bot.user:
            return

        if user == message.author:
            await message.remove_reaction(emoji, user)
            return

        if emoji.name == "✅":

            check_mark_reaction = None
            for reaction in message.reactions:
                if reaction.emoji == "✅":
                    check_mark_reaction = reaction

            if check_mark_reaction.count > 3:
                role = discord.utils.find(lambda m: m.name == 'player', user.guild.roles)
                await message.author.add_roles(role)
                role = discord.utils.find(lambda m: m.name == 'prospect', user.guild.roles)
                await message.author.remove_roles(role)
                await message.channel.send(f"{message.author.mention} あなたは承認されました！")
                await message.delete()
            else:
                m = await message.channel.send(f"{user.mention} 申請を承認しました")
                await asyncio.sleep(3)
                await m.delete()

        elif emoji.name == "❎":

            x_mark_reaction = None
            for reaction in message.reactions:
                if reaction.emoji == "❎":
                    x_mark_reaction = reaction

            if x_mark_reaction.count > 3:
                await message.channel.send(f"{message.author.mention} 申請が否認されました")
                await message.delete()
            else:
                m = await message.channel.send(f"{user.mention} 申請を否認しました")
                await asyncio.sleep(5)
                await m.delete()

        else:
            await message.remove_reaction(emoji, user)

    @commands.command()
    @commands.check(has_no_roles)
    async def agree(self, ctx):
        """承認待ちができます"""
        role = discord.utils.find(lambda m: m.name == 'prospect', ctx.guild.roles)
        await ctx.author.add_roles(role)
        await ctx.message.add_reaction("✅")
        await ctx.message.add_reaction("❎")
        m = await ctx.send(f"{ctx.author.mention} 承認待ちユーザーになりました！")
        await asyncio.sleep(5)
        await m.delete()
