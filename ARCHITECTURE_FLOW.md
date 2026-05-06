# UPSC ReelForge End-to-End Architecture and Code Flow

## Purpose

This document explains how UPSC ReelForge works from the moment a topic is selected to the point where a final vertical video is generated, logged, and made available for download. It is intended as an engineering walkthrough for reviewers, collaborators, and future maintainers.

## System Overview

UPSC ReelForge is a local-first educational video automation system with two entry points:

1. Manual generation from the React dashboard.
2. Autonomous daily generation from the APScheduler-driven agent.

Both paths converge into the same backend orchestration layer, so the business logic is centralized and reusable.

## High-Level Architecture

```text
                +----------------------+
                |   React Dashboard    |
                |  Manual UI Trigger   |
                +----------+-----------+
                           |
                           v
                    +-------------+
                    |  FastAPI    |
                    |  API Layer  |
                    +------+------+        +----------------------+
                           |               | APScheduler Agent    |
                           |               | Daily Auto Trigger   |
                           |               +----------+-----------+
                           |                          |
                           +------------+-------------+
                                        |
                                        v
                              +-------------------+
                              | Pipeline Service  |
                              | Orchestration     |
                              +---------+---------+
                                        |
          +-----------------------------+------------------------------+
          |             |                |             |               |
          v             v                v             v               v
   Topic Manager   Script Engine    Voice Engine  Subtitle Engine  Animation Engine
          |             |                |             |               |
          +-------------+----------------+-------------+---------------+
                                        |
                                        v
                                 Video Engine
                                        |
                                        v
                           outputs/YYYY-MM-DD/{job_id}/
                                        |
                                        v
                          metadata.json + generated_log.json
```

## Repository Areas

### Root

- `README.md`: project overview and setup.
- `PROJECT_REPORT.md`: polished report for review/submission.
- `demo_script.md`: 2-minute presentation walkthrough.
- `ARCHITECTURE_FLOW.md`: this technical flow explanation.
- `docker-compose.yml`: local multi-service setup.
- `Dockerfile`: root-level backend health service image.

### Backend

- `backend/app/main.py`: FastAPI app, route registration, service bootstrapping.
- `backend/app/pipeline.py`: shared orchestration for all generation jobs.
- `backend/app/agent.py`: daily autonomous generation agent.
- `backend/app/topic_manager.py`: topic selection and duplicate-prevention logic.
- `backend/app/script_engine.py`: deterministic content generation.
- `backend/app/voice_engine.py`: TTS and fallback audio generation.
- `backend/app/animation_engine.py`: storyboard and placeholder animation generation.
- `backend/app/subtitle_engine.py`: subtitle segmentation and timing.
- `backend/app/video_engine.py`: final media assembly.
- `backend/app/storage.py`: safe JSON persistence and output directory management.
- `backend/app/logger.py`: per-job structured logging.
- `backend/data/*.json`: local topics, templates, config, and generation history.

### Frontend

- `frontend/src/App.tsx`: dashboard state, routing by view, polling.
- `frontend/src/api.ts`: typed calls to `http://localhost:8000`.
- `frontend/src/components/*`: SaaS dashboard sections.
- `frontend/src/types.ts`: shared frontend contracts.

## End-to-End Request Flow

## 1. Manual UI Flow

The user opens the dashboard and uses the Generate Video page.

### Frontend side

1. `App.tsx` loads bootstrap data:
   - `/api/topics`
   - `/api/history`
   - `/api/config`
   - `/api/agent/status`
2. The user fills the topic form in `TopicForm.tsx`.
3. The frontend sends a `POST /api/generate` request through `api.ts`.
4. The API returns a `job_id` and an initial `queued` progress object.
5. `App.tsx` starts polling `/api/jobs/{job_id}` every 1.5 seconds.
6. `ProgressPanel.tsx` updates stage-by-stage status.
7. `VideoPreview.tsx` enables the download link when the job is completed.

### Backend side

1. `main.py` receives `GenerateRequest`.
2. `PipelineService.create_job()` creates a job id and stores in-memory status.
3. A background thread starts `PipelineService.run_job()`.
4. Each stage updates the shared `JobStatus`.
5. Final artifacts and metadata are persisted to disk.
6. `/api/jobs/{job_id}` returns the latest status snapshot to the frontend.

## 2. Autonomous Agent Flow

The daily automation path does not depend on the UI, though the UI can observe and trigger it.

