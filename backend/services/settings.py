import os
from pathlib import Path


def load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        clean_key = key.strip().lstrip("\ufeff")
        clean_value = value.strip().strip('"').strip("'")
        if not os.environ.get(clean_key):
            os.environ[clean_key] = clean_value


def get_setting(name: str, default: str = "") -> str:
    load_dotenv()
    return os.getenv(name, default)
