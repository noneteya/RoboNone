from discord.ext import commands


class RoboNone(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='?',
            description='A bot that greets the user back.',
        )
        self.load_cogs()

    def load_cogs(self, unload=False):
        # ./cogs/*.py をすべてロード/アンロードする
        module_names = []
        from pathlib import Path
        for p in Path('./cogs').glob('*.py'):
            if unload:
                self.unload_extension(f'cogs.{p.stem}')
            else:
                self.load_extension(f'cogs.{p.stem}')
            module_names.append(p.stem)
        return module_names

    async def on_member_join(self, member):
        greeting_channel = self.get_channel(535622641520738314)
        await greeting_channel.send(f"{member.mention}さん、おはよう")
