"""
ScholarAI Elite v4 — AI Engine
Groq Llama3 primary | Full data-based fallback when no API key
"""

import os, re, json, random
from typing import Dict, List, Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ── Complete Scholarship Knowledge Base ──────────────────
SCHOLARSHIPS = [
    {"name": "Fulbright Foreign Student Program", "country": "USA", "amount": "Full Tuition + Stipend + Airfare + Health Insurance", "deadline": "Oct 15, 2026", "gpa": 3.5, "ielts": 6.5, "field": "All Fields", "degree": "Masters/PhD", "success": "15%", "url": "https://foreign.fulbrightonline.org", "notes": "Apply through US Embassy Pakistan. 4000 awards yearly. Most prestigious US scholarship."},
    {"name": "Chevening Scholarship", "country": "UK", "amount": "Full Tuition + £1378-1690/month + Airfare", "deadline": "Oct 7, 2026", "gpa": 3.0, "ielts": 6.5, "field": "All Fields", "degree": "Masters", "success": "8%", "url": "https://chevening.org", "notes": "Requires 2+ years work experience. 1500 awards yearly. UK government flagship."},
    {"name": "Gates Cambridge Scholarship", "country": "UK", "amount": "Full Tuition + £21000/year + Airfare", "deadline": "Dec 3, 2026", "gpa": 3.7, "ielts": 7.5, "field": "All Fields", "degree": "Masters/PhD", "success": "2%", "url": "https://gatescambridge.org", "notes": "~80 awards per year. Bill Gates funded. University of Cambridge."},
    {"name": "DAAD Scholarship", "country": "Germany", "amount": "€934-1200/month + Health + Travel", "deadline": "Oct 15, 2026", "gpa": 3.2, "ielts": 6.0, "field": "STEM/Sciences/Social Sciences", "degree": "Masters/PhD", "success": "30%", "url": "https://daad.de/en", "notes": "One of world's largest scholarship orgs. German or English programs available."},
    {"name": "Australia Awards", "country": "Australia", "amount": "Full Tuition + AUD 27082/year + Airfare + Health", "deadline": "Apr 30, 2026", "gpa": 3.0, "ielts": 6.5, "field": "Agriculture/Education/Health/Infrastructure", "degree": "Masters/PhD", "success": "25%", "url": "https://australiaawards.gov.au", "notes": "Apply via Australian High Commission Islamabad. Opens Jan-Feb each year."},
    {"name": "Erasmus Mundus", "country": "Europe (Multiple)", "amount": "€24000/year + Travel", "deadline": "Jan 15, 2026", "gpa": 3.0, "ielts": 6.5, "field": "Various", "degree": "Masters", "success": "20%", "url": "https://erasmus-plus.ec.europa.eu", "notes": "Study across 2-3 European universities. 200+ programs available."},
    {"name": "Rhodes Scholarship", "country": "UK (Oxford)", "amount": "£21000/year + Full Fees + Airfare", "deadline": "Oct 1, 2026", "gpa": 3.7, "ielts": 7.0, "field": "All Fields", "degree": "Masters/PhD", "success": "2%", "url": "https://rhodeshouse.ox.ac.uk", "notes": "Oldest scholarship (1902). ~100 scholars/year. Extraordinary academic + leadership needed."},
    {"name": "Commonwealth Scholarship", "country": "UK", "amount": "Full Tuition + £1347/month + Airfare", "deadline": "Dec 17, 2026", "gpa": 3.0, "ielts": 6.0, "field": "STEM/Agriculture/Health/Governance", "degree": "Masters/PhD", "success": "18%", "url": "https://cscuk.fcdo.gov.uk", "notes": "Apply via HEC Pakistan. 700+ awards yearly. Research-focused."},
    {"name": "Swedish Institute Scholarship", "country": "Sweden", "amount": "13000 SEK/month + 15000 SEK grant + Insurance", "deadline": "Feb 10, 2026", "gpa": 3.2, "ielts": 6.5, "field": "All Fields (priority: sustainable dev)", "degree": "Masters", "success": "25%", "url": "https://si.se/en/apply/scholarships", "notes": "Pakistan eligible. Opens Nov-Dec annually."},
    {"name": "MEXT Japan", "country": "Japan", "amount": "144000-145000 JPY/month + Full Tuition + Airfare", "deadline": "May 31, 2026", "gpa": 3.0, "ielts": 5.5, "field": "All Fields", "degree": "Masters/PhD", "success": "20%", "url": "https://www.studyinjapan.go.jp/en", "notes": "6-month Japanese language training included. Apply via Japanese Embassy Islamabad."},
    {"name": "Aga Khan Foundation Scholarship", "country": "Various Top Universities", "amount": "50% Grant + 50% Loan (forgiven for community service)", "deadline": "Mar 31, 2026", "gpa": 3.0, "ielts": 6.0, "field": "Health/Education/Rural Dev/Natural Resources", "degree": "Masters", "success": "15%", "url": "https://www.akdn.org", "notes": "Need-based + merit. Opens January each year. Financial need is key."},
    {"name": "KGSP Korea", "country": "South Korea", "amount": "Full Tuition + 900000 KRW/month + Language Training + Airfare", "deadline": "Feb 28, 2026", "gpa": 3.0, "ielts": 5.5, "field": "All Fields", "degree": "Masters/PhD", "success": "30%", "url": "https://www.niied.go.kr/eng", "notes": "1 year free Korean language training. Apply via Korean Embassy Islamabad."},
    {"name": "CSC China Scholarship", "country": "China", "amount": "Full Tuition + 3000 CNY/month + Accommodation + Airfare", "deadline": "Mar 15, 2026", "gpa": 3.0, "ielts": 6.0, "field": "All Fields", "degree": "Masters/PhD", "success": "40%", "url": "https://www.csc.edu.cn/studyinchina", "notes": "Most accessible for Pakistanis. 50000+ awards yearly. HEC Pakistan has quota."},
    {"name": "Stipendium Hungaricum", "country": "Hungary", "amount": "Full Tuition + 130000-180000 HUF/month + Accommodation + Health", "deadline": "Jan 16, 2026", "gpa": 3.0, "ielts": 5.5, "field": "All Fields", "degree": "Masters/PhD", "success": "45%", "url": "https://stipendiumhungaricum.hu", "notes": "Pakistan has bilateral agreement. Apply via HEC Pakistan. One of easier options."},
    {"name": "HEC Need Based Scholarship", "country": "Pakistan", "amount": "Full Tuition + 5000 PKR/month", "deadline": "Jun 30, 2026", "gpa": 2.5, "ielts": 0.0, "field": "All Fields", "degree": "Undergraduate/Masters", "success": "60%", "url": "https://www.hec.gov.pk", "notes": "For Pakistani universities only. Financial need documentation required."},
    {"name": "Rotary Peace Fellowship", "country": "USA/Japan/Sweden/UK", "amount": "Full Tuition + Stipend + Airfare + All Expenses", "deadline": "May 15, 2027", "gpa": 3.0, "ielts": 6.5, "field": "Peace/Development/International Relations", "degree": "Masters", "success": "10%", "url": "https://rotary.org/en/our-programs/peace-fellowships", "notes": "Apply via local Rotary Club. 3+ years work experience required."},
]

