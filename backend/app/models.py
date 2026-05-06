from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


StageStatus = Literal["pending", "processing", "completed", "failed", "skipped"]
JobState = Literal["queued", "processing", "completed", "failed"]


class PipelineProgress(BaseModel):
    script: StageStatus = "pending"
    voice: StageStatus = "pending"
    animation: StageStatus = "pending"
    subtitles: StageStatus = "pending"
    video: StageStatus = "pending"


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=3)
    category: str = Field(min_length=3)
    duration_seconds: int = Field(default=180, ge=30, le=600)
    voice: str = Field(default="gtts")
    include_music: bool = True
    include_subtitles: bool = True


class GenerateResponse(BaseModel):
    job_id: str
    status: JobState
    topic: str
    progress: PipelineProgress


class ScriptSection(BaseModel):
    topic: str
    hook: str
    explanation: str
    example: str
    upsc_tip: str
    closing: str
    full_script: str
    estimated_duration: int


class VideoMetadata(BaseModel):
    job_id: str
    topic: str
    category: str
    status: JobState
    created_at: datetime = Field(default_factory=datetime.utcnow)
    output_path: str | None = None
    audio_path: str | None = None
    animation_path: str | None = None
    storyboard_path: str | None = None
    subtitles_path: str | None = None
    metadata_path: str | None = None
    error: str | None = None
    repeated_topic: bool = False
    duration_seconds: int = 180
    include_music: bool = True
    include_subtitles: bool = True


class JobStatus(BaseModel):
    job_id: str
    topic: str
    status: JobState
    progress: PipelineProgress
    output_path: str | None = None
    download_url: str | None = None
    error: str | None = None


class AgentStatus(BaseModel):
    enabled: bool = True
    topics_per_day: int = 2
    generated_today: int = 0
    last_run: str | None = None
    next_run: str | None = None


class AppConfig(BaseModel):
    videos_per_day: int = Field(default=2, ge=1, le=10)
    max_retries: int = Field(default=2, ge=0, le=5)
    default_duration_seconds: int = Field(default=180, ge=30, le=600)
    output_width: int = Field(default=1080)
    output_height: int = Field(default=1920)
    voice_engine: str = "gtts"
    include_subtitles: bool = True
    include_music: bool = True
    recycle_topics: bool = False


class TopicItem(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    keywords: list[str] = Field(default_factory=list)


class JobRecord(BaseModel):
    job_id: str
    topic_id: str | None = None
    topic: str
    category: str
    created_at: str
    status: str
    output_path: str | None = None
    repeated_topic: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
