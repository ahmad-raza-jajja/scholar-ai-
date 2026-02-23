"""
ScholarAI Elite — RAG Engine
Retrieval-Augmented Generation for scholarship intelligence
Uses TF-IDF + cosine similarity (no external ML libraries needed on Streamlit Cloud)
"""

import re
import math
import json
from typing import List, Dict, Tuple, Optional
import pandas as pd


class RAGEngine:
    """
    Lightweight RAG engine using TF-IDF vectors.
    No external ML deps - works on Streamlit Cloud without extra packages.
    """

    def __init__(self):
        self.documents: List[str] = []
        self.metadata: List[Dict] = []
        self.tfidf_matrix: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self.is_built = False

    # ── Text Processing ──────────────────────────────────
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        # Remove very short tokens
        return [t for t in tokens if len(t) > 1]

    def _tf(self, tokens: List[str]) -> Dict[str, float]:
        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        total = len(tokens) if tokens else 1
        return {t: c / total for t, c in counts.items()}

    def _build_idf(self, all_token_sets: List[List[str]]) -> Dict[str, float]:
        N = len(all_token_sets)
        doc_freq: Dict[str, int] = {}
        for tokens in all_token_sets:
            for t in set(tokens):
                doc_freq[t] = doc_freq.get(t, 0) + 1
        idf = {}
        for t, df in doc_freq.items():
            idf[t] = math.log((N + 1) / (df + 1)) + 1
        return idf

    def _tfidf(self, tf: Dict[str, float]) -> Dict[str, float]:
        return {t: v * self.idf.get(t, 1.0) for t, v in tf.items()}

    def _cosine(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        common = set(a) & set(b)
        if not common:
            return 0.0
        dot = sum(a[k] * b[k] for k in common)
        norm_a = math.sqrt(sum(v**2 for v in a.values()))
        norm_b = math.sqrt(sum(v**2 for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    # ── Index Building ────────────────────────────────────
    def build_index(self, df: pd.DataFrame) -> None:
        """Build TF-IDF index from scholarship DataFrame"""
        self.documents = []
        self.metadata = []
        all_tokens = []

        for _, row in df.iterrows():
            # Combine all fields into searchable document
            doc = " ".join([
                str(row.get('name', '')),
                str(row.get('country', '')),
                str(row.get('field', '')),
                str(row.get('degree', '')),
                str(row.get('description', '')),
                str(row.get('amount', '')),
                str(row.get('language requirement', '')),
                str(row.get('notes 2026', '')),
            ])
            tokens = self._tokenize(doc)
            self.documents.append(doc)
            self.metadata.append(row.to_dict())
            all_tokens.append(tokens)

        self.idf = self._build_idf(all_tokens)
        self.tfidf_matrix = [self._tfidf(self._tf(tokens)) for tokens in all_tokens]
        self.is_built = True

    # ── Retrieval ─────────────────────────────────────────
    def retrieve(self, query: str, top_k: int = 4) -> List[Dict]:
        """Retrieve top-k most relevant scholarships for a query"""
        if not self.is_built:
            return []

        q_tokens = self._tokenize(query)
        q_tf = self._tf(q_tokens)
        q_tfidf = self._tfidf(q_tf)

        scores = []
        for i, doc_vec in enumerate(self.tfidf_matrix):
            score = self._cosine(q_tfidf, doc_vec)
            scores.append((score, i))

        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            if score > 0.01:  # Relevance threshold
                item = self.metadata[idx].copy()
                item['_rag_score'] = round(score, 4)
                results.append(item)

        return results

    def format_context(self, results: List[Dict]) -> str:
        """Format retrieved results as context for AI prompt"""
        if not results:
            return ""

        parts = ["=== RELEVANT SCHOLARSHIPS FROM DATABASE ===\n"]
        for i, r in enumerate(results, 1):
            name = r.get('name', 'Unknown')
            country = r.get('country', 'N/A')
            amount = r.get('amount', 'N/A')
            deadline = r.get('deadline', 'N/A')
            gpa = r.get('gpa required', 'N/A')
            lang = r.get('language requirement', 'N/A')
            desc = r.get('description', 'N/A')
            success = r.get('success rate', 'N/A')
            url = r.get('url', '#')
            notes = r.get('notes 2026', '')
            field = r.get('field', 'N/A')
            degree = r.get('degree', 'N/A')

            parts.append(f"""
[{i}] {name}
  Country: {country} | Field: {field} | Degree: {degree}
  Amount: {amount}
  Deadline: {deadline}
  GPA Required: {gpa}+
  Language: {lang}
  Success Rate: {success}
  Description: {desc}
  {f'2026 Notes: {notes}' if notes and str(notes) != 'nan' else ''}
  URL: {url}
""")
        parts.append("=== END DATABASE CONTEXT ===\n")
        return "\n".join(parts)
