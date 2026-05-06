# UPSC ReelForge Code Reference

## Purpose

This document is a code-level reference for UPSC ReelForge. It explains:

1. How the project starts and runs from the beginning.
2. What every major file is responsible for.
3. What each class, function, and important method does.
4. How frontend and backend pieces connect end to end.

This is intentionally more implementation-focused than `README.md`, `PROJECT_REPORT.md`, or `ARCHITECTURE_FLOW.md`.

## How The Project Starts

## 1. Development startup

### Backend startup path

When you run:

```bash
cd backend
uvicorn app.main:app --reload
```

The startup path is:

1. Python imports `app.main`.
2. `main.py` imports and instantiates shared services:
   - `ScriptEngine`
   - `VoiceEngine`
   - `AnimationEngine`
   - `SubtitleEngine`
   - `VideoEngine`
   - `TopicManager`
   - `PipelineService`
   - `DailyGenerationAgent`
3. FastAPI app is created.
4. The lifespan handler starts the scheduler agent.
5. API routes become available on `http://localhost:8000`.

### Frontend startup path

When you run:

```bash
cd frontend
npm run dev
```

The startup path is:

1. Vite serves `index.html`.
2. `src/main.tsx` mounts React.
3. `App.tsx` renders the dashboard.
4. `App.tsx` immediately loads:
   - topics
   - history
   - config
   - agent status
5. The UI becomes interactive and can call backend APIs.

## 2. Runtime generation flow

There are two ways the code begins processing content:

### Manual start

1. User clicks `Generate Video`.
2. Frontend sends `POST /api/generate`.
3. Backend creates a job.
4. Background thread starts the pipeline.
5. Frontend polls job status until completion.

### Scheduled start

1. APScheduler runs `DailyGenerationAgent.run_once()`.
2. The agent picks topics from the local queue.
3. The agent creates generation requests.
4. The same pipeline executes for each topic.

This is a key architectural decision: manual and scheduled jobs share the same core code path.

## Root-Level Files

## `.gitignore`

Purpose:

- Excludes Python caches, Node modules, generated outputs, logs, media files, and local build artifacts.

Why it exists:

- Keeps the repository clean and review-friendly.

## `README.md`

Purpose:

- Main product-facing overview of the project.

Contents:

- problem statement
- architecture summary
- setup commands
- endpoint list
- testing and demo guidance

## `PROJECT_REPORT.md`

Purpose:

- Formal written project report for assessment, review, or submission.

## `ARCHITECTURE_FLOW.md`

Purpose:

- End-to-end engineering flow and architecture explanation.

## `CODE_REFERENCE.md`

Purpose:

- This file; a code-level reference.

## `demo_script.md`

Purpose:

- Presentation script for showing the system in action.

## `docker-compose.yml`

Purpose:

- Runs backend and frontend together in containers.

## Root `Dockerfile`

Purpose:

- Builds a backend-only root image suitable for repository-level execution checks.

## Backend Code Reference

## `backend/app/__init__.py`

Purpose:

- Marks `app` as a Python package.

## `backend/app/models.py`

This file defines the Pydantic data contracts used by the API and pipeline.

### `StageStatus`

Type alias for per-stage progress states:

- `pending`
- `processing`
- `completed`
- `failed`
- `skipped`

### `JobState`

Type alias for top-level job states:

- `queued`
- `processing`
- `completed`
- `failed`

### `PipelineProgress`

Purpose:

- Tracks stage-by-stage job progress.

Fields:

- `script`
- `voice`
- `animation`
- `subtitles`
- `video`

### `GenerateRequest`

Purpose:

- Input schema for video generation requests.

Fields:

- `topic`
- `category`
- `duration_seconds`
- `voice`
- `include_music`
- `include_subtitles`

### `GenerateResponse`

Purpose:

- Initial response returned when a job is queued.

Fields:

- `job_id`
- `status`
- `topic`
- `progress`

### `ScriptSection`

Purpose:

- Structured output from the script engine.

Fields:

- `topic`
- `hook`
- `explanation`
- `example`
- `upsc_tip`
- `closing`
- `full_script`
- `estimated_duration`

### `VideoMetadata`

Purpose:

- Represents video-generation metadata for a job.

Note:

- The current implementation mostly uses a plain metadata dictionary during pipeline execution, but this model remains useful for future consistency and expansion.

