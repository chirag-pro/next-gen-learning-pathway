"""
data_manager.py — Unified read/write helpers for JSON and CSV data stores.
All boolean comparisons normalised — CSV stores "True"/"False" as strings.
"""
import os
import json
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PROGRESS_FILE  = os.path.join(DATA_DIR, "progress.csv")
RESOURCES_FILE = os.path.join(DATA_DIR, "resources.csv")
ROADMAP_CACHE_FILE = os.path.join(DATA_DIR, "roadmap_cache.json")


# ─── helpers ─────────────────────────────────────────────────────────────────

def _ensure_progress_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PROGRESS_FILE):
        pd.DataFrame(columns=["username","skill","topic","phase","completed","timestamp"]
                     ).to_csv(PROGRESS_FILE, index=False)


def _normalise_bool(series):
    """Convert 'True'/'False' strings AND actual booleans to bool dtype."""
    return series.map(lambda v: str(v).strip().lower() == "true")


# ─── Progress CSV ─────────────────────────────────────────────────────────────

def load_all_progress():
    _ensure_progress_file()
    try:
        df = pd.read_csv(PROGRESS_FILE, dtype=str)   # read everything as str
        if df.empty:
            return pd.DataFrame(columns=["username","skill","topic","phase","completed","timestamp"])
        df["completed"] = _normalise_bool(df["completed"])
        return df
    except Exception:
        return pd.DataFrame(columns=["username","skill","topic","phase","completed","timestamp"])


def load_progress(username):
    df = load_all_progress()
    if df.empty:
        return df
    return df[df["username"] == username].copy()


def save_topic_progress(username, skill, topic, phase, completed):
    """Upsert a topic's completion status."""
    _ensure_progress_file()
    df = load_all_progress()
    now = datetime.now().isoformat()

    mask = (
        (df["username"] == username) &
        (df["skill"]    == skill)    &
        (df["topic"]    == topic)
    )
    if mask.any():
        df.loc[mask, "completed"] = completed
        df.loc[mask, "timestamp"] = now
    else:
        new_row = pd.DataFrame([{
            "username": username, "skill": skill, "topic": topic,
            "phase": phase, "completed": completed, "timestamp": now,
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(PROGRESS_FILE, index=False)


def get_completed_topics(username, skill):
    """Return list of completed topic names for a skill."""
    df = load_progress(username)
    if df.empty:
        return []
    mask = (df["skill"] == skill) & (df["completed"] == True)
    return df[mask]["topic"].tolist()


def get_progress_percentage(username, skill, total_topics):
    if total_topics == 0:
        return 0.0
    done = len(get_completed_topics(username, skill))
    return round((done / total_topics) * 100, 1)


# ─── Resources CSV ────────────────────────────────────────────────────────────

def load_resources():
    if not os.path.exists(RESOURCES_FILE):
        return pd.DataFrame(columns=["topic","title","type","url","difficulty","skill"])
    try:
        return pd.read_csv(RESOURCES_FILE)
    except Exception:
        return pd.DataFrame(columns=["topic","title","type","url","difficulty","skill"])


def get_resources_for_topic(topic):
    df = load_resources()
    if df.empty:
        return df
    mask = df["topic"].str.lower().str.contains(topic.lower(), na=False)
    return df[mask].copy()


def get_resources_for_skill(skill):
    df = load_resources()
    if df.empty:
        return df
    return df[df["skill"].str.lower() == skill.lower()].copy()


# ─── Roadmap Cache (JSON) ─────────────────────────────────────────────────────

def load_roadmap_cache():
    if not os.path.exists(ROADMAP_CACHE_FILE):
        return {}
    try:
        with open(ROADMAP_CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_roadmap_cache(skill, level, roadmap):
    cache = load_roadmap_cache()
    key = f"{skill}|{level}"
    cache[key] = {"roadmap": roadmap, "generated_at": datetime.now().isoformat()}
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(ROADMAP_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def get_cached_roadmap(skill, level):
    cache = load_roadmap_cache()
    entry = cache.get(f"{skill}|{level}")
    return entry["roadmap"] if entry else None
