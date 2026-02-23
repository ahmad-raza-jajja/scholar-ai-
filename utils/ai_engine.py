"""
ScholarAI Elite v4 — AI Engine
Groq Llama3 primary | RAG-enhanced responses | Smart fallback
"""

import os
import re
import json
import random
from typing import Dict, List, Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def get_secret(key: str, fallback: str = "") -> str:
    """Read from Streamlit secrets or environment"""
    try:
        import streamlit as st
        try:
            val = st.secrets[key]
            if val:
                return str(val).strip()
        except Exception:
            pass
        val = st.secrets.get(key, "")
        if val:
            return str(val).strip()
    except Exception:
        pass
    return str(os.environ.get(key, fallback)).strip()


class AIEngine:
    def __init__(self, groq_key: str = "", gemini_key: str = ""):
        self.groq_key = groq_key or get_secret("GROQ_API_KEY")
        self.gemini_key = gemini_key or get_secret("GEMINI_API_KEY")
        self.groq_client = None
        self.gemini_model = None
        self.rag = None
        self._init_models()

    def _init_models(self):
        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception:
                self.groq_client = None
        if GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
            except Exception:
                self.gemini_model = None

    def set_rag(self, rag_engine):
        """Inject RAG engine for context retrieval"""
        self.rag = rag_engine

    def _groq_call(self, messages: List[Dict], max_tokens: int = 1500, temp: float = 0.7) -> Optional[str]:
        if not self.groq_client:
            return None
        try:
            resp = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temp,
            )
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "limit" in err:
                return "⚠️ Rate limit reached. Please wait 30 seconds and try again."
            if "auth" in err or "invalid" in err:
                return "⚠️ Groq API key invalid. Please re-enter in ⚙️ Settings."
            return None

    def _ai_call(self, system: str, user_msg: str, max_tokens: int = 1500) -> Optional[str]:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]
        result = self._groq_call(messages, max_tokens)
        if result:
            return result
        if self.gemini_model:
            try:
                return self.gemini_model.generate_content(f"{system}\n\n{user_msg}").text
            except Exception:
                pass
        return None

    # ─────────────────────────────────────────────────────────────
    # CHAT WITH RAG
    # ─────────────────────────────────────────────────────────────
    def chat_response(self, message: str, profile: Dict, history: List) -> str:
        cgpa = profile.get("cgpa", 3.0)
        field = profile.get("field", "General")
        ielts = profile.get("ielts", 6.5)
        country = profile.get("country", "Any")
        name = profile.get("name", "Student")

        # RAG: retrieve relevant scholarships
        rag_context = ""
        if self.rag and self.rag.is_built:
            rag_results = self.rag.retrieve(message, top_k=4)
            if rag_results:
                rag_context = self.rag.format_context(rag_results)

        system = f"""You are ScholarAI Elite — a world-class international scholarship advisor powered by RAG (Retrieval-Augmented Generation).

Student Profile:
- Name: {name} | CGPA: {cgpa}/4.0 | Field: {field}
- Target Country: {country} | IELTS: {ielts}

{rag_context}

CRITICAL RULES:
1. ALWAYS use the scholarship database context above when answering — cite real scholarship names, amounts, deadlines
2. Answer EXACTLY what is asked — never give generic advice
3. Be SPECIFIC: real scholarship names, real deadlines from the database, real GPA requirements
4. Based on their CGPA {cgpa} and IELTS {ielts} — tell them which scholarships they qualify for
5. If they ask about career → give field-specific paths for {field}
6. Be honest: if something needs improvement, say so clearly with specific fix
7. Use emojis and structured bullet points for readability
8. Keep responses focused and actionable
9. If the database has relevant info, ALWAYS reference it with specific details"""

        messages = [{"role": "system", "content": system}]
        for h in history[-8:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        if self.groq_client:
            try:
                resp = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=messages,
                    max_tokens=1400,
                    temperature=0.7,
                )
                return resp.choices[0].message.content
            except Exception as e:
                err = str(e).lower()
                if "rate" in err:
                    return "⚠️ Rate limit reached. Please wait 30 seconds and try again."
                if "auth" in err or "invalid" in err:
                    return "⚠️ Groq API key error. Please re-enter your key in ⚙️ Settings."

        if self.gemini_model:
            try:
                full = f"{system}\n\nPrevious: {str(history[-2:])}\n\nUser: {message}"
                return self.gemini_model.generate_content(full).text
            except Exception:
                pass

        return self._local_chat(message, profile)

    def _local_chat(self, msg: str, profile: Dict) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        field = str(profile.get("field", "")).lower()
        ielts = float(profile.get("ielts", 6.5))
        m = msg.lower()

        if any(k in m for k in ["career", "path", "future", "job", "work"]):
            return self._career_advice(field, cgpa)
        elif any(k in m for k in ["scholarship", "fund", "which", "best", "apply", "option"]):
            return self._scholarship_match(cgpa, ielts, field)
        elif any(k in m for k in ["sop", "statement", "purpose", "essay"]):
            return """**SOP Writing — Key Principles:**

🎯 **Opening** — Never start with "I have always been passionate about..."
✅ Start with a specific moment, problem you solved, or insight that defines you

📋 **Structure (600-800 words):**
1. **Hook** — One specific story or insight (2-3 sentences)
2. **Academic Journey** — Your achievements with numbers
3. **Research/Work** — What you DID and what RESULTED
4. **Why This Program** — Name specific professors, courses, labs
5. **Future Plan** — Concrete role you will take in Pakistan after

✅ **Power Words:** catalyzed, spearheaded, quantified, pioneered, demonstrated
❌ **Remove:** passionate, hardworking, always wanted, dream of"""

        elif any(k in m for k in ["ielts", "toefl", "english", "band"]):
            target = f"Your current score: **{ielts}**"
            return f"""**IELTS Guide — {target}**

🎯 **Target Scores by Scholarship:**
- CSC China, HEC: 6.0 ({'✅ You qualify' if ielts >= 6.0 else '❌ Need improvement'})
- DAAD, Australia Awards: 6.5 ({'✅ You qualify' if ielts >= 6.5 else '❌ Need improvement'})
- Fulbright, Chevening: 6.5-7.0 ({'✅ You qualify' if ielts >= 6.5 else '❌ Need improvement'})
- Gates Cambridge, Rhodes: 7.5 ({'✅ You qualify' if ielts >= 7.5 else '❌ Need improvement'})

📚 **Fastest Improvement Strategy:**
• Reading & Listening → Practice 1 full test daily (fastest gains)
• Writing Task 1 → Master 5 graph vocabulary sets
• Writing Task 2 → Learn 3 essay structures
• Speaking → Record yourself daily, use HelloTalk app

⏱️ With daily 2-hour study → ~0.5 band improvement per month"""

        elif any(k in m for k in ["reject", "why", "weak", "chance"]):
            return self._rejection_local(profile)
        else:
            return self._scholarship_match(cgpa, ielts, field)

    def _career_advice(self, field: str, cgpa: float) -> str:
        career_map = {
            "computer": ["🤖 AI/ML Researcher → DAAD/Fulbright → $120k+ globally", "🔒 Cybersecurity Engineer → UK/USA", "📊 Data Scientist → Australia/Canada → PR pathway", "☁️ Cloud Solutions Architect → Remote work possible"],
            "engineering": ["⚡ Renewable Energy → Germany DAAD → EU Green Deal", "🏗️ Infrastructure → Australia Awards", "🤖 Robotics → Japan MEXT", "✈️ Aerospace → USA Fulbright"],
            "business": ["📈 Investment Banking → LSE/Wharton → Chevening path", "🌍 Development Economics → World Bank pipeline", "🚀 Tech Entrepreneurship → Silicon Valley", "📊 Management Consulting → INSEAD/Harvard MBA"],
            "biology": ["🧬 Biomedical Research → USA/UK PhD", "💊 Pharmaceutical R&D → Germany DAAD", "🌿 Environmental Science → Australia Awards", "🔬 Genomics/Bioinformatics → Fastest growing field"],
            "medicine": ["🏥 Clinical Research → UK Commonwealth", "🔬 Medical Research → Fulbright", "🌍 Global Health → Chevening", "💊 Pharmacology → DAAD → German pharma"],
            "economics": ["🏦 Central Banking → PhD Economics", "🌍 International Trade Policy → WTO career", "📊 Econometrics Research → Academia", "💹 Financial Regulation → IMF/World Bank"],
        }
        matched = []
        for key, options in career_map.items():
            if key in field:
                matched = options
                break
        if not matched:
            matched = ["🎓 Academic Research → PhD scholarship", "🌍 International Development → UN/World Bank", "💼 Public Policy → Government/Think tanks", "📚 Education Leadership → Ministry positions"]

        note = ("⭐ Your CGPA qualifies for elite programs" if cgpa >= 3.7 else
                "✅ CGPA is competitive for Fulbright, Chevening, DAAD" if cgpa >= 3.5 else
                "⚠️ Compensate with strong research + exceptional SOP" if cgpa >= 3.0 else
                "🔴 Target CSC China, KGSP Korea first")

        return f"""**Career Paths for {field.title() or 'Your Field'}:**

{chr(10).join(f'• {p}' for p in matched)}

**Your CGPA Assessment ({cgpa}/4.0):** {note}

💡 **Strategy:** Pick ONE direction → align SOP + research + references to that single narrative."""

    def _scholarship_match(self, cgpa: float, ielts: float, field: str) -> str:
        options = []
        if cgpa >= 3.7 and ielts >= 7.5:
            options += ["⭐ Gates Cambridge (UK) — Full funding — Dec 3, 2026", "⭐ Rhodes Scholarship (Oxford) — £21k/year — Oct 1, 2026"]
        if cgpa >= 3.5 and ielts >= 6.5:
            options += ["✅ Fulbright (USA) — Full funding — Oct 15, 2026", "✅ Chevening (UK) — Full funding — Oct 7, 2026"]
        if cgpa >= 3.2 and ielts >= 6.0:
            options += ["✅ DAAD (Germany) — €934-1200/month — Oct 15, 2026", "✅ Commonwealth (UK) — Full funding — Dec 17, 2026"]
        if cgpa >= 3.0 and ielts >= 6.5:
            options += ["✅ Australia Awards — Full funding — Apr 30, 2026", "✅ Swedish Institute — 13k SEK/month — Feb 10, 2026"]
        if cgpa >= 3.0:
            options += ["📌 CSC China — Full funding — Mar 15, 2026", "📌 KGSP Korea — Full funding — Feb 28, 2026", "📌 Stipendium Hungaricum — Full funding — Jan 16, 2026"]
        if not options:
            options = ["📌 HEC Need-Based (Pakistan) — Full tuition — Jun 30, 2026", "📌 CSC China — Full funding — Mar 15, 2026 (most accessible)"]

        return f"""**Scholarships You Qualify For (CGPA: {cgpa} | IELTS: {ielts}):**

{chr(10).join(f'  {o}' for o in options)}

**Strategy:**
• Apply to 6-8 simultaneously — never just 1-2
• {'🔴 Improve IELTS to 7.0 first — unlocks 5 more scholarships' if ielts < 7.0 else '✅ IELTS sufficient for most options'}
• Start SOP now — good SOP takes 2-3 months of revision"""

    def _rejection_local(self, profile: Dict) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        ielts = float(profile.get("ielts", 6.5))
        risks = []
        if cgpa < 3.5:
            risks.append(f"🔴 CGPA {cgpa} — Below competitive threshold (need 3.5+)")
        if ielts < 7.0:
            risks.append(f"🔴 IELTS {ielts} — Most UK/US scholarships want 7.0+")
        if profile.get("research", "none") in ["none", "minimal"]:
            risks.append("🟡 No research output — critical gap for academic scholarships")
        if profile.get("leadership", "none") in ["none", "minimal"]:
            risks.append("🟡 Leadership gap — Chevening requires 2+ years leadership")
        risks.append("🟡 SOP quality unknown — 70% of rejections are SOP-related")
        score = max(15, 85 - (len([r for r in risks if '🔴' in r]) * 20) - (len([r for r in risks if '🟡' in r]) * 8))
        return f"""**Your Rejection Risk Factors:**
{chr(10).join(risks)}

**Overall Success Probability: {score}%**
{'🔴 High Risk — major improvements needed' if score < 40 else '🟡 Medium Risk — targeted improvements will help' if score < 65 else '🟢 Good Standing — focus on SOP quality'}

**Top Priority:** {'Retake IELTS — biggest impact on eligibility' if ielts < 7.0 else 'Build research portfolio — separates you from competition'}"""

    # ─────────────────────────────────────────────────────────────
    # CV ANALYZER
    # ─────────────────────────────────────────────────────────────
    def analyze_cv(self, cv_text: str) -> Dict:
        system = "You are an expert CV analyst for international scholarships. Be specific and critical. Respond in valid JSON only — no markdown, no extra text."
        prompt = f"""Analyze this CV for scholarship applications. Return ONLY this JSON:
{{
  "ats_score": <number 0-100>,
  "grade": "<A/B/C/D>",
  "assessment": "<2-3 specific sentences about THIS CV>",
  "weaknesses": ["<specific weakness 1>","<specific weakness 2>","<specific weakness 3>","<specific weakness 4>","<specific weakness 5>"],
  "improvements": ["<specific improvement 1>","<specific improvement 2>","<specific improvement 3>","<specific improvement 4>","<specific improvement 5>"],
  "missing_keywords": ["keyword1","keyword2","keyword3","keyword4","keyword5"],
  "sections_found": ["section1","section2"],
  "sections_missing": ["section1","section2"]
}}

CV:
{cv_text[:4000]}"""

        result = self._ai_call(system, prompt, 1200)
        if result:
            try:
                m = re.search(r'\{[\s\S]*\}', result)
                if m:
                    return json.loads(m.group())
            except Exception:
                pass

        tl = cv_text.lower()
        score = 40
        found, missing = [], []
        checks = {"Education": ["education","university","degree"], "Experience": ["experience","internship","work"], "Skills": ["skills","technical","programming"], "Research": ["research","publication","paper"], "Awards": ["award","scholarship","honor"], "Volunteer": ["volunteer","community","service"], "References": ["reference","referee"]}
        for sec, kws in checks.items():
            if any(k in tl for k in kws):
                found.append(sec); score += 7
            else:
                missing.append(sec)
        score = min(score, 82)
        return {
            "ats_score": score, "grade": "A" if score>=80 else "B" if score>=65 else "C" if score>=50 else "D",
            "assessment": f"CV has {len(found)} of {len(checks)} key sections. Scholarship committees need evidence of research, leadership, and quantifiable impact.",
            "weaknesses": ["Achievements not quantified — no numbers or percentages","Research section absent or insufficient","Leadership roles not clearly documented","No publications or conference presentations","Skills section missing scholarship-relevant keywords"],
            "improvements": ["Add metrics: 'Led project improving efficiency by 35%'","Create dedicated 'Research & Projects' section","Add 'Academic Achievements' section with rank, GPA, awards","Document all community service with hours and specific role","Add 'Language Proficiency' section with IELTS score"],
            "missing_keywords": ["Research","Leadership","Impact","Publication","International"],
            "sections_found": found or ["Education"],
            "sections_missing": missing
        }

    # ─────────────────────────────────────────────────────────────
    # SOP REWRITER
    # ─────────────────────────────────────────────────────────────
    def rewrite_sop(self, original: str, target: str = "") -> Dict:
        system = "You are a world-class SOP writer who helped 500+ students win Fulbright, Chevening, Gates Cambridge. Respond in valid JSON only — no markdown backticks."
        prompt = f"""Rewrite this SOP for {target or 'international scholarship'} with HIGH IMPACT.
Return ONLY this JSON:
{{
  "rewritten_sop": "<complete rewritten SOP minimum 400 words>",
  "score_before": <number 25-55>,
  "score_after": <number 75-92>,
  "changes": ["<change 1>","<change 2>","<change 3>","<change 4>"],
  "suggestions": ["<suggestion 1>","<suggestion 2>","<suggestion 3>"]
}}

Original SOP:
{original[:2500]}"""

        result = self._ai_call(system, prompt, 2500)
        if result:
            try:
                m = re.search(r'\{[\s\S]*\}', result)
                if m:
                    return json.loads(m.group())
            except Exception:
                pass

        return {
            "rewritten_sop": f"""The turning point came when I realized that theoretical knowledge alone could not solve the problem in front of me. As a dedicated {target or 'scholarship'} applicant, I have spent years not just studying my field, but living its challenges and testing its solutions in real environments.

{original[:300] if len(original) > 300 else original}

My academic journey has been defined by one principle: research must create measurable impact. During my undergraduate studies, I led projects that resulted in concrete outcomes, demonstrating my ability to bridge theory and practice.

The {target or 'this program'} represents the precise environment I need to amplify this impact. Upon completing this program, I will return to Pakistan with a specific mandate — to establish concrete initiatives directly addressing national challenges.

[ACTION: Replace bracketed items with your specific details]""",
            "score_before": 35, "score_after": 74,
            "changes": ["Replaced generic opening with specific insight moment", "Added quantifiable achievement framework", "Included specific program knowledge references", "Created clear narrative arc: problem → experience → program → impact"],
            "suggestions": ["Add specific professor name from target university", "Include one quantifiable achievement with numbers", "Make Pakistan contribution paragraph more concrete with institution name"]
        }

    # ─────────────────────────────────────────────────────────────
    # REJECTION SIMULATOR
    # ─────────────────────────────────────────────────────────────
    def simulate_rejection(self, profile: Dict) -> Dict:
        system = "You are a strict scholarship committee member. Give realistic rejection analysis. Respond in valid JSON only."
        prompt = f"""Analyze rejection risk for this student:
CGPA: {profile.get('cgpa',3.0)}, IELTS: {profile.get('ielts',6.5)}, Field: {profile.get('field','General')}, Research: {profile.get('research','none')}, Leadership: {profile.get('leadership','none')}, Target: {profile.get('target_scholarship','International Scholarship')}

Return ONLY this JSON:
{{
  "success_probability": <5-90>,
  "verdict": "<High Risk|Medium Risk|Good Standing|Strong Candidate>",
  "estimated_timeline": "<specific timeline to be competitive>",
  "risks": [{{"factor":"<factor name>","severity":"<High|Medium|Low>","detail":"<specific detail>","fix":"<actionable fix>"}}],
  "top_recommendation": "<single most important action they should take NOW>"
}}"""

        result = self._ai_call(system, prompt, 1000)
        if result:
            try:
                m = re.search(r'\{[\s\S]*\}', result)
                if m:
                    return json.loads(m.group())
            except Exception:
                pass

        cgpa = float(profile.get('cgpa', 3.0))
        ielts = float(profile.get('ielts', 6.5))
        research = profile.get('research', 'none')
        leadership = profile.get('leadership', 'none')
        score = 50
        risks = []
        if cgpa < 3.0:
            score -= 25; risks.append({"factor":"Critical CGPA","severity":"High","detail":f"CGPA {cgpa} disqualifies you from 80% of scholarships.","fix":"Target CSC China (3.0+) or HEC Pakistan while rebuilding profile."})
        elif cgpa < 3.5:
            score -= 10; risks.append({"factor":"Below-Average CGPA","severity":"Medium","detail":f"CGPA {cgpa} limits options. Most competitive scholarships need 3.5+.","fix":"Compensate with exceptional research output and very specific SOP."})
        else:
            score += 15
        if ielts < 6.5:
            score -= 20; risks.append({"factor":"Low Language Score","severity":"High","detail":f"IELTS {ielts} blocks UK/US/Australia scholarships.","fix":"Register for IELTS now. 0.5 band improvement per month with focused study."})
        elif ielts < 7.0:
            score -= 5; risks.append({"factor":"Borderline Language Score","severity":"Medium","detail":f"IELTS {ielts} meets minimum but not competitive threshold.","fix":"One more IELTS attempt targeting 7.0+ is worth the investment."})
        else:
            score += 10
        if research in ["none","minimal"]:
            score -= 15; risks.append({"factor":"Weak Research Profile","severity":"Medium","detail":"No publications or research experience significantly hurts PhD applications.","fix":"Co-author with professor, present at conference, or complete research internship."})
        else:
            score += 10
        if leadership in ["none","minimal"]:
            risks.append({"factor":"Leadership Gap","severity":"Medium","detail":"Chevening requires documented leadership. Fulbright values community leadership.","fix":"Start or lead any community initiative NOW. Document existing informal leadership."})
        else:
            score += 5
        risks.append({"factor":"SOP Risk","severity":"Medium","detail":"70% of rejections are SOP-related. Generic SOPs are immediately identified.","fix":"Use SOP Improve tool, get 3 rounds of feedback from professors and scholarship recipients."})
        score = max(10, min(88, score))
        verdict = "High Risk" if score<40 else "Medium Risk" if score<60 else "Good Standing" if score<78 else "Strong Candidate"
        return {"success_probability":score,"verdict":verdict,"estimated_timeline":"18-24 months" if score<40 else "6-12 months" if score<60 else "Ready now — focus on SOP quality","risks":risks,"top_recommendation":risks[0]["fix"] if risks else "Polish SOP with specific program details"}

    # ─────────────────────────────────────────────────────────────
    # INTERVIEW EVALUATOR
    # ─────────────────────────────────────────────────────────────
    def evaluate_answer(self, question: str, answer: str) -> Dict:
        system = "You are a scholarship interview panelist. Evaluate critically and fairly. Respond in valid JSON only."
        prompt = f"""Evaluate this interview answer:
Question: {question}
Answer: {answer}

Return ONLY this JSON:
{{
  "clarity": <0-25>,
  "relevance": <0-25>,
  "evidence": <0-25>,
  "communication": <0-25>,
  "total": <sum of above>,
  "grade": "<A+/A/B+/B/C+/C>",
  "strengths": ["<strength 1>","<strength 2>"],
  "improvements": ["<specific improvement 1>","<specific improvement 2>"],
  "model_answer_tip": "<what a band A answer would include>"
}}"""

        result = self._ai_call(system, prompt, 700)
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
        has_ex = any(k in answer.lower() for k in ["when","during","example","result","outcome","achieved"])
        has_num = any(c.isdigit() for c in answer)
        cl = min(23, 12+(words//15)); rel = 18 if len(answer)>100 else 12
        ev = 21 if (has_ex and has_num) else 15 if has_ex else 10; com = 19 if words>80 else 13
        total = cl+rel+ev+com
        return {"clarity":cl,"relevance":rel,"evidence":ev,"communication":com,"total":total,
                "grade":"A+" if total>90 else "A" if total>85 else "B+" if total>75 else "B" if total>65 else "C+",
                "strengths":["Good response length" if words>80 else "Concise answer","Specific example included" if has_ex else "Direct response"],
                "improvements":["Add numbers/metrics: 'led team of 12', 'improved by 35%'" if not has_num else "Good use of metrics ✅","Use STAR format: Situation→Task→Action→Result"],
                "model_answer_tip":"Top answers: context (30s) + ONE specific example with measurable result (60s) + connect to scholarship goals (30s)."}

    # ─────────────────────────────────────────────────────────────
    # IELTS PROMPT GENERATOR
    # ─────────────────────────────────────────────────────────────
    def generate_ielts_prompt(self, part: str, topic: str) -> str:
        system = "You are an expert IELTS examiner with 10+ years experience. Generate realistic, useful prompts with full guidance."
        prompt = f"""Generate an IELTS Speaking {part} prompt for topic: {topic}.
Include: 1) The actual prompt card 2) What to cover 3) Timing 4) Band 7+ vocabulary 5) Common mistakes 6) Model opening sentence."""
        result = self._ai_call(system, prompt, 800)
        if result:
            return result

        prompts_map = {"Education": "Describe a teacher who significantly influenced your academic journey.", "Technology": "Talk about a piece of technology that has changed your daily life.", "Environment": "Describe an environmental problem in your area and suggest solutions.", "Culture": "Describe a cultural tradition from Pakistan that you find meaningful.", "Work & Career": "Talk about a job or career you would like to pursue in the future.", "Health": "Describe a healthy habit you have developed or would like to develop.", "Random": "Describe a significant challenge you overcame and what you learned."}
        q = prompts_map.get(topic, prompts_map["Random"])
        return f"""**IELTS Speaking {part} — {topic}**

📋 **Prompt Card:** *"{q}"*

You should say:
• What/who/where it is and when you encountered it
• Why it is significant or important to you
• How it has impacted your life or thinking
• What you would say to others about it

⏱️ **Timing:** 1 min prep → 2 min speaking → 1 min follow-up

🎯 **Band 7+ Vocabulary:**
• good → *remarkable, exceptional, profound, invaluable*
• said → *articulated, emphasized, conveyed, highlighted*
• Connectors: *Furthermore | In contrast | Consequently | Notably*

✅ **Model Opening:** *"This is something that profoundly shaped my perspective because..."*

❌ **Common Mistakes:** Memorized answers, speaking too fast, generic examples"""

    # ─────────────────────────────────────────────────────────────
    # ROADMAP GENERATOR
    # ─────────────────────────────────────────────────────────────
    def generate_roadmap(self, current_year: str, field: str, target_degree: str, target_year: str, profile: Dict) -> str:
        system = "You are a scholarship strategy expert who guided 1000+ students. Create specific, realistic roadmaps."
        prompt = f"""Create a detailed month-by-month scholarship roadmap for:
- Current Year: {current_year}, Field: {field}, Target: {target_degree} starting {target_year}
- CGPA: {profile.get('cgpa',3.0)}, IELTS: {profile.get('ielts',6.5)}
- Research: {profile.get('research','none')}, Leadership: {profile.get('leadership','none')}

Be SPECIFIC. Include real scholarship deadlines from database. Give honest assessment of their competitiveness."""

        result = self._ai_call(system, prompt, 2000)
        if result:
            return result

        cgpa = float(profile.get("cgpa", 3.0))
        ielts = float(profile.get("ielts", 6.5))
        return f"""**Your Personalized Scholarship Roadmap**
CGPA: {cgpa} | IELTS: {ielts} | Field: {field} | Target: {target_degree}

**🗓️ MONTHS 1-2: Honest Assessment & Planning**
• {'✅ CGPA competitive — focus on research' if cgpa>=3.5 else '🔴 CGPA needs compensation — plan exceptional research + SOP'}
• {'✅ IELTS sufficient' if ielts>=6.5 else '🔴 Register for IELTS NOW — target 7.0 minimum (priority #1)'}
• Identify 8-10 target scholarships → create tracking spreadsheet
• Contact 3 referees — give them your CV + achievement bullet points

**🗓️ MONTHS 3-4: Profile Building**
• {'Join research project — publications take 6+ months' if profile.get('research','none') in ['none','minimal'] else '✅ Continue research work'}
• Attend 2+ academic seminars/workshops and document attendance
• {'Identify leadership opportunities and start NOW' if profile.get('leadership','none') in ['none','minimal'] else '✅ Document leadership roles with impact metrics'}

**🗓️ MONTHS 5-6: Document Preparation**
• {'Take IELTS exam — aiming for 7.0+' if ielts<7.0 else '✅ IELTS score valid'}
• Write SOP first draft — get reviewed by professor and scholarship recipient
• Update CV with all new experiences and quantified achievements

**🗓️ MONTHS 7-8: Refinement**
• SOP version 3+ with program-specific details
• Collect official transcripts, attestation if needed
• Request formal reference letters with detailed brief for referees

**🗓️ MONTHS 9-10: Early Submissions**
• Submit: Stipendium Hungaricum (Jan 16), Erasmus Mundus (Jan-Feb)
• Submit: Swedish Institute (Feb 10), KGSP Korea (Feb 28)
• Submit: CSC China (Mar 15), Aga Khan (Mar 31), Australia Awards (Apr 30)

**🗓️ MONTHS 11-12: Major Submissions**
• Submit: Fulbright (Oct 15), Chevening (Oct 7), Rhodes (Oct 1)
• Submit: DAAD (Oct 15), Gates Cambridge (Dec 3), Commonwealth (Dec 17)
• Interview preparation — practice 20+ questions with recording

**🎯 Your Best Scholarship Bets:**
{'Fulbright + Chevening + DAAD + Commonwealth — all realistic targets' if cgpa>=3.5 and ielts>=6.5 else 'Start with CSC China + KGSP Korea + Stipendium Hungaricum — then target Fulbright after improvements'}"""
