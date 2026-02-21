import os
from pathlib import Path

from dotenv import load_dotenv


def load_env_file():
    base_dir = Path(__file__).resolve().parent
    candidates = [base_dir.parent / ".env", base_dir / ".env"]

    for env_path in candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            return


def get_env(key, default=None):
    value = os.getenv(key)
    if value is not None and str(value).strip() != "":
        return value
    return default
