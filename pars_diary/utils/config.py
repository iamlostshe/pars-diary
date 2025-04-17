"""Получает все константы из ".env"."""

from os import getenv

from dotenv import load_dotenv

from .pars import Parser

# Get token for telegram bot from .env
load_dotenv()

TOKEN = getenv("TOKEN_TG")
ADMINS_TG = getenv("ADMINS_TG").replace(" ", "").split(",")
GIT_URL = getenv("GIT_URL")
HF_TOKEN = getenv("HF_TOKEN")

# Setting and initializing parser
parser = Parser()
