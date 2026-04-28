# 🎓 NGLP — VIVA PREPARATION GUIDE
## For: Final Year CS Project | Examiner: CS Professor

---

## ⭐ TOP 15 VIVA QUESTIONS WITH STRONG ANSWERS

---

### Q1. "What is NGLP and what problem does it solve?"

**🗣 SPEAK THIS:**
> "NGLP — Next Gen Learning Pathway — is an AI-powered personalised educational guidance
> system built for students who want to learn technical skills but don't know where to start
> or what to study next. The core problem is that existing platforms provide content but
> not direction. A student searching how to learn Python gets thousands of unstructured
> results. Our system uses a Large Language Model to generate a structured, phased
> learning roadmap personalised to the student's chosen skill and current proficiency level.
> It then tracks their progress, provides an AI chatbot mentor, and recommends the most
> relevant resources for each topic they are studying."

**🧠 HINGLISH MEMORY TRICK:**
> "Problem = direction nahi. Solution = AI se personalised roadmap. Simple."

---

### Q2. "Why did you choose Streamlit over Flask or Django?"

**🗣 SPEAK THIS:**
> "We evaluated three options. Flask and Django are excellent web frameworks but they
> require separate frontend development using HTML, CSS, and JavaScript — which would
> have significantly increased development time for what is primarily a data and AI
> application. Streamlit was designed specifically for Python data applications. It allows
> us to build interactive, reactive UI components entirely in Python, which meant our team
> could focus all effort on the AI and data logic rather than frontend engineering.
> Additionally, Streamlit's built-in session state management simplified our authentication
> flow and page routing considerably."

**🧠 HINGLISH:**
> "Flask mein frontend alag banana padta. Streamlit mein sab Python mein hota hai.
> Time save, focus AI pe."

---

### Q3. "How does the AI roadmap generation work technically?"

**🗣 SPEAK THIS (MOST IMPORTANT):**
> "The roadmap generation follows a priority chain with four levels. First, we check a
> local JSON cache — if the student has previously generated this roadmap, we return it
> instantly without any API call. Second, if not cached, we call the Groq API with the
> LLaMA-3 8B model. We send a carefully engineered structured prompt that instructs the
> model to return a strictly formatted JSON object containing phases, topics, estimated
> hours, key concepts arrays, and project ideas. The model's response is validated by
> our _validate_roadmap() function which checks structural correctness. Third, if the API
> is unavailable, we have 24 pre-built static roadmaps — all 8 skills at all 3 levels.
> Fourth, if none of the above work, a generic fallback generator creates a basic
> structured roadmap. This four-layer approach ensures the system is always functional."

**🧠 HINGLISH:**
> "Yaad karo: Cache → Groq AI → 24 Static Fallbacks → Generic. Ye chain hai.
> Professor ko impress karne ka point = 'four-layer resilience.'"

---

### Q4. "What is TF-IDF and how did you use it?"

**🗣 SPEAK THIS:**
> "TF-IDF stands for Term Frequency-Inverse Document Frequency. It is a classical NLP
> technique for measuring how relevant a word is to a document in a collection.
> TF measures how often a term appears in a specific document. IDF penalises terms
> that appear in many documents — meaning common words like 'the' or 'and' get low
> scores, while specific terms like 'gradient descent' or 'convolutional' get high scores.
> In our system, we build a corpus where each document is the concatenated metadata of
> a learning resource — its topic name, title, skill, difficulty level, and type.
> We vectorise this corpus using Scikit-learn's TfidfVectorizer, then compute cosine
> similarity between a query vector — which is the current topic plus skill — and all
> resource vectors. The resources with the highest similarity scores are recommended.
> This is fundamentally more intelligent than keyword matching because it understands
> semantic relevance, not just exact word overlap."

**🧠 HINGLISH:**
> "TF = kitni baar word aaya. IDF = common words ko penalty. Together = smart search.
> Example: 'neural network' zyada specific hai 'learning' se. TF-IDF yahi samajhta hai."

---

### Q5. "How did you implement the chatbot?"

