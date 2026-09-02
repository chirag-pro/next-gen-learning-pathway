"""
chatbot.py — AI chatbot using Groq API (direct SDK + LangChain fallback).
All imports lazy. GROQ_API_KEY read fresh on every call.
No Python 3.10+ type hint syntax.
"""
import os
import re

MODEL = "llama3-8b-8192"

SYSTEM_PROMPT = """You are NGLP Assistant, an expert educational mentor inside the
Next Gen Learning Pathway platform. Help learners succeed by:
1. Answering technical and conceptual questions clearly with examples
2. Suggesting what to learn next based on their progress
3. Explaining difficult topics with simple analogies and code snippets
4. Motivating and guiding learners when stuck
5. Recommending learning resources and study strategies

Learner context:
- Skill: {skill}
- Level: {level}
- Current topic: {topic}
- Progress: {progress}%

Be concise, friendly, and practical. Use bullet points for lists.
Provide short code examples when explaining technical concepts.
Keep responses under 350 words unless a detailed explanation is requested."""


# ── Groq direct SDK (primary) ─────────────────────────────────────────────────

def _groq_direct(messages, context):
    """Call Groq SDK directly. Returns text or None."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        system_text = SYSTEM_PROMPT.format(
            skill=context.get("skill", "General"),
            level=context.get("level", "Beginner"),
            topic=context.get("current_topic", "your current topic"),
            progress=context.get("progress", 0),
        )
        groq_msgs = [{"role": "system", "content": system_text}]
        # Only include role/content keys — strip internal keys like "source"
        for m in messages:
            if m.get("role") in ("user", "assistant"):
                groq_msgs.append({"role": m["role"], "content": m["content"]})
        response = client.chat.completions.create(
            model=MODEL,
            messages=groq_msgs,
            temperature=0.6,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def _langchain_groq(messages, context):
    """Try LangChain+Groq. Returns text or None."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        system_text = SYSTEM_PROMPT.format(
            skill=context.get("skill", "General"),
            level=context.get("level", "Beginner"),
            topic=context.get("current_topic", "your current topic"),
            progress=context.get("progress", 0),
        )
        lc_msgs = [SystemMessage(content=system_text)]
        for m in messages:
            if m.get("role") == "user":
                lc_msgs.append(HumanMessage(content=m["content"]))
            elif m.get("role") == "assistant":
                lc_msgs.append(AIMessage(content=m["content"]))
        llm = ChatGroq(api_key=api_key, model_name=MODEL,
                       temperature=0.6, max_tokens=1024)
        result = llm.invoke(lc_msgs)
        return result.content.strip() if result and result.content else None
    except Exception:
        return None


# ── Rule-based fallback ───────────────────────────────────────────────────────

RULES = [
    (r"\b(hello|hi|hey)\b",
     "👋 Hi! I'm your NGLP AI mentor for **{skill}**. Ask me anything — "
     "concepts, next steps, project ideas, or career advice!"),

    (r"\b(next|what should i (learn|study)|next step|next topic)\b",
     "🗺 Based on your progress in **{skill}**, focus on: **{topic}**.\n\n"
     "Steps to tackle it:\n"
     "1. Read the description on the Roadmap page\n"
     "2. Watch a YouTube tutorial (~1 hour)\n"
     "3. Code the suggested project\n"
     "4. Ask me if you get stuck!\n\n"
     "You're at {progress}% — keep going! 💪"),

    (r"\b(explain|what is|tell me about|how does|how do|what are)\b",
     "Great question! To understand any topic in **{skill}**, follow this approach:\n\n"
     "1. **Concept** — understand *what* it is and *why* it exists\n"
     "2. **Example** — see it in action with a simple code snippet\n"
     "3. **Practice** — build something tiny that uses it\n"
     "4. **Teach it** — explain it to someone else\n\n"
     "Click **Explain Current Topic** below for a detailed AI explanation of **{topic}**."),

    (r"\b(resource|tutorial|course|video|article|book|learn from|where to learn)\b",
     "📚 For **{skill}** resources:\n\n"
     "- **Videos**: Search YouTube for '{topic} tutorial'\n"
     "- **Courses**: Coursera, Udemy, freeCodeCamp\n"
     "- **Docs**: Official documentation is always the best reference\n"
     "- **Practice**: Click 📚 Show Resources on any topic card in the Roadmap page\n\n"
     "All resources are curated for each topic on your roadmap!"),

    (r"\b(stuck|confused|don.t understand|not getting|struggling|hard|difficult)\b",
     "Don't worry — getting stuck is *part of learning*! Here's your unstuck plan:\n\n"
     "1. **Simplify** — reduce the problem to its smallest form\n"
     "2. **YouTube** — search '{topic} explained simply'\n"
     "3. **Rubber duck** — explain the problem out loud step by step\n"
     "4. **Ask specifically** — tell me exactly what part confuses you\n\n"
     "What specifically are you stuck on? I'll help you break it down 🎯"),

    (r"\b(progress|how am i doing|completion|percent)\b",
     "📊 You're at **{progress}%** completion in **{skill}**!\n\n"
     "Current focus: **{topic}**\n\n"
     "💡 To accelerate: study 45–90 min/day with the Pomodoro technique "
     "(25 min focused, 5 min break). Consistency beats intensity every time."),

    (r"\b(motivat|inspire|tired|give up|quit|discouraged|boring)\b",
     "🌟 Every expert was once a beginner — including the people who built {skill}!\n\n"
     "Your {progress}% progress is *real work* you can't lose. Remember:\n\n"
     "- **Small daily wins** compound into massive results\n"
     "- **Struggle = growth** — your brain is literally rewiring\n"
     "- **{topic}** is temporary; the skill you're building is permanent\n\n"
     "Set a 25-minute timer right now and just start. You'll feel better in 5 minutes 🚀"),

    (r"\b(project|build|make|create|practise|practice)\b",
     "🛠 Best way to learn **{skill}**: build things!\n\n"
     "For **{topic}**, try:\n"
     "1. Start with the project idea on the roadmap topic card\n"
     "2. Break it into the smallest possible version first\n"
     "3. Add features one at a time\n"
     "4. Share it on GitHub — portfolio gold!\n\n"
     "Want me to suggest a specific project for your current level?"),

    (r"\b(how long|time|duration|weeks|months|finish|complete)\b",
     "⏱ Your **{skill}** roadmap is designed for your pace.\n\n"
     "Rough estimates:\n"
     "- **30 min/day** → complete in 6–8 months\n"
     "- **1 hour/day** → complete in 3–4 months\n"
     "- **2+ hours/day** → complete in 6–8 weeks\n\n"
     "You're {progress}% done. Quality over speed — understanding > rushing!"),

    (r"\b(career|job|salary|interview|hire|work|employed)\b",
     "💼 **{skill}** opens great career doors!\n\n"
     "Roadmap to your first role:\n"
     "1. ✅ Complete your NGLP roadmap\n"
     "2. 🛠 Build 2–3 portfolio projects (GitHub)\n"
     "3. 📝 Write about your learning (blog/LinkedIn)\n"
     "4. 🤝 Network in communities (Discord, Reddit, Meetups)\n"
     "5. 💪 Practice coding challenges (LeetCode, HackerRank)\n\n"
     "Most learners get their first role within 6–12 months of consistent study."),
]

