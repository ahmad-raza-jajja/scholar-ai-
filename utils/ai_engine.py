"""
ScholarAI Elite v4 — AI Engine FIXED
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


def get_groq_key() -> str:
    """Get Groq API key — tries every possible method"""
    # Method 1: Environment variable
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    # Method 2: Streamlit secrets .get()
    try:
        import streamlit as st
        key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        if key and key != "None":
            return key
    except Exception:
        pass
    # Method 3: Streamlit secrets direct
    try:
        import streamlit as st
        key = str(st.secrets["GROQ_API_KEY"]).strip()
        if key and key != "None":
            return key
    except Exception:
        pass
    return ""


class AIEngine:
    def __init__(self, groq_key: str = "", gemini_key: str = ""):
        secret_key = get_groq_key()
        self.groq_key = secret_key or groq_key.strip()
        self.gemini_key = gemini_key
        self.groq_client = None
        self.rag = None
        self._init_models()

    def _init_models(self):
        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception:
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
                return "⚠️ Rate limit. Wait 30 seconds and try again."
            if "auth" in err or "invalid" in err or "key" in err:
                return "⚠️ Groq API key invalid. Check ⚙️ Settings."
            return None

    # ── CHAT WITH RAG ────────────────────────────────────
    def chat_response(self, message: str, profile: Dict, history: List) -> str:
        cgpa = profile.get("cgpa", 3.0)
        field = profile.get("field", "General")
        ielts = profile.get("ielts", 6.5)
        country = profile.get("country", "Any")
        name = profile.get("name", "Student")

        rag_context = ""
        if self.rag and self.rag.is_built:
            results = self.rag.retrieve(message, top_k=4)
            if results:
                rag_context = self.rag.format_context(results)

        system = f"""You are ScholarAI Elite — world-class AI scholarship advisor with RAG database.

Student: {name} | CGPA: {cgpa}/4.0 | Field: {field} | IELTS: {ielts} | Target: {country}

{rag_context}

RULES:
1. Use scholarship database above — cite real names, deadlines, amounts
2. Be SPECIFIC to CGPA {cgpa} and IELTS {ielts}
3. Never generic advice — always personalized
4. Use emojis and bullet points
5. Honest about weaknesses, give specific fixes"""

        messages = [{"role": "system", "content": system}]
        for h in history[-6:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        result = self._groq(messages, 1400)
        if result:
            return result
        return self._local_chat(message, profile)

    def _local_chat(self, msg: str, profile: Dict) -> str:
        cgpa = float(profile.get("cgpa", 3.0))
        field = str(profile.get("field", "")).lower()
        ielts = float(profile.get("ielts", 6.5))
        m = msg.lower()

        if any(k in m for k in ["scholarship", "which", "apply", "qualify", "option"]):
            return self._scholarship_match(cgpa, ielts, field)
        elif any(k in m for k in ["career", "job", "future", "path"]):
            return self._career_advice(field, cgpa)
        elif any(k in m for k in ["ielts", "toefl", "band", "english"]):
            return f"""**IELTS Guide (Your score: {ielts})**

🎯 Requirements:
- CSC China: 6.0 ({'✅' if ielts>=6.0 else '❌'})
- DAAD Germany: 6.0 ({'✅' if ielts>=6.0 else '❌'})
- Fulbright/Chevening: 6.5 ({'✅' if ielts>=6.5 else '❌'})
- Gates Cambridge: 7.5 ({'✅' if ielts>=7.5 else '❌'})

📚 Fastest improvement:
• 1 full practice test daily
• Writing Task 2: 3 essay structures
• Speaking: Record yourself daily"""
        elif any(k in m for k in ["sop", "statement", "essay"]):
            return """**SOP Writing Tips:**
❌ Never: "I have always been passionate about..."
✅ Start: A specific moment or achievement

Structure:
1. Hook — specific story
2. Academic achievements with numbers
3. Research — what you DID and RESULTED
4. Why this program — name professors/labs
5. Future plan — concrete role in Pakistan"""
        else:
            return self._scholarship_match(cgpa, ielts, field)

    def _scholarship_match(self, cgpa: float, ielts: float, field: str) -> str:
        options = []
        if cgpa >= 3.7 and ielts >= 7.5:
            options += ["⭐ Gates Cambridge — Full funding — Dec 3, 2026", "⭐ Rhodes Scholarship — £21k/year — Oct 1, 2026"]
        if cgpa >= 3.5 and ielts >= 6.5:
            options += ["✅ Fulbright USA — Full funding — Oct 15, 2026", "✅ Chevening UK — Full funding — Oct 7, 2026"]
        if cgpa >= 3.2 and ielts >= 6.0:
            options += ["✅ DAAD Germany — €934-1200/month — Oct 15, 2026", "✅ Commonwealth UK — Full funding — Dec 17, 2026"]
        if cgpa >= 3.0 and ielts >= 6.5:
            options += ["✅ Australia Awards — Full funding — Apr 30, 2026", "✅ Swedish Institute — 13k SEK/month — Feb 10, 2026"]
        if cgpa >= 3.0:
            options += ["📌 CSC China — Full funding — Mar 15, 2026", "📌 KGSP Korea — Feb 28, 2026", "📌 Stipendium Hungaricum — Jan 16, 2026"]
        if not options:
            options = ["📌 HEC Pakistan — Jun 30, 2026", "📌 CSC China — Mar 15, 2026"]

        return f"""**Your Scholarships (CGPA: {cgpa} | IELTS: {ielts}):**

