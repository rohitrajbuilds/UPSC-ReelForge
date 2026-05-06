from __future__ import annotations

from math import ceil

from .config import TEMPLATES_PATH
from .models import ScriptSection
from .storage import JSONStorage


class ScriptEngine:
    def __init__(self, storage: JSONStorage, templates_path=TEMPLATES_PATH) -> None:
        self.storage = storage
        self.templates_path = templates_path
        self.templates = self.storage.read_json(self.templates_path, default={})

    @staticmethod
    def _choose(options: list[str], seed: str) -> str:
        if not options:
            return "{topic}"
        index = sum(ord(ch) for ch in seed) % len(options)
        return options[index]

    def generate(self, topic: str, category: str, duration_seconds: int) -> ScriptSection:
        seed = f"{topic}:{category}:{duration_seconds}"
        hook = self._choose(self.templates.get("hook_templates", []), seed).format(topic=topic, category=category)
        explanation = self._choose(self.templates.get("explanation_templates", []), seed + "e").format(
            topic=topic,
            category=category,
        )
        example = self._choose(self.templates.get("example_templates", []), seed + "x").format(
            topic=topic,
            category=category,
        )
        tip = self._choose(self.templates.get("upsc_tip_templates", []), seed + "u").format(
            topic=topic,
            category=category,
        )
        closing = self._choose(self.templates.get("closing_templates", []), seed + "c").format(
            topic=topic,
            category=category,
        )

        full_script = " ".join([hook, explanation, example, tip, closing])
        estimated_duration = max(45, min(duration_seconds, ceil(len(full_script.split()) / 2.6)))
        return ScriptSection(
            topic=topic,
            hook=hook,
            explanation=explanation,
            example=example,
            upsc_tip=tip,
            closing=closing,
            full_script=full_script,
            estimated_duration=estimated_duration,
        )
