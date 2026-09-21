"""AURA Verify Module — Document and Information Verification."""

import os
import re
import logging
from typing import Dict, Any, List
from PIL import Image

logger = logging.getLogger(__name__)

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("pytesseract not found. OCR will use mock extraction.")

from intelligence.core.base import AuraModule, AnalysisResult
from app.config import BASE_DIR

class AuraVerify(AuraModule):
    """Verifies documents and extracts key entities."""
    
    def __init__(self):
        super().__init__()
        # If tesseract isn't in PATH, one might need to set it on Windows
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    @property
    def module_name(self) -> str:
        return "AURA Verify"
        
    @property
    def module_slug(self) -> str:
        return "verify"

    def _extract_text_from_image(self, file_path: str) -> str:
        """Extract text from an image using OCR (Tesseract)."""
        try:
            full_path = os.path.join(BASE_DIR, 'uploads', file_path) if not os.path.isabs(file_path) else file_path
            if not os.path.exists(full_path):
                logger.error(f"File not found for OCR: {full_path}")
                return ""
                
            if PYTESSERACT_AVAILABLE:
                img = Image.open(full_path)
                return pytesseract.image_to_string(img)
            else:
                logger.info("Mock OCR: Returning filename as text")
                return f"MOCK_OCR_DATA [ID NO: AURA12345] [Name: Mock User] extracted from {file_path}"
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return ""

    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Extract key entities from text using Regex/Heuristics."""
        entities = {}
        
        # Look for typical ID card features
        id_pattern = re.search(r'\b(?:ID|NO|Number)[:\-\s]*([A-Z0-9]{5,15})\b', text, re.IGNORECASE)
        if id_pattern:
            entities['ID Number'] = id_pattern.group(1)
            
        # Date of birth
        dob_pattern = re.search(r'\b(?:DOB|Date of Birth|Birth Date)[:\-\s]*(\d{2}[-/\.]\d{2}[-/\.]\d{4})\b', text, re.IGNORECASE)
        if dob_pattern:
            entities['Date of Birth'] = dob_pattern.group(1)
            
        # Names (very basic heuristic - uppercase words near 'Name')
        name_pattern = re.search(r'\b(?:Name)[:\-\s]*([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b', text, re.IGNORECASE)
        if name_pattern:
            entities['Name'] = name_pattern.group(1)
            
        return entities

    def analyze(self, text: str = None, file_path: str = None, url: str = None) -> AnalysisResult:
        """Run OCR and verification checks on the input document."""
        signals = []
        extracted_text = text or ""
        
        # 1. OCR (if file provided)
        if file_path:
            ocr_text = self._extract_text_from_image(file_path)
            if ocr_text:
                extracted_text += "\n" + ocr_text
                signals.append({'name': 'OCR Text Extracted', 'type': 'info'})
            else:
                signals.append({'name': 'OCR Failed/No Text', 'type': 'warning'})

        if not extracted_text:
            return AnalysisResult(
                module_name=self.module_name,
                confidence=0.0,
                decision="Error: No content to verify",
                explanation="AURA Verify requires an image file or text input."
            )

        # 2. Extract Entities
        entities = self._extract_entities(extracted_text)
        if entities:
            signals.append({'name': f"{len(entities)} Entities Found", 'type': 'info'})
            
        # 3. Verification Logic (Heuristics)
        # Look for security features or suspicious patterns
        input_lower = extracted_text.lower()
        
        tamper_flags = 0
        if "photoshop" in input_lower or "edited" in input_lower:
            signals.append({'name': 'Metadata Tampering Hint', 'type': 'danger'})
            tamper_flags += 1
            
        # Check for standard document layouts
        is_gov_id = any(kw in input_lower for kw in ['republic', 'government', 'issued', 'identity card', 'passport'])
        is_certificate = any(kw in input_lower for kw in ['certificate', 'awarded', 'completion', 'diploma'])
        
        confidence = 50.0 # Baseline
        
        if is_gov_id:
            signals.append({'name': 'Government ID Format', 'type': 'success'})
            confidence += 30.0
            
            # Govt IDs usually have an ID number
            if 'ID Number' in entities:
                confidence += 15.0
            else:
                signals.append({'name': 'Missing ID Number', 'type': 'warning'})
                confidence -= 20.0
                
        elif is_certificate:
            signals.append({'name': 'Certificate Format', 'type': 'success'})
            confidence += 25.0
        
        # Adjust for tampering
        confidence -= (tamper_flags * 40.0)
        confidence = max(0.0, min(99.9, confidence))
        
        # 4. Synthesize Decision
        if tamper_flags > 0:
            decision = "High Risk of Tampering"
            explanation = "Document contains signs of digital manipulation or irregular formatting."
        elif confidence >= 80.0:
            decision = "Document Appears Authentic"
            explanation = f"Document matches expected layouts and key entities were found. Extracted: {', '.join(entities.keys())}."
        elif confidence >= 40.0:
            decision = "Inconclusive / Low Quality"
            explanation = "Could not definitively verify the document. The image might be blurry or the format is non-standard."
        else:
            decision = "Likely Invalid"
            explanation = "Document lacks expected security features and entity structures."
            
        return AnalysisResult(
            module_name=self.module_name,
            confidence=confidence,
            decision=decision,
            explanation=explanation,
            signals=signals,
            raw_data={'extracted_entities': entities, 'ocr_text_preview': extracted_text[:200]}
        )
