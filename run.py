# -*- coding=utf-8 -*-
from bot import RoboNone
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

if not os.getenv("ON_SERVER"):
    # ローカルで走らせる場合
    env_path = Path('.') / '.env.local'
    load_dotenv(dotenv_path=env_path)
sys.stderr.flush()

robo_none = RoboNone()
robo_none.run(os.getenv("BOT_TOKEN"))
