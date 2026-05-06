from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock
from uuid import uuid4

from .animation_engine import AnimationEngine
from .config import GENERATED_LOG_PATH, OUTPUTS_DIR
from .logger import build_job_logger
from .models import GenerateRequest, JobRecord, JobStatus, PipelineProgress
from .script_engine import ScriptEngine
from .storage import JSONStorage
from .subtitle_engine import SubtitleEngine
from .video_engine import VideoEngine
from .voice_engine import VoiceEngine


class PipelineService:
    def __init__(
        self,
        storage: JSONStorage,
        script_engine: ScriptEngine,
        voice_engine: VoiceEngine,
        animation_engine: AnimationEngine,
        subtitle_engine: SubtitleEngine,
        video_engine: VideoEngine,
        outputs_dir: Path = OUTPUTS_DIR,
        history_path: Path = GENERATED_LOG_PATH,
        max_retries: int = 2,
    ) -> None:
        self.storage = storage
        self.script_engine = script_engine
        self.voice_engine = voice_engine
        self.animation_engine = animation_engine
        self.subtitle_engine = subtitle_engine
        self.video_engine = video_engine
        self.outputs_dir = outputs_dir
        self.history_path = history_path
        self.max_retries = max_retries
        self._jobs: dict[str, JobStatus] = {}
        self._lock = Lock()

    def create_job(self, request: GenerateRequest) -> JobStatus:
        job_id = uuid4().hex
        status = JobStatus(
            job_id=job_id,
            topic=request.topic,
            status="queued",
            progress=PipelineProgress(),
        )
        with self._lock:
            self._jobs[job_id] = status
        return status

    def list_jobs(self) -> dict[str, JobStatus]:
        return self._jobs

    def get_job(self, job_id: str) -> JobStatus | None:
        return self._jobs.get(job_id)

    def _save_status(self, status: JobStatus) -> None:
        with self._lock:
            self._jobs[status.job_id] = status

    def _set_stage(self, status: JobStatus, stage: str, value: str) -> None:
        setattr(status.progress, stage, value)
        self._save_status(status)

    def run_job(self, job_id: str, request: GenerateRequest, topic_id: str | None = None, repeated: bool = False) -> JobStatus:
        status = self._jobs[job_id]
        status.status = "processing"
        self._save_status(status)

        job_dir = self.storage.ensure_job_dir(self.outputs_dir, job_id)
        logger = build_job_logger(job_dir, "pipeline")
        logger.info("Starting job for topic '%s'", request.topic)

        metadata = {
            "job_id": job_id,
            "topic": request.topic,
            "category": request.category,
            "created_at": datetime.utcnow().isoformat(),
            "status": "processing",
            "repeated_topic": repeated,
        }

        try:
            self._set_stage(status, "script", "processing")
            script = self.script_engine.generate(request.topic, request.category, request.duration_seconds)
            self._set_stage(status, "script", "completed")
            metadata["script"] = script.model_dump()
            logger.info("Script generation completed")

            self._set_stage(status, "voice", "processing")
            voice_result = self.voice_engine.generate(script.full_script, job_dir, request.voice)
            self._set_stage(status, "voice", "completed")
            metadata["voice"] = voice_result
            logger.info("Voice generation completed using %s", voice_result["engine"])

            self._set_stage(status, "animation", "processing")
            animation_result = self.animation_engine.generate(request.topic, request.category, script, job_dir)
            self._set_stage(status, "animation", "completed")
            metadata["animation"] = animation_result
            logger.info("Animation generation completed with %s", animation_result["status"])

            subtitles_result = None
            if request.include_subtitles:
                self._set_stage(status, "subtitles", "processing")
                subtitles_result = self.subtitle_engine.generate(script, job_dir)
                self._set_stage(status, "subtitles", "completed")
                metadata["subtitles"] = subtitles_result
                logger.info("Subtitle generation completed")
            else:
                self._set_stage(status, "subtitles", "skipped")

            self._set_stage(status, "video", "processing")
            video_result = self.video_engine.assemble(
                job_dir,
                animation_result["animation_path"],
                voice_result["audio_path"],
                request.include_music,
                subtitles_result["srt_path"] if subtitles_result else None,
            )
            self._set_stage(status, "video", "completed")
            metadata["video"] = video_result
            logger.info("Final video assembly completed")

            status.status = "completed"
            status.output_path = video_result["final_video_path"]
            status.download_url = f"/api/download/{job_id}"
            metadata["status"] = "completed"
            metadata["output_path"] = status.output_path
            metadata["metadata_path"] = str(job_dir / "metadata.json")
        except Exception as exc:
            logger.exception("Job failed: %s", exc)
            status.status = "failed"
            status.error = str(exc)
            metadata["status"] = "failed"
            metadata["error"] = str(exc)
            for stage in ["script", "voice", "animation", "subtitles", "video"]:
                if getattr(status.progress, stage) == "processing":
                    self._set_stage(status, stage, "failed")
                    break
        finally:
            self._save_status(status)
            self.storage.save_job_metadata(job_dir, metadata)
            record = JobRecord(
                job_id=job_id,
                topic_id=topic_id,
                topic=request.topic,
                category=request.category,
                created_at=metadata["created_at"],
                status=status.status,
                output_path=status.output_path,
                repeated_topic=repeated,
                metadata={"job_dir": str(job_dir)},
            )
            self.storage.append_history(self.history_path, record.model_dump())
        return status