### `JobStatus`

Purpose:

- Tracks the current state of a job exposed through `/api/jobs/{job_id}`.

Fields:

- `job_id`
- `topic`
- `status`
- `progress`
- `output_path`
- `download_url`
- `error`

### `AgentStatus`

Purpose:

- API model for agent health and activity.

Fields:

- `enabled`
- `topics_per_day`
- `generated_today`
- `last_run`
- `next_run`

### `AppConfig`

Purpose:

- Typed representation of local app configuration.

Fields:

- `videos_per_day`
- `max_retries`
- `default_duration_seconds`
- `output_width`
- `output_height`
- `voice_engine`
- `include_subtitles`
- `include_music`
- `recycle_topics`

### `TopicItem`

Purpose:

- Represents a curated topic entry loaded from `topics.json`.

### `JobRecord`

Purpose:

- Structure used when appending generation history into `generated_log.json`.

## `backend/app/storage.py`

This file provides low-level safe JSON persistence and output folder creation.

### `class JSONStorage`

Purpose:

- Central utility for file-based storage operations.

### `JSONStorage.__init__(base_dir)`

Purpose:

- Stores base directory reference and initializes a thread lock.

Why the lock matters:

- Prevents concurrent write corruption when multiple operations attempt JSON writes.

### `JSONStorage.read_json(path, default)`

Purpose:

- Safely reads JSON and returns `default` if the file is missing or invalid.

Used by:

- config loading
- topic loading
- history loading

### `JSONStorage.write_json(path, payload)`

Purpose:

- Writes JSON atomically using a temp file and `os.replace`.

Why it matters:

- Reduces risk of partial writes or corrupted JSON.

### `JSONStorage.ensure_job_dir(outputs_dir, job_id, run_date=None)`

Purpose:

- Creates the dated output directory for a job.

Output pattern:

- `outputs/YYYY-MM-DD/{job_id}`

### `JSONStorage.save_job_metadata(job_dir, payload)`

Purpose:

- Writes `metadata.json` for a job and returns the path.

### `JSONStorage.append_history(history_path, record)`

Purpose:

- Reads history, appends a new record, and writes the full JSON list back.

## `backend/app/config.py`

This file centralizes static paths and config loading.

### Module constants

- `BASE_DIR`
- `DATA_DIR`
- `OUTPUTS_DIR`
- `CONFIG_PATH`
- `TOPICS_PATH`
- `TEMPLATES_PATH`
- `GENERATED_LOG_PATH`

Purpose:

- Prevents path duplication across modules.

### `storage`

Purpose:

- Shared `JSONStorage` instance used across the backend.

### `load_config()`

Purpose:

- Loads `config.json` and returns an `AppConfig`.

### `save_config(config)`

Purpose:

- Writes new config values to `config.json` and returns the saved object.

## `backend/app/logger.py`

This file builds per-job loggers.

### `build_job_logger(job_dir, name)`

Purpose:

- Creates a configured logger for a specific job.

Behavior:

- writes to `run.log`
- also writes to console
- avoids duplicate handlers if called again

## `backend/app/topic_manager.py`

This file manages the local topic library and reuse rules.

### `VALID_CATEGORIES`

Purpose:

- Enumerates supported topic categories.

### `class TopicManager`

Purpose:

- Loads topics, reads generation history, and selects fresh or recycled topics.

### `TopicManager.__init__(storage, topics_path=..., history_path=...)`

Purpose:

- Stores data sources so the manager can be reused in tests with temporary files.

### `TopicManager.load_topics()`

Purpose:

- Reads topic entries from `topics.json` and converts them into `TopicItem` models.

### `TopicManager.load_history()`

Purpose:

- Reads `generated_log.json`.

### `TopicManager.get_topics(category=None)`

Purpose:

- Returns all topics or a category-filtered subset.

### `TopicManager._used_ids()`

Purpose:

- Internal helper to build a set of previously generated `topic_id` values.

### `TopicManager.select_topics(config, category=None, limit=1)`

Purpose:

- Picks available topics according to config rules.

Logic:

1. Load topics.
2. Build used topic set.
3. Prefer unused topics.
4. If none remain and `recycle_topics` is true, reuse old ones.
5. Return selected topics plus a `repeated` flag.

This is one of the main business-logic functions in the project.

