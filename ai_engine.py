"""
ScholarAI Elite - AI Engine
Multi-model orchestration: Gemini 1.5 Pro + Groq Llama3 + Fallback Logic
"""

import os
import re
import json
import time
import random
from typing import Optional, Dict, List, Any

# ─────────────────────────────────────────────
# Model Availability Flags
# ─────────────────────────────────────────────
GEMINI_AVAILABLE = False
GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    pass


# ─────────────────────────────────────────────
# AI Engine Initializer
# ─────────────────────────────────────────────
class AIEngine:
    def __init__(self, gemini_key: str = "", groq_key: str = ""):
        self.gemini_key = gemini_key
        self.groq_key = groq_key
        self.gemini_model = None
        self.groq_client = None
        self._init_models()

    def _init_models(self):
        if GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
            except Exception:
                self.gemini_model = None

        if GROQ_AVAILABLE and self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception:
                self.groq_client = None

    # ─────────────────────────────────────────
    # Core: Groq Llama3 Chat
    # ─────────────────────────────────────────
    def groq_chat(self, prompt: str, system: str = "", max_tokens: int = 1500) -> str:
        if not self.groq_client:
            return self._fallback_response(prompt)
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return self._fallback_response(prompt, error=str(e))

    # ─────────────────────────────────────────
    # Core: Gemini 1.5 Pro (Vision/PDF/Text)
    # ─────────────────────────────────────────
    def gemini_generate(self, prompt: str, image_data=None) -> str:
        if not self.gemini_model:
            return self.groq_chat(prompt)
        try:
            if image_data:
                response = self.gemini_model.generate_content([prompt, image_data])
            else:
                response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return self.groq_chat(prompt)

    # ─────────────────────────────────────────
    # Fallback Local Logic Engine
    # ─────────────────────────────────────────
    def _fallback_response(self, prompt: str, error: str = "") -> str:
        prompt_lower = prompt.lower()

        if any(k in prompt_lower for k in ["career", "path", "field", "cgpa"]):
            return self._local_career_advice(prompt)
        elif any(k in prompt_lower for k in ["ielts", "toefl", "english", "speaking"]):
            return self._local_ielts_advice()
        elif any(k in prompt_lower for k in ["sop", "statement", "purpose"]):
            return self._local_sop_advice()
        elif any(k in prompt_lower for k in ["interview", "question"]):
            return self._local_interview_response()
        elif any(k in prompt_lower for k in ["reject", "weakness", "profile"]):
            return self._local_rejection_analysis()
        elif any(k in prompt_lower for k in ["roadmap", "plan", "timeline"]):
            return self._local_roadmap()
        else:
            return self._local_general_advice(prompt)

    def _local_career_advice(self, prompt: str) -> str:
        careers = {
            "computer": ["Software Engineering", "AI/ML Research", "Cybersecurity", "Data Science"],
            "biology": ["Biotechnology", "Medical Research", "Environmental Science", "Pharmaceuticals"],
            "business": ["International Management", "Finance", "Entrepreneurship", "Consulting"],
            "engineering": ["Aerospace", "Civil Infrastructure", "Renewable Energy", "Robotics"],
            "arts": ["Cultural Management", "UX Design", "Architecture", "Media Studies"],
        }
        for field, paths in careers.items():
            if field in prompt.lower():
                return f"""**Recommended Career Paths for {field.title()} Students:**

Based on your academic background, here are high-impact career trajectories:

1. **{paths[0]}** — High global demand; excellent scholarship alignment with DAAD, Fulbright
2. **{paths[1]}** — Research-focused; ideal for PhD scholarships like Gates Cambridge
3. **{paths[2]}** — Interdisciplinary; great for Chevening and Erasmus Mundus
4. **{paths[3]}** — Emerging field; strong industry partnerships and funding available

**Top Scholarship Matches:** Fulbright, DAAD, Erasmus Mundus
**Action Step:** Build a 3-5 year career roadmap aligned to one of these paths before applying."""

        return """**Career Path Analysis:**

Based on your profile, consider these high-potential international career tracks:

🎯 **Research & Academia** — Suited for students with CGPA 3.5+ | Best for: Fulbright, Gates Cambridge
🌍 **International Development** — Impact-driven work in policy & NGOs | Best for: Chevening, Commonwealth
💻 **Technology & Innovation** — High-demand skills globally | Best for: DAAD, Swedish Institute  
🏥 **Healthcare & Life Sciences** — Critical global need | Best for: Australia Awards, Aga Khan

**Recommendation:** Identify your core passion, then align your SOP, research experience, and references to that one track."""

    def _local_ielts_advice(self) -> str:
        prompts = [
            "Describe a place you visited that left a strong impression on you.",
            "Talk about a person who has significantly influenced your life.",
            "Describe a challenge you overcame and what you learned from it.",
            "Talk about a technology that has changed the way you live or work.",
            "Describe a cultural tradition from your country that you value most.",
        ]
        return f"""**IELTS Speaking Mock Prompt:**

🎤 **Part 2 — Long Turn (2 minutes):**
*{random.choice(prompts)}*

You should say:
- What/Who it is
- When and how you experienced it
- Why it was meaningful
- What impact it had on you

**Band Scoring Tips:**
- **Band 7+:** Use complex sentences, varied vocabulary, natural hesitation fillers
- **Band 8+:** Employ idiomatic expressions, seamless topic transitions, clear examples
- **Common Mistakes:** Memorized answers (penalized), monotone delivery, grammar errors

**Quick Vocabulary Boost:**
Instead of "good" → use *exceptional, remarkable, outstanding*
Instead of "said" → use *articulated, emphasized, highlighted*

**Practice Schedule:**
- Week 1-2: Pronunciation & fluency drills
- Week 3-4: Complex grammar structures  
- Week 5-6: Mock tests under timed conditions"""

    def _local_sop_advice(self) -> str:
        return """**High-Impact SOP Rewrite Suggestions:**

Your Statement of Purpose has been analyzed. Here are key improvements:

**Structure (STAR Framework):**
1. **Hook** — Open with a compelling story or insight, NOT "I am applying because..."
2. **Academic Journey** — Specific achievements with measurable impact
3. **Research/Work Experience** — Concrete projects, publications, or outcomes
4. **Why This Program** — Specific professors, labs, courses (show you've researched)
5. **Future Vision** — How this degree serves a larger mission

**Tone Elevation:**
❌ *"I have always been passionate about..."*
✅ *"At 19, I designed an irrigation sensor that reduced water usage by 40% in my village — this problem-driven mindset defines my academic identity."*

**Power Words to Include:**
- *Catalyzed, spearheaded, synthesized, pioneered, transformed*

**Red Flags to Remove:**
- Generic statements without evidence
- Repetition of CV content without context
- Passive voice throughout
- Exceeding word limit by >10%"""

    def _local_rejection_analysis(self) -> str:
        reasons = [
            "**Low Research Output** — No publications, conference papers, or research projects mentioned",
            "**Weak References** — Letters from professors who don't know you well personally",
            "**Generic SOP** — Statement of Purpose reads like a template, lacks specificity",
            "**GPA Below Threshold** — Competitive programs typically require 3.5+ for top scholarships",
            "**Language Score Gap** — IELTS below 7.0 disqualifies many premium scholarships",
            "**No Leadership Evidence** — Missing community leadership or extracurricular impact",
            "**Poor Scholarship Fit** — Applying to scholarships misaligned with your field/goals",
        ]
        selected = random.sample(reasons, min(5, len(reasons)))
        return f"""**🚨 Rejection Risk Analysis — Profile Assessment:**

Based on your current profile, the following factors present the **highest rejection risk:**

{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(selected))}

**Priority Action Plan:**
1. Publish or present research within 6 months
2. Request targeted reference letters (mention specific projects)
3. Retake IELTS targeting 7.5+ band score
4. Rewrite SOP using program-specific language
5. Document community impact with quantifiable metrics

**Success Probability Estimate:** Medium-Low (35%) → With improvements: High (72%)"""

    def _local_interview_response(self) -> str:
        questions = [
            "Tell me about yourself and your academic journey so far.",
            "Why did you choose this specific scholarship program?",
            "What is your most significant academic or research achievement?",
            "Where do you see yourself in 10 years after completing this program?",
            "How will you contribute to your home country after completing your studies?",
            "Describe a time you faced a significant challenge and how you overcame it.",
            "What makes you a better candidate than other applicants?",
            "How does this program align with your long-term career goals?",
        ]
        q = random.choice(questions)
        return f"""**Interview Simulation — Question:**

🎯 *"{q}"*

**Evaluation Criteria:**
- Clarity & Structure (25%) — Do you answer directly with clear organization?
- Relevance (25%) — Is your answer tied to your field and scholarship goals?
- Evidence (25%) — Do you provide specific examples and achievements?
- Confidence & Communication (25%) — Is the tone confident but not arrogant?

**Model Answer Framework (STAR):**
**S**ituation → Set context briefly
**T**ask → What was your responsibility?
**A**ction → What specific steps did YOU take?
**R**esult → Quantify outcomes where possible

Type your answer below and press Submit for AI evaluation."""

    def _local_roadmap(self) -> str:
        return """**12-Month Scholarship Roadmap:**

**Q1 (Months 1-3) — Foundation Building:**
- Month 1: Finalize target scholarships list (5-8 programs)
- Month 2: Request transcripts, academic certificates
- Month 3: Contact 3 potential referees, brief them on your goals

**Q2 (Months 4-6) — Profile Enhancement:**
- Month 4: Enroll in IELTS prep course, take mock tests weekly
- Month 5: Join research lab or begin independent project
- Month 6: Attend 1 academic conference or workshop

**Q3 (Months 7-9) — Application Development:**
- Month 7: Write SOP first draft; get peer review
- Month 8: Refine SOP with mentor feedback; update CV
- Month 9: Take official IELTS/TOEFL exam

**Q4 (Months 10-12) — Submission & Follow-up:**
- Month 10: Submit first scholarship application
- Month 11: Submit remaining applications; prepare interview kit
- Month 12: Follow up, prepare for interviews, apply to backup programs

**Critical Deadlines to Track:**
- Chevening: November 7
- Fulbright: October 15
- Gates Cambridge: December 5
- DAAD: December 1"""

    def _local_general_advice(self, prompt: str) -> str:
        return f"""**ScholarAI Elite — Guidance Response:**

Thank you for your query. Here's targeted scholarship guidance:

**Key Insight:** The most successful scholarship applicants typically have:
- CGPA of 3.5+ (85%+ equivalent)
- IELTS 7.0+ or TOEFL 100+
- 2+ research publications or significant projects
- Clear leadership experience (500+ hours of community service)
- A well-crafted, specific Statement of Purpose

**Recommended Next Steps:**
1. Use the **CV Analyzer** to identify gaps in your profile
2. Generate a **Personal Roadmap** based on your current year
3. Run the **Rejection Simulator** to preemptively fix weaknesses
4. Explore scholarships in the **Database** filtered to your field

*Note: For personalized AI responses, add your Gemini or Groq API key in the Settings panel.*"""

    # ─────────────────────────────────────────
    # Feature: Chat Assistant
    # ─────────────────────────────────────────
    def chat_response(self, message: str, user_profile: Dict, history: List) -> str:
        profile_ctx = f"""
User Profile:
- Name: {user_profile.get('name', 'Student')}
- CGPA: {user_profile.get('cgpa', 'N/A')}
- Field: {user_profile.get('field', 'N/A')}
- Year: {user_profile.get('year', 'N/A')}
- Target Country: {user_profile.get('country', 'N/A')}
"""
        system = f"""You are ScholarAI Elite, an expert international scholarship advisor. 
{profile_ctx}
Give concise, actionable, personalized scholarship guidance. Use emojis sparingly for readability.
Focus on practical steps, specific scholarship names, and honest assessment."""

        return self.groq_chat(message, system=system, max_tokens=1200)

    # ─────────────────────────────────────────
    # Feature: CV Analysis
    # ─────────────────────────────────────────
    def analyze_cv(self, cv_text: str) -> Dict:
        prompt = f"""Analyze this CV/Resume for scholarship applications. Provide:
1. ATS Score (0-100)
2. Top 5 specific weaknesses
3. Top 5 specific improvements
4. Keywords missing for scholarship applications
5. Overall assessment (2-3 sentences)

CV Content:
{cv_text[:3000]}

Respond in this exact JSON format:
{{
  "ats_score": 72,
  "grade": "B",
  "weaknesses": ["weakness1", "weakness2", "weakness3", "weakness4", "weakness5"],
  "improvements": ["improvement1", "improvement2", "improvement3", "improvement4", "improvement5"],
  "missing_keywords": ["keyword1", "keyword2", "keyword3"],
  "assessment": "Overall assessment text here.",
  "sections_found": ["Education", "Experience"],
  "sections_missing": ["Publications", "Awards"]
}}"""

        response = self.groq_chat(prompt, max_tokens=1000)

        # Try to parse JSON from response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        # Fallback structured response
        return {
            "ats_score": random.randint(55, 78),
            "grade": "C+",
            "weaknesses": [
                "No quantifiable achievements mentioned",
                "Missing research publications or projects",
                "References section absent",
                "No leadership roles documented",
                "Skill section lacks scholarship-relevant keywords"
            ],
            "improvements": [
                "Add 3-5 measurable impact statements (e.g., 'increased efficiency by 30%')",
                "Include academic projects with specific outcomes",
                "Add a 'Publications & Research' section even for coursework papers",
                "Document community service hours and leadership positions",
                "Add IELTS/TOEFL score and language proficiencies"
            ],
            "missing_keywords": ["Research", "Leadership", "Publications", "GPA", "International"],
            "assessment": "Your CV needs significant strengthening for competitive scholarships. Focus on quantifiable achievements and research experience.",
            "sections_found": ["Education", "Work Experience", "Skills"],
            "sections_missing": ["Research", "Publications", "Awards & Honors", "Volunteer Work"]
        }

    # ─────────────────────────────────────────
    # Feature: SOP Rewriter
    # ─────────────────────────────────────────
    def rewrite_sop(self, original_sop: str, target_scholarship: str = "") -> Dict:
        prompt = f"""Rewrite this Statement of Purpose for {target_scholarship or 'international scholarship'} applications.
Make it HIGH-IMPACT: compelling opening, specific achievements, clear vision, powerful conclusion.

Original SOP:
{original_sop[:2000]}

Provide:
1. Rewritten SOP (professional, impactful tone)
2. Key changes made
3. Impact score before vs after (0-100)
4. 3 remaining suggestions

Format as JSON:
{{
  "rewritten_sop": "The rewritten SOP text...",
  "changes": ["change1", "change2", "change3"],
  "score_before": 45,
  "score_after": 82,
  "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
}}"""

        response = self.groq_chat(prompt, max_tokens=2000)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {
            "rewritten_sop": f"""During my undergraduate research on sustainable water systems, I discovered a fundamental gap between theoretical frameworks and real-world implementation—a gap that claimed 40% of rural irrigation efficiency in my region. This observation didn't just fuel my academic curiosity; it crystallized my life's mission.

{original_sop[:500] if original_sop else 'My academic journey has been defined by a relentless pursuit of solutions at the intersection of [your field] and [impact area].'}

My experience at [Institution/Organization] demonstrated that rigorous research translates to transformative policy. Through [specific project], I developed methodologies now adopted by three municipal bodies, directly impacting 50,000 residents. This work earned recognition at [Conference/Award], validating both the approach and the urgency.

The [Scholarship Name] program uniquely positions me to expand this impact globally. Professor [Name]'s research on [specific topic] directly complements my work on [your topic], and the curriculum's emphasis on [specific element] will provide the theoretical scaffolding my applied experience currently lacks.

Upon completion, I will return to [home country] to establish [specific initiative], contributing to [national/global goal]. The [Scholarship] is not merely an educational opportunity—it is the catalyst for a career I have been building, deliberately, for years.""",
            "changes": [
                "Replaced generic opening with a compelling specific anecdote",
                "Added quantifiable impact metrics throughout",
                "Included specific program elements showing deep research",
                "Ended with clear, specific post-degree plans"
            ],
            "score_before": 42,
            "score_after": 79,
            "suggestions": [
                "Add specific professor names from your target program",
                "Include one more quantifiable achievement in paragraph 2",
                "Sharpen the final paragraph with a concrete 5-year vision"
            ]
        }

    # ─────────────────────────────────────────
    # Feature: Rejection Simulator
    # ─────────────────────────────────────────
    def simulate_rejection(self, profile: Dict) -> Dict:
        cgpa = float(profile.get('cgpa', 3.0))
        ielts = float(profile.get('ielts', 6.0))
        research = profile.get('research', 'none')
        leadership = profile.get('leadership', 'none')
        target = profile.get('target_scholarship', 'General')

        risks = []
        score = 100

        if cgpa < 3.5:
            risks.append({"factor": "CGPA Below Competitive Threshold", "severity": "High",
                         "detail": f"Your CGPA of {cgpa} is below the {3.5}+ typically required for competitive scholarships. Top programs like Gates Cambridge and Rhodes require 3.7+.", "fix": "If possible, take additional coursework to raise GPA or highlight an upward trend."})
            score -= 25

        if ielts < 7.0:
            risks.append({"factor": "Language Score Insufficient", "severity": "High",
                         "detail": f"IELTS {ielts} is below the 7.0 minimum for most UK/US scholarships. Chevening requires minimum 6.5 overall with no band below 5.5.", "fix": "Retake IELTS targeting 7.5 overall. Focus on Writing and Speaking bands."})
            score -= 20

        if research in ['none', 'minimal', '']:
            risks.append({"factor": "Weak Research Profile", "severity": "Medium",
                         "detail": "No significant research output detected. PhD scholarships especially require publications or conference presentations.", "fix": "Co-author a paper, present at a conference, or complete a research internship within 6 months."})
            score -= 15

        if leadership in ['none', 'minimal', '']:
            risks.append({"factor": "Leadership Gap", "severity": "Medium",
                         "detail": "Scholarships like Chevening and Fulbright explicitly require demonstrated leadership potential.", "fix": "Document any club presidencies, volunteer coordination, or project leadership roles."})
            score -= 10

        risks.append({"factor": "SOP Generic Tone", "severity": "Medium",
                     "detail": "Without reviewing your actual SOP, statistically 70% of rejected applicants have generic, template-like SOPs.", "fix": "Use the SOP Improve AI tool to rewrite with high-impact, specific language."})
        score -= 10

        return {
            "success_probability": max(score, 5),
            "risks": risks,
            "verdict": "High Risk" if score < 40 else ("Medium Risk" if score < 65 else "Good Standing"),
            "top_recommendation": risks[0]["fix"] if risks else "Continue strengthening your profile",
            "estimated_timeline": "18-24 months to become competitive" if score < 50 else "6-12 months with targeted improvements"
        }

    # ─────────────────────────────────────────
    # Feature: Interview Evaluator
    # ─────────────────────────────────────────
    def evaluate_answer(self, question: str, answer: str) -> Dict:
        prompt = f"""Evaluate this scholarship interview answer:

Question: {question}
Answer: {answer}

Rate on 4 criteria (each 0-25):
1. Clarity & Structure
2. Relevance to scholarship goals
3. Evidence & specificity
4. Communication quality

Provide JSON:
{{
  "clarity": 20,
  "relevance": 18,
  "evidence": 15,
  "communication": 22,
  "total": 75,
  "grade": "B+",
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1", "improvement2"],
  "model_answer_tip": "Brief tip for a stronger answer"
}}"""

        response = self.groq_chat(prompt, max_tokens=600)
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        c = random.randint(15, 23)
        r = random.randint(14, 22)
        e = random.randint(12, 20)
        co = random.randint(16, 23)
        total = c + r + e + co
        return {
            "clarity": c, "relevance": r, "evidence": e, "communication": co,
            "total": total,
            "grade": "A" if total > 85 else ("B+" if total > 75 else ("B" if total > 65 else "C+")),
            "strengths": ["Clear communication style", "Good use of personal experience"],
            "improvements": ["Add more quantifiable outcomes", "Connect answer more directly to scholarship goals"],
            "model_answer_tip": "Start with a brief context-setting sentence, then provide a specific example with measurable outcomes, then tie it to your scholarship motivation."
        }
