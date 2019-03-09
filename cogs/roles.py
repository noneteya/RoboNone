import discord
from discord.ext import commands
from . import discord_db
import typing
from dotenv import load_dotenv
import os
from pathlib import Path

# DB_GUILD_ID = 553724445156704281

if not os.getenv("ON_SERVER"):
    # ローカルで走らせる場合
    env_path = Path('./..') / '.env.local'
    load_dotenv(dotenv_path=env_path)

DB_GUILD_ID = os.getenv("DB_GUILD_ID")


def setup(bot):
    bot.add_cog(RoleManager(bot))


class RoleManager:
    def __init__(self, bot):
        self.bot = bot
        self.handler = discord_db.DiscordDBHandler(bot)

    async def on_ready(self):
        # ここでロードしないと準備が整わないうちに実行されてcommands.Bot.guildsが取得できないことがある
        self.db = self.handler.get_db(DB_GUILD_ID)

    async def get_table(self, ctx):
        try:
            return self.db.get_table(f"{ctx.guild.id}-attachable-roles")
        except Exception:
            return await self.db.create_table(f"{ctx.guild.id}-attachable-roles", "初回参照")

    @commands.command()
    async def attach(self, ctx, roles: commands.Greedy[discord.Role]):
        """指定した役職を自分に付与できます"""
        table = await self.get_table(ctx)
        attachables: typing.List[int] = [int(r.name) for r in table.records()]
        for role in set(roles):
            if role.id in [r.id for r in ctx.author.roles]:
                await ctx.send(":warning: あなたはすでにその役職を持っています")
            elif role.id not in attachables:
                await ctx.send(":warning: {role.name}は付与できません")
            else:
                try:
                    await ctx.author.add_roles(role)
                    await ctx.send(f":white_check_mark:  {ctx.author.name}さんが{role.name}に参加しました")
                except discord.errors.Forbidden:
                    await ctx.send(":warning: その役職は付与できません")

    @commands.command(aliases=["remove"])
    async def detach(self, ctx, roles: commands.Greedy[discord.Role]):
        """指定した役職を外します"""
        table = await self.get_table(ctx)
        attachables: typing.List[int] = [int(r.name) for r in table.records()]
        for role in set(roles):
            if role not in ctx.author.roles:
                await ctx.send(":warning: あなたはその役職を持っていません")
            elif role.id not in attachables:
                await ctx.send(":warning: {role.name}は削除できません")
            else:
                try:
                    await ctx.author.remove_roles(role)
                    await ctx.send(f":white_check_mark:  {ctx.author.name}さんが{role.name}から退出しました")
                except discord.errors.Forbidden:
                    await ctx.send(":warning: その役職は削除できません")

    @commands.command(aliases=["addattach"])
    @commands.has_permissions(manage_roles=True)
    async def add_attachables(self, ctx, roles: commands.Greedy[discord.Role]):
        """編集可能な役職を追加します"""
        for role in set(roles):
            table = await self.get_table(ctx)
            attachables: typing.List[int] = [int(r.name) for r in table.records()]
            if role.id in attachables:
                await ctx.send(f":warning: {ctx.role}はすでに編集可能です")
            else:
                await table.create_record(str(role.id), f"{ctx.author} の要請")
            await ctx.send(":white_check_mark: 役職を編集できるように設定しました")

    @commands.command(aliases=["removeattach"])
    @commands.has_permissions(manage_roles=True)
    async def remove_attachables(self, ctx, roles: commands.Greedy[discord.Role]):
        """編集可能な役職を削除します"""
        for role in set(roles):
            table = await self.get_table(ctx)
            attachables: typing.List[int] = [int(r.name) for r in table.records()]
            if role.id in attachables:
                record = table.get_record(str(role.id))
                await record.delete(reason=f'{ctx.author} の要請')
                await ctx.send(":white_check_mark: 役職を編集できないように設定しました")
            else:
                await table.create_record(str(role.id), f"{ctx.author} の要請")
                await ctx.send(":warning: その役職はすでに編集できません")

    @commands.command(aliases=["show"])
    async def show_attachables(self, ctx):
        """編集可能な役職の一覧を表示させます"""
        table = await self.get_table(ctx)
        role_ids = [int(r.name) for r in table.records()]
        msg = ', '.join(r.name for r in ctx.guild.roles if r.id in role_ids)
        if msg != "":
            await ctx.send(msg)
        else:
            await ctx.send("編集できる役職はありません")