### `TopicManager.category_counts()`

Purpose:

- Returns a category-to-count summary for available topics.

### `TopicManager.has_topic(title)`

Purpose:

- Checks whether a title already exists in the topic library.

## `backend/app/script_engine.py`

This file produces deterministic educational script sections.

### `class ScriptEngine`

Purpose:

- Generates original placeholder scripts from local templates.

### `ScriptEngine.__init__(storage, templates_path=...)`

Purpose:

- Loads template JSON and stores it for reuse.

### `ScriptEngine._choose(options, seed)`

Purpose:

- Deterministically selects one template using a simple hash-like seed mechanism.

Why this exists:

- Keeps output stable across repeated runs for the same input.

### `ScriptEngine.generate(topic, category, duration_seconds)`

Purpose:

- Produces a complete `ScriptSection`.

Behavior:

1. Builds a seed from topic/category/duration.
2. Selects one template for each script section.
3. Formats section text with placeholders.
4. Builds a full script string.
5. Estimates the speech duration.

Output:

- `ScriptSection`

## `backend/app/voice_engine.py`

This file handles audio generation and fallbacks.

### `class VoiceEngine`

Purpose:

- Converts script text to audio or a safe fallback file.

### `VoiceEngine.__init__(max_retries=2)`

Purpose:

- Stores retry count.

### `VoiceEngine._build_silent_wav(path, duration_seconds)`

Purpose:

- Creates a silent WAV file for environments where real TTS is unavailable.

Why it matters:

- Lets the pipeline keep working without external services.

### `VoiceEngine.generate(script_text, output_dir, engine_name="gtts")`

Purpose:

- Main audio generation entry point.

Behavior:

1. Estimate voice duration.
2. Try `gTTS` if selected.
3. Try `pyttsx3` if selected.
4. If those fail, generate silent fallback audio.
5. Return metadata describing what happened.

Return keys:

- `engine`
- `audio_path`
- `duration_seconds`
- `attempt`
- optional `warning`

## `backend/app/animation_engine.py`

This file produces the visual scene plan and optional placeholder video.

### `ICON_MAP`

Purpose:

- Maps topic categories to symbolic icons used in storyboards.

### `class AnimationEngine`

Purpose:

- Creates a vertical animation plan for educational shorts.

### `AnimationEngine.__init__(width=1080, height=1920)`

Purpose:

- Stores target vertical resolution.

### `AnimationEngine._storyboard(topic, category, script)`

Purpose:

- Builds a JSON-friendly storyboard with:
  - layout
  - category icon
  - six planned scenes
  - transition styles

### `AnimationEngine.generate(topic, category, script, output_dir)`

Purpose:

- Writes storyboard JSON and attempts placeholder MP4 generation.

Behavior:

1. Build storyboard.
2. Save `storyboard.json`.
3. Try to create a simple placeholder clip using MoviePy.
4. If that fails, write an empty placeholder file and continue.

Return keys:

- `animation_path`
- `storyboard_path`
- `status`

## `backend/app/subtitle_engine.py`

This file creates subtitle assets.

### `class SubtitleEngine`

Purpose:

- Converts structured script sections into timed subtitle files.

### `SubtitleEngine._chunks(script)`

Purpose:

- Splits the script into logical labeled chunks.

### `SubtitleEngine._fmt(seconds)`

Purpose:

- Converts integer seconds into SRT timestamp format.

### `SubtitleEngine.generate(script, output_dir)`

Purpose:

- Writes both `.srt` and `.json` subtitle outputs.

Behavior:

1. Split the script into chunks.
2. Estimate section durations based on word count.
3. Build SRT entries.
4. Build JSON subtitle objects.
5. Save both files.

Return keys:

- `srt_path`
- `json_path`

## `backend/app/video_engine.py`

This file assembles final video output.

### `class VideoAssemblyError`

Purpose:

- Custom exception raised when final assembly fails.

### `class VideoEngine`

Purpose:

- Combines audio and visual assets into the final MP4.

### `VideoEngine.assemble(output_dir, animation_path, audio_path, include_music, subtitles_path=None)`

Purpose:

- Main final assembly method.

Behavior:

1. Load animation file if present and non-empty.
2. Otherwise create a fallback visual clip.
3. Load audio.
4. Attach audio to the base clip.
5. Export `final_video.mp4`.
6. Raise `VideoAssemblyError` if anything fails.

