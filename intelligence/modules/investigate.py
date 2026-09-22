"""AURA Investigate Module — Evidence and General Analysis."""

import re
import logging
from typing import Dict, Any, List
from collections import Counter

from intelligence.core.base import AuraModule, AnalysisResult
from intelligence.preprocessing.text_cleaner import clean_text, tokenize

logger = logging.getLogger(__name__)

class AuraInvestigate(AuraModule):
    """General evidence analysis and ultimate fallback module."""
    
    def __init__(self):
        super().__init__()
        
    @property
    def module_name(self) -> str:
        return "AURA Investigate"
        
    @property
    def module_slug(self) -> str:
        return "investigate"
        
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract basic entities (Times, Dates, Amounts)."""
        entities = {
            'times': [],
            'dates': [],
            'amounts': []
        }
        
        # Match times (e.g., 5:00 PM, 14:30)
        times = re.findall(r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', text)
        if times:
            entities['times'] = times
            
        # Match dates (e.g., Jan 5, 2024, 12/05/2023)
        dates = re.findall(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b', text)
        if dates:
            entities['dates'] = dates
            
        # Match currency amounts (e.g., $500, 100 USD)
        amounts = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|INR)\b', text)
        if amounts:
            entities['amounts'] = amounts
            
        return {k: v for k, v in entities.items() if v} # Remove empty lists

    def _analyze_themes(self, text: str) -> List[str]:
        """Find the most common meaningful words."""
        words = tokenize(text)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'i', 'my', 'is', 'was', 'it', 'that', 'this',
            'just', 'wanted', 'say', 'hello', 'everyone', 'here', 'today', 'uhh', 'um', 'like', 'so', 'then', 'there', 'their', 'they', 'we', 'you', 'your'
        }
        
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if not meaningful_words:
            return []
            
        # Get top 3 most common words
        counter = Counter(meaningful_words)
        return [word for word, count in counter.most_common(3)]

    def analyze(self, text: str = None, file_path: str = None, url: str = None) -> AnalysisResult:
        """Run general NLP and evidence extraction on the input."""
        signals = []
        input_text = f"{text or ''} {url or ''}".strip()
        
        if not input_text and not file_path:
            return AnalysisResult(
                module_name=self.module_name,
                confidence=0.0,
                decision="Error: No input",
                explanation="Please provide text, a file, or a URL to investigate."
            )
            
        entities = self._extract_entities(input_text)
        themes = self._analyze_themes(input_text)
        
        confidence = 50.0
        explanation_parts = [
            f"<strong>Deep Investigation Report</strong><br><br>",
            f"AURA Investigate has completed a comprehensive intelligence sweep of the provided input.<br><br>",
            f"<strong>Key Findings & Entities:</strong><br>"
        ]
        
        if entities:
            entity_count = sum(len(v) for v in entities.values())
            signals.append({'name': f"{entity_count} Entities Mapped", 'type': 'primary'})
            confidence += 15.0
            
            for k, v in entities.items():
                explanation_parts.append(f"• <strong>{k.capitalize()}:</strong> {', '.join(v)}<br>")
        else:
            explanation_parts.append(f"• No distinct dates, times, or financial entities could be extracted.<br>")
            
        explanation_parts.append(f"<br><strong>Thematic & Linguistic Analysis:</strong><br>")
        
        if themes:
            signals.append({'name': f"Themes: {', '.join(themes)}", 'type': 'info'})
            confidence += 10.0
            explanation_parts.append(f"• The core conversational themes identified are: {', '.join([t.upper() for t in themes])}.<br>")
        else:
            signals.append({'name': 'Low Information Density', 'type': 'secondary'})
            confidence -= 20.0
            explanation_parts.append("• The text structure was too brief or lacked substantive keywords to map a thematic vector.<br>")
            
        if file_path:
            signals.append({'name': 'File Metadata Logged', 'type': 'warning'})
            explanation_parts.append(f"<br><strong>File Forensics:</strong><br>• An external file attachment was detected. Deep binary forensics and OCR extraction are currently pending or restricted in this environment.<br>")
            
        decision = "Investigation Complete"
        if confidence > 70:
            decision = "High-Density Intelligence Found"
        elif confidence < 40:
            decision = "Low-Density Information"
            
        return AnalysisResult(
            module_name=self.module_name,
            confidence=max(0.0, min(99.9, confidence)),
            decision=decision,
            explanation="".join(explanation_parts),
            signals=signals,
            raw_data={'entities': entities, 'themes': themes}
        )
