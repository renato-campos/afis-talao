import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = PROJECT_ROOT / "assets" / ".env"


def load_env_file():
    """Carrega variaveis de ambiente do arquivo assets/.env quando existir."""
    if ENV_FILE_PATH.exists():
        load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)


def get_env(key, default=None):
    """Retorna variavel de ambiente nao vazia ou valor padrao."""
    value = os.getenv(key)
    if value is not None and str(value).strip() != "":
        return value
    return default
