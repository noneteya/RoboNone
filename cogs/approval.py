import discord
from discord.ext import commands
import typing
import asyncio


def setup(bot):
    bot.add_cog(Approval(bot))


def has_no_roles(ctx):
    return len(ctx.message.author.roles) == 1


def has_prospect(member):
    for role in member.roles:
        if role.name == 'prospect':
            return True


class Approval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.guild:
            member = message.guild.get_member(payload.user_id)
        else:
            return

        if member == self.bot.user or not has_prospect(message.author):
            return

        if member == message.author or has_prospect(member) or len(member.roles) == 1:
            await message.remove_reaction(emoji, member)
            return

        if emoji.name == "✅":

            check_mark_reaction = None
            for reaction in message.reactions:
                if reaction.emoji == "✅":
                    check_mark_reaction = reaction

            o_users = await check_mark_reaction.users().flatten()
            o_users_name = [user.name for user in o_users]

            if check_mark_reaction and check_mark_reaction.count > 3:
                role = discord.utils.find(lambda m: m.name == 'player', member.guild.roles)
                await message.author.add_roles(role)
                role = discord.utils.find(lambda m: m.name == 'prospect', member.guild.roles)
                await message.author.remove_roles(role)
                await message.author.send(f"{message.author.mention} あなたは承認されました！")
                await message.guild.owner.send(f"{message.author}さんが {o_users_name} によって承認されました。")
                await message.delete()
            else:
                m = await message.channel.send(f"{member.mention} 申請を承認しました")
                await asyncio.sleep(3)
                await m.delete()

        elif emoji.name == "❎":

            x_mark_reaction = None
            for reaction in message.reactions:
                if reaction.emoji == "❎":
                    x_mark_reaction = reaction

            x_users = await x_mark_reaction.users().flatten()
            x_users_name = [user.name for user in x_users]


            if x_mark_reaction and x_mark_reaction.count > 3:
                role = discord.utils.find(lambda m: m.name == 'prospect', member.guild.roles)
                await message.author.remove_roles(role)
                await message.author.send(f"{message.author.mention} 申請が否認されました。"
                                          f"twitter連携が正しくできているか、参加要件を満たしているかもう一度確認してください。")
                await message.guild.owner.send(f"{message.author}さんが {x_users_name} によって否認されました ")
                await message.delete()

            else:
                m = await message.channel.send(f"{member.mention} 申請を否認しました")
                await asyncio.sleep(5)
                await m.delete()

        else:
            await message.remove_reaction(emoji, member)

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