{chr(10).join(f'  {o}' for o in options)}

💡 Strategy:
• Apply to 6-8 simultaneously
• {'🔴 Improve IELTS to 7.0 first' if ielts < 7.0 else '✅ IELTS sufficient'}
• Start SOP now — takes 2-3 months"""

    def _career_advice(self, field: str, cgpa: float) -> str:
        career_map = {
            "computer": ["🤖 AI/ML → DAAD/Fulbright", "🔒 Cybersecurity → UK/USA", "📊 Data Science → Australia"],
            "engineering": ["⚡ Renewable Energy → DAAD", "🏗️ Infrastructure → Australia Awards", "🤖 Robotics → MEXT Japan"],
            "business": ["📈 Investment Banking → Chevening", "🌍 Development Economics → World Bank", "📊 Management Consulting → MBA"],
            "biology": ["🧬 Biomedical Research → USA/UK PhD", "💊 Pharma R&D → DAAD"],
            "medicine": ["🏥 Clinical Research → Commonwealth", "🌍 Global Health → Chevening"],
        }
        matched = []
        for key, opts in career_map.items():
            if key in field:
                matched = opts
                break
        if not matched:
            matched = ["🎓 Academic Research → PhD", "🌍 International Development → UN/World Bank", "💼 Public Policy → Government"]

        note = ("⭐ CGPA qualifies for Gates Cambridge" if cgpa >= 3.7 else
                "✅ Competitive for Fulbright, Chevening" if cgpa >= 3.5 else
                "⚠️ Compensate with strong research + SOP" if cgpa >= 3.0 else
                "🔴 Target CSC China, KGSP Korea first")

        return f"""**Career Paths for {field.title() or 'Your Field'}:**
{chr(10).join(f'• {p}' for p in matched)}

