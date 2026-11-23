
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from memento import MemoryStore, MementoConfig
from memento.config import EmbeddingConfig, LLMConfig

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "executive_memory.db"
MODEL = "gemini-3.8-flash"

config = MementoConfig(
    db_path=DB_PATH,
    embedding=EmbeddingConfig(
        provider="sentence-transformers"
    ),
    llm=LLMConfig(
        provider="gemini",
        api_key=os.getenv("GEMINI_API_KEY", ""),
        extraction_model=MODEL,
        tiebreaker_model=MODEL,
        chat_model=MODEL
    )
)

memory = MemoryStore(config)

PREFERENCES_FILE = DATA_DIR / "preferences.json"
HISTORY_FILE = DATA_DIR / "briefing_history.json"


def read_json(file_path, default):
    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_preferences(topic, company, format_type):
    preferences = {
        "topic": topic,
        "company": company,
        "format": format_type
    }

    write_json(PREFERENCES_FILE, preferences)

    memory.ingest(
        text=(
            f"Executive briefing preference: "
            f"Topic: {topic}. Company or industry: {company}. "
            f"Preferred format: {format_type}."
        ),
        conversation_id="executive-preferences"
    )

    return preferences


def get_preferences():
    return read_json(PREFERENCES_FILE, {})


def save_briefing_history(briefing):
    history = read_json(HISTORY_FILE, [])
    history.append(briefing)
    write_json(HISTORY_FILE, history[-20:])

    memory.ingest(
        text=(
            f"Previous executive briefing about "
            f"{briefing['company']} on {briefing['topic']}. "
            f"Format: {briefing['format']}. "
            f"Briefing: {briefing['briefing'][:3000]}"
        ),
        conversation_id="executive-briefing-history"
    )


def get_briefing_history():
    return read_json(HISTORY_FILE, [])


def recall_executive_memory(query):
    result = memory.recall(query)
    return result.text