SOP_TIPS = """
📝 **SOP Writing — Complete Guide**

**❌ Never start with:**
"I have always been passionate about..."
"Since childhood I dreamed of..."
"I am writing to apply for..."

**✅ Strong Opening Examples:**
• "When I debugged my first neural network at 2 AM, I realized..."
• "The 40% crop failure in my village made me pursue agricultural research..."
• "After leading a team of 15 to deliver Pakistan's first XYZ, I understood..."

**📋 Perfect Structure (700-800 words):**
1. **Hook** (50 words) — One specific moment that defines you
2. **Academic Journey** (150 words) — Achievements WITH numbers (GPA rank, projects, grades)
3. **Research/Work Experience** (200 words) — What you DID, what RESULTED, what you LEARNED
4. **Why This Program** (150 words) — Name specific professors, courses, labs, research groups
5. **Future Plan** (150 words) — Concrete role in Pakistan (name institution, problem you'll solve)

**✅ Power Words:** catalyzed, spearheaded, quantified, pioneered, demonstrated, implemented
**❌ Weak Words:** passionate, hardworking, always wanted, dream of, believe, hope

**🎯 Golden Rules:**
• Every sentence must answer: "So what?" — add the RESULT/IMPACT
• Never say "I want to learn" — say "I will apply X to solve Y in Pakistan"
• Mention 1-2 specific faculty members by name from the target university
• End with Pakistan impact — committees want scholars who will give back
"""

CV_TIPS = """
📄 **CV Guide for Scholarship Applications**

**Essential Sections (in order):**
1. **Personal Info** — Name, email, LinkedIn, ORCID (if researcher)
2. **Education** — Reverse chronological, include CGPA, rank if good (e.g., Top 5%)
3. **Research Experience** — Most important for academic scholarships
4. **Publications/Conferences** — Even if just submitted or in preparation
5. **Work/Internship Experience** — With bullet points showing IMPACT
6. **Leadership & Volunteering** — Club president, community work, NGO
7. **Awards & Scholarships** — Every recognition matters
8. **Skills** — Programming languages, lab techniques, language scores
9. **References** — 2-3 professors who know your work well

**❌ Common Mistakes:**
• Generic bullet points: "Worked on project" → ❌
• No numbers: "Led team" → ❌
• Missing IELTS score
• Longer than 2 pages (for Masters applications)
• Including photo (not needed for UK/US/Europe)

**✅ Strong Bullet Point Formula:**
[Action verb] + [What you did] + [Result/Impact with numbers]
Example: "Developed ML model achieving 94% accuracy, reducing processing time by 40%"
Example: "Led team of 8 volunteers reaching 2000+ students across 5 schools"
"""

IELTS_GUIDE = """
🎤 **Complete IELTS Preparation Guide**

**📊 Band Requirements by Scholarship:**
• HEC Pakistan: No requirement
• CSC China: 6.0
• DAAD Germany: 6.0
• Stipendium Hungaricum: 5.5
• Australia Awards: 6.5
• Fulbright USA: 6.5
• Chevening UK: 6.5
• Commonwealth: 6.0
• Swedish Institute: 6.5
• Gates Cambridge: 7.5
• Rhodes Oxford: 7.0

**📚 Section-wise Strategy:**

**Reading (Target: 7.0+)**
• Read questions FIRST, then skim passage
• True/False/Not Given — "Not Given" = info absent from text
• 20 minutes max per section
• Practice: Cambridge IELTS books 14-18

**Writing Task 1 (Target: 7.0+)**
• Always write Overview paragraph (most skip this — big mistake)
• 170-190 words (not just 150)
• Compare specific data points with numbers
• Vocab: increased dramatically, fell sharply, remained stable, peaked at, fluctuated between

**Writing Task 2 (Target: 7.0+)**
• State YOUR position clearly in introduction
• Each body paragraph: Topic sentence + 2 examples + impact
• Use: Furthermore, In contrast, Consequently, Notably, Nevertheless
• 270-290 words target

**Listening (Target: 7.5+)**
• Read questions during 30-second preview
• Answers come in ORDER in audio
• Watch distractors — correct answer often comes AFTER correction

**Speaking (Target: 7.0+)**
• Use PEEL: Point, Example, Explanation, Link
• Buy time: "That's an interesting question, let me think..."
• Avoid one-word answers — always elaborate
• Record yourself daily for 10 minutes

**⏱️ Realistic Improvement Timeline:**
• With 2 hours daily study: +0.5 band per month
• Reading + Listening improve fastest
• Writing + Speaking need consistent practice
"""

INTERVIEW_GUIDE = """
🎯 **Scholarship Interview Preparation Guide**

**Most Common Questions + How to Answer:**

**1. "Tell me about yourself"**
• WRONG: Full life story from birth
• RIGHT: 60-second pitch — field, key achievement, why this scholarship, future goal
• Formula: "I'm a [year] [field] student at [university] with [key achievement]. My research on [topic] showed [result]. I'm applying for [scholarship] because [specific reason], and after completion I plan to [concrete Pakistan role]."

**2. "Why this specific scholarship?"**
• WRONG: "Because it provides full funding"
• RIGHT: Know their VALUES — Chevening=leadership, Fulbright=mutual understanding, Rhodes=service
• Research the committee, mention specific alumni who inspired you

**3. "What will you do after?"**
• WRONG: "I want to help Pakistan develop"
• RIGHT: "I will join [specific institution] as [specific role] to work on [specific problem] using [specific skills from program]"

**4. "Your greatest achievement?"**
• Use STAR: Situation (10%) → Task (10%) → Action (60%) → Result (20%)
• Must include numbers: "increased by 35%", "reached 500 students", "saved 3 months of work"

**5. "Why should we choose you?"**
• Your unique combination = Academic excellence + field expertise + community commitment + Pakistan need
• End with: "I will multiply the impact of this investment through [specific plan]"

**⚠️ Common Mistakes:**
• Memorized answers (panels detect immediately — vary your words)
• Not knowing scholarship history/values
• Vague future plans
• Speaking too fast when nervous (slow down deliberately)
• Not asking any questions at end (always prepare 2 questions)

**✅ 2-Week Prep Plan:**
• Week 1: Research scholarship deeply, prepare 5 core stories
• Week 2: Mock interviews daily (record yourself), refine answers
"""

