from __future__ import annotations

import logging
from pathlib import Path


def build_job_logger(job_dir: Path, name: str) -> logging.Logger:
    logger = logging.getLogger(f"reelforge.{name}.{job_dir.name}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(job_dir / "run.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
