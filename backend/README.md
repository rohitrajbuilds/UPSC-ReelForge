# UPSC ReelForge Backend

The backend is a FastAPI service that manages topic selection, deterministic script generation, audio fallback handling, animation asset creation, subtitle generation, video assembly, and autonomous scheduled runs.

## Architecture

- `main.py`: API layer and application lifecycle.
- `pipeline.py`: Central orchestration for script, voice, animation, subtitles, and final video.
- `agent.py`: APScheduler-based daily automation agent.
- `topic_manager.py`: Topic library loading and duplicate-avoidance rules.
- `storage.py`: Safe JSON read/write and job output directory creation.
- `voice_engine.py`, `animation_engine.py`, `subtitle_engine.py`, `video_engine.py`: Media stages with graceful fallbacks.

## Pipeline

The generation flow is:

1. Validate request and create a job id.
2. Generate original placeholder UPSC-style educational script from templates.
3. Generate voice with `gTTS`, then fall back to `pyttsx3` or a silent placeholder file.
4. Generate animation assets and storyboard JSON for a vertical 1080x1920 format.
5. Generate readable subtitles.
6. Assemble the final MP4 with MoviePy.
7. Save metadata and append generation history.

## Agent

The daily agent reads `backend/data/config.json`, picks unused topics, and runs the same pipeline used by the manual UI flow. When topics are exhausted, recycle mode can be enabled from config.

## Media Generation

- If real TTS fails, the system still completes by using local fallback output.
- If rich animation rendering is unavailable, a storyboard and placeholder animation asset are still created.
- If final assembly fails, intermediate assets remain on disk for debugging.

## API Endpoints

- `GET /`
- `POST /api/generate`
- `GET /api/jobs/{job_id}`
- `GET /api/download/{job_id}`
- `GET /api/topics`
- `POST /api/agent/run-once`
- `GET /api/agent/status`
- `GET /api/history`
- `GET /api/config`
- `POST /api/config`

## Testing

```bash
cd backend
pytest -q
```