**🗣 SPEAK THIS:**
> "The chatbot uses a three-layer architecture for maximum reliability. The primary
> layer calls the Groq API directly using their Python SDK with a context-injected
> system prompt. This system prompt tells the model its role — an educational mentor
> — and provides the student's current state: their skill, level, current topic, and
> progress percentage. This grounds the model's responses in the student's specific
> context. The secondary layer wraps the same call through LangChain's ChatGroq
> class, which provides better conversation history management. The tertiary layer is
> a rule-based engine that pattern-matches the user's message against 10 categories
> using regular expressions and returns a contextual templated response. This means
> the chatbot always provides a useful response even without internet connectivity."

**🧠 HINGLISH:**
> "Teen layers: Groq Direct → LangChain → Rules. Never crashes.
> Context injection = AI ko student ka background pata hai."

---

### Q6. "How does your authentication system work?"

**🗣 SPEAK THIS:**
> "Authentication is implemented in auth.py using Python's built-in hashlib library.
> When a user registers, their password is hashed using SHA-256 — a one-way
> cryptographic hash function. The hash, not the password, is stored in users.json.
> During login, we re-hash the entered password and compare it with the stored hash.
> Since SHA-256 is deterministic — the same input always produces the same output —
> matching hashes confirm the correct password without ever storing or transmitting
> the plain text. Session management uses Streamlit's session_state dictionary,
> which persists data across page rerenders within a single browser session."

**🧠 HINGLISH:**
> "Password store nahi hota. Hash store hota hai. SHA-256 one-way hai —
> hash se password nahi nikalta. Ye security ka basic principle hai."

---

### Q7. "What is the system architecture?"

**🗣 SPEAK THIS:**
> "The system follows a three-tier architecture. The Presentation Layer consists of
> Streamlit — the main app.py handles routing and authentication UI, while four
> page modules handle dashboard, roadmap, chatbot, and progress views. The Business
> and AI Logic Layer contains seven modules: auth handles identity, data_manager
> handles all file I/O, pathway_engine handles roadmap generation, chatbot handles
> conversational AI, recommender handles TF-IDF recommendations, visualizer generates
> charts, and the new notifications module handles contextual alerts. The Data Layer
> uses JSON for user accounts and roadmap cache, and CSV for progress tracking and
> learning resources. This separation ensures each layer can be modified independently
> without breaking others."

**🧠 HINGLISH:**
> "Three tiers: UI (Streamlit) → Logic (7 modules) → Data (JSON + CSV).
> Modular hai matlab ek file change karo, baaki sab safe hai."

---

### Q8. "Why did you use Groq instead of OpenAI?"

**🗣 SPEAK THIS:**
> "We evaluated multiple LLM providers. OpenAI's GPT-4 is excellent but expensive for
> an academic project with multiple API calls per session. Groq offers free-tier access
> with the LLaMA-3 model — which is Meta's open-source model. Crucially, Groq's
> inference engine is currently the fastest publicly available LLM inference platform,
> achieving speeds of 500 to 800 tokens per second compared to OpenAI's 60 to 100
> tokens per second. For a real-time application like roadmap generation and chatbot
> responses, this speed difference is significant — it means the student sees the
> response in under 2 seconds rather than 10 to 15 seconds."

**🧠 HINGLISH:**
> "Groq = fastest + free tier. OpenAI = expensive. Speed matter karta hai
> real-time app mein. Ye practical decision hai."

---

### Q9. "How do you handle the case when the internet is not available?"

**🗣 SPEAK THIS:**
> "This was a deliberate design decision. Every AI-dependent component has a fallback.
> For roadmap generation, if Groq API fails, the system serves from 24 pre-built
> static roadmaps. For the chatbot, a rule-based engine with regex pattern matching
> handles 10 question categories. For resources, a keyword overlap fallback activates
> if TF-IDF vectorisation fails. All user data — progress, accounts — is stored locally
> in JSON and CSV files. The system is therefore fully functional in offline mode,
> just without AI-generated content."

**🧠 HINGLISH:**
> "System kabhi crash nahi karta. Har AI component ka backup hai.
> Ye 'graceful degradation' hai — professor ko ye term bolna."

---

### Q10. "What are the limitations of your project?"

