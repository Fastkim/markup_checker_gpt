# config.py
import os
import json
from pathlib import Path

APP_NAME = "markup_checker_ai"
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / APP_NAME
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def load_api_key() -> str:
    # 1) 환경변수 우선
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key:
        return key

    # 2) 로컬 설정파일
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return (data.get("OPENAI_API_KEY") or "").strip()
    except Exception:
        pass

    return ""

def save_api_key(key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {"OPENAI_API_KEY": key.strip(), "OPENAI_MODEL": DEFAULT_MODEL}
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
