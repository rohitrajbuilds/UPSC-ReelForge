# UPSC ReelForge

UPSC ReelForge is a private-repository-ready educational vertical video automation system for generating original placeholder revision content from a modular local pipeline.

## Problem Statement

UPSC educators and internal media teams often spend too much time turning syllabus topics into short-form vertical videos. Manual scripting, voice generation, visual assembly, and output tracking slow down daily publishing.

## Why This Project Exists

This project demonstrates how a local-first, no-paid-API pipeline can turn a topic queue into repeatable educational video assets while keeping orchestration, auditability, and operator control inside one internal dashboard.

## Solution Overview

The system supports two operating modes:

- Manual generation from a React dashboard.
- Autonomous daily generation from a scheduled topic queue.

All content is original placeholder educational material. No external LLM is required, and no copyrighted UPSC book content is included.

## Features

- FastAPI backend with real job orchestration
- Deterministic template-based script generation
- Local TTS with fallback behavior
- Manim-compatible storyboard generation for vertical video scenes
- MoviePy-based assembly flow with graceful error handling
- APScheduler daily agent
- Local JSON topic/config/history storage
- React + TypeScript dashboard
- Backend pytest suite
- Docker and docker-compose support

## Architecture Diagram

```text
React Dashboard / Scheduled Agent
            |
            v
       FastAPI API
            |
            v
    Pipeline Orchestrator
            |
            +--> Topic Manager --> topics.json / generated_log.json
            +--> Script Engine --> templates.json
            +--> Voice Engine --> voice asset
            +--> Animation Engine --> animation.mp4 + storyboard.json
            +--> Subtitle Engine --> .srt + .json
            +--> Video Engine --> final_video.mp4
            |
            v
     outputs/YYYY-MM-DD/job_id/
```

## Tech Stack

- Backend: Python 3.11, FastAPI, Pydantic, APScheduler, gTTS, pyttsx3 fallback, MoviePy, Pytest
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Storage: Local JSON files only

## Folder Structure

```text
upsc-reelforge/
├── backend/
├── frontend/
├── docker-compose.yml
├── Dockerfile
├── README.md
├── PROJECT_REPORT.md
├── demo_script.md
└── .gitignore
```

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Docker Setup

```bash
docker compose up --build
```

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

## Sample Input

```json
{
  "topic": "Directive Principles of State Policy",
  "category": "Polity",
  "duration_seconds": 180,
  "voice": "gtts",
  "include_music": true,
  "include_subtitles": true
}
```

## Sample Output

```json
{
  "job_id": "ec6ce7db8e7047d28ddf4c40f1c78a0e",
  "status": "queued",
  "topic": "Directive Principles of State Policy",
  "progress": {
    "script": "pending",
    "voice": "pending",
    "animation": "pending",
    "subtitles": "pending",
    "video": "pending"
  }
}
```

## Testing Commands

```bash
cd backend
pytest -q
```

## Demo Walkthrough

1. Open the dashboard and review the Generate Video page.
2. Enter a topic or use a curated one from the topic library.
3. Start generation and watch script, voice, animation, subtitle, and video stages update.
4. Download the generated MP4 when the job completes.
5. Visit Daily Agent to inspect scheduler state and trigger a run manually.
6. Review Output History to confirm auditability.

## Future Improvements

- Rich Manim scene rendering with branded motion templates
- Smarter subtitle segmentation
- Better background music layering
- Optional future integration with external LLMs and premium TTS providers

## Additional Technical Docs

- `ARCHITECTURE_FLOW.md`: end-to-end engineering walkthrough of request flow, pipeline stages, data persistence, and frontend/backend interaction.
- `CODE_REFERENCE.md`: code-level reference explaining how the app starts, what each file does, and what every major function/class is responsible for.

## Content Note

All educational copy in this project is original placeholder material generated from local deterministic templates. No copyrighted UPSC book content is included.
