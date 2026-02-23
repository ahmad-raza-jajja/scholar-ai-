# 🎓 ScholarAI Elite v4.0
> **Groq Llama3-70B + RAG + Streamlit** | AI Scholarship Intelligence Platform

---

## 🚀 Quick Deploy to Streamlit Cloud

### Step 1: GitHub Upload
Upload these files maintaining folder structure:
```
scholarai/
├── app.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── data_manager.py
│   └── rag_engine.py
└── data/
    └── scholarships.csv
```

### Step 2: Deploy
1. Go to **share.streamlit.io**
2. GitHub se login karo
3. **New app** → apna repo select karo → Main file: `app.py`
4. **Deploy!**

### Step 3: Add Groq API Key (CRITICAL)
1. App khulne ke baad → **share.streamlit.io** → Your app → **⋮ (3 dots)** → **Settings** → **Secrets**
2. Ye paste karo:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```
3. **Save** → App restart hogi → AI active!

### Get Free Groq API Key
1. **console.groq.com** jao
2. Sign Up karo (free)
3. Left sidebar → **API Keys** → **Create API Key**
4. Key copy karo (starts with `gsk_`)

---

## 💻 Local Setup
```bash
cd scholarai
pip install -r requirements.txt
streamlit run app.py
```

---

## ✨ Features v4.0
| Feature | Description |
|---------|-------------|
| 🤖 RAG AI Chat | Retrieves scholarship data first, then generates context-aware answers |
| 🔍 RAG Engine | TF-IDF semantic search over all 16 scholarships |
| 📄 CV Analyzer | ATS score + 5 weaknesses + specific improvements |
| ✍️ SOP Improve | Before/after score + high-impact rewrite |
| 🗺️ Roadmap | 12-month personalized plan |
| ⚠️ Rejection Sim | AI predicts your rejection risks with fixes |
| 🎤 IELTS Prep | Mock prompts + band scoring tips |
| 🎯 Interview Prep | Simulated Q&A with AI scoring |
| 📊 Compare | Side-by-side scholarship comparison |
| 🔖 Bookmarks | Save favorite scholarships |
| 📥 PDF Export | Export any result as PDF |

---

## 🔑 Tech Stack
- **Groq Llama3-70B** — Primary AI (free, ultra-fast)
- **RAG Engine** — TF-IDF semantic search (no extra deps)
- **Gemini 1.5 Pro** — Optional fallback
- **Streamlit** — UI framework
- **16 verified 2026 scholarships** in database

---

## 📌 Default Login
- **Username:** `demo`
- **Password:** `demo123`

---

## ⚠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| AI not responding | Add GROQ_API_KEY to Streamlit Secrets |
| Data not showing | Check data/scholarships.csv is uploaded |
| Import errors | Run `pip install -r requirements.txt` |
