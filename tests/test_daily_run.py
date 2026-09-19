from datetime import datetime

from src.daily_run import DailyRunGuard


def test_daily_guard_marks_and_detects_completed_run(tmp_path, monkeypatch):
    state = tmp_path / "daily_runs.json"
    guard = DailyRunGuard(state)
    monkeypatch.setattr(guard, "today", lambda: "2026-09-19")

    assert not guard.already_completed()
    guard.mark_completed(3)
    assert guard.already_completed()
