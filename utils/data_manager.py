"""
ScholarAI Elite v4 — Data Manager
CSV loading, filtering, comparison, PDF export, RAG index builder
"""

import os
import io
import json
import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd


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
            df.columns = [col.strip().lower() for col in df.columns]
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    df[col] = "N/A"
            if 'deadline' in df.columns:
                df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
            return df
        except FileNotFoundError:
            return self._get_fallback_data()
        except Exception:
            return self._get_fallback_data()

    def _get_fallback_data(self) -> pd.DataFrame:
        data = {
            'name': ['Fulbright Scholarship', 'Chevening Scholarship', 'DAAD Scholarship', 'CSC China Scholarship', 'KGSP Korea'],
            'country': ['USA', 'UK', 'Germany', 'China', 'South Korea'],
            'field': ['All Fields', 'All Fields', 'STEM', 'All Fields', 'All Fields'],
            'degree': ['Masters/PhD', 'Masters', 'Masters/PhD', 'Masters/PhD', 'Masters/PhD'],
            'amount': ['$45000', '£18000', '€1200/month', 'Full + 3000CNY/month', 'Full + 900k KRW/month'],
            'deadline': [pd.Timestamp('2026-10-15'), pd.Timestamp('2026-10-07'), pd.Timestamp('2026-10-15'), pd.Timestamp('2026-03-15'), pd.Timestamp('2026-02-28')],
            'gpa required': ['3.5', '3.0', '3.2', '3.0', '3.0'],
            'language requirement': ['IELTS 6.5', 'IELTS 6.5', 'IELTS 6.0', 'IELTS 6.0', 'IELTS 5.5'],
            'description': ['US government prestigious scholarship', 'UK government global scholarship', 'German Academic Exchange scholarship', 'China government large scholarship', 'Korean government full scholarship'],
            'url': ['https://foreign.fulbrightonline.org', 'https://chevening.org', 'https://daad.de', 'https://csc.edu.cn', 'https://niied.go.kr'],
            'success rate': ['15%', '8%', '30%', '40%', '30%'],
            'duration': ['1-2 years', '1 year', '2 years', '2-4 years', '2-3 years']
        }
        return pd.DataFrame(data)

    def filter_scholarships(self, country="All", field="All", degree="All", min_gpa=0.0, search_query="") -> pd.DataFrame:
        df = self.df.copy()
        if country and country != "All":
            df = df[df['country'].str.contains(country, case=False, na=False)]
        if field and field != "All":
            mask = (df['field'].str.contains(field, case=False, na=False) | df['field'].str.contains('All Fields', case=False, na=False))
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

    def get_deadline_status(self, deadline) -> Tuple[str, str, int]:
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

    def compare_scholarships(self, name1: str, name2: str) -> Dict:
        df = self.df
        rows1 = df[df['name'].str.lower() == name1.lower()]
        rows2 = df[df['name'].str.lower() == name2.lower()]
        if rows1.empty or rows2.empty:
            return {}
        s1, s2 = rows1.iloc[0], rows2.iloc[0]
        criteria = ['country', 'field', 'degree', 'amount', 'gpa required', 'language requirement', 'success rate', 'duration']
        comparison = {}
        for c in criteria:
            comparison[c] = {'label': c.replace('_', ' ').title(), name1: s1.get(c, 'N/A'), name2: s2.get(c, 'N/A')}
        return comparison

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

    def calculate_profile_strength(self, profile: Dict) -> Dict:
        fields = {
            'name': ('Basic Info', 5), 'cgpa': ('Academic', 20), 'field': ('Field', 10),
            'year': ('Current Year', 5), 'country': ('Target Country', 10),
            'ielts': ('Language', 20), 'research': ('Research', 15), 'leadership': ('Leadership', 10),
        }
        score = 0
        completed, missing = [], []
        for key, (label, weight) in fields.items():
            val = profile.get(key, '')
            if val and str(val) not in ['', 'None', '0', 'none', 'N/A']:
                score += weight; completed.append(label)
            else:
                missing.append(label)
        strength = "🔴 Weak" if score < 40 else "🟡 Building" if score < 65 else "🟢 Strong" if score < 85 else "⭐ Elite"
        return {'score': score, 'strength': strength, 'completed': completed, 'missing': missing}

    def export_to_pdf(self, title: str, content_sections: List[Dict]) -> bytes:
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 20)
            pdf.set_text_color(0, 200, 255)
            pdf.cell(0, 15, "ScholarAI Elite", ln=True, align='C')
            pdf.set_font("Arial", "B", 14)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 8, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}", ln=True, align='C')
            pdf.ln(5)
            pdf.set_draw_color(0, 200, 255)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)
            for section in content_sections:
                heading = section.get('heading', '')
                body = section.get('body', '')
                if heading:
                    pdf.set_font("Arial", "B", 12)
                    pdf.set_text_color(0, 150, 200)
                    pdf.cell(0, 8, heading, ln=True)
                    pdf.set_draw_color(200, 200, 200)
                    pdf.set_line_width(0.2)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(3)
                if body:
                    pdf.set_font("Arial", "", 10)
                    pdf.set_text_color(60, 60, 60)
                    for line in body.split('\n'):
                        clean_line = line.strip().replace('**', '').replace('*', '').replace('##', '').replace('#', '')
                        if clean_line:
                            if clean_line.startswith('- ') or clean_line.startswith('• '):
                                pdf.cell(5)
                                clean_line = '• ' + clean_line[2:]
                            try:
                                pdf.multi_cell(0, 6, clean_line.encode('latin-1', 'replace').decode('latin-1'))
                            except Exception:
                                pdf.multi_cell(0, 6, clean_line[:100])
                    pdf.ln(4)
            pdf.set_font("Arial", "I", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, "ScholarAI Elite v4 | AI-Powered Scholarship Intelligence with RAG", ln=True, align='C')
            return pdf.output(dest='S').encode('latin-1')
        except ImportError:
            content = f"ScholarAI Elite — {title}\n{'='*50}\n\n"
            for section in content_sections:
                content += f"\n{section.get('heading','')}\n{'-'*30}\n{section.get('body','')}\n"
            return content.encode('utf-8')
        except Exception as e:
            return f"Export error: {str(e)}".encode('utf-8')


def extract_text_from_pdf(uploaded_file) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            text = "".join(page.extract_text() + "\n" for page in pdf.pages if page.extract_text())
        return text if text.strip() else ""
    except Exception:
        pass
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "".join(page.extract_text() + "\n" for page in reader.pages)
        return text if text.strip() else ""
    except Exception:
        pass
    return "PDF extraction requires: pip install pdfplumber\n\nPlease paste your CV text manually."
