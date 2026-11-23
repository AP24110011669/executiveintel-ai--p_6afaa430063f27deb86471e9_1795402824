
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
HISTORY_FILE = DATA_DIR / "briefing_history.json"


def read_json(file_path, default):
    DATA_DIR.mkdir(exist_ok=True)

    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def write_json(file_path, data):
    DATA_DIR.mkdir(exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_preferences(topic, company, format_type):
    preferences = {
        "topic": topic,
        "company": company,
        "format": format_type
    }

    write_json(PREFERENCES_FILE, preferences)
    return preferences


def get_preferences():
    return read_json(PREFERENCES_FILE, {})


def save_briefing_history(briefing):
    history = read_json(HISTORY_FILE, [])

    history.append(briefing)

    write_json(HISTORY_FILE, history[-20:])


def get_briefing_history():
    return read_json(HISTORY_FILE, [])
