"""AURA Intelligence Base Classes."""

from typing import List, Dict, Any, Optional
from datetime import datetime

class AnalysisResult:
    """Standardized output format for all AURA analysis."""
    
    def __init__(
        self,
        module_name: str,
        confidence: float = 0.0,
        decision: str = "Unknown",
        explanation: str = "",
        signals: Optional[List[Dict[str, str]]] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.module_name = module_name
        self.confidence = max(0.0, min(100.0, confidence)) # Keep between 0 and 100
        self.decision = decision
        self.explanation = explanation
        self.signals = signals or []
        self.raw_data = raw_data or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization and DB storage."""
        return {
            'module': self.module_name,
            'confidence': round(self.confidence, 1),
            'decision': self.decision,
            'explanation': self.explanation,
            'signals': self.signals,
            'raw_data': self.raw_data,
            'timestamp': datetime.utcnow().isoformat()
        }


class AuraModule:
    """Base class that all AURA modules must inherit from."""
    
    @property
    def module_name(self) -> str:
        """Name of the module (e.g., 'AURA Trust')."""
        raise NotImplementedError
        
    @property
    def module_slug(self) -> str:
        """Slug identifier (e.g., 'trust')."""
        raise NotImplementedError
        
    def analyze(self, text: str = None, file_path: str = None, url: str = None) -> AnalysisResult:
        """Perform analysis on the given inputs.
        
        Args:
            text: User provided text.
            file_path: Path to an uploaded file.
            url: Provided URL.
            
        Returns:
            AnalysisResult object containing standardized findings.
        """
        raise NotImplementedError("Each module must implement the analyze method.")
