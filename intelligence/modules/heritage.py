"""AURA Heritage Module — Historical Artifact Analysis."""

import re
import logging
from typing import Dict, Any, List

from intelligence.core.base import AuraModule, AnalysisResult
from intelligence.preprocessing.text_cleaner import clean_text

logger = logging.getLogger(__name__)

class AuraHeritage(AuraModule):
    """Analyzes historical artifacts, monuments, and eras."""
    
    def __init__(self):
        super().__init__()
        
        # Mock historical knowledge base for Stage 12
        self.heritage_db = {
            'roman': {
                'era': 'Roman Empire (27 BC - 476 AD)',
                'keywords': ['roman', 'colosseum', 'gladiator', 'aqueduct', 'julius', 'caesar', 'latin'],
                'risk': 'Low',
                'context': 'The Roman Empire was characterized by significant architectural and engineering advancements.'
            },
            'egyptian': {
                'era': 'Ancient Egypt (c. 3100 BC - 30 BC)',
                'keywords': ['egypt', 'egyptian', 'pyramid', 'pharaoh', 'sphinx', 'hieroglyph', 'nile'],
                'risk': 'Medium',
                'context': 'Ancient Egyptian civilization is famous for its monumental architecture and complex religion.'
            },
            'mayan': {
                'era': 'Maya Civilization (c. 2000 BC - 1697 AD)',
                'keywords': ['maya', 'mayan', 'chichen itza', 'mesoamerica', 'yucatan', 'temple'],
                'risk': 'High',
                'context': 'The Maya developed a complex writing system and made significant astronomical discoveries.'
            }
        }
        
    @property
    def module_name(self) -> str:
        return "AURA Heritage"
        
    @property
    def module_slug(self) -> str:
        return "heritage"
        
    def _extract_years(self, text: str) -> List[str]:
        """Extract historical years from text (e.g., 200 BC, 1492 AD)."""
        years = re.findall(r'\b\d{1,4}\s*(?:BC|BCE|AD|CE)\b', text, re.IGNORECASE)
        return [y.upper() for y in years]
        
    def _match_civilization(self, text: str) -> str:
        """Find the matching civilization based on keywords."""
        text_lower = text.lower()
        
        best_match = None
        max_overlap = 0
        
        for civ, data in self.heritage_db.items():
            overlap = sum(1 for kw in data['keywords'] if kw in text_lower)
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = civ
                
        return best_match

    def analyze(self, text: str = None, file_path: str = None, url: str = None) -> AnalysisResult:
        """Analyze the historical query or artifact description."""
        signals = []
        input_text = text or ""
        
        if not input_text:
            return AnalysisResult(
                module_name=self.module_name,
                confidence=0.0,
                decision="Error: No input",
                explanation="Please provide a description of the artifact or historical site."
            )
            
        years_found = self._extract_years(input_text)
        if years_found:
            signals.append({'name': f"Timeframes Detected: {', '.join(years_found)}", 'type': 'info'})
            
        civ_match = self._match_civilization(input_text)
        
        if civ_match:
            civ_data = self.heritage_db[civ_match]
            confidence = 88.5
            decision = f"Origin: {civ_data['era']}"
            
            signals.append({'name': 'Civilization Identified', 'type': 'success'})
            
            risk_type = 'danger' if civ_data['risk'] == 'High' else ('warning' if civ_data['risk'] == 'Medium' else 'primary')
            signals.append({'name': f"Artifact Trafficking Risk: {civ_data['risk']}", 'type': risk_type})
            
            explanation_parts = [
                f"<strong>Historical Analysis Report</strong><br><br>",
                f"AURA Heritage has matched the described artifact or query to the <strong>{civ_data['era']}</strong>.<br><br>",
                f"<strong>Historical Context:</strong><br>",
                f"• {civ_data['context']}<br>"
            ]
            
            if years_found:
                explanation_parts.append(f"• <strong>Chronology:</strong> The specified dates ({', '.join(years_found)}) overlap with this civilization's timeline.<br>")
                
            explanation_parts.append(f"<br><strong>Preservation & Trafficking Risk: {civ_data['risk']}</strong><br>")
            explanation_parts.append(f"Artifacts and monuments from this era currently face a {civ_data['risk'].lower()} risk profile regarding illegal antiquities trafficking, looting, or forgery. Authentication by a certified archaeologist is highly recommended.")
            
            explanation = "".join(explanation_parts)
            raw_data = civ_data
        else:
            confidence = 45.0
            decision = "Unknown Origin"
            signals.append({'name': 'No Civilization Match', 'type': 'warning'})
            
            explanation = (
                f"<strong>Historical Analysis Report</strong><br><br>"
                f"AURA Heritage could not definitively match the artifact's characteristics to a primary civilization in our current architectural database.<br><br>"
                f"<strong>Recommended Actions:</strong><br>"
                f"• Provide more specific structural keywords (e.g., 'columns', 'hieroglyphs', 'bronze').<br>"
                f"• The artifact may belong to a more obscure era, or require specialized radiocarbon (C-14) dating and expert appraisal."
            )
            raw_data = {}
            
        return AnalysisResult(
            module_name=self.module_name,
            confidence=confidence,
            decision=decision,
            explanation=explanation,
            signals=signals,
            raw_data=raw_data
        )
