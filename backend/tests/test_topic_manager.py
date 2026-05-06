from pathlib import Path

from app.models import AppConfig
from app.storage import JSONStorage
from app.topic_manager import TopicManager


def test_loads_topics():
    manager = TopicManager(JSONStorage(Path(__file__).resolve().parents[1]))
    topics = manager.load_topics()
    assert len(topics) >= 30


def test_selects_unused_topic(tmp_path):
    storage = JSONStorage(tmp_path)
    topics_path = tmp_path / "topics.json"
    history_path = tmp_path / "generated_log.json"
    storage.write_json(topics_path, [{"id": "t1", "title": "Topic 1", "category": "Polity", "difficulty": "Beginner", "keywords": []}])
    storage.write_json(history_path, [])
    manager = TopicManager(storage, topics_path, history_path)

    chosen = manager.select_topics(AppConfig(recycle_topics=False), limit=1)
    assert chosen[0]["topic"].title == "Topic 1"
    assert chosen[0]["repeated"] is False


def test_avoids_duplicate_when_recycle_false(tmp_path):
    storage = JSONStorage(tmp_path)
    topics_path = tmp_path / "topics.json"
    history_path = tmp_path / "generated_log.json"
    storage.write_json(topics_path, [{"id": "t1", "title": "Topic 1", "category": "Polity", "difficulty": "Beginner", "keywords": []}])
    storage.write_json(history_path, [{"topic_id": "t1"}])
    manager = TopicManager(storage, topics_path, history_path)

    chosen = manager.select_topics(AppConfig(recycle_topics=False), limit=1)
    assert chosen == []


def test_allows_repeat_when_recycle_true(tmp_path):
    storage = JSONStorage(tmp_path)
    topics_path = tmp_path / "topics.json"
    history_path = tmp_path / "generated_log.json"
    storage.write_json(topics_path, [{"id": "t1", "title": "Topic 1", "category": "Polity", "difficulty": "Beginner", "keywords": []}])
    storage.write_json(history_path, [{"topic_id": "t1"}])
    manager = TopicManager(storage, topics_path, history_path)

    chosen = manager.select_topics(AppConfig(recycle_topics=True), limit=1)
    assert chosen[0]["repeated"] is True
