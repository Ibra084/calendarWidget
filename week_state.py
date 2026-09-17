"""Persists and computes which timetable week (A or B) applies to a given date.

The user tells the widget "it is currently Week A/B" exactly once (or
whenever the rotation gets out of sync, e.g. after a holiday). From that
single reference point we can work out Week A/B for any other date, since
the school alternates weeks every calendar week (Monday-start).
"""
import datetime
import json
import os
from pathlib import Path

_APP_DIR_NAME = "CalendarWidget"


def _config_dir():
    base = os.getenv("APPDATA")  # Windows roaming profile
    if not base:
        base = str(Path.home())
    return Path(base) / _APP_DIR_NAME


def _config_file():
    return _config_dir() / "config.json"


def load_config():
    path = _config_file()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(data):
    d = _config_dir()
    d.mkdir(parents=True, exist_ok=True)
    _config_file().write_text(json.dumps(data, indent=2))


def _monday_of(d):
    return d - datetime.timedelta(days=d.weekday())


def is_configured():
    cfg = load_config()
    return "ref_monday" in cfg and "ref_week" in cfg


def set_current_week(week_letter, ref_date=None):
    """Tell the widget that `week_letter` ('A' or 'B') is in effect during
    the calendar week containing `ref_date` (defaults to today)."""
    ref_date = ref_date or datetime.date.today()
    cfg = load_config()
    cfg["ref_monday"] = _monday_of(ref_date).isoformat()
    cfg["ref_week"] = week_letter
    save_config(cfg)


def get_current_week(today=None):
    """Return 'A' or 'B' for `today` (defaults to today), or None if the
    widget hasn't been configured yet."""
    cfg = load_config()
    if "ref_monday" not in cfg or "ref_week" not in cfg:
        return None
    today = today or datetime.date.today()
    ref_monday = datetime.date.fromisoformat(cfg["ref_monday"])
    this_monday = _monday_of(today)
    weeks_diff = (this_monday - ref_monday).days // 7
    other_week = "B" if cfg["ref_week"] == "A" else "A"
    return cfg["ref_week"] if weeks_diff % 2 == 0 else other_week


def get_window_position():
    cfg = load_config()
    pos = cfg.get("window_pos")
    if pos and "x" in pos and "y" in pos:
        return pos["x"], pos["y"]
    return None


def set_window_position(x, y):
    cfg = load_config()
    cfg["window_pos"] = {"x": x, "y": y}
    save_config(cfg)
