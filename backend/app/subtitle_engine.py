from __future__ import annotations

import json
from pathlib import Path

from .models import ScriptSection


class SubtitleEngine:
    @staticmethod
    def _chunks(script: ScriptSection) -> list[tuple[str, str]]:
        return [
            ("Hook", script.hook),
            ("Concept", script.explanation),
            ("Example", script.example),
            ("UPSC Tip", script.upsc_tip),
            ("Closing", script.closing),
        ]

    @staticmethod
    def _fmt(seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02},000"

    def generate(self, script: ScriptSection, output_dir: Path) -> dict:
        chunks = self._chunks(script)
        total_words = max(len(script.full_script.split()), 1)
        cursor = 0
        srt_lines: list[str] = []
        json_payload: list[dict] = []

        for index, (title, content) in enumerate(chunks, start=1):
            chunk_words = max(len(content.split()), 1)
            duration = max(4, round((chunk_words / total_words) * script.estimated_duration))
            start = cursor
            end = cursor + duration
            cursor = end
            body = f"{title}: {content}"
            srt_lines.extend([str(index), f"{self._fmt(start)} --> {self._fmt(end)}", body, ""])
            json_payload.append({"index": index, "title": title, "start": start, "end": end, "text": body})

        srt_path = output_dir / "subtitles.srt"
        json_path = output_dir / "subtitles.json"
        srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
        json_path.write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"srt_path": str(srt_path), "json_path": str(json_path)}
