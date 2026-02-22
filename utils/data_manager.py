"""
ScholarAI Elite - Data Manager
Handles CSV loading, filtering, comparison, and PDF export
"""

import os
import io
import csv
import json
import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd


# ─────────────────────────────────────────────
# Scholarship Data Manager
# ─────────────────────────────────────────────
class DataManager:
    REQUIRED_COLUMNS = [
        'name', 'country', 'field', 'degree', 'amount',
        'deadline', 'gpa required', 'language requirement',
        'description', 'url', 'success rate', 'duration'
    ]

    def __init__(self, csv_path: str = "data/scholarships.csv"):
        self.csv_path = csv_path
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.csv_path)
            # Normalize column names: strip spaces, lowercase
            df.columns = [col.strip().lower() for col in df.columns]

            # Ensure all required columns exist (add empty if missing)
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = "N/A"

            # Parse deadlines safely
            if 'deadline' in df.columns:
                df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')

            return df
        except FileNotFoundError:
            return self._get_fallback_data()
        except Exception as e:
            return self._get_fallback_data()

    def _get_fallback_data(self) -> pd.DataFrame:
        data = {
            'name': ['Fulbright Scholarship', 'Chevening Scholarship', 'DAAD Scholarship'],
            'country': ['USA', 'UK', 'Germany'],
            'field': ['All Fields', 'All Fields', 'STEM'],
            'degree': ['Masters/PhD', 'Masters', 'Masters/PhD'],
            'amount': ['$45000', '£18000', '€1200/month'],
            'deadline': [pd.Timestamp('2024-10-15'), pd.Timestamp('2024-11-07'), pd.Timestamp('2024-12-01')],
            'gpa required': ['3.5', '3.0', '3.2'],
            'language requirement': ['IELTS 7.0', 'IELTS 6.5', 'IELTS 6.0'],
            'description': [
                'US government scholarship for international students',
                'UK government global scholarship for future leaders',
                'German Academic Exchange Service scholarship'
            ],
            'url': ['https://fulbrightscholarships.org', 'https://chevening.org', 'https://daad.de'],
            'success rate': ['45%', '20%', '35%'],
            'duration': ['1-2 years', '1 year', '2 years']
        }
        return pd.DataFrame(data)

    # ─────────────────────────────────────────
    # Filtering
    # ─────────────────────────────────────────
    def filter_scholarships(
        self,
        country: str = "All",
        field: str = "All",
        degree: str = "All",
        min_gpa: float = 0.0,
        search_query: str = ""
    ) -> pd.DataFrame:
        df = self.df.copy()

        if country and country != "All":
            df = df[df['country'].str.contains(country, case=False, na=False)]

        if field and field != "All":
            mask = (df['field'].str.contains(field, case=False, na=False) |
                   df['field'].str.contains('All Fields', case=False, na=False))
            df = df[mask]

        if degree and degree != "All":
            df = df[df['degree'].str.contains(degree, case=False, na=False)]

        if min_gpa > 0:
            def check_gpa(val):
                try:
                    return float(str(val).split()[0]) <= min_gpa + 0.5
                except Exception:
                    return True
            df = df[df['gpa required'].apply(check_gpa)]

        if search_query:
            mask = (
                df['name'].str.contains(search_query, case=False, na=False) |
                df['description'].str.contains(search_query, case=False, na=False) |
                df['country'].str.contains(search_query, case=False, na=False)
            )
            df = df[mask]

        return df.reset_index(drop=True)

    # ─────────────────────────────────────────
    # Deadline Analysis
    # ─────────────────────────────────────────
    def get_deadline_status(self, deadline) -> Tuple[str, str, int]:
        """Returns (badge_text, color, days_remaining)"""
        try:
            if pd.isna(deadline):
                return "No Deadline", "gray", 999

            now = pd.Timestamp.now()
            delta = deadline - now
            days = delta.days

            if days < 0:
                return "Closed", "gray", days
            elif days <= 30:
                return f"⚠️ {days}d left", "red", days
            elif days <= 60:
                return f"🟡 {days}d left", "orange", days
            else:
                return f"✅ {days}d left", "green", days
        except Exception:
            return "Check Website", "blue", 999

    # ─────────────────────────────────────────
    # Scholarship Comparison
    # ─────────────────────────────────────────
    def compare_scholarships(self, name1: str, name2: str) -> Dict:
        df = self.df
        s1 = df[df['name'].str.lower() == name1.lower()].iloc[0] if len(df[df['name'].str.lower() == name1.lower()]) > 0 else None
        s2 = df[df['name'].str.lower() == name2.lower()].iloc[0] if len(df[df['name'].str.lower() == name2.lower()]) > 0 else None

        if s1 is None or s2 is None:
            return {}

        criteria = ['country', 'field', 'degree', 'amount', 'gpa required',
                   'language requirement', 'success rate', 'duration']

        comparison = {}
        for c in criteria:
            comparison[c] = {
                'label': c.replace('_', ' ').title(),
                name1: s1.get(c, 'N/A'),
                name2: s2.get(c, 'N/A')
            }
        return comparison

    # ─────────────────────────────────────────
    # Unique Filter Values
    # ─────────────────────────────────────────
    def get_countries(self) -> List[str]:
        return ["All"] + sorted(self.df['country'].dropna().unique().tolist())

    def get_fields(self) -> List[str]:
        raw = self.df['field'].dropna().unique().tolist()
        fields = set()
        for f in raw:
            for part in f.split('/'):
                fields.add(part.strip())
        return ["All"] + sorted(fields)

    def get_degrees(self) -> List[str]:
        return ["All", "Masters", "PhD", "Undergraduate", "Postdoctoral"]

    def get_all_names(self) -> List[str]:
        return self.df['name'].dropna().tolist()

    # ─────────────────────────────────────────
    # Profile Completion Score
    # ─────────────────────────────────────────
    def calculate_profile_strength(self, profile: Dict) -> Dict:
        fields = {
            'name': ('Basic Info', 5),
            'cgpa': ('Academic Performance', 20),
            'field': ('Field of Study', 10),
            'year': ('Current Year', 5),
            'country': ('Target Country', 10),
            'ielts': ('Language Score', 20),
            'research': ('Research Experience', 15),
            'leadership': ('Leadership', 10),
            'sop_ready': ('SOP Ready', 5),
        }

        score = 0
        completed = []
        missing = []

        for key, (label, weight) in fields.items():
            val = profile.get(key, '')
            if val and str(val) not in ['', 'None', '0', 'none', 'N/A']:
                score += weight
                completed.append(label)
            else:
                missing.append(label)

        strength = "🔴 Weak" if score < 40 else ("🟡 Building" if score < 65 else ("🟢 Strong" if score < 85 else "⭐ Elite"))
        return {
            'score': score,
            'strength': strength,
            'completed': completed,
            'missing': missing
        }

    # ─────────────────────────────────────────
    # PDF Export
    # ─────────────────────────────────────────
    def export_to_pdf(self, title: str, content_sections: List[Dict]) -> bytes:
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_font("Arial", "B", 20)
            pdf.set_text_color(30, 100, 200)
            pdf.cell(0, 15, "ScholarAI Elite", ln=True, align='C')

            pdf.set_font("Arial", "B", 14)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 10, title, ln=True, align='C')

            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 8, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}", ln=True, align='C')
            pdf.ln(5)

            # Divider
            pdf.set_draw_color(30, 100, 200)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)

            # Content sections
            for section in content_sections:
                heading = section.get('heading', '')
                body = section.get('body', '')

                if heading:
                    pdf.set_font("Arial", "B", 12)
                    pdf.set_text_color(30, 100, 200)
                    pdf.cell(0, 8, heading, ln=True)
                    pdf.set_draw_color(200, 200, 200)
                    pdf.set_line_width(0.2)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(3)

                if body:
                    pdf.set_font("Arial", "", 10)
                    pdf.set_text_color(60, 60, 60)
                    # Handle long text
                    for line in body.split('\n'):
                        clean_line = line.strip()
                        if clean_line:
                            # Remove markdown symbols
                            clean_line = clean_line.replace('**', '').replace('*', '').replace('##', '').replace('#', '')
                            if clean_line.startswith('- ') or clean_line.startswith('• '):
                                pdf.cell(5)
                                clean_line = '• ' + clean_line[2:]
                            try:
                                pdf.multi_cell(0, 6, clean_line.encode('latin-1', 'replace').decode('latin-1'))
                            except Exception:
                                pdf.multi_cell(0, 6, clean_line[:100])
                    pdf.ln(4)

            # Footer
            pdf.set_font("Arial", "I", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "ScholarAI Elite | AI-Powered Scholarship Intelligence Platform", ln=True, align='C')

            return pdf.output(dest='S').encode('latin-1')

        except ImportError:
            # Fallback: plain text as bytes
            content = f"ScholarAI Elite — {title}\n{'='*50}\n\n"
            for section in content_sections:
                content += f"\n{section.get('heading', '')}\n{'-'*30}\n{section.get('body', '')}\n"
            return content.encode('utf-8')
        except Exception as e:
            return f"Export error: {str(e)}".encode('utf-8')


# ─────────────────────────────────────────────
# CV Text Extractor
# ─────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        import pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text if text.strip() else "Could not extract text from PDF."
    except ImportError:
        pass

    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text if text.strip() else "Could not extract text from PDF."
    except ImportError:
        pass

    try:
        import fitz  # PyMuPDF
        data = uploaded_file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text if text.strip() else "Could not extract text from PDF."
    except Exception:
        pass

    return "PDF extraction requires: pip install pdfplumber PyPDF2 pymupdf\n\nPlease paste your CV text manually in the text area below."


# ─────────────────────────────────────────────
# Lottie Animation Loader
# ─────────────────────────────────────────────
def load_lottie_url(url: str) -> Optional[dict]:
    try:
        import requests
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def load_lottie_file(filepath: str) -> Optional[dict]:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return None
