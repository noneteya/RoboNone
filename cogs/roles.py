import discord
from discord.ext import commands
import typing
from dotenv import load_dotenv
import os
from pathlib import Path
from .utils import database

blacklist_table_name = "blacklist"
attachables_table_name = "attachables"

if not os.getenv("ON_SERVER"):
    # ローカルで走らせる場合
    env_path = Path('./..') / '.env.local'
    load_dotenv(dotenv_path=env_path)

DB_URL = os.getenv("DB_URL")


def setup(bot):
    bot.add_cog(RoleManager(bot))


class RoleManager:
    def __init__(self, bot):
        self.bot = bot
        self.handler = database.DBHandler(DB_URL)

    @commands.command()
    async def attach(self, ctx, roles: commands.Greedy[discord.Role]):
        """指定した役職を自分に付与できます"""
        attachables = self.handler.fetch_column("role_id", attachables_table_name, where=f"guild_id = {ctx.author.guild.id}")
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
        attachables = self.handler.fetch_column("role_id", attachables_table_name,
                                                where=f"guild_id = {ctx.author.guild.id}")
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
            attachables = self.handler.fetch_column("role_id", attachables_table_name,
                                                    where=f"guild_id = {ctx.author.guild.id}")
            if role.id in attachables:
                await ctx.send(f":warning: {role.name}はすでに編集可能です")
            else:
                self.handler.insert_data((ctx.author.guild.id, role.id), ("guild_id", "role_id"), attachables_table_name)
                await ctx.send(":white_check_mark: 役職を編集できるように設定しました")

    @commands.command(aliases=["removeattach"])
    @commands.has_permissions(manage_roles=True)
    async def remove_attachables(self, ctx, roles: commands.Greedy[discord.Role]):
        """編集可能な役職を削除します"""
        attachables = self.handler.fetch_column("role_id", attachables_table_name,
                                                where=f"guild_id = {ctx.author.guild.id}")
        for role in set(roles):
            if role.id in attachables:
                self.handler.delete_data((ctx.author.guild.id, role.id), ("guild_id", "role_id"), attachables_table_name)
                await ctx.send(":white_check_mark: 役職を編集できないように設定しました")
            else:

                await ctx.send(":warning: その役職はすでに編集できません")

    @commands.command(aliases=["show"])
    async def show_attachables(self, ctx):
        """編集可能な役職の一覧を表示させます"""
        attachables = self.handler.fetch_column("role_id", attachables_table_name,
                                                where=f"guild_id = {ctx.author.guild.id}")
        msg = ', '.join(r.name for r in ctx.guild.roles if r.id in attachables)
        if msg != "":
            await ctx.send(msg)
        else:
            await ctx.send("編集できる役職はありません")
