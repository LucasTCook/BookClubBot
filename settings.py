import pathlib
import os
import logging
import discord
from logging.config import dictConfig
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
FIND_A_GROUP_CHANNEL_ID = int(os.getenv("FIND_A_GROUP_CHANNEL_ID"))
VOTE_CHANNEL_ID = int(os.getenv("VOTE_CHANNEL_ID"))
RESULT_CHANNEL_ID = int(os.getenv("RESULT_CHANNEL_ID"))
HOME_CATEGORY_ID = int(os.getenv("HOME_CATEGORY_ID"))
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

BASE_DIR = pathlib.Path(__file__).parent

SQL_DB = BASE_DIR / "database" / os.getenv("SQL_DB")
CMDS_DIR = BASE_DIR / "bot" / "cmds"
COGS_DIR = BASE_DIR / "bot" / "cogs"

# VIDEOCMDS_DIR = BASE_DIR / "videocmds"

GUILDS_ID = discord.Object(id=int(os.getenv("GUILD")))
# FEEDBACK_CH = int(os.getenv("FEEDBACK_CH", 0))
GUILD_ID_INT = int(os.getenv("GUILD"))

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {
            "handlers": ["console"],
            "level": "INFO", 
            "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)