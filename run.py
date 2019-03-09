# -*- coding=utf-8 -*-
from bot import ManagementBot
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

if not os.getenv("ON_SERVER"):
    # ローカルで走らせる場合
    env_path = Path('.') / '.env.local'
    load_dotenv(dotenv_path=env_path)
print(os.getenv("BOT_TOKEN"), file=sys.stderr)
sys.stderr.flush()

management_bot = ManagementBot()
management_bot.run(os.getenv("BOT_TOKEN"))
