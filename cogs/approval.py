import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
from pathlib import Path

from .utils.database import Handler, DBManager

create_table = """
    CREATE TABLE approval IF NOT EXISTS(
guild_id int,
reaction_channel_id int,
approval_channel_id int,
wait_people_numbers int
);
""".replace("\n", "")

if not os.getenv("ON_SERVER"):
    # ローカルで走らせる場合
    env_path = Path('./..') / '.env.local'
    load_dotenv(dotenv_path=env_path)

DB_URL = os.getenv("DATABASE_URL")
admins = []


def setup(bot):
    bot.add_cog(Approval(bot))


def is_everyone_only(author):
    return len(author.roles) == 1


class Approval:
    def __init__(self, bot: commands.Bot):
        global admins
        self.bot = bot
        self.waiting = {}
        self.manager = DBManager(DB_URL)
        # なければ作成
        self.manager.do(Handler(processing='execute', sql=create_table, fetch=False))
        self.admins = [476172941692895232, 212513828641046529, bot.owner_id]
        admins = self.admins

    @commands.command()
    @commands.check(lambda ctx: ctx.author.id in admins)
    async def create_setting(self, ctx, reaction_channel: discord.TextChannel, approval_channel: discord.TextChannel):
        # DMの場合無視
        if not ctx.guild:
            return
        sql = f"INSERT INTO approval VALUES ({ctx.guild.id}, {reaction_channel.id}, {approval_channel.id});"
        self.manager.do(Handler(processing='execute', sql=sql, fetch=False))

    def get_guild_setting(self, guild_id: int):
        result = self.manager.do(Handler(processing="execute",
                                         cmd=f"SELECT * FROM approval WHERE guild_id = {guild_id}"))
        if not result:
            return []
        return list(result[0])

    def is_admin(self, _id):
        return _id in self.admins

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        emoji = payload.emoji
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.get_message(payload.message_id)
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        setting = self.get_guild_setting(guild.id)
        # ここからチェック
        #botの場合無視
        if member.bot:
            return
        # settingが空の場合無視
        if not setting:
            return
        # 絵文字が\U00002705でない場合無視
        if not emoji == "\U00002705":
            return
        # チャンネルが規約チャンネル以外の場合無視
        if channel.id != setting[1]:
            # 自分の承認のやつに反応できないように
            if channel.id == setting[2]:
                if is_everyone_only(member):
                    await message.remove_reaction(emoji, member)
                    return

            return
        # ユーザーがeveryone以外の権限を持っていたら無視
        if not is_everyone_only(member):
            return

        # DMに承認を待つように送る、ダメであればチャンネルに送る
        embed = discord.Embed(title="やさしいかくめいラボ 2.0 運営",
                              description="承認要求を受理しました。承認まで今しばらくお待ちください。",
                              color=discord.Color(0x00bfff))
        try:
            await member.send(embed=embed)
        except discord.DiscordException:
            c = guild.get_channel(setting[2])
            await c.send(embed=embed)

        # 承認を待つ関数を呼ぶ
        # create_taskをすることで一旦処理を終わらせる
        self.bot.loop.create_task(self.wait_approval(member, guild))

    async def wait_approval(self, member: discord.Member, guild: discord.Guild):
        """3人の承認を待つ"""
        setting = self.get_guild_setting(guild.id)
        # 承認用メッセージを作成
        channel = guild.get_channel(setting[2])
        embed = discord.Embed(title=f"{member.display_name}さんの承認要求を受理しました",
                              description="承認要求を承認してくださる方は\U00002705を押してください。"
                                          "押されなかった場合は10分後に自動的に拒否されます。")
        message = await channel.send(embed=embed)
        await message.add_reaction("\U00002705")

        # 2分ごとにチェック
        for t in range(5):
            # キャッシュから取ると更新されないので新しくメッセージを取る
            check_channel = self.bot.get_channel(setting[2])
            check_message = await check_channel.get_message(message.id)
            for reaction in check_message.reacions:
                if reaction.emoji == "\U00002705":
                    if reaction.count >= 4:
                        await channel.send(f"{member.mention} さんの承認要求が許可されました！")
                        role = discord.utils.find(lambda m: m.name == 'player', guild.roles)
                        # 言わせてもらおう
                        # 元の処理何？なんで役職を消す処理なんてしてんのじゃあなんで二つ以上の役職持ってるのにhasnt_any_rolesあんの
                        await member.add_roles(role)
        await channel.send(f"{member.mention} さんの承認要求は拒否されました。")
