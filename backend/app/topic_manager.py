from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .config import GENERATED_LOG_PATH, TOPICS_PATH
from .models import AppConfig, TopicItem
from .storage import JSONStorage


VALID_CATEGORIES = {
    "Polity",
    "History",
    "Geography",
    "Economy",
    "Environment",
    "Science",
    "Current Affairs",
}


class TopicManager:
    def __init__(self, storage: JSONStorage, topics_path=TOPICS_PATH, history_path=GENERATED_LOG_PATH) -> None:
        self.storage = storage
        self.topics_path = topics_path
        self.history_path = history_path

    def load_topics(self) -> list[TopicItem]:
        payload = self.storage.read_json(self.topics_path, default=[])
        return [TopicItem(**item) for item in payload]

    def load_history(self) -> list[dict]:
        return self.storage.read_json(self.history_path, default=[])

    def get_topics(self, category: str | None = None) -> list[TopicItem]:
        topics = self.load_topics()
        if category:
            return [topic for topic in topics if topic.category == category]
        return topics

    def _used_ids(self) -> set[str]:
        return {
            item.get("topic_id")
            for item in self.load_history()
            if item.get("topic_id")
        }

    def select_topics(
        self,
        config: AppConfig,
        category: str | None = None,
        limit: int = 1,
    ) -> list[dict]:
        topics = self.get_topics(category)
        used_ids = self._used_ids()
        fresh = [topic for topic in topics if topic.id not in used_ids]
        if fresh:
            chosen = fresh[: max(1, min(limit, 3))]
            return [{"topic": item, "repeated": False} for item in chosen]
        if config.recycle_topics:
            chosen = topics[: max(1, min(limit, 3))]
            return [{"topic": item, "repeated": True} for item in chosen]
        return []

    def category_counts(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for topic in self.load_topics():
            counts[topic.category] += 1
        return dict(counts)

    def has_topic(self, title: str) -> bool:
        normalized = title.strip().lower()
        return any(topic.title.lower() == normalized for topic in self.load_topics())
