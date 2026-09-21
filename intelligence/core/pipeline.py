"""AURA Central Intelligence Pipeline."""

import logging
import json
from database.db import execute_db
from intelligence.core.router import route_input
from intelligence.core.base import AnalysisResult

logger = logging.getLogger(__name__)

class IntelligencePipeline:
    """Orchestrates the entire intelligence flow from input to final decision."""
    
    def __init__(self):
        # We will dynamically load modules later, but for Stage 5 we mock them
        self._modules = {}
        
    def _get_mock_module_result(self, module_slug: str, text: str, filename: str, url: str) -> AnalysisResult:
        """Execute the appropriate intelligence module."""
        
        if module_slug == 'trust':
            # Lazy load the module to save memory
            if 'trust' not in self._modules:
                from intelligence.modules.trust import AuraTrust
                self._modules['trust'] = AuraTrust()
            return self._modules['trust'].analyze(text=text, file_path=filename, url=url)
            
        elif module_slug == 'verify':
            if 'verify' not in self._modules:
                from intelligence.modules.verify import AuraVerify
                self._modules['verify'] = AuraVerify()
            return self._modules['verify'].analyze(text=text, file_path=filename, url=url)
            
        elif module_slug == 'find':
            return AnalysisResult(
                module_name="AURA Find",
                confidence=60.0,
                decision="Potential Matches Found (3)",
                explanation="Found 3 similar items in the regional database reported in the last 7 days.",
                signals=[
                    {'name': 'Color Match', 'type': 'info'},
                    {'name': 'Location Proximity', 'type': 'info'}
                ],
                raw_data={'mock': True}
            )
        else:
            return AnalysisResult(
                module_name=f"AURA {module_slug.capitalize()}",
                confidence=50.0,
                decision="Analysis Complete",
                explanation="General analysis performed using fallback heuristics.",
                signals=[{'name': 'Generic Analysis', 'type': 'info'}],
                raw_data={'mock': True}
            )

    def process(self, user_id: int, text: str = None, file_path: str = None, filename: str = None, url: str = None) -> dict:
        """Run the full intelligence pipeline on the user's input.
        
        Args:
            user_id: ID of the user requesting analysis.
            text: Text input.
            file_path: Path to saved file on disk.
            filename: Original name of the uploaded file.
            url: URL input.
            
        Returns:
            dict: The analysis result data.
        """
        logger.info(f"Pipeline started for user {user_id}")
        
        # 1. Determine input type
        input_type = 'mixed'
        if text and not file_path and not url:
            input_type = 'text'
        elif file_path and not text and not url:
            input_type = 'document' if filename.split('.')[-1].lower() in ['pdf', 'doc'] else 'image'
        elif url and not text and not file_path:
            input_type = 'url'
            
        input_summary = (text[:50] + "...") if text else (filename if filename else url)
            
        # 2. Routing (Understand Stage)
        target_slug = route_input(text, filename, url)
        logger.info(f"Input routed to: {target_slug}")
        
        # 3. Create initial History Record
        history_id = execute_db(
            'INSERT INTO analysis_history (user_id, input_type, input_summary, detected_module, status) VALUES (?, ?, ?, ?, ?)',
            (user_id, input_type, input_summary, target_slug, 'processing')
        )
        
        try:
            # 4. Execute Module (Analyze, Predict, Decide Stages)
            # In Stage 5, we use the mock result generator
            result = self._get_mock_module_result(target_slug, text, filename, url)
            
            # 5. Save Results to DB
            execute_db(
                '''INSERT INTO analysis_results 
                   (analysis_id, result_data, signals, decision, explanation) 
                   VALUES (?, ?, ?, ?, ?)''',
                (
                    history_id,
                    json.dumps(result.to_dict()),
                    json.dumps(result.signals),
                    result.decision,
                    result.explanation
                )
            )
            
            # 6. Update History Record
            execute_db(
                'UPDATE analysis_history SET status = ?, intent = ?, confidence = ? WHERE id = ?',
                ('completed', 'general_query', result.confidence / 100.0, history_id)
            )
            
            # Return result dict
            return {
                'status': 'success',
                'analysis_id': history_id,
                **result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            execute_db('UPDATE analysis_history SET status = ? WHERE id = ?', ('failed', history_id))
            return {
                'status': 'error',
                'message': str(e)
            }
