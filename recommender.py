"""
recommender.py — Topic and resource recommendations.
Uses TF-IDF cosine similarity. No Python 3.10+ type hints.
"""
import numpy as np
import pandas as pd
from modules.data_manager import load_resources, get_completed_topics


# ── Next-topic recommender ────────────────────────────────────────────────────

def recommend_next_topic(username, skill, roadmap):
    """Return the next incomplete topic dict, or None if all done."""
    completed = set(get_completed_topics(username, skill))
    for phase in roadmap.get("phases", []):
        for topic in phase.get("topics", []):
            if topic.get("name","") not in completed:
                return {
                    **topic,
                    "phase_title":  phase.get("phase_title", ""),
                    "phase_number": phase.get("phase_number", 0),
                }
    return None


def get_phase_progress(username, skill, roadmap):
    """Return per-phase completion stats as list of dicts."""
    completed = set(get_completed_topics(username, skill))
    stats = []
    for phase in roadmap.get("phases", []):
        topics = phase.get("topics", [])
        done = sum(1 for t in topics if t.get("name","") in completed)
        total = len(topics)
        stats.append({
            "phase":        phase.get("phase_title", ""),
            "phase_number": phase.get("phase_number", 0),
            "completed":    done,
            "total":        total,
            "pct":          round((done / total) * 100, 1) if total else 0.0,
        })
    return stats


# ── Resource recommender (TF-IDF) ────────────────────────────────────────────

def recommend_resources(topic, skill, top_n=5):
    """Return top-N resources for a topic+skill using TF-IDF cosine similarity."""
    df = load_resources()
    if df.empty:
        return pd.DataFrame()

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        df2 = df.copy()
        df2["corpus"] = (
            df2["topic"].fillna("") + " " +
            df2["title"].fillna("") + " " +
            df2["skill"].fillna("") + " " +
            df2["difficulty"].fillna("") + " " +
            df2["type"].fillna("")
        )
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(df2["corpus"])
        query_vec = vectorizer.transform([f"{topic} {skill}"])
        scores = cosine_similarity(query_vec, matrix).flatten()
        df2["_score"] = scores
        result = df2.sort_values("_score", ascending=False).head(top_n)
        result = result[result["_score"] > 0]
        if not result.empty:
            return result[["topic","title","type","url","difficulty","skill"]].reset_index(drop=True)
    except Exception:
        pass

    # Keyword fallback
    t_low = topic.lower()
    s_low = skill.lower()
    mask = (
        df["topic"].str.lower().str.contains(t_low, na=False) |
        df["skill"].str.lower().str.contains(s_low, na=False)
    )
    return df[mask].head(top_n)[["topic","title","type","url","difficulty","skill"]].reset_index(drop=True)


def recommend_skill_resources(skill, difficulty=None, top_n=6):
    """All resources for a skill, optionally filtered by difficulty."""
    df = load_resources()
    if df.empty:
        return pd.DataFrame()
    mask = df["skill"].str.lower() == skill.lower()
    result = df[mask].copy()
    if difficulty and difficulty != "All" and not result.empty:
        dm = result["difficulty"].str.lower() == difficulty.lower()
        if dm.any():
            result = result[dm]
    return result.head(top_n)[["topic","title","type","url","difficulty","skill"]].reset_index(drop=True)


# ── Skill score ───────────────────────────────────────────────────────────────

def compute_skill_score(username, skill, roadmap):
    """Weighted skill score 0-100 and list of weak phases."""
    completed = set(get_completed_topics(username, skill))
    phase_scores = []
    for phase in roadmap.get("phases", []):
        topics = phase.get("topics", [])
        if not topics:
            continue
        done = sum(1 for t in topics if t.get("name","") in completed)
        pct = (done / len(topics)) * 100
        weight = phase.get("phase_number", 1)
        phase_scores.append({"phase": phase.get("phase_title",""), "score": pct, "weight": weight})

    if not phase_scores:
        return {"overall": 0.0, "phases": [], "weak_areas": []}

    total_w  = sum(p["weight"] for p in phase_scores)
    weighted = sum(p["score"] * p["weight"] for p in phase_scores)
    overall  = round(weighted / total_w, 1) if total_w else 0.0
    weak     = [p["phase"] for p in phase_scores if p["score"] < 50]
    return {"overall": overall, "phases": phase_scores, "weak_areas": weak}


def get_similar_skills(skill):
    """Rule-based related skills."""
    MAP = {
        "Python":                ["Machine Learning", "Data Science", "Artificial Intelligence", "DevOps"],
        "Machine Learning":      ["Artificial Intelligence", "Data Science", "Python"],
        "Data Science":          ["Python", "Machine Learning", "Artificial Intelligence"],
        "Web Development":       ["Python", "DevOps", "Cloud Computing"],
        "Artificial Intelligence":["Machine Learning", "Data Science", "Python"],
        "DevOps":                ["Cloud Computing", "Cybersecurity", "Web Development"],
        "Cloud Computing":       ["DevOps", "Cybersecurity", "Web Development"],
        "Cybersecurity":         ["DevOps", "Cloud Computing", "Web Development"],
    }
    return MAP.get(skill, [])
