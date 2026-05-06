from __future__ import annotations

from pathlib import Path

from .models import AppConfig
from .storage import JSONStorage


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CONFIG_PATH = DATA_DIR / "config.json"
TOPICS_PATH = DATA_DIR / "topics.json"
TEMPLATES_PATH = DATA_DIR / "templates.json"
GENERATED_LOG_PATH = DATA_DIR / "generated_log.json"

storage = JSONStorage(BASE_DIR)


def load_config() -> AppConfig:
    payload = storage.read_json(CONFIG_PATH, default={})
    return AppConfig(**payload)


def save_config(config: AppConfig) -> AppConfig:
    storage.write_json(CONFIG_PATH, config.model_dump())
    return config
