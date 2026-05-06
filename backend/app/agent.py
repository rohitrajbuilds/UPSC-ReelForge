from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from .config import load_config
from .models import AgentStatus, GenerateRequest
from .pipeline import PipelineService
from .topic_manager import TopicManager


class DailyGenerationAgent:
    def __init__(self, pipeline: PipelineService, topic_manager: TopicManager) -> None:
        self.pipeline = pipeline
        self.topic_manager = topic_manager
        self.scheduler = BackgroundScheduler(timezone="Asia/Calcutta")
        self.status = AgentStatus()
        self.status.enabled = True
        self._configure()

    def _configure(self) -> None:
        if not self.scheduler.get_jobs():
            self.scheduler.add_job(self.run_once, "cron", hour=7, minute=0, id="daily_generation")

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
        self.refresh_status()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def refresh_status(self) -> AgentStatus:
        config = load_config()
        self.status.topics_per_day = config.videos_per_day
        today = datetime.now().date().isoformat()
        history = self.topic_manager.load_history()
        self.status.generated_today = len([item for item in history if str(item.get("created_at", "")).startswith(today)])
        job = self.scheduler.get_job("daily_generation")
        self.status.next_run = job.next_run_time.isoformat() if job and job.next_run_time else None
        return self.status

    def run_once(self) -> list[str]:
        config = load_config()
        selected = self.topic_manager.select_topics(config, limit=config.videos_per_day)
        completed_jobs: list[str] = []
        for item in selected:
            topic = item["topic"]
            request = GenerateRequest(
                topic=topic.title,
                category=topic.category,
                duration_seconds=config.default_duration_seconds,
                voice=config.voice_engine,
                include_music=config.include_music,
                include_subtitles=config.include_subtitles,
            )
            status = self.pipeline.create_job(request)
            self.pipeline.run_job(status.job_id, request, topic_id=topic.id, repeated=item["repeated"])
            completed_jobs.append(status.job_id)

        self.status.last_run = datetime.utcnow().isoformat()
        self.refresh_status()
        return completed_jobs