**🗣 SPEAK THIS (Be honest — professors respect this):**
> "I would identify four primary limitations. First, the data layer uses flat files —
> for a production system with thousands of users, a relational database like PostgreSQL
> would be necessary. Second, the chatbot has no persistent memory across sessions —
> each login starts a fresh conversation history. Third, we used SHA-256 for password
> hashing which is functional but bcrypt with salt is the industry standard. Fourth,
> the recommendation system is content-based only — a collaborative filtering layer
> that learns from what similar users studied would make recommendations significantly
> more personalised. These are known limitations with clear paths to improvement."

**🧠 HINGLISH:**
> "Limitations honestly bolo. CSV → Database, SHA-256 → bcrypt,
> no memory → session persistence, content-based → collaborative filtering.
> Ye improvements future work mein mention karo."

---

### Q11. "Explain the progress tracking system."

**🗣 SPEAK THIS:**
> "Progress tracking is implemented across three modules. In data_manager.py, the
> save_topic_progress function performs an upsert operation on progress.csv — it
> updates an existing row if the topic was previously tracked, or appends a new row.
> Each row stores the username, skill, topic name, phase name, a boolean completion
> flag, and a timestamp. A critical bug we addressed was that CSV files store Python
> booleans as the strings True and False, so our _normalise_bool helper converts all
> boolean columns on every read to ensure correct comparison. The visualizer module
> then reads this data to generate six different chart types showing progress over time,
> by phase, and as a heatmap of study activity days."

**🧠 HINGLISH:**
> "CSV mein True/False string ban jaata hai. Ye ek real bug tha jo humne fix kiya.
> Ye baat viva mein bolna — professor ko real problem-solving dikhao."

---

### Q12. "What is the notification system?"

**🗣 SPEAK THIS:**
> "The notification system is implemented in notifications.py and provides contextual
> alerts based on the student's current state. It tracks three metrics: the study streak
> in consecutive days, the count of topics completed today, and milestone completions
> at 1, 5, 10, 20, and 50 topics. Based on these, it generates typed notifications —
> milestone, success, info, or warning — with appropriate messages. For example, a
> seven-day streak triggers a fire emoji milestone alert, completing no topics today
> triggers a study reminder, and crossing 75% completion triggers an encouragement
> notification. Notifications are dismissible per session using session_state boolean
> flags, and a maximum of two notifications show at once to avoid overwhelming the
> student."

---

### Q13. "How did you ensure code quality and modularity?"

**🗣 SPEAK THIS:**
> "Modularity was a core design principle. Each module has a single responsibility —
> auth.py only handles identity, data_manager.py only handles file I/O, and so on.
> Pages import from modules, but modules never import from pages — this is a unidirectional
> dependency structure that prevents circular imports and makes each module independently
> testable. Error handling is implemented at every external call — API calls, file reads,
> and CSV operations all have try-except blocks with meaningful fallbacks. All Groq and
> LangChain imports are lazy — inside functions rather than at module level — so missing
> packages don't crash the application."

---

### Q14. "How does the back navigation work?"

**🗣 SPEAK THIS:**
> "The back navigation uses a simple page history stack implemented in session_state.
> The navigate_to function pushes the current page onto a history list before switching
> to the new page, keeping the last 10 pages. The go_back function pops the most recent
> entry and navigates to it. The sidebar checks if the history stack is non-empty and
> conditionally renders a Back button showing the previous page's name. This gives
> the application browser-like back navigation without requiring JavaScript or any
> frontend framework."

---

### Q15. "What would you improve if you had more time?"

**🗣 SPEAK THIS:**
> "Five improvements are on my roadmap. One — replace the CSV/JSON data layer with
> PostgreSQL using SQLAlchemy for proper scalability. Two — add persistent chatbot
> memory using a vector database like Chroma so the AI remembers previous conversations.
> Three — implement collaborative filtering alongside TF-IDF to recommend resources
> based on what similar learners found useful. Four — add a quiz system that automatically
> generates MCQs for each topic using the AI to test knowledge retention. Five — replace
> SHA-256 password hashing with bcrypt and add OAuth2 social login. Each of these is
> a concrete technical improvement with a clear implementation path."

---

