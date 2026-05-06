from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from threading import Thread

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .agent import DailyGenerationAgent
from .animation_engine import AnimationEngine
from .config import GENERATED_LOG_PATH, OUTPUTS_DIR, load_config, save_config, storage
from .models import AppConfig, GenerateRequest, GenerateResponse
from .pipeline import PipelineService
from .script_engine import ScriptEngine
from .subtitle_engine import SubtitleEngine
from .topic_manager import TopicManager
from .video_engine import VideoEngine
from .voice_engine import VoiceEngine


script_engine = ScriptEngine(storage)
voice_engine = VoiceEngine()
animation_engine = AnimationEngine()
subtitle_engine = SubtitleEngine()
video_engine = VideoEngine()
topic_manager = TopicManager(storage)
pipeline_service = PipelineService(
    storage=storage,
    script_engine=script_engine,
    voice_engine=voice_engine,
    animation_engine=animation_engine,
    subtitle_engine=subtitle_engine,
    video_engine=video_engine,
    max_retries=load_config().max_retries,
)
agent_service = DailyGenerationAgent(pipeline_service, topic_manager)


@asynccontextmanager
async def lifespan(_: FastAPI):
    agent_service.start()
    yield
    agent_service.shutdown()


app = FastAPI(title="UPSC ReelForge", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "UPSC ReelForge",
        "description": "Educational vertical video automation system",
    }


@app.post("/api/generate", response_model=GenerateResponse)
def generate_video(request: GenerateRequest) -> GenerateResponse:
    status = pipeline_service.create_job(request)

    def _runner() -> None:
        pipeline_service.run_job(status.job_id, request)

    Thread(target=_runner, daemon=True).start()
    return GenerateResponse(
        job_id=status.job_id,
        status="queued",
        topic=request.topic,
        progress=status.progress,
    )


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = pipeline_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/download/{job_id}")
def download_job(job_id: str):
    job = pipeline_service.get_job(job_id)
    if not job or not job.output_path:
        raise HTTPException(status_code=404, detail="Output not available")
    path = Path(job.output_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    return FileResponse(path, media_type="video/mp4", filename=f"{job_id}.mp4")


@app.get("/api/topics")
def get_topics(category: str | None = None):
    return [topic.model_dump() for topic in topic_manager.get_topics(category)]


@app.post("/api/agent/run-once")
def run_agent_once():
    jobs = agent_service.run_once()
    return {"status": "completed", "job_ids": jobs}


@app.get("/api/agent/status")
def get_agent_status():
    return agent_service.refresh_status().model_dump()


@app.get("/api/history")
def get_history():
    return storage.read_json(GENERATED_LOG_PATH, default=[])


@app.get("/api/config")
def get_config():
    return load_config().model_dump()


@app.post("/api/config")
def update_config(config: AppConfig):
    saved = save_config(config)
    agent_service.refresh_status()
    return saved.model_dump()