REJECTION_DATA = """
**Why Applications Get Rejected — Committee Insights:**

🔴 **High Risk Factors:**
1. CGPA below 3.0 — disqualifies for most international scholarships
2. IELTS below 6.5 — blocks UK/US/Australia access
3. Generic SOP — "passionate about learning" with no specific achievements
4. No research output — critical gap for PhD scholarships
5. Work experience missing — Chevening requires 2800+ hours

🟡 **Medium Risk Factors:**
6. Weak references — supervisors who don't know your work
7. Mismatched field — applying to wrong country for your specialty
8. No community service — Fulbright, Rhodes heavily value this
9. Poor interview preparation — vague future plans
10. Missing documents — transcripts, certificates, attestation

🟢 **Easy Wins (Fix These First):**
11. Get IELTS 7.0+ — single biggest eligibility unlock
12. Ask professor for research co-authorship
13. Start any community initiative and document it
14. Tailor SOP for each scholarship specifically
15. Apply to 8-10 scholarships simultaneously — never just 1-2
"""

def get_groq_key() -> str:
    key = "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"
    if key:
        return key
    
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    try:
        import streamlit as st
        key = str(st.secrets["GROQ_API_KEY"]).strip()
        if key and key != "None" and key != "":
            return key
    except (KeyError, Exception):
        pass
    try:
        import streamlit as st
        key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        if key and key != "None" and key != "":
            return key
    except Exception:
        pass
    return ""


class AIEngine:
    def __init__(self, groq_key: str = "", gemini_key: str = ""):
    self.groq_key = "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"
    self.gemini_key = gemini_key
    self.groq_client = None
    self.rag = None
    self._init_models()