Return keys:

- `final_video_path`
- `include_music`
- `subtitles_path`

## `backend/app/pipeline.py`

This is the core orchestration layer of the application.

### `class PipelineService`

Purpose:

- Runs the full content generation pipeline and tracks jobs.

### `PipelineService.__init__(...)`

Purpose:

- Receives all engine dependencies and storage paths.

Why dependency injection matters:

- Makes the service easy to test with fake engines.

### `PipelineService.create_job(request)`

Purpose:

- Creates a new job id and in-memory `JobStatus`.

Used by:

- manual generation endpoint
- agent flow

### `PipelineService.list_jobs()`

Purpose:

- Returns the in-memory job dictionary.

### `PipelineService.get_job(job_id)`

Purpose:

- Fetches a single in-memory job by id.

### `PipelineService._save_status(status)`

Purpose:

- Internal helper to persist an updated `JobStatus` in memory.

### `PipelineService._set_stage(status, stage, value)`

Purpose:

- Internal helper to update stage progress and save it.

### `PipelineService.run_job(job_id, request, topic_id=None, repeated=False)`

Purpose:

- Executes the full pipeline for a job.

This is the single most important function in the backend.

Step-by-step behavior:

1. Mark job as `processing`.
2. Create job output directory.
3. Create per-job logger.
4. Initialize metadata dictionary.
5. Run script stage.
6. Run voice stage.
7. Run animation stage.
8. Run subtitle stage unless disabled.
9. Run video assembly stage.
10. Mark job `completed` and set download URL.
11. On failure:
    - log exception
    - mark job failed
    - mark current stage failed
12. In all cases:
    - save `metadata.json`
    - append to history log
    - return final status

Why it matters:

- It is the shared business workflow for both UI-triggered and scheduler-triggered jobs.

## `backend/app/agent.py`

This file implements the autonomous daily generation system.

### `class DailyGenerationAgent`

Purpose:

- Runs scheduled topic generation through APScheduler.

### `DailyGenerationAgent.__init__(pipeline, topic_manager)`

Purpose:

- Stores dependencies, initializes scheduler, builds a default `AgentStatus`, and registers the scheduled job.

### `DailyGenerationAgent._configure()`

Purpose:

- Adds the daily cron job if it is not already registered.

### `DailyGenerationAgent.start()`

Purpose:

- Starts the scheduler when the FastAPI app starts.

### `DailyGenerationAgent.shutdown()`

Purpose:

- Stops the scheduler when the app shuts down.

### `DailyGenerationAgent.refresh_status()`

Purpose:

- Recomputes live agent status from:
  - config
  - generated history
  - scheduler next-run metadata

### `DailyGenerationAgent.run_once()`

Purpose:

- Manually or automatically executes one agent cycle.

Behavior:

1. Load config.
2. Select topics with `TopicManager`.
3. Create `GenerateRequest` for each chosen topic.
4. Create job through `PipelineService`.
5. Run pipeline immediately.
6. Record `last_run`.
7. Refresh status.

Return:

- list of created job ids

## `backend/app/main.py`

This file is the API entrypoint and dependency wiring layer.

### Module-level service instances

These are created once when `main.py` is imported:

- `script_engine`
- `voice_engine`
- `animation_engine`
- `subtitle_engine`
- `video_engine`
- `topic_manager`
- `pipeline_service`
- `agent_service`

Why this matters:

- These instances act like application-level singletons within the process.

### `lifespan(app)`

Purpose:

- FastAPI lifespan handler.

Behavior:

1. Start scheduler agent on app startup.
2. Yield control to FastAPI.
3. Shut down scheduler on app shutdown.

### `app = FastAPI(...)`

Purpose:

- Creates the API application.

### CORS middleware setup

Purpose:

- Allows the frontend on `http://localhost:5173` to call the backend.

### `root()`

Route:

- `GET /`

Purpose:

- Health/status response.

### `generate_video(request)`

Route:

- `POST /api/generate`

Purpose:

- Queues and launches a manual generation job.

Behavior:

1. Create a job immediately.
2. Start a background thread that runs the pipeline.
3. Return initial queued response.

### `get_job(job_id)`

Route:

- `GET /api/jobs/{job_id}`