1. `DailyGenerationAgent` starts with the FastAPI app lifecycle.
2. APScheduler registers a daily cron job.
3. On run, the agent reads `config.json` through `load_config()`.
4. `TopicManager.select_topics()` chooses fresh topics based on:
   - `videos_per_day`
   - used topics in `generated_log.json`
   - `recycle_topics`
5. For each selected topic, the agent creates a `GenerateRequest`.
6. The same `PipelineService` executes the generation flow.
7. `generated_today`, `last_run`, and `next_run` are exposed at `/api/agent/status`.

This keeps the scheduler thin and pushes all actual business work into the pipeline layer.

## Pipeline Stage Breakdown

## Stage 1: Topic Selection

Handled by `topic_manager.py`.

Responsibilities:

- Load local UPSC topics from `topics.json`.
- Support category filtering.
- Detect previously used topics using `generated_log.json`.
- Avoid duplicates when `recycle_topics` is false.
- Permit re-use and mark `repeated_topic=true` when recycling is enabled.

Why it matters:

This ensures the content engine behaves like a real scheduled content system rather than blindly repeating the same topic.

## Stage 2: Script Generation

Handled by `script_engine.py`.

Responsibilities:

- Load reusable local templates from `templates.json`.
- Generate deterministic original placeholder educational content.
- Produce:
  - hook
  - explanation
  - example
  - UPSC tip
  - closing
  - combined full script
  - estimated duration

Design choice:

The script engine does not call any external LLM. Instead, it uses deterministic template selection based on the topic/category seed. This keeps the output reproducible, testable, and free from paid dependency requirements.

## Stage 3: Voice Generation

Handled by `voice_engine.py`.

Responsibilities:

- Attempt speech generation with `gTTS`.
- Fall back to `pyttsx3` when requested or needed.
- Fall back again to a locally generated silent WAV placeholder if voice synthesis is unavailable.
- Return:
  - engine used
  - audio path
  - estimated duration
  - attempt count

Stored asset:

- `outputs/YYYY-MM-DD/{job_id}/voice.mp3` or `voice.wav`

Design choice:

This tiered fallback system ensures the pipeline still completes in restricted environments, which is important for CI, offline testing, and private review environments.

## Stage 4: Animation and Storyboard

Handled by `animation_engine.py`.

Responsibilities:

- Create a 1080x1920 vertical scene plan.
- Map category to a visual icon where relevant.
- Build scene sequence:
  - title
  - hook
  - explanation
  - example
  - tip
  - closing
- Save `storyboard.json`.
- Try generating a placeholder MP4 asset if rendering support is available.

Stored assets:

- `outputs/YYYY-MM-DD/{job_id}/storyboard.json`
- `outputs/YYYY-MM-DD/{job_id}/animation.mp4`

Design choice:

The engine is Manim-compatible at the design level, but safe in constrained environments. Even when rich rendering is unavailable, the storyboard remains useful for debugging, testing, and future renderer upgrades.

## Stage 5: Subtitles

Handled by `subtitle_engine.py`.

Responsibilities:

- Break the script into readable sections.
- Estimate start/end timings based on content length.
- Save:
  - `subtitles.srt`
  - `subtitles.json`

Stored assets:

- `outputs/YYYY-MM-DD/{job_id}/subtitles.srt`
- `outputs/YYYY-MM-DD/{job_id}/subtitles.json`

Design choice:

Subtitles are generated as sidecar assets so the system stays flexible even when direct subtitle burn-in is not desirable or available.

## Stage 6: Video Assembly

Handled by `video_engine.py`.

Responsibilities:

- Combine animation video and audio using MoviePy.
- Respect subtitle and music inclusion settings.
- Write the final MP4.
- Raise a meaningful error if assembly fails.

Stored asset:

- `outputs/YYYY-MM-DD/{job_id}/final_video.mp4`

Design choice:

If MoviePy or FFmpeg fails, the system preserves all intermediate outputs instead of deleting them. That makes debugging realistic and production-friendly.

## Job State and Progress Tracking

Handled mostly by `pipeline.py` and `models.py`.

The pipeline uses `PipelineProgress` with statuses:

- `pending`
- `processing`
- `completed`
- `failed`
- `skipped`

Each job also has a high-level status:

- `queued`
- `processing`
- `completed`
- `failed`

How progress is updated:

1. `create_job()` creates an in-memory `JobStatus`.
2. `run_job()` moves each stage from `pending` to `processing`.
3. On success, the stage becomes `completed`.
4. If subtitles are disabled, that stage becomes `skipped`.
5. On failure, the current stage becomes `failed` and the job is marked failed.

This is what the frontend polls and displays in the progress tracker.

## Persistence Model

Handled by `storage.py`.

