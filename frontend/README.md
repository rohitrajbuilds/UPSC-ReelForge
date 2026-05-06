# UPSC ReelForge Frontend

The frontend is a Vite + React + TypeScript dashboard designed as an internal SaaS-style operations console for educational short-form video generation.

## Architecture

- `App.tsx`: page orchestration, data fetching, polling, and shared state.
- `api.ts`: typed API client targeting `http://localhost:8000`.
- `types.ts`: shared TypeScript interfaces for backend payloads.
- `components/`: dashboard building blocks for generation, progress, history, agent status, topic library, and settings.

## Pages

- Generate Video
- Daily Agent
- Output History
- Topic Library
- Settings

## Run

```bash
cd frontend
npm install
npm run dev
```

## Notes

- The UI calls real backend endpoints.
- The design emphasizes a production-style internal tool layout instead of a minimal demo page.