Purpose:

- Returns current job state or 404.

### `download_job(job_id)`

Route:

- `GET /api/download/{job_id}`

Purpose:

- Returns the generated MP4 via `FileResponse`.

### `get_topics(category=None)`

Route:

- `GET /api/topics`

Purpose:

- Returns all local topics or category-filtered topics.

### `run_agent_once()`

Route:

- `POST /api/agent/run-once`

Purpose:

- Manually triggers the scheduler workflow.

### `get_agent_status()`

Route:

- `GET /api/agent/status`

Purpose:

- Returns current agent counters and scheduling info.

### `get_history()`

Route:

- `GET /api/history`

Purpose:

- Returns generation history from JSON.

### `get_config()`

Route:

- `GET /api/config`

Purpose:

- Returns active configuration.

### `update_config(config)`

Route:

- `POST /api/config`

Purpose:

- Writes new config values and refreshes agent status.

## Backend Data Files

## `backend/data/topics.json`

Purpose:

- Local structured UPSC topic library.

Used by:

- `TopicManager`
- frontend topic library page

## `backend/data/templates.json`

Purpose:

- Script template source for deterministic educational content generation.

Used by:

- `ScriptEngine`

## `backend/data/config.json`

Purpose:

- Runtime configuration for generation behavior and scheduler volume.

Used by:

- `load_config()`
- agent
- settings page

## `backend/data/generated_log.json`

Purpose:

- Persistent run history.

Used by:

- `TopicManager`
- history API
- agent status

## Backend Tests Reference

## `backend/tests/conftest.py`

Purpose:

- Adds the backend root to `sys.path` so tests can import `app.*`.

## `backend/tests/test_script_engine.py`

Purpose:

- Validates script completeness and deterministic generation.

### `test_script_contains_all_sections()`

Checks:

- hook exists
- explanation exists
- example exists
- UPSC tip exists
- closing exists
- duration is positive

### `test_script_is_deterministic_for_same_input()`

Checks:

- same input produces same script

## `backend/tests/test_topic_manager.py`

Purpose:

- Verifies topic loading and duplicate rules.

### `test_loads_topics()`

Checks:

- topic library size is at least expected baseline

### `test_selects_unused_topic(tmp_path)`

Checks:

- fresh topic is selected correctly

### `test_avoids_duplicate_when_recycle_false(tmp_path)`

Checks:

- no topic is returned when all are used and recycling is disabled

### `test_allows_repeat_when_recycle_true(tmp_path)`

Checks:

- repeated topics are allowed when configured

## `backend/tests/test_storage.py`

Purpose:

- Validates JSON storage behavior.

### `test_json_read_write_roundtrip(tmp_path)`

Checks:

- JSON data survives a write/read cycle

### `test_missing_json_returns_default(tmp_path)`

Checks:

- missing file returns default safely

### `test_output_folder_created(tmp_path)`

Checks:

- job output folder creation works

## `backend/tests/test_pipeline.py`

Purpose:

- Verifies pipeline orchestration logic using fake engines.

### `FakeVoiceEngine.generate(...)`

Purpose:

- Test double that creates a small fake voice file.

### `FakeAnimationEngine.generate(...)`

Purpose:

- Test double that creates placeholder animation and storyboard files.

### `FakeVideoEngine.assemble(...)`

Purpose:

- Test double that creates a fake final video.

### `FailingVideoEngine.assemble(...)`

Purpose:

- Test double that simulates a pipeline failure.

### `make_pipeline(tmp_path, video_engine)`

Purpose:

- Builds a test-friendly pipeline using fakes and temp paths.

### `test_pipeline_creates_job_and_metadata(tmp_path)`

Checks:

- job id exists
- pipeline completes
- metadata file is created

### `test_pipeline_updates_progress(tmp_path)`

Checks:

- stages move to completed state

### `test_pipeline_handles_failed_stage(tmp_path)`

Checks:

- failures are surfaced cleanly

## `backend/tests/test_api.py`

Purpose:

- Verifies major API responses.

### `client = TestClient(app)`

Purpose:

- FastAPI test client used for integration-style API tests.

### `test_root_status()`

Checks:

- `/` returns healthy status

### `test_topics_returns_list()`

Checks:

- `/api/topics` returns a list

### `test_generate_returns_job_id(monkeypatch)`