DEFAULT_RESPONSE = (
    "I'm your NGLP AI mentor for **{skill}**! Here's what I can help with:\n\n"
    "- 📖 **Explain** any topic with examples\n"
    "- 🗺 **Suggest** what to learn next\n"
    "- 🛠 **Project ideas** for practice\n"
    "- 💼 **Career** guidance and interview tips\n"
    "- 💪 **Motivation** when you're stuck\n\n"
    "*(Offline mode — set GROQ_API_KEY for full AI responses)*\n\n"
    "Try: *'What should I learn next?'* or *'Explain {topic}'*"
)


def _rule_response(user_message, context):
    msg = user_message.lower()
    skill    = context.get("skill", "your subject")
    topic    = context.get("current_topic", "your current topic")
    progress = context.get("progress", 0)
    for pattern, template in RULES:
        if re.search(pattern, msg, re.IGNORECASE):
            return template.format(skill=skill, topic=topic, progress=progress)
    return DEFAULT_RESPONSE.format(skill=skill, topic=topic, progress=progress)


# ── Public API ────────────────────────────────────────────────────────────────

def get_chat_response(messages, context):
    """
    Returns (response_text: str, source: str)
    source is 'groq' or 'fallback'
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if api_key:
        # Try direct SDK first (faster), then LangChain
        reply = _groq_direct(messages, context)
        if not reply:
            reply = _langchain_groq(messages, context)
        if reply:
            return reply, "groq"

    # Rule-based fallback
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = m["content"]
            break
    return _rule_response(last_user, context), "fallback"


def get_topic_explanation(topic, skill):
    """Get a detailed explanation of a specific topic."""
    messages = [{
        "role": "user",
        "content": (
            f"Explain '{topic}' in {skill} clearly. Cover:\n"
            f"1. Simple definition (1-2 sentences)\n"
            f"2. Why it matters / real-world use\n"
            f"3. A concrete code example or analogy\n"
            f"4. Common beginner mistakes to avoid"
        )
    }]
    ctx = {"skill": skill, "level": "Beginner",
           "current_topic": topic, "progress": 0}
    return get_chat_response(messages, ctx)


def suggest_next_steps(skill, level, completed_topics, current_topic):
    """Get personalised next-step suggestions."""
    done_str = (", ".join(completed_topics[-5:])
                if completed_topics else "None yet")
    messages = [{
        "role": "user",
        "content": (
            f"I'm learning {skill} at {level} level.\n"
            f"Completed topics: {done_str}\n"
            f"Current topic: '{current_topic}'\n\n"
            f"Give me 3-5 specific, actionable things to focus on this week "
            f"to make the best progress. Be concrete, not generic."
        )
    }]
    ctx = {
        "skill": skill, "level": level,
        "current_topic": current_topic,
        "progress": min(len(completed_topics) * 8, 100),
    }
    return get_chat_response(messages, ctx)
