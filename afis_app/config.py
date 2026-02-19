import os
from pathlib import Path


def load_env_file():
    base_dir = Path(__file__).resolve().parent
    candidates = [base_dir / ".env", base_dir.parent / ".env"]

    for env_path in candidates:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ[key] = value
        break


def get_env(primary_key, *aliases, default=None):
    for key in (primary_key, *aliases):
        value = os.getenv(key)
        if value is not None and str(value).strip() != "":
            return value
    return default