Checks:

- `/api/generate` returns a job id

### `test_history_returns_list()`

Checks:

- `/api/history` returns a list

### `test_config_returns_config()`

Checks:

- `/api/config` returns valid config data

## Frontend Code Reference

## `frontend/src/main.tsx`

Purpose:

- React entrypoint.

Behavior:

1. Import styles.
2. Create root.
3. Render `App` inside `React.StrictMode`.

## `frontend/src/types.ts`

Purpose:

- Shared frontend TypeScript interfaces matching backend payloads.

### Main exported types

- `StageStatus`
- `TopicItem`
- `PipelineProgress`
- `GenerateRequest`
- `GenerateResponse`
- `JobStatus`
- `AgentStatus`
- `AppConfig`
- `HistoryItem`

Why it matters:

- Keeps backend/frontend contracts explicit and typed.

## `frontend/src/api.ts`

Purpose:

- Central API client layer.

### `API_BASE`

Purpose:

- Defines backend origin as `http://localhost:8000`.

### `request<T>(path, options?)`

Purpose:

- Generic helper for JSON-based API requests.

Behavior:

1. Builds full URL.
2. Performs fetch.
3. Throws an error for non-OK responses.
4. Parses JSON into the expected type.

### `api.getTopics()`

Purpose:

- Calls `/api/topics`.

### `api.generate(payload)`

Purpose:

- Calls `/api/generate`.

### `api.getJob(jobId)`

Purpose:

- Calls `/api/jobs/{jobId}`.

### `api.getAgentStatus()`

Purpose:

- Calls `/api/agent/status`.

### `api.runAgentOnce()`

Purpose:

- Calls `/api/agent/run-once`.

### `api.getHistory()`

Purpose:

- Calls `/api/history`.

### `api.getConfig()`

Purpose:

- Calls `/api/config`.

### `api.updateConfig(payload)`

Purpose:

- Calls `POST /api/config`.

### `api.downloadUrl(jobId)`

Purpose:

- Builds a direct download URL for the final MP4.

## `frontend/src/App.tsx`

This is the frontend orchestration component.

### `defaultForm`

Purpose:

- Provides initial form state before config and topics load.

### `pages`

Purpose:

- Lists supported dashboard views.

### `TopicLibrary({ topics })`

Purpose:

- Inline page component that renders searchable topic cards.

Behavior:

- stores search query
- filters topics
- displays category and difficulty labels

### `ErrorBanner({ message })`

Purpose:

- Reusable error-state banner for UI failures.

### `App()`

Purpose:

- Main dashboard component and state manager.

State managed here:

- current page
- generation form
- topics
- history
- config
- current job
- agent status
- loading flags
- error message
- polling interval reference

### `bootstrap()`

Purpose:

- Initial data-loading function for the dashboard.

Behavior:

1. Fetch topics, history, config, and agent status in parallel.
2. Store results in component state.
3. Update form defaults using backend config.

### `useEffect(...)`

Purpose:

- Triggers initial bootstrap and clears polling on unmount.

### `refreshHistoryAndAgent()`

Purpose:

- Reloads history and agent status together after job or agent actions.

### `startPolling(jobId)`

Purpose:

- Polls backend job status repeatedly until completion or failure.

Behavior:

1. Clears previous interval.
2. Polls `/api/jobs/{jobId}` every 1.5 seconds.
3. Updates `job` state.
4. Stops when completed or failed.
5. Refreshes history and agent status.

### `handleGenerate()`

Purpose:

- Sends the manual generation request and starts polling.

### `handleRunAgent()`

Purpose:

- Triggers one autonomous run from the UI.

### `handleSaveSettings()`

Purpose:

- Writes updated local config through the API.

### JSX render tree

Purpose:

- Lays out the app with:
  - sidebar
  - header
  - error banner
  - active page content

## Frontend Components

## `frontend/src/components/Sidebar.tsx`

### `Sidebar({ page, onSelect })`

Purpose:

- Renders left navigation and active-page highlighting.

## `frontend/src/components/Header.tsx`

### `Header()`

Purpose:

- Renders product title, subtitle, and top-level dashboard summary cards.

## `frontend/src/components/TopicForm.tsx`

### `TopicForm({ form, categories, loading, onChange, onSubmit })`

Purpose:

- Renders manual generation controls.

