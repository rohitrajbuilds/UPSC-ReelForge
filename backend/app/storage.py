from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path
from threading import Lock
from typing import Any


class JSONStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self._lock = Lock()

    def read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return default

    def write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            fd, temp_path = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, indent=2, ensure_ascii=False)
                os.replace(temp_path, path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def ensure_job_dir(self, outputs_dir: Path, job_id: str, run_date: date | None = None) -> Path:
        stamp = (run_date or date.today()).isoformat()
        target = outputs_dir / stamp / job_id
        target.mkdir(parents=True, exist_ok=True)
        return target

    def save_job_metadata(self, job_dir: Path, payload: dict[str, Any]) -> Path:
        metadata_path = job_dir / "metadata.json"
        self.write_json(metadata_path, payload)
        return metadata_path

    def append_history(self, history_path: Path, record: dict[str, Any]) -> None:
        history = self.read_json(history_path, default=[])
        history.append(record)
        self.write_json(history_path, history)
