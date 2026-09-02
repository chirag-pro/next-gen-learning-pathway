"""
resource_manager.py — Load, filter, display learning resources from CSV.
"""
import pandas as pd
from modules.data_manager import load_resources

TYPE_ICONS = {
    "video":   "🎬",
    "article": "📄",
    "course":  "🎓",
    "book":    "📚",
    "tool":    "🛠",
}
DIFFICULTY_COLORS = {
    "Beginner":     "#22C55E",
    "Intermediate": "#F59E0B",
    "Advanced":     "#EF4444",
}


def get_resource_type_icon(rtype):
    return TYPE_ICONS.get(str(rtype).lower(), "🔗")


def get_difficulty_color(difficulty):
    return DIFFICULTY_COLORS.get(str(difficulty).strip(), "#6366F1")


def get_resources_for_topic(topic, skill=None):
    df = load_resources()
    if df.empty:
        return df
    t = topic.lower()
    mask = df["topic"].str.lower().str.contains(t, na=False)
    result = df[mask].copy()
    if result.empty:
        # word-overlap fallback
        words = set(t.split())
        def overlap(row_topic):
            return bool(words & set(str(row_topic).lower().split()))
        result = df[df["topic"].apply(overlap)].copy()
    if skill and not result.empty:
        sm = result["skill"].str.lower() == skill.lower()
        if sm.any():
            result = result[sm]
    return result.reset_index(drop=True)


def get_resources_for_skill(skill, difficulty=None):
    df = load_resources()
    if df.empty:
        return df
    result = df[df["skill"].str.lower() == skill.lower()].copy()
    if difficulty and difficulty != "All" and not result.empty:
        dm = result["difficulty"].str.lower() == difficulty.lower()
        if dm.any():
            result = result[dm]
    return result.reset_index(drop=True)


def get_available_skills():
    df = load_resources()
    if df.empty:
        return []
    return sorted(df["skill"].dropna().unique().tolist())


def search_resources(query):
    df = load_resources()
    if df.empty:
        return df
    q = query.lower()
    mask = (
        df["topic"].str.lower().str.contains(q, na=False) |
        df["title"].str.lower().str.contains(q, na=False) |
        df["skill"].str.lower().str.contains(q, na=False)
    )
    return df[mask].reset_index(drop=True)


def get_resource_stats(skill):
    df = get_resources_for_skill(skill)
    if df.empty:
        return {"total": 0, "by_type": {}, "by_difficulty": {}}
    return {
        "total":        len(df),
        "by_type":      df["type"].value_counts().to_dict(),
        "by_difficulty": df["difficulty"].value_counts().to_dict(),
    }
