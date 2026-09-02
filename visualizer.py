"""
visualizer.py — All charts return clean Matplotlib Figure objects.
Figures are always closed after creation to prevent memory leaks.
No tight_layout on already-closed figures.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from modules.data_manager import load_progress

sns.set_theme(style="whitegrid", palette="muted")

INDIGO   = "#6366F1"
GREEN    = "#22C55E"
AMBER    = "#F59E0B"
BLUE     = "#3B82F6"
PINK     = "#EC4899"
TEAL     = "#14B8A6"
GREY     = "#E2E8F0"
DARK     = "#1E293B"
MUTED    = "#94A3B8"
COLORS   = [INDIGO, GREEN, AMBER, BLUE, PINK, TEAL]


def _finish(fig):
    """Tighten layout and return — do NOT close here; Streamlit needs it open."""
    try:
        fig.patch.set_facecolor("white")
        fig.tight_layout(pad=2.0)
    except Exception:
        pass
    return fig


# ── Phase progress horizontal bar chart ──────────────────────────────────────

def plot_phase_progress(phase_stats):
    if not phase_stats:
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.text(0.5, 0.5, "No roadmap data yet.", ha="center", va="center",
                fontsize=12, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    labels = [s["phase"] for s in phase_stats]
    values = [s["pct"]   for s in phase_stats]
    done   = [s["completed"] for s in phase_stats]
    totals = [s["total"]     for s in phase_stats]

    h = max(3.0, len(labels) * 1.1)
    fig, ax = plt.subplots(figsize=(8, h))

    bar_colors = [GREEN if v == 100 else INDIGO if v > 0 else GREY for v in values]
    ax.barh(labels, [100]*len(labels), color=GREY,     height=0.55, zorder=2)
    ax.barh(labels, values,            color=bar_colors, height=0.55, zorder=3)

    for i, (v, d, t) in enumerate(zip(values, done, totals)):
        ax.text(min(v + 2, 96), i,
                f" {d}/{t} ({v:.0f}%)",
                va="center", ha="left", fontsize=8.5,
                color=DARK, fontweight="bold")

    ax.set_xlim(0, 115)
    ax.set_xlabel("Completion (%)", fontsize=9)
    ax.set_title("Phase-by-Phase Progress", fontsize=12,
                 fontweight="bold", color=DARK, pad=10)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.35, zorder=1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    return _finish(fig)


# ── Overall donut ─────────────────────────────────────────────────────────────

def plot_overall_donut(pct, skill):
    fig, ax = plt.subplots(figsize=(4, 4))
    clr = GREEN if pct >= 80 else INDIGO if pct >= 40 else AMBER
    ax.pie([pct, 100 - pct], colors=[clr, GREY], startangle=90,
           wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2))
    ax.text(0, 0.1,  f"{pct:.0f}%", ha="center", va="center",
            fontsize=26, fontweight="bold", color=DARK)
    ax.text(0, -0.22, "complete",   ha="center", va="center",
            fontsize=10, color=MUTED)
    ax.text(0, -0.7,  skill[:20],   ha="center", va="center",
            fontsize=10, fontweight="semibold", color="#475569")
    ax.set_title("Overall Progress", fontsize=11, fontweight="bold",
                 color=DARK, pad=6)
    fig.patch.set_facecolor("white")
    return _finish(fig)


# ── Timeline ──────────────────────────────────────────────────────────────────

def plot_completion_timeline(username, skill):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    df = load_progress(username)

    if df.empty or skill not in df["skill"].values:
        ax.text(0.5, 0.5, "Complete topics to see your timeline.",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    skill_df = df[(df["skill"] == skill) & (df["completed"] == True)].copy()
    if skill_df.empty:
        ax.text(0.5, 0.5, "No completed topics yet — start learning!",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    skill_df["ts"] = pd.to_datetime(skill_df["timestamp"], errors="coerce")
    skill_df = skill_df.dropna(subset=["ts"]).sort_values("ts")
    skill_df["cum"] = range(1, len(skill_df) + 1)

    ax.plot(skill_df["ts"], skill_df["cum"], color=INDIGO,
            linewidth=2.5, marker="o", markersize=6,
            markerfacecolor="white", markeredgecolor=INDIGO, markeredgewidth=2)
    ax.fill_between(skill_df["ts"], skill_df["cum"], alpha=0.1, color=INDIGO)

    ax.set_xlabel("Date", fontsize=9)
    ax.set_ylabel("Topics Completed", fontsize=9)
    ax.set_title(f"Learning Timeline — {skill}", fontsize=12,
                 fontweight="bold", color=DARK, pad=10)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.tick_params(axis="x", rotation=20, labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.3)
    return _finish(fig)


# ── Radar chart ───────────────────────────────────────────────────────────────

def plot_skill_radar(phase_stats):
    if not phase_stats or len(phase_stats) < 3:
        return plot_phase_progress(phase_stats)

    labels = [s["phase"] for s in phase_stats]
    values = [s["pct"]   for s in phase_stats]
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    v_plot = values + [values[0]]
    a_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(a_plot, v_plot, color=INDIGO, linewidth=2.5)
    ax.fill(a_plot, v_plot, alpha=0.18, color=INDIGO)
    ax.set_xticks(angles)
    ax.set_xticklabels(
        [l[:18] for l in labels], size=8, color="#475569")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20","40","60","80","100"], size=7, color=MUTED)
    ax.grid(color="#CBD5E1", linewidth=0.8)
    ax.spines["polar"].set_color(GREY)
    ax.set_title("Skill Coverage", fontsize=11, fontweight="bold",
                 color=DARK, pad=16)
    fig.patch.set_facecolor("white")
    return _finish(fig)


# ── Activity heatmap ──────────────────────────────────────────────────────────

def plot_activity_heatmap(username):
    fig, ax = plt.subplots(figsize=(9, 3))
    df = load_progress(username)

    if df.empty:
        ax.text(0.5, 0.5, "No activity yet — start completing topics!",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    done_df = df[df["completed"] == True].copy()
    if done_df.empty:
        ax.text(0.5, 0.5, "Complete topics to see your activity heatmap.",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    done_df["ts"] = pd.to_datetime(done_df["timestamp"], errors="coerce")
    done_df = done_df.dropna(subset=["ts"])
    if done_df.empty:
        ax.text(0.5, 0.5, "No valid timestamps found.",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    done_df["dow"]  = done_df["ts"].dt.dayofweek
    done_df["week"] = done_df["ts"].dt.isocalendar().week.astype(int)

    pivot = done_df.groupby(["dow", "week"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(index=range(7), fill_value=0)

    sns.heatmap(pivot, ax=ax, cmap="BuPu", linewidths=0.5,
                linecolor="#F1F5F9",
                cbar_kws={"label": "Topics"},
                yticklabels=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                annot=True, fmt="d", annot_kws={"size": 8})
    ax.set_xlabel("Week of Year", fontsize=9)
    ax.set_ylabel("", fontsize=9)
    ax.set_title("Study Activity Heatmap", fontsize=12,
                 fontweight="bold", color=DARK, pad=10)
    ax.tick_params(axis="x", rotation=0, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=8)
    return _finish(fig)


# ── Multi-skill comparison ────────────────────────────────────────────────────

def plot_multi_skill_comparison(username):
    fig, ax = plt.subplots(figsize=(7, 4))
    df = load_progress(username)

    if df.empty:
        ax.text(0.5, 0.5, "No skills started yet.",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    done_df  = df[df["completed"] == True]
    total_df = df.groupby("skill").size().reset_index(name="total")

    if done_df.empty:
        ax.text(0.5, 0.5, "Complete topics to see skill comparison.",
                ha="center", va="center", fontsize=11, color=MUTED)
        ax.axis("off")
        return _finish(fig)

    summary = (done_df.groupby("skill").size()
               .reset_index(name="done"))
    merged = summary.merge(total_df, on="skill", how="left")
    merged["pct"] = (merged["done"] / merged["total"] * 100).round(1)

    bar_colors = [COLORS[i % len(COLORS)] for i in range(len(merged))]
    bars = ax.bar(merged["skill"], merged["pct"], color=bar_colors,
                  width=0.55, zorder=3, edgecolor="white", linewidth=1.2)

    for bar, pct in zip(bars, merged["pct"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{pct:.0f}%", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=DARK)

    ax.set_ylim(0, 115)
    ax.set_ylabel("Completion (%)", fontsize=9)
    ax.set_title("Progress Across All Skills", fontsize=12,
                 fontweight="bold", color=DARK, pad=10)
    ax.tick_params(axis="x", rotation=15, labelsize=9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, zorder=1)
    return _finish(fig)
