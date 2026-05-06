from app.config import storage
from app.script_engine import ScriptEngine


def test_script_contains_all_sections():
    engine = ScriptEngine(storage)
    script = engine.generate("Directive Principles of State Policy", "Polity", 180)

    assert script.hook
    assert script.explanation
    assert script.example
    assert script.upsc_tip
    assert script.closing
    assert "Directive Principles" in script.full_script
    assert script.estimated_duration > 0


def test_script_is_deterministic_for_same_input():
    engine = ScriptEngine(storage)
    first = engine.generate("Fiscal Deficit Explained", "Economy", 180)
    second = engine.generate("Fiscal Deficit Explained", "Economy", 180)

    assert first.full_script == second.full_script
