# PROJECT REPORT

## Project Summary

UPSC ReelForge is a full-stack internal automation system for producing vertical educational revision videos from a local topic library. It combines topic selection, script generation, voice generation, scene planning, subtitle generation, and final assembly into a single SaaS-style workflow.

## User Problem

Short-form educational video creation is repetitive and operationally heavy. Teams need a way to standardize topic handling, monitor progress, preserve output metadata, and automate daily runs without depending on paid AI APIs.

## System Architecture

The system is split into a FastAPI backend and a React dashboard. The backend exposes job APIs, stores operational data in JSON, and runs a deterministic media pipeline. The frontend acts as the operator console for manual triggers, status tracking, history inspection, and config updates.

## AI Agent Design

The autonomous agent uses APScheduler to execute a daily run. It reads local configuration, selects unused topics, respects recycle rules, dispatches the same pipeline used by manual jobs, and reports status through the API.

## Script Generation Design

Script generation is deterministic and template-driven. The engine combines hook, concept explanation, example, UPSC tip, and closing sections from local JSON templates. This keeps the system original, testable, and independent from external LLMs.

## Voice Generation Design

The voice engine tries `gTTS` first, supports `pyttsx3` as a local alternative, and falls back to a generated silent audio asset if voice synthesis is unavailable. This ensures the pipeline can still complete in constrained environments.

## Manim Animation Design

The animation engine produces a Manim-compatible storyboard for a 1080x1920 layout with title, hook, explanation, example, tip, and closing scenes. If full rendering is not available, it still writes storyboard JSON and a safe placeholder asset so the system remains operable and testable.

## Video Assembly Design

The video engine uses MoviePy to combine animation and audio into a final MP4. Subtitle output can be attached as a sidecar asset. When assembly fails, intermediate files remain on disk and a meaningful error is returned instead of losing job context.

## Frontend Dashboard Overview

The frontend presents a polished internal-tool layout with sections for generation, daily agent status, output history, topic library, and settings. It calls the backend directly, polls active jobs, and renders real responses rather than mocked content.

## Testing Strategy

Pytest covers script generation, topic selection logic, JSON storage behavior, pipeline orchestration, and API responses. Heavy media stages are mocked or replaced with lightweight fallback implementations so tests run quickly and reliably.

## Limitations

- Placeholder animation output is minimal without a richer rendering environment.
- Subtitle burn-in is not fully styled inside the final MP4.
- gTTS may be limited in offline or restricted network conditions, though fallback behavior is included.
- JSON storage is sufficient for private internal usage but not ideal for high-concurrency production scaling.

## Future Scope

- Add richer Manim scenes and branded motion systems
- Support multilingual educational outputs
- Introduce queue persistence and worker separation
- Add analytics, approval states, and reviewer workflows
- Optionally integrate external LLM and premium TTS providers in the future

## Conclusion

UPSC ReelForge demonstrates a practical internal SaaS-style content automation system built with local-first components, modular media stages, and production-aware fallback logic. It is suitable as a strong private repository submission because it shows end-to-end engineering depth, realistic architecture, and clear extensibility.
