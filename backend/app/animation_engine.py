from __future__ import annotations

import json
from pathlib import Path

from .models import ScriptSection


ICON_MAP = {
    "Polity": "⚖️",
    "History": "🏛️",
    "Current Affairs": "🏛️",
    "Governance": "🏛️",
    "Constitution": "📜",
    "Geography": "🌍",
    "Economy": "💰",
    "Environment": "🌱",
}


class AnimationEngine:
    def __init__(self, width: int = 1080, height: int = 1920) -> None:
        self.width = width
        self.height = height

    def _storyboard(self, topic: str, category: str, script: ScriptSection) -> dict:
        icon = ICON_MAP.get(category, "🎓")
        return {
            "layout": {"width": self.width, "height": self.height, "orientation": "vertical"},
            "category": category,
            "icon": icon,
            "scenes": [
                {"name": "title", "headline": topic, "body": f"{icon} {category} quick revision"},
                {"name": "hook", "headline": "Why it matters", "body": script.hook},
                {"name": "explanation", "headline": "Core concept", "body": script.explanation},
                {"name": "example", "headline": "Easy example", "body": script.example},
                {"name": "tip", "headline": "UPSC tip", "body": script.upsc_tip},
                {"name": "closing", "headline": "Takeaway", "body": script.closing},
            ],
            "transitions": ["fade", "slide-up", "cross-dissolve"],
            "manim_compatible": True,
        }

    def generate(self, topic: str, category: str, script: ScriptSection, output_dir: Path) -> dict:
        storyboard = self._storyboard(topic, category, script)
        storyboard_path = output_dir / "storyboard.json"
        with storyboard_path.open("w", encoding="utf-8") as handle:
            json.dump(storyboard, handle, indent=2, ensure_ascii=False)

        animation_path = output_dir / "animation.mp4"
        try:
            from moviepy import ColorClip  # type: ignore

            clip = ColorClip(size=(540, 960), color=(18, 34, 58), duration=3)
            clip.write_videofile(
                str(animation_path),
                fps=24,
                codec="libx264",
                audio=False,
                logger=None,
            )
            clip.close()
            status = "rendered-placeholder-video"
        except Exception:
            animation_path.write_bytes(b"")
            status = "storyboard-only"

        return {
            "animation_path": str(animation_path),
            "storyboard_path": str(storyboard_path),
            "status": status,
        }
