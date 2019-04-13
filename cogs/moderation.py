import argparse
import copy
import datetime
import re
import shlex
from typing import Union
import time

import discord
from discord.ext import commands


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


def setup(bot):
    bot.add_cog(Moderation(bot))


def is_owner(ctx):
    return ctx.author == ctx.guild.owner_id


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(is_owner)
    async def sudo(self, ctx, who: Union[discord.Member, discord.User], *, command: str):
        """Run a command as another user."""
        msg = copy.copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)