def _init_models(self):
    if GROQ_AVAILABLE and self.groq_key:
        try:
            self.groq_client = Groq(api_key=self.groq_key)
        except Exception as e:
            self.groq_client = None

    def set_rag(self, rag_engine):
        self.rag = rag_engine

    def _groq(self, messages: List[Dict], max_tokens: int = 1400) -> Optional[str]:
        if not self.groq_client:
            return None
        try:
            resp = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e).lower()
            if "rate" in err:
                return None  # Fall through to local fallback
            return None  # Fall through to local fallback

    # ── CHAT ─────────────────────────────────────────────
    def chat_response(self, message: str, profile: Dict, history: List) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        field = str(profile.get("field", "General"))
        ielts = float(profile.get("ielts", 6.5))
        country = str(profile.get("country", "Any"))
        name = str(profile.get("name", "Student"))

        # Try Groq with RAG context
        if self.groq_client:
            rag_context = ""
            if self.rag and self.rag.is_built:
                results = self.rag.retrieve(message, top_k=4)
                if results:
                    rag_context = self.rag.format_context(results)

            system = f"""You are ScholarAI Elite — expert scholarship advisor.

Student: {name} | CGPA: {cgpa}/4.0 | Field: {field} | IELTS: {ielts} | Target: {country}

{rag_context}

Be SPECIFIC: use real scholarship names, deadlines, amounts from database.
Base advice on their actual CGPA {cgpa} and IELTS {ielts}.
Use emojis and bullet points. Be honest and actionable."""

            messages = [{"role": "system", "content": system}]
            for h in history[-6:]:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": message})

            result = self._groq(messages, 1400)
            if result:
                return result

        # Full local fallback — data-rich answers
        return self._smart_local_chat(message, profile)

    def _smart_local_chat(self, msg: str, profile: Dict) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        field = str(profile.get("field", "")).lower()
        ielts = float(profile.get("ielts", 6.5))
        m = msg.lower()

        if any(k in m for k in ["scholarship", "which", "apply", "qualify", "option", "fund", "best"]):
            return self._match_scholarships(cgpa, ielts, field)
        elif any(k in m for k in ["career", "job", "future", "path", "work after"]):
            return self._career_advice(field, cgpa)
        elif any(k in m for k in ["ielts", "toefl", "band", "english", "language"]):
            return IELTS_GUIDE
        elif any(k in m for k in ["sop", "statement", "purpose", "essay", "write"]):
            return SOP_TIPS
        elif any(k in m for k in ["cv", "resume", "curriculum"]):
            return CV_TIPS
        elif any(k in m for k in ["interview", "question", "prepare", "panel"]):
            return INTERVIEW_GUIDE
        elif any(k in m for k in ["reject", "why", "weak", "chance", "probability", "risk"]):
            return self._rejection_analysis(profile)
        elif any(k in m for k in ["reference", "letter", "recommendation", "referee"]):
            return self._reference_tips()
        elif any(k in m for k in ["deadline", "when", "date", "time"]):
            return self._upcoming_deadlines()
        elif any(k in m for k in ["daad", "germany", "german"]):
            return self._scholarship_detail("DAAD Scholarship")
        elif any(k in m for k in ["fulbright", "usa", "america", "american"]):
            return self._scholarship_detail("Fulbright Foreign Student Program")
        elif any(k in m for k in ["chevening", "uk", "britain", "british"]):
            return self._scholarship_detail("Chevening Scholarship")
        elif any(k in m for k in ["gates", "cambridge"]):
            return self._scholarship_detail("Gates Cambridge Scholarship")
        elif any(k in m for k in ["australia", "australian"]):
            return self._scholarship_detail("Australia Awards")
        elif any(k in m for k in ["china", "csc", "chinese"]):
            return self._scholarship_detail("CSC China Scholarship")
        elif any(k in m for k in ["korea", "kgsp", "korean"]):
            return self._scholarship_detail("KGSP Korea")
        elif any(k in m for k in ["hec", "pakistan local", "domestic"]):
            return self._scholarship_detail("HEC Need Based Scholarship")
        elif any(k in m for k in ["6 month", "months before", "timeline", "plan", "roadmap"]):
            return self._quick_roadmap(profile)
        elif any(k in m for k in ["cgpa", "gpa", "grade", "marks"]):
            return self._cgpa_advice(cgpa)
        else:
            # Default — give scholarship matches + tips
            return self._match_scholarships(cgpa, ielts, field)

    def _match_scholarships(self, cgpa: float, ielts: float, field: str) -> str:
        qualified = []
        almost = []
        not_yet = []

        for s in SCHOLARSHIPS:
            gpa_ok = cgpa >= s["gpa"]
            ielts_ok = ielts >= s["ielts"] or s["ielts"] == 0
            if gpa_ok and ielts_ok:
                qualified.append(s)
            elif gpa_ok and not ielts_ok:
                almost.append(s)
            else:
                not_yet.append(s)

        result = f"**🎯 Your Scholarship Matches — CGPA: {cgpa} | IELTS: {ielts}**\n\n"

        if qualified:
            result += "**✅ YOU QUALIFY NOW:**\n"
            for s in qualified[:8]:
                result += f"• **{s['name']}** ({s['country']}) — {s['amount']}\n"
                result += f"  📅 Deadline: {s['deadline']} | ✅ Success Rate: {s['success']}\n"
                result += f"  💡 {s['notes']}\n\n"

        if almost:
            result += f"\n**🟡 QUALIFY AFTER IELTS IMPROVEMENT (need 7.0+):**\n"
            for s in almost[:4]:
                result += f"• **{s['name']}** — needs IELTS {s['ielts']}+ (you have {ielts})\n"

        result += f"\n**📌 STRATEGY:**\n"
        result += f"• Apply to ALL {len(qualified)} scholarships you qualify for simultaneously\n"
        result += f"• {'🔴 Priority: Improve IELTS to 7.0 — unlocks ' + str(len(almost)) + ' more scholarships!' if almost else '✅ IELTS is good — focus on SOP quality'}\n"
        result += f"• {'⚠️ CGPA ' + str(cgpa) + ' — compensate with strong research + exceptional SOP' if cgpa < 3.5 else '✅ CGPA is competitive — keep it up'}\n"
        result += f"• Start SOP writing NOW — takes 2-3 months to perfect\n"
        result += f"• Get 3 strong reference letters from professors who know your work"

        return result

    def _scholarship_detail(self, name: str) -> str:
        for s in SCHOLARSHIPS:
            if name.lower() in s["name"].lower():
                return f"""**📋 {s['name']} — Complete Details**

🌍 **Country:** {s['country']}
💰 **Amount:** {s['amount']}
📅 **Deadline:** {s['deadline']}
🎓 **Degree:** {s['degree']}
📚 **Field:** {s['field']}
📊 **Min CGPA:** {s['gpa']}+
🗣️ **IELTS:** {s['ielts']}+
✅ **Success Rate:** {s['success']}
🔗 **Apply:** {s['url']}

**📌 Important Notes:**
{s['notes']}

**💡 Tips to Win:**
• Research the scholarship's core values deeply
• Tailor your SOP specifically for this scholarship's mission
• Get references from professors who know your research
• Apply early — don't wait for deadline
• Prepare for interview with scholarship-specific Q&A"""
        return "Scholarship details not found. Ask me about Fulbright, Chevening, DAAD, Gates Cambridge, Australia Awards, CSC China, KGSP Korea, etc."

    def _career_advice(self, field: str, cgpa: float) -> str:
        career_map = {
            "computer": {
                "paths": ["🤖 AI/ML Engineer → DAAD Germany / Fulbright USA", "🔒 Cybersecurity Specialist → UK/USA", "📊 Data Scientist → Australia/Canada (PR pathway)", "☁️ Cloud Architect → Remote/International"],
                "best_scholarships": ["Fulbright", "DAAD", "Australia Awards"],
                "top_countries": ["Germany (AI research hub)", "USA (Silicon Valley)", "Canada (PR pathway)"],
            },
            "engineering": {
                "paths": ["⚡ Renewable Energy Engineer → DAAD Germany (EU Green Deal)", "🏗️ Infrastructure Engineer → Australia Awards", "🤖 Robotics Engineer → MEXT Japan", "✈️ Aerospace Engineer → Fulbright USA"],
                "best_scholarships": ["DAAD", "Australia Awards", "MEXT Japan"],
                "top_countries": ["Germany (engineering excellence)", "Japan (robotics leader)", "Australia (infrastructure boom)"],
            },
            "business": {
                "paths": ["📈 Investment Banking → Chevening UK", "🌍 Development Economics → World Bank/IMF pathway", "🚀 Entrepreneurship → Silicon Valley programs", "📊 Management Consulting → MBA (INSEAD/Harvard)"],
                "best_scholarships": ["Chevening", "Fulbright", "Commonwealth"],
                "top_countries": ["UK (finance hub)", "USA (business schools)", "Singapore (Asia hub)"],
            },
            "biology": {
                "paths": ["🧬 Biomedical Researcher → USA/UK PhD", "💊 Pharmaceutical R&D → DAAD Germany", "🌿 Environmental Scientist → Australia Awards", "🔬 Genomics/Bioinformatics → Fastest growing field"],
                "best_scholarships": ["Fulbright", "DAAD", "Commonwealth"],
                "top_countries": ["USA (NIH funding)", "Germany (pharma industry)", "UK (MRC grants)"],
            },
            "medicine": {
                "paths": ["🏥 Clinical Researcher → Commonwealth UK", "🔬 Medical Research → Fulbright USA", "🌍 Global Health → Chevening UK", "💊 Pharmacologist → DAAD Germany"],
                "best_scholarships": ["Commonwealth", "Fulbright", "Chevening"],
                "top_countries": ["UK (NHS pathway)", "USA (NIH)", "Germany (medical research)"],
            },
            "economics": {
                "paths": ["🏦 Central Banking → PhD Economics → State Bank Pakistan", "🌍 Trade Policy → WTO/World Bank career", "📊 Econometrics → Academia → Top universities", "💹 Financial Regulation → IMF career"],
                "best_scholarships": ["Fulbright", "Chevening", "DAAD"],
                "top_countries": ["USA (World Bank/IMF)", "UK (LSE)", "Germany (economic research)"],
            },
            "education": {
                "paths": ["📚 Education Policy → Commonwealth UK", "🌍 International Education → Fulbright USA", "🎓 Curriculum Development → MEXT Japan", "👩‍🏫 Ed-Tech Research → Australia Awards"],
                "best_scholarships": ["Commonwealth", "Fulbright", "Australia Awards"],
                "top_countries": ["UK (education excellence)", "Australia (multicultural ed)", "Finland (best education system)"],
            },
        }

        matched = None
        for key, data in career_map.items():
            if key in field:
                matched = data
                break

        if not matched:
            matched = {
                "paths": ["🎓 Academic Research → PhD scholarship → University faculty", "🌍 International Development → UN/World Bank", "💼 Public Policy → Government think tanks", "📚 Education Leadership → Ministry positions"],
                "best_scholarships": ["Fulbright", "Chevening", "Commonwealth"],
                "top_countries": ["UK", "USA", "Germany"],
            }

        cgpa_note = ("⭐ CGPA qualifies for Gates Cambridge + Rhodes — apply!" if cgpa >= 3.7 else
                     "✅ CGPA competitive for Fulbright, Chevening, DAAD" if cgpa >= 3.5 else
                     "⚠️ Compensate with exceptional research output + specific SOP" if cgpa >= 3.0 else
                     "🔴 Target CSC China + KGSP Korea first, then rebuild for western scholarships")

        return f"""**🚀 Career Paths for {field.title() or 'Your Field'}:**

{chr(10).join(f'• {p}' for p in matched['paths'])}

**🏆 Best Scholarships for Your Field:**
{', '.join(matched['best_scholarships'])}

**🌍 Top Countries for {field.title() or 'Your Field'}:**
{chr(10).join(f'• {c}' for c in matched['top_countries'])}

**📊 Your CGPA {cgpa} Assessment:**
{cgpa_note}

**💡 Key Strategy:**
Pick ONE career direction → align your SOP + research + references to that single narrative.
Committees reject scattered applications. Be laser-focused."""

    def _rejection_analysis(self, profile: Dict) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        ielts = float(profile.get("ielts", 6.5))
        research = profile.get("research", "none")
        leadership = profile.get("leadership", "none")

        score = 60
        issues = []
        fixes = []

        if cgpa < 3.0:
            score -= 30
            issues.append("🔴 CGPA below 3.0 — disqualifies from 80% of scholarships")
            fixes.append("Target CSC China (3.0+) and HEC Pakistan (2.5+) immediately")
        elif cgpa < 3.5:
            score -= 15
            issues.append(f"🟡 CGPA {cgpa} — below competitive threshold (3.5+ preferred)")
            fixes.append("Compensate with research publications + exceptional SOP + strong references")
        else:
            score += 10

        if ielts < 6.0:
            score -= 25
            issues.append(f"🔴 IELTS {ielts} — blocks ALL major international scholarships")
            fixes.append("Register for IELTS immediately. 2 hours daily = 0.5 band improvement per month")
        elif ielts < 6.5:
            score -= 15
            issues.append(f"🟡 IELTS {ielts} — below Fulbright/Chevening/Australia minimum (6.5)")
            fixes.append("One IELTS retake targeting 6.5+ — this single fix unlocks 8 more scholarships")
        elif ielts < 7.0:
            score -= 5
            issues.append(f"🟡 IELTS {ielts} — borderline. 7.0+ makes you more competitive")
            fixes.append("Optional IELTS retake for 7.0+ — worthwhile for Gates Cambridge/Rhodes")
        else:
            score += 10

        if research in ["none", "minimal"]:
            score -= 15
            issues.append("🟡 No research output — critical gap for academic scholarships")
            fixes.append("Co-author with professor in next 3 months. Even conference abstract helps")
        elif research in ["coursework projects"]:
            score -= 5
            issues.append("🟡 Only coursework projects — formal research needed for top scholarships")
            fixes.append("Convert best project into conference paper submission")
        else:
            score += 10

        if leadership in ["none", "minimal"]:
            score -= 10
            issues.append("🟡 Leadership gap — Chevening requires 2+ years documented leadership")
            fixes.append("Start/lead any community initiative NOW. Document every role with impact numbers")
        else:
            score += 5

        issues.append("🟡 SOP quality unknown — 70% of rejections are SOP-related")
        fixes.append("Use SOP Improve feature. Get feedback from 3 people including a professor")

        score = max(5, min(90, score))
        verdict = "🔴 High Risk" if score < 35 else "🟡 Medium Risk" if score < 60 else "🟢 Good Standing" if score < 80 else "⭐ Strong Candidate"

        result = f"""**⚠️ Rejection Risk Analysis — Your Profile**

**Overall Success Probability: {score}% — {verdict}**

**🚨 Issues Found:**
{chr(10).join(f'{i+1}. {issue}' for i, issue in enumerate(issues))}

**✅ Priority Fixes (in order):**
{chr(10).join(f'{i+1}. {fix}' for i, fix in enumerate(fixes))}

{REJECTION_DATA}

**🎯 Your #1 Action Right Now:**
{fixes[0] if fixes else 'Perfect your SOP with specific program details and quantified achievements'}"""

        return result

    def _reference_tips(self) -> str:
        return """**📝 How to Get Strong Reference Letters**

**Who to Ask (in order of strength):**
1. Research supervisor who knows your work deeply
2. Professor whose course you topped or did project with
3. Internship/work supervisor with documented projects
4. Department head (only if they know you personally)

**❌ Never Ask:**
• Professors who barely remember you
• Someone just because they're famous/senior
• Non-academic references for academic scholarships

**📋 How to Make It Easy for Them:**
Send a "Reference Brief" including:
• Your CV (updated)
• The scholarship's core values/mission
• 5 bullet points of YOUR achievements they witnessed
• Specific story they can mention (the project, the results)
• Deadline + submission instructions
• Draft outline (optional but appreciated)

**⏰ Timeline:**
• Ask 2-3 months before deadline
• Send reminder 3 weeks before
• Send final reminder 1 week before
• Always thank them after (regardless of result)

**📧 Email Template:**
Subject: Reference Letter Request — [Scholarship Name] — [Your Name]

"Dear Prof. [Name], I hope this message finds you well. I am applying for [Scholarship] with deadline [Date]. Given your direct knowledge of my work on [specific project], I would be honored if you could provide a reference letter. I have attached my CV and a brief summary of key points you might find helpful. Please let me know if this is possible or if you need any additional information. Thank you for your time and mentorship."

**💡 Pro Tip:** The best reference letters are SPECIFIC — they mention a particular challenge you overcame, a specific result you achieved, and why you specifically will succeed internationally."""

    def _upcoming_deadlines(self) -> str:
        sorted_s = sorted(SCHOLARSHIPS, key=lambda x: x["deadline"])
        result = "**📅 Upcoming Scholarship Deadlines 2026:**\n\n"
        for s in sorted_s:
            result += f"• **{s['deadline']}** — {s['name']} ({s['country']})\n"
            result += f"  💰 {s['amount']} | Min CGPA: {s['gpa']} | IELTS: {s['ielts']}+\n\n"
        result += "\n**⚡ Apply to multiple simultaneously — never just one!**"
        return result

    def _quick_roadmap(self, profile: Dict) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        ielts = float(profile.get("ielts", 6.5))
        research = profile.get("research", "none")

        return f"""**🗺️ Your 12-Month Scholarship Roadmap**
CGPA: {cgpa} | IELTS: {ielts}

**📌 MONTHS 1-2: Foundation**
• {'✅ CGPA competitive — focus on research output' if cgpa >= 3.5 else '🔴 CGPA needs compensation — plan exceptional research + SOP'}
• {'✅ IELTS sufficient — maintain score validity' if ielts >= 6.5 else '🔴 Register for IELTS NOW — target 7.0+ (this is PRIORITY #1)'}
• Make list of 10 target scholarships with deadlines in spreadsheet
• Contact 3 professors for reference letters (start early!)

**📌 MONTHS 3-5: Profile Building**
• {'✅ Continue current research + aim for conference submission' if research not in ['none', 'minimal'] else '🔴 Join research project immediately — publications take 6+ months'}
• Start attending academic seminars, document everything
• Start leadership role if missing — even small initiatives count

**📌 MONTHS 6-8: Documents**
• Write SOP first draft (use SOP Improve feature)
• Get SOP reviewed by professor + scholarship recipient + native English speaker
• Update CV with all new experiences + quantified achievements
• Request formal reference letters with full brief to referees

**📌 MONTHS 9-10: Early Deadlines**
• Jan 16: Stipendium Hungaricum
• Jan-Feb: Erasmus Mundus programs
• Feb 10: Swedish Institute
• Feb 28: KGSP Korea
• Mar 15: CSC China
• Mar 31: Aga Khan Foundation
• Apr 30: Australia Awards

**📌 MONTHS 11-12: Major Deadlines**
• Oct 1: Rhodes (Oxford)
• Oct 7: Chevening (UK)
• Oct 15: Fulbright (USA) + DAAD (Germany)
• Dec 3: Gates Cambridge
• Dec 17: Commonwealth (UK)

**🎯 Your Realistic Targets:**
{'⭐ Fulbright + Chevening + DAAD + Commonwealth + Australia Awards — all achievable!' if cgpa >= 3.5 and ielts >= 6.5 else '📌 Start: CSC China + KGSP Korea + Stipendium Hungaricum → Then: Fulbright + DAAD after improving IELTS/research'}"""

    def _cgpa_advice(self, cgpa: float) -> str:
        if cgpa >= 3.7:
            return f"""**🏆 CGPA {cgpa} — ELITE LEVEL**

✅ You qualify for ALL scholarships including:
• Gates Cambridge (min 3.7)
• Rhodes Scholarship (min 3.7)
• Fulbright, Chevening, DAAD — all open

**Your Strategy:**
• Apply for Gates Cambridge + Rhodes (Pakistan quota exists)
• Aim for IELTS 7.5+ to unlock all options
• Focus on research publications — 1-2 papers will make you nearly unstoppable
• Your CGPA is your biggest asset — highlight it prominently"""

        elif cgpa >= 3.5:
            return f"""**✅ CGPA {cgpa} — COMPETITIVE**

You qualify for most top scholarships:
• Fulbright USA ✅ | Chevening UK ✅ | DAAD Germany ✅
• Commonwealth ✅ | Australia Awards ✅ | Swedish Institute ✅
• CSC China ✅ | KGSP Korea ✅ | Stipendium Hungaricum ✅

**Gates Cambridge/Rhodes:** Need to strengthen research portfolio.

**Your Strategy:**
• Get IELTS 7.0+ to maximize competitiveness
• 1 research publication will significantly boost your profile
• Write tailored SOPs for each scholarship"""

        elif cgpa >= 3.0:
            return f"""**🟡 CGPA {cgpa} — NEEDS COMPENSATION**

You qualify for:
• CSC China ✅ | KGSP Korea ✅ | Stipendium Hungaricum ✅
• DAAD Germany ✅ | Commonwealth ✅ | Australia Awards ✅

Fulbright + Chevening need stronger profile — compensate with:

**CGPA Compensation Strategy:**
1. Research publication — even 1 paper changes everything
2. Exceptional SOP — must show extraordinary potential
3. Strong references from well-known professors
4. Leadership evidence with quantified impact
5. IELTS 7.0+ shows academic ability

**💡 Remember:** Committees consider WHOLE profile. CGPA is ONE factor. Many {cgpa} CGPA students have won Fulbright with exceptional everything else."""

        else:
            return f"""**🔴 CGPA {cgpa} — NEEDS IMMEDIATE FOCUS**

Currently limited options:
• HEC Pakistan ✅ (CGPA 2.5+ needed)
• CSC China — borderline (need 3.0)

**Immediate Action Plan:**
1. Focus on final semester grades — every point matters
2. Apply to HEC Need-Based Scholarship immediately
3. Build research portfolio NOW — will compensate CGPA later
4. Get internship/work experience while improving
5. Consider retaking weak subjects if university allows

**Message of Hope:** Many Pakistani students with low initial CGPAs improved, got research experience, and won international scholarships 2-3 years later. This is a delay, not a dead end."""

    # ── CV ANALYZER ──────────────────────────────────────
    def analyze_cv(self, cv_text: str) -> Dict:
        if self.groq_client:
            system = "You are an expert CV analyst for scholarships. Respond in valid JSON only — no markdown, no extra text."
            prompt = f"""Analyze this CV. Return ONLY valid JSON:
{{
  "ats_score": <0-100>,
  "grade": "<A/B/C/D>",
  "assessment": "<2-3 specific sentences>",
  "weaknesses": ["w1","w2","w3","w4","w5"],
  "improvements": ["i1","i2","i3","i4","i5"],
  "missing_keywords": ["k1","k2","k3","k4","k5"],
  "sections_found": ["s1"],
  "sections_missing": ["s1"]
}}

CV:
{cv_text[:3500]}"""
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            result = self._groq(messages, 1000)
            if result:
                try:
                    m = re.search(r'\{[\s\S]*\}', result)
                    if m:
                        return json.loads(m.group())
                except Exception:
                    pass

        # Smart local fallback
        tl = cv_text.lower()
        score = 35
        found, missing = [], []
        checks = {
            "Education": ["education","university","degree","bachelor","master"],
            "Experience": ["experience","internship","work","job","position"],
            "Skills": ["skills","technical","programming","software"],
            "Research": ["research","publication","paper","thesis","study"],
            "Awards": ["award","scholarship","honor","prize","distinction"],
            "Volunteer": ["volunteer","community","service","ngo","club"],
            "Projects": ["project","developed","built","created","implemented"],
        }
        for sec, kws in checks.items():
            if any(k in tl for k in kws):
                found.append(sec); score += 8
            else:
                missing.append(sec)

        has_numbers = bool(re.search(r'\d+%|\d+ (people|students|members|projects)', tl))
        if has_numbers:
            score += 10

        score = min(score, 85)

        return {
            "ats_score": score,
            "grade": "A" if score>=80 else "B" if score>=65 else "C" if score>=50 else "D",
            "assessment": f"CV contains {len(found)} of {len(checks)} key sections. {'Good quantification found.' if has_numbers else 'Achievements lack numbers and metrics — biggest weakness.'} Scholarship committees need specific evidence of research and leadership impact.",
            "weaknesses": [
                "Achievements not quantified — add percentages and numbers to every bullet point",
                "Research section absent or insufficient — critical for academic scholarships" if "Research" not in found else "Publications section needs more detail",
                "Leadership roles not clearly documented with impact metrics",
                "Missing IELTS/TOEFL score in skills section",
                "No scholarship-specific keywords like 'impact', 'research', 'leadership', 'publication'"
            ],
            "improvements": [
                "Add metrics to EVERY achievement: 'Led project improving X by 35%', 'Taught 200+ students'",
                "Create dedicated 'Research & Projects' section with outcomes and results",
                "Add 'Academic Achievements' section with GPA rank, class position, awards",
                "Document all community service with hours, role, and people impacted",
                "Add 'Language Proficiency' section with IELTS score and date taken"
            ],
            "missing_keywords": ["Research", "Leadership", "Impact", "Publication", "International", "Community", "Innovation"],
            "sections_found": found or ["Education"],
            "sections_missing": missing
        }

    # ── SOP REWRITER ─────────────────────────────────────
    def rewrite_sop(self, original: str, target: str = "") -> Dict:
        if self.groq_client:
            system = "You are a world-class SOP writer. Respond in valid JSON only."
            prompt = f"""Rewrite SOP for {target or 'scholarship'}. Return ONLY valid JSON:
{{
  "rewritten_sop": "<complete rewritten SOP 400+ words>",
  "score_before": <25-55>,
  "score_after": <75-92>,
  "changes": ["c1","c2","c3","c4"],
  "suggestions": ["s1","s2","s3"]
}}

ORIGINAL:
{original[:2000]}"""
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            result = self._groq(messages, 2500)
            if result:
                try:
                    m = re.search(r'\{[\s\S]*\}', result)
                    if m:
                        return json.loads(m.group())
                except Exception:
                    pass

        # Local fallback — structural analysis + tips
        word_count = len(original.split())
        has_specific = any(w in original.lower() for w in ["percent", "%", "students", "team", "led", "developed", "research"])
        has_future = any(w in original.lower() for w in ["plan", "will", "goal", "return", "pakistan", "contribute"])
        score = 30 + (10 if has_specific else 0) + (10 if has_future else 0) + (5 if word_count > 300 else 0)

        return {
            "rewritten_sop": f"""[Add Groq API key in ⚙️ Settings for AI-powered full rewrite]

Based on analysis of your SOP, here is a strengthened version framework:

---

**SUGGESTED OPENING (replace your current opening):**
Replace your opening with a specific moment: "When I [specific situation], I realized [insight that led to your field/research direction]."

**YOUR ORIGINAL CONTENT (analyzed):**
{original[:600]}{'...' if len(original) > 600 else ''}

---

**STRUCTURAL IMPROVEMENTS NEEDED:**
{chr(10).join([
    '1. Opening: Start with a specific story/moment, not a general statement',
    '2. Achievement section: Add numbers — GPA rank, project results, team size',
    '3. Research section: Explain what you found, not just what you did',
    '4. Program fit: Name specific professors and why their work matches yours',
    '5. Pakistan impact: Give a SPECIFIC institution and role you will take',
])}

**TO GET AI-POWERED FULL REWRITE:**
Add your Groq API key in ⚙️ Settings → The AI will completely rewrite your SOP with all improvements applied.""",
            "score_before": score,
            "score_after": score + 35,
            "changes": [
                "Opening needs specific story/moment instead of generic statement",
                "Achievements need quantification (numbers, percentages, team sizes)",
                "Research section needs results/outcomes, not just process",
                "Future plan needs specific institution name in Pakistan"
            ],
            "suggestions": [
                "Add Groq API key for complete AI-powered SOP rewrite",
                "Name 1-2 specific professors at target university whose work matches yours",
                "Include one quantifiable achievement (e.g., 'top 5% of class', 'led team of 12')"
            ]
        }

    # ── REJECTION SIMULATOR ───────────────────────────────
    def simulate_rejection(self, profile: Dict) -> Dict:
        if self.groq_client:
            system = "You are a strict scholarship committee. Respond in valid JSON only."
            prompt = f"""Analyze rejection risk:
CGPA: {profile.get('cgpa',3.0)}, IELTS: {profile.get('ielts',6.5)}, Research: {profile.get('research','none')}, Leadership: {profile.get('leadership','none')}, Target: {profile.get('target_scholarship','International')}

Return ONLY valid JSON:
{{
  "success_probability": <5-90>,
  "verdict": "<High Risk|Medium Risk|Good Standing|Strong Candidate>",
  "estimated_timeline": "<timeline>",
  "risks": [{{"factor":"f","severity":"High","detail":"d","fix":"fix"}}],
  "top_recommendation": "<action>"
}}"""
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            result = self._groq(messages, 900)
            if result:
                try:
                    m = re.search(r'\{[\s\S]*\}', result)
                    if m:
                        return json.loads(m.group())
                except Exception:
                    pass

        # Rich local fallback
        cgpa = float(profile.get('cgpa', 3.0))
        ielts = float(profile.get('ielts', 6.5))
        research = profile.get('research', 'none')
        leadership = profile.get('leadership', 'none')
        score = 55
        risks = []

        if cgpa < 3.0:
            score -= 30
            risks.append({"factor":"Critical CGPA","severity":"High","detail":f"CGPA {cgpa} disqualifies from 80% of international scholarships. Gates Cambridge needs 3.7+, Fulbright needs 3.5+, most need 3.0+.","fix":"Apply to HEC Pakistan and CSC China now. Build research profile for 1-2 years then reapply to international scholarships."})
        elif cgpa < 3.5:
            score -= 15
            risks.append({"factor":"Below-Average CGPA","severity":"Medium","detail":f"CGPA {cgpa} limits access to top-tier scholarships. Competitive applicants have 3.5-3.9.","fix":"Compensate with 1 research publication + exceptional SOP + strong references from well-known professors."})
        else:
            score += 15

        if ielts < 6.0:
            score -= 30
            risks.append({"factor":"Critical Language Score","severity":"High","detail":f"IELTS {ielts} blocks ALL major UK/US/Australia scholarships. Minimum is 6.0-6.5 everywhere.","fix":"Register for IELTS NOW. With 2 hours daily study, gain 0.5 band per month. This is your #1 priority."})
        elif ielts < 6.5:
            score -= 20
            risks.append({"factor":"Low Language Score","severity":"High","detail":f"IELTS {ielts} blocks Fulbright, Chevening, Australia Awards (all need 6.5+).","fix":"One IELTS retake targeting 6.5+ will unlock 8 additional scholarships immediately."})
        elif ielts < 7.0:
            score -= 8
            risks.append({"factor":"Borderline Language Score","severity":"Medium","detail":f"IELTS {ielts} meets minimum but 7.0+ makes you significantly more competitive.","fix":"Optional: one more IELTS attempt for 7.0+. Especially important for Gates Cambridge and Rhodes."})
        else:
            score += 12

        if research in ["none", "minimal"]:
            score -= 15
            risks.append({"factor":"Weak Research Profile","severity":"Medium","detail":"No publications or formal research experience significantly weakens PhD scholarship applications. Committees want evidence of research potential.","fix":"Contact professor for research collaboration. Even one conference paper or poster submission helps enormously."})
        elif research in ["coursework projects"]:
            score -= 5
            risks.append({"factor":"Informal Research Only","severity":"Low","detail":"Coursework projects don't substitute for formal research for competitive scholarships.","fix":"Convert best project into a conference paper submission or journal article."})
        else:
            score += 12

        if leadership in ["none", "minimal"]:
            score -= 10
            risks.append({"factor":"Leadership Gap","severity":"Medium","detail":"Chevening requires 2+ years documented leadership. Fulbright, Rhodes heavily value community leadership and impact.","fix":"Start leading ANY initiative NOW — even small. Document with numbers (people reached, funds raised, outcomes achieved)."})
        else:
            score += 8

        risks.append({"factor":"SOP Quality Risk","severity":"Medium","detail":"70% of scholarship rejections are SOP-related. Generic SOPs that could be written by anyone are immediately rejected.","fix":"Use SOP Improve feature. Get feedback from 3 people: professor, scholarship recipient, native English speaker. Revise 3+ times."})

        score = max(8, min(90, score))
        verdict = "High Risk" if score < 35 else "Medium Risk" if score < 60 else "Good Standing" if score < 80 else "Strong Candidate"
        timeline = "18-24 months of profile building needed" if score < 35 else "6-12 months of targeted improvement" if score < 60 else "Ready now — focus on SOP quality"

        return {
            "success_probability": score,
            "verdict": verdict,
            "estimated_timeline": timeline,
            "risks": risks,
            "top_recommendation": risks[0]["fix"] if risks else "Perfect your SOP with specific program details and quantified achievements"
        }

    # ── EVALUATE ANSWER ───────────────────────────────────
    def evaluate_answer(self, question: str, answer: str) -> Dict:
        if self.groq_client:
            system = "You are a scholarship interview panelist. Respond in valid JSON only."
            prompt = f"""Evaluate:
Q: {question}
A: {answer}

Return ONLY valid JSON:
{{"clarity":<0-25>,"relevance":<0-25>,"evidence":<0-25>,"communication":<0-25>,"total":<sum>,"grade":"<A+/A/B+/B/C+/C>","strengths":["s1","s2"],"improvements":["i1","i2"],"model_answer_tip":"<tip>"}}"""
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            result = self._groq(messages, 600)
            if result:
                try:
                    m = re.search(r'\{[\s\S]*\}', result)
                    if m:
                        data = json.loads(m.group())
                        data["total"] = data.get("clarity",0)+data.get("relevance",0)+data.get("evidence",0)+data.get("communication",0)
                        return data
                except Exception:
                    pass

        words = len(answer.split())
        has_ex = any(k in answer.lower() for k in ["when","example","result","achieved","during","project","team"])
        has_num = bool(re.search(r'\d+', answer))
        has_pakistan = any(k in answer.lower() for k in ["pakistan","contribute","return","impact","community"])
        has_star = any(k in answer.lower() for k in ["situation","challenge","task","action","result"])

        cl = min(23, 10 + (words // 12))
        rel = 20 if len(answer) > 150 else 14 if len(answer) > 80 else 10
        ev = 22 if (has_ex and has_num) else 16 if has_ex else 10
        com = 20 if (words > 80 and has_pakistan) else 16 if words > 60 else 10
        total = cl + rel + ev + com

        strengths = []
        improvements = []
        if words > 100: strengths.append("Good response length — well-developed answer")
        else: improvements.append("Too short — aim for 200-280 words for scholarship interviews")
        if has_ex: strengths.append("Included specific example — panels appreciate concrete evidence")
        else: improvements.append("Add a specific example using STAR format: Situation→Task→Action→Result")
        if has_num: strengths.append("Used numbers/metrics — strengthens credibility")
        else: improvements.append("Add quantifiable metrics: 'led 12 people', 'improved by 35%', 'reached 200 students'")
        if has_pakistan: strengths.append("Mentioned Pakistan impact — committees value this")
        else: improvements.append("Connect your answer to Pakistan impact/contribution — very important for Pakistani applicants")

        return {
            "clarity": cl, "relevance": rel, "evidence": ev, "communication": com, "total": total,
            "grade": "A+" if total>90 else "A" if total>85 else "B+" if total>75 else "B" if total>65 else "C+",
            "strengths": strengths[:2] if strengths else ["You attempted the answer"],
            "improvements": improvements[:2] if improvements else ["Practice STAR format responses"],
            "model_answer_tip": "Top answers: 30s context + 60s specific example with measurable result + 30s connect to scholarship goal and Pakistan impact."
        }

    # ── IELTS PROMPT ──────────────────────────────────────
    def generate_ielts_prompt(self, part: str, topic: str) -> str:
        if self.groq_client:
            system = "You are an expert IELTS examiner."
            prompt = f"Generate IELTS Speaking {part} for topic: {topic}. Include prompt card, timing, Band 7+ vocabulary, mistakes, model opening."
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            result = self._groq(messages, 700)
            if result:
                return result

        prompts_map = {
            "Education": ("Describe a teacher or professor who had a significant positive influence on your academic or personal development.", ["inspiring, transformative, dedicated, knowledgeable, encouraging", "shaped, influenced, motivated, guided, mentored"]),
            "Technology": ("Describe a piece of technology that has significantly changed the way you live or work.", ["revolutionary, innovative, indispensable, transformative, cutting-edge", "streamlined, automated, enhanced, optimized, facilitated"]),
            "Environment": ("Describe an environmental problem in your local area or country and suggest what can be done about it.", ["deteriorating, alarming, sustainable, eco-friendly, conservation", "mitigate, address, combat, tackle, alleviate"]),
            "Culture": ("Describe a cultural tradition or festival from your country that you find particularly meaningful.", ["heritage, ancestral, vibrant, ceremonial, commemorative", "preserve, celebrate, honor, symbolize, represent"]),
            "Work & Career": ("Describe a job or career that you think would be particularly challenging but rewarding.", ["demanding, fulfilling, prestigious, lucrative, specialized", "pursue, achieve, develop, contribute, excel"]),
            "Health": ("Describe a healthy habit that you have or that you think is particularly important for people to develop.", ["beneficial, essential, disciplined, consistent, holistic", "maintain, cultivate, adopt, prioritize, sustain"]),
            "Random": ("Describe a significant challenge you faced and explain how you overcame it.", ["daunting, formidable, overwhelming, persistent, resilient", "persevere, overcome, navigate, tackle, resolve"]),
        }

        q, (vocab1, vocab2) = prompts_map.get(topic, prompts_map["Random"])

        return f"""**🎤 IELTS Speaking {part} — {topic}**

**📋 Prompt Card:**
*"{q}"*

**You should say:**
• What/who/where it is and when you first encountered it
• Why it is significant or important to you personally
• How it has affected your life, studies, or thinking
• What you would tell others about this topic

**⏱️ Timing:**
• 1 minute preparation (take notes — use keywords not full sentences)
• 2 minutes speaking (examiner will stop you at 2 mins)
• 1-2 follow-up questions from examiner

**🎯 Band 7+ Vocabulary for this topic:**
• Adjectives: {vocab1}
• Verbs: {vocab2}
• Academic connectors: *Furthermore, In contrast, Consequently, Notably, It is worth mentioning that*

**✅ Model Opening (memorize this structure):**
*"I'd like to talk about [topic]. What makes this particularly [adjective] is [specific reason]. I first [encountered/experienced] this when [specific time/situation]..."*

**❌ Common Mistakes to Avoid:**
• Starting with "Um, I think..." (costs fluency marks)
• Memorized answers (examiners detect immediately — vary your words)
• Stopping when unsure (use fillers: "That's an interesting point to consider...")
• Speaking too fast when nervous (deliberately slow down by 20%)
• One-word answers to follow-up questions (always elaborate)

**💡 Scoring Tip:**
Band 7 requires: natural pace + varied vocabulary + logical structure + few errors
Band 8 requires: all of above + idiomatic expressions + complex sentence structures"""

    # ── ROADMAP ───────────────────────────────────────────
    def generate_roadmap(self, current_year: str, field: str, target_degree: str, target_year: str, profile: Dict) -> str:
        if self.groq_client:
            system = "You are a scholarship strategy expert."
            prompt = f"""Month-by-month scholarship roadmap:
Year: {current_year}, Field: {field}, Target: {target_degree} in {target_year}
CGPA: {profile.get('cgpa',3.0)}, IELTS: {profile.get('ielts',6.5)}
Research: {profile.get('research','none')}, Leadership: {profile.get('leadership','none')}
Be specific with real deadlines and honest assessment."""
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            result = self._groq(messages, 1800)
            if result:
                return result

        return self._quick_roadmap(profile)