## 🔴 CRITICAL SECTION: "Did you build this yourself?"

### 🗣 EXACTLY WHAT TO SAY:

> "Yes, I built this project. Let me be transparent about the development process, which
> I believe actually demonstrates advanced technical skill. I used AI as a development
> tool — similar to how professional software engineers today use GitHub Copilot,
> ChatGPT, and other AI assistants as part of their workflow. The AI generated code
> structures, but I was responsible for system design decisions, identifying and debugging
> critical bugs — like the CSV boolean normalisation issue and the lazy import fix —
> integrating multiple technologies into a coherent architecture, and understanding
> every component well enough to explain it to you right now.
>
> Using AI tools to accelerate software development is not cheating — it is the current
> industry standard. Junior developers at Google, Microsoft, and Amazon use Copilot
> every day. What matters is whether I understand the system I built — and I do. I can
> explain every module, every design decision, every bug fix, and every technology choice
> with technical precision."

### 🧠 HINGLISH — REMEMBER THIS:
> "Bolo: 'AI development tool ki tarah use kiya, jaise GitHub Copilot.
> Professional engineers bhi yahi karte hain. Main apna system
> fully samajhta hoon — yehi important hai.' Confident raho, defensive mat bano."

---

## ⚠️ COMMON MISTAKES TO AVOID

| Mistake | What Happens | What to Do Instead |
|---|---|---|
| Saying "I don't know" | Professor thinks you don't understand | Say "That's a great point — in our implementation we handled it this way..." |
| Memorising without understanding | Professor asks follow-up and you're stuck | Understand the WHY behind each decision |
| Being defensive about AI usage | Creates bad impression | Be confident and frame it as industry practice |
| Explaining only what, not why | Sounds like reading documentation | Always add "...and we chose this because..." |
| Rushing through the demo | Professor misses features | Slow down, narrate every action you perform |
| Not knowing error handling | Critical gap for CS professor | Know your fallback chains cold |
| Saying "the code does X" | Passive, shows no ownership | Say "I implemented X by..." |

---

## 🎯 DEMO SCRIPT (For Live Demo)

### Open with this:
> "Let me walk you through a complete user journey on our system."

### Step 1 — Registration:
> "First I'll create a new account. Notice the password is never stored in plain text —
> we use SHA-256 hashing. The account is saved to users.json."

### Step 2 — Skill Selection:
> "On first login, the student selects their skill and level. I'll choose Python Beginner
> — now watch the AI generate a personalised roadmap."

### Step 3 — Dashboard:
> "The dashboard immediately shows the most important thing — the next topic to study.
> This 'LEARN THIS NEXT' card is designed so the student knows what to do with a
> single glance. No reading required."

### Step 4 — Roadmap:
> "The roadmap shows all phases. The current topic has the 'LEARN NOW' badge in indigo.
> I'll mark this topic complete — watch the progress bars update in real time."

### Step 5 — Chatbot:
> "The AI mentor. I'll ask it to explain the current topic — see how it includes my
> current skill and progress in its context before calling the API."

### Step 6 — Progress:
> "The progress page shows six different visualisations of my learning data."

### Step 7 — Notifications:
> "Notice this notification — it detected I completed a topic today and is encouraging
> me to continue."

---

## 💡 IMPORTANT LINES TO DEFINITELY SPEAK IN VIVA

1. *"We implemented a four-layer fallback chain for roadmap generation — API cache, Groq AI, 24 static roadmaps, and a generic generator."*

2. *"A critical bug we identified and fixed was CSV boolean normalisation — Python's True becomes the string 'True' in CSV, which breaks all comparison operations."*

3. *"The chatbot uses context injection — before every API call we inject the student's skill, level, current topic, and progress percentage into the system prompt."*

4. *"We chose Groq over OpenAI specifically because of inference speed — 500 to 800 tokens per second versus 60 to 100."*

5. *"The architecture follows a unidirectional dependency rule — pages import from modules, but modules never import from pages."*

6. *"The recommendation engine uses TF-IDF vectorisation with cosine similarity — not simple keyword matching."*

7. *"All external library imports are lazy — inside functions — so the application never crashes on missing packages."*
