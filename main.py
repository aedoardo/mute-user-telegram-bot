import os
import logging
from dotenv import load_dotenv
import sqlite3
from src.bot import Bot

DOTENV_FILE_PATH = "./configuration.env" # configuration file path

load_dotenv(dotenv_path=DOTENV_FILE_PATH)

# enable logging
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

telegram_token = os.getenv('TELEGRAM_BOT_API_TOKEN')
bot = Bot(telegram_token, os.getenv('SQLITE_DATABASE_PATH'))


if __name__ == "__main__":
    bot.main()