**CGPA {cgpa}:** {note}"""

    # ── CV ANALYZER ──────────────────────────────────────
    def analyze_cv(self, cv_text: str) -> Dict:
        system = "You are an expert CV analyst for scholarships. Respond in valid JSON only — no markdown, no extra text."
        prompt = f"""Analyze this CV. Return ONLY valid JSON:
{{
  "ats_score": <0-100>,
  "grade": "<A/B/C/D>",
  "assessment": "<2-3 sentences>",
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

        tl = cv_text.lower()
        score = 40
        found, missing = [], []
        checks = {"Education": ["education","university","degree"], "Experience": ["experience","internship","work"], "Skills": ["skills","technical","programming"], "Research": ["research","publication","paper"], "Awards": ["award","scholarship","honor"], "Volunteer": ["volunteer","community","service"]}
        for sec, kws in checks.items():
            if any(k in tl for k in kws):
                found.append(sec); score += 7
            else:
                missing.append(sec)
        score = min(score, 80)
        return {
            "ats_score": score, "grade": "A" if score>=80 else "B" if score>=65 else "C" if score>=50 else "D",
            "assessment": f"CV has {len(found)} of {len(checks)} sections. Add research and quantified achievements.",
            "weaknesses": ["Achievements not quantified","Research missing","Leadership not documented","No publications","Keywords insufficient"],
            "improvements": ["Add metrics: 'improved by 35%'","Add Research section","Document leadership","Add conference/paper","Add IELTS score"],
            "missing_keywords": ["Research","Leadership","Impact","Publication","International"],
            "sections_found": found or ["Education"],
            "sections_missing": missing
        }

    # ── SOP REWRITER ─────────────────────────────────────
    def rewrite_sop(self, original: str, target: str = "") -> Dict:
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

        return {
            "rewritten_sop": f"[Add Groq API key for full rewrite]\n\nOriginal:\n{original[:400]}",
            "score_before": 35, "score_after": 72,
            "changes": ["Specific opening hook needed", "Quantify achievements", "Name specific professors", "Concrete Pakistan plan"],
            "suggestions": ["Add professor name", "Add quantifiable achievement", "Make future plan specific"]
        }

    # ── REJECTION SIMULATOR ───────────────────────────────
    def simulate_rejection(self, profile: Dict) -> Dict:
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

        cgpa = float(profile.get('cgpa', 3.0))
        ielts = float(profile.get('ielts', 6.5))
        score = 50
        risks = []
        if cgpa < 3.5:
            score -= 15; risks.append({"factor":"CGPA","severity":"High" if cgpa<3.0 else "Medium","detail":f"CGPA {cgpa} limits options.","fix":"Compensate with research + exceptional SOP."})
        else:
            score += 15
        if ielts < 7.0:
            score -= 15; risks.append({"factor":"IELTS","severity":"High" if ielts<6.5 else "Medium","detail":f"IELTS {ielts} — need 7.0+ for top scholarships.","fix":"Register for IELTS retake."})
        else:
            score += 10
        if profile.get('research','none') in ['none','minimal']:
            score -= 10; risks.append({"factor":"No Research","severity":"Medium","detail":"No publications hurts applications.","fix":"Co-author with professor."})
        risks.append({"factor":"SOP Quality","severity":"Medium","detail":"70% rejections are SOP-related.","fix":"Use SOP Improve tool, 3 rounds feedback."})
        score = max(10, min(88, score))
        verdict = "High Risk" if score<40 else "Medium Risk" if score<60 else "Good Standing" if score<78 else "Strong Candidate"
        return {"success_probability":score,"verdict":verdict,"estimated_timeline":"12-18 months" if score<50 else "Ready now","risks":risks,"top_recommendation":risks[0]["fix"] if risks else "Polish SOP"}

    # ── EVALUATE ANSWER ───────────────────────────────────
    def evaluate_answer(self, question: str, answer: str) -> Dict:
        system = "You are a scholarship interview panelist. Respond in valid JSON only."
        prompt = f"""Evaluate:
Q: {question}
A: {answer}

Return ONLY valid JSON:
{{
  "clarity": <0-25>, "relevance": <0-25>, "evidence": <0-25>, "communication": <0-25>,
  "total": <sum>, "grade": "<A+/A/B+/B/C+/C>",
  "strengths": ["s1","s2"], "improvements": ["i1","i2"],
  "model_answer_tip": "<tip>"
}}"""

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
        has_ex = any(k in answer.lower() for k in ["when","example","result","achieved"])
        has_num = any(c.isdigit() for c in answer)
        cl = min(22, 12+(words//15)); rel = 18 if len(answer)>100 else 12
        ev = 20 if (has_ex and has_num) else 14 if has_ex else 9; com = 18 if words>80 else 12
        total = cl+rel+ev+com
        return {"clarity":cl,"relevance":rel,"evidence":ev,"communication":com,"total":total,
                "grade":"A" if total>85 else "B+" if total>75 else "B" if total>65 else "C+",
                "strengths":["Good length" if words>80 else "Concise","Specific example" if has_ex else "Direct"],
                "improvements":["Add numbers" if not has_num else "Good metrics ✅","Use STAR format"],
                "model_answer_tip":"30s context + 60s specific example with result + 30s connect to goal."}

    # ── IELTS PROMPT ──────────────────────────────────────
    def generate_ielts_prompt(self, part: str, topic: str) -> str:
        system = "You are an expert IELTS examiner."
        prompt = f"Generate IELTS Speaking {part} for topic: {topic}. Include prompt card, timing, Band 7+ vocabulary, mistakes, model opening."
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        result = self._groq(messages, 700)
        if result:
            return result

        prompts_map = {"Education": "Describe a teacher who influenced you.", "Technology": "Talk about a technology that changed your life.", "Random": "Describe a challenge you overcame."}
        q = prompts_map.get(topic, prompts_map["Random"])
        return f"""**IELTS Speaking {part} — {topic}**
📋 *"{q}"*
• What/who + when • Why significant • How it impacted you
⏱️ 1 min prep → 2 min speaking
🎯 Band 7+: remarkable, profound, consequently, furthermore
✅ Opening: "This profoundly shaped my perspective because..."
❌ Avoid: memorized answers, generic examples"""

    # ── ROADMAP ───────────────────────────────────────────
    def generate_roadmap(self, current_year: str, field: str, target_degree: str, target_year: str, profile: Dict) -> str:
        system = "You are a scholarship strategy expert."
        prompt = f"""Month-by-month roadmap:
Year: {current_year}, Field: {field}, Target: {target_degree} in {target_year}
CGPA: {profile.get('cgpa',3.0)}, IELTS: {profile.get('ielts',6.5)}
Research: {profile.get('research','none')}, Leadership: {profile.get('leadership','none')}
Be specific with real deadlines."""

        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        result = self._groq(messages, 1800)
        if result:
            return result

        cgpa = float(profile.get("cgpa", 3.0))
        ielts = float(profile.get("ielts", 6.5))
        return f"""**Personalized Roadmap** | CGPA: {cgpa} | IELTS: {ielts} | {field}

**MONTHS 1-2:** {'✅ CGPA OK' if cgpa>=3.5 else '🔴 Need strong research'} | {'✅ IELTS OK' if ielts>=6.5 else '🔴 Register IELTS NOW'}
**MONTHS 3-5:** {'Join research project' if profile.get('research','none') in ['none','minimal'] else '✅ Continue research'} | Document everything
**MONTHS 6-8:** SOP 3 drafts → CV update → Reference letters
**MONTHS 9-12:** Jan: Stipendium/Erasmus | Feb: Swedish/KGSP | Mar: CSC | Oct: Fulbright/Chevening | Dec: Gates Cambridge

**Best bets:** {'Fulbright + Chevening + DAAD' if cgpa>=3.5 and ielts>=6.5 else 'CSC China + KGSP Korea + Stipendium Hungaricum'}"""
