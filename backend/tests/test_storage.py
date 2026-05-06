from pathlib import Path

from app.storage import JSONStorage


def test_json_read_write_roundtrip(tmp_path):
    storage = JSONStorage(tmp_path)
    path = tmp_path / "sample.json"
    payload = {"name": "UPSC ReelForge"}
    storage.write_json(path, payload)

    assert storage.read_json(path, {}) == payload


def test_missing_json_returns_default(tmp_path):
    storage = JSONStorage(tmp_path)
    assert storage.read_json(tmp_path / "missing.json", default=[]) == []


def test_output_folder_created(tmp_path):
    storage = JSONStorage(tmp_path)
    output_dir = tmp_path / "outputs"
    target = storage.ensure_job_dir(output_dir, "job-123")
    assert target.exists()
    assert target.name == "job-123"