Inputs:

- topic
- category
- duration
- voice engine
- subtitles toggle
- music toggle

## `frontend/src/components/ProgressPanel.tsx`

### `labels`

Purpose:

- Defines stage order shown in the UI.

### `badge(status)`

Purpose:

- Maps status values to Tailwind badge styles.

### `ProgressPanel({ progress, status })`

Purpose:

- Displays current pipeline stage state.

## `frontend/src/components/VideoPreview.tsx`

### `VideoPreview({ job, downloadUrl })`

Purpose:

- Shows the final preview/download state for a job.

Behavior:

- completed job shows download button
- failed job shows error
- idle/processing shows placeholder state

## `frontend/src/components/OutputHistory.tsx`

### `OutputHistory({ items })`

Purpose:

- Renders the generation history table.

Behavior:

- empty state if no jobs exist
- shows download button for completed jobs

## `frontend/src/components/AgentStatus.tsx`

### `AgentStatus({ status, loading, onRun })`

Purpose:

- Displays scheduler activity and provides manual trigger button.

## `frontend/src/components/SettingsPanel.tsx`

### `SettingsPanel({ config, saving, onChange, onSave })`

Purpose:

- Renders editable local config controls.

Editable settings:

- videos per day
- default duration
- voice engine
- max retries
- subtitles toggle
- music toggle

## Frontend Support Files

## `frontend/src/styles/index.css`

Purpose:

- Imports Tailwind layers and sets baseline global styles.

## `frontend/src/vite-env.d.ts`

Purpose:

- Provides Vite ambient type support.

## `frontend/node-env.d.ts`

Purpose:

- Supplies a narrow ambient type needed for Vite/TypeScript environment compatibility in this repo setup.

## Build and Config Files

## `frontend/package.json`

Purpose:

- Declares frontend dependencies and scripts.

Main scripts:

- `npm run dev`
- `npm run build`
- `npm run preview`

## `frontend/tailwind.config.js`

Purpose:

- Tailwind theme customization for colors, fonts, and shadows.

## `frontend/postcss.config.js`

Purpose:

- Enables Tailwind and Autoprefixer in the CSS pipeline.

## `frontend/tsconfig.json`

Purpose:

- Main TypeScript config for the frontend source.

## `frontend/tsconfig.node.json`

Purpose:

- TypeScript config for Node-side tooling files like Vite config.

## `frontend/vite.config.ts`

Purpose:

- Vite configuration with React plugin.

## How Everything Connects

## Manual generation path

```text
TopicForm.tsx
   -> api.generate()
   -> POST /api/generate
   -> main.py generate_video()
   -> PipelineService.create_job()
   -> background thread
   -> PipelineService.run_job()
   -> engines + storage + logging
   -> metadata/output files
   -> /api/jobs/{job_id}
   -> ProgressPanel.tsx and VideoPreview.tsx
```

## Agent path

```text
FastAPI lifespan
   -> DailyGenerationAgent.start()
   -> APScheduler cron trigger
   -> DailyGenerationAgent.run_once()
   -> TopicManager.select_topics()
   -> PipelineService.create_job()
   -> PipelineService.run_job()
   -> generated_log.json updated
   -> AgentStatus.tsx and OutputHistory.tsx reflect results
```

## Why The Codebase Is Structured This Way

The project is intentionally separated into small, realistic service modules:

- models for contracts
- storage for persistence
- config for shared paths and settings
- one engine per media stage
- one pipeline for orchestration
- one agent for scheduling
- one API layer for delivery
- one frontend orchestrator with focused UI components

This structure makes the project easier to:

- test
- debug
- extend
- review in a private repository setting

## Suggested Reading Order For A New Reviewer

If someone wants to understand the code quickly, this is the best order:

1. `README.md`
2. `ARCHITECTURE_FLOW.md`
3. `backend/app/main.py`
4. `backend/app/pipeline.py`
5. `backend/app/topic_manager.py`
6. `backend/app/script_engine.py`
7. `backend/app/voice_engine.py`
8. `backend/app/animation_engine.py`
9. `backend/app/subtitle_engine.py`
10. `backend/app/video_engine.py`
11. `frontend/src/App.tsx`
12. `frontend/src/api.ts`
13. backend tests

That reading path moves from high-level architecture into execution flow and then into UI wiring.
