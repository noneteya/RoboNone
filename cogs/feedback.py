import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(Feedback(bot))


class Feedback:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        none = self.bot.get_user(476172941692895232)

        if message.author == none and message.content.startswith("."):
            message = message.content.split()[1:]

            target = self.bot.get_user(int(message[0]))
            await target.send(message[1])

        if isinstance(message.channel, discord.abc.PrivateChannel):
            if message.content is not "":
                await none.send(f"{message.author} : **{message.content}**")
            else:
                await none.send(f"{message.author} : ")

            if message.attachments is not None:
                m = "Attachments : \n"

                for attachment in message.attachments:
                    m += f"{attachment.url}\n"

                await none.send(m)


