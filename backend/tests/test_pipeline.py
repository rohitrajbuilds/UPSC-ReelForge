from pathlib import Path

from app.models import GenerateRequest
from app.pipeline import PipelineService
from app.script_engine import ScriptEngine
from app.storage import JSONStorage
from app.subtitle_engine import SubtitleEngine


class FakeVoiceEngine:
    def generate(self, script_text, output_dir, engine_name="gtts"):
        path = output_dir / "voice.wav"
        path.write_bytes(b"voice")
        return {"engine": engine_name, "audio_path": str(path), "duration_seconds": 60}


class FakeAnimationEngine:
    def generate(self, topic, category, script, output_dir):
        animation = output_dir / "animation.mp4"
        storyboard = output_dir / "storyboard.json"
        animation.write_bytes(b"video")
        storyboard.write_text("{}", encoding="utf-8")
        return {"animation_path": str(animation), "storyboard_path": str(storyboard), "status": "mocked"}


class FakeVideoEngine:
    def assemble(self, output_dir, animation_path, audio_path, include_music, subtitles_path=None):
        final_path = output_dir / "final_video.mp4"
        final_path.write_bytes(b"final")
        return {"final_video_path": str(final_path)}


class FailingVideoEngine:
    def assemble(self, output_dir, animation_path, audio_path, include_music, subtitles_path=None):
        raise RuntimeError("movie assembly failed")


def make_pipeline(tmp_path, video_engine):
    storage = JSONStorage(tmp_path)
    templates_path = Path(__file__).resolve().parents[1] / "data" / "templates.json"
    script_engine = ScriptEngine(storage, templates_path)
    return PipelineService(
        storage=storage,
        script_engine=script_engine,
        voice_engine=FakeVoiceEngine(),
        animation_engine=FakeAnimationEngine(),
        subtitle_engine=SubtitleEngine(),
        video_engine=video_engine,
        outputs_dir=tmp_path / "outputs",
        history_path=tmp_path / "generated_log.json",
    )


def test_pipeline_creates_job_and_metadata(tmp_path):
    pipeline = make_pipeline(tmp_path, FakeVideoEngine())
    request = GenerateRequest(topic="Fundamental Rights", category="Polity", duration_seconds=180)
    job = pipeline.create_job(request)
    result = pipeline.run_job(job.job_id, request)

    assert job.job_id
    assert result.status == "completed"
    metadata_path = next((tmp_path / "outputs").rglob("metadata.json"))
    assert metadata_path.exists()


def test_pipeline_updates_progress(tmp_path):
    pipeline = make_pipeline(tmp_path, FakeVideoEngine())
    request = GenerateRequest(topic="Inflation and Its Measurement", category="Economy", duration_seconds=180)
    job = pipeline.create_job(request)
    result = pipeline.run_job(job.job_id, request)

    assert result.progress.script == "completed"
    assert result.progress.video == "completed"


def test_pipeline_handles_failed_stage(tmp_path):
    pipeline = make_pipeline(tmp_path, FailingVideoEngine())
    request = GenerateRequest(topic="Wetland Conservation", category="Environment", duration_seconds=180)
    job = pipeline.create_job(request)
    result = pipeline.run_job(job.job_id, request)

    assert result.status == "failed"
    assert result.progress.video == "failed"