### JSON files used

- `topics.json`: local topic library
- `templates.json`: script phrase templates
- `config.json`: operator settings
- `generated_log.json`: history of runs

### Job folder layout

```text
backend/outputs/
└── YYYY-MM-DD/
    └── {job_id}/
        ├── run.log
        ├── metadata.json
        ├── voice.mp3 or voice.wav
        ├── animation.mp4
        ├── storyboard.json
        ├── subtitles.srt
        ├── subtitles.json
        └── final_video.mp4
```

### Safe writes

`JSONStorage.write_json()` writes to a temp file first and then atomically replaces the target file. This reduces the risk of corrupting JSON when writes are interrupted.

## Logging Strategy

Handled by `logger.py`.

Every job gets a dedicated logger writing to:

- `outputs/YYYY-MM-DD/{job_id}/run.log`

This keeps pipeline diagnostics grouped by job instead of mixing everything into one global log.

## FastAPI Endpoint Architecture

Defined in `main.py`.

### Public routes

- `GET /`
  - service heartbeat and description

- `POST /api/generate`
  - creates a job and starts asynchronous processing

- `GET /api/jobs/{job_id}`
  - returns current progress and output info

- `GET /api/download/{job_id}`
  - returns final MP4 if available

- `GET /api/topics`
  - returns topic library from local JSON

- `POST /api/agent/run-once`
  - manually triggers the autonomous generation agent

- `GET /api/agent/status`
  - returns scheduler state and counters

- `GET /api/history`
  - returns `generated_log.json`

- `GET /api/config`
  - returns local config

- `POST /api/config`
  - updates local config

## Frontend Architecture

The frontend is intentionally built as a small internal SaaS dashboard rather than a single-page form.

### `App.tsx`

Acts as the orchestration shell:

- bootstraps API state
- manages selected page
- starts/stops job polling
- stores current job, history, config, topics, and agent status

### Component responsibilities

- `Sidebar.tsx`: left navigation
- `Header.tsx`: product framing and dashboard summary
- `TopicForm.tsx`: manual generation controls
- `ProgressPanel.tsx`: per-stage status display
- `VideoPreview.tsx`: final output panel
- `OutputHistory.tsx`: generated jobs table
- `AgentStatus.tsx`: scheduler information and manual run trigger
- `SettingsPanel.tsx`: local config editor

### API coupling

All HTTP calls are centralized in `api.ts`, which keeps UI components focused on rendering and interaction rather than fetch boilerplate.

## Error Handling Philosophy

The project is designed to fail gracefully.

Examples:

- TTS failure falls back to another engine or silent audio.
- Animation failure still preserves the storyboard.
- Video assembly failure preserves intermediate files.
- Missing JSON files return safe defaults.
- The frontend shows empty states and error banners instead of crashing.

This is important for a private repository review because it demonstrates operational realism rather than ideal-path-only code.

## Testing Strategy

The test suite focuses on behavior, not heavy media rendering.

### What is tested

- `test_script_engine.py`
  - script structure and deterministic output

- `test_topic_manager.py`
  - loading, duplicate avoidance, and recycle behavior

- `test_pipeline.py`
  - job creation, progress changes, failure handling, metadata creation

- `test_storage.py`
  - JSON persistence and output folder creation

- `test_api.py`
  - key endpoint responses

### Why mocks/fallbacks are used

Media generation libraries can be slow or environment-sensitive. The tests replace heavy stages with lightweight fake implementations so the suite stays fast and reliable.

## Deployment and Runtime Model

### Local development

- Backend runs on `localhost:8000`
- Frontend runs on `localhost:5173`

### Docker

- `backend/Dockerfile` builds the backend API container
- root `Dockerfile` provides a backend-centric repository-level image
- `docker-compose.yml` runs backend and frontend together

## End-to-End Summary

In one sentence:

UPSC ReelForge takes a locally curated educational topic, turns it into a deterministic original script, attempts voice generation with fallbacks, builds a vertical storyboard and animation asset, generates subtitles, assembles a final MP4, stores all outputs and metadata on disk, and exposes the whole lifecycle through a production-style dashboard and API.

## Why This Architecture Is Strong for Review

- Real modular backend, not a monolithic script
- Shared pipeline for both manual and scheduled flows
- Clean separation of concerns across services
- Local-first and no paid dependency requirement
- Graceful degradation in constrained environments
- Persistent audit trail through JSON and job folders
- Tests for business logic and APIs
- Frontend tied to live backend responses

This combination makes the project look and behave like a serious internal automation tool instead of a toy prototype.
