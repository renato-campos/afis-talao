import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE_PATH = Path(__file__).resolve().parent / ".env"


def load_env_file():
    if ENV_FILE_PATH.exists():
        load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)


def get_env(key, default=None):
    value = os.getenv(key)
    if value is not None and str(value).strip() != "":
        return value
    return default
