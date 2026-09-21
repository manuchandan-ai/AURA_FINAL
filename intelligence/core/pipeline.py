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
            if 'find' not in self._modules:
                from intelligence.modules.find import AuraFind
                self._modules['find'] = AuraFind()
            return self._modules['find'].analyze(text=text, file_path=filename, url=url)
            
        elif module_slug == 'life':
            if 'life' not in self._modules:
                from intelligence.modules.life import AuraLife
                self._modules['life'] = AuraLife()
            return self._modules['life'].analyze(text=text, file_path=filename, url=url)
            
        elif module_slug == 'heritage':
            if 'heritage' not in self._modules:
                from intelligence.modules.heritage import AuraHeritage
                self._modules['heritage'] = AuraHeritage()
            return self._modules['heritage'].analyze(text=text, file_path=filename, url=url)
            
        else:
            if 'investigate' not in self._modules:
                from intelligence.modules.investigate import AuraInvestigate
                self._modules['investigate'] = AuraInvestigate()
            return self._modules['investigate'].analyze(text=text, file_path=filename, url=url)

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
            result = self._get_mock_module_result(target_slug, text, filename, url)
            
            # 4.5 Stage 13 Correlation & Memory
            try:
                from database.db import query_db
                
                input_string = f"{text or ''} {url or ''}".lower()
                
                # Check for previously flagged entities
                bad_entities = query_db("SELECT entity_type, entity_value FROM global_entities WHERE risk_level = 'high'")
                flagged = []
                for row in bad_entities:
                    if str(row['entity_value']).lower() in input_string:
                        flagged.append(str(row['entity_value']))
                
                if flagged:
                    result.signals.append({'name': 'Previously Flagged Entity Detected', 'type': 'danger'})
                    result.explanation = f"WARNING: Correlation Engine identified known high-risk data ({', '.join(flagged)}). " + result.explanation
                    if 'Risk' not in result.decision:
                        result.decision = f"Elevated Risk: {result.decision}"
                
                # Save new high-risk entities
                if result.confidence > 70 and any(w in result.decision.lower() for w in ['risk', 'fake', 'phishing', 'tampering']):
                    # Add URL if present
                    if url:
                        execute_db(
                            "INSERT OR IGNORE INTO global_entities (entity_type, entity_value, associated_module, risk_level) VALUES (?, ?, ?, ?)",
                            ('url', url, result.module_name, 'high')
                        )
                    # Add extracted entities if present
                    if 'entities' in result.raw_data:
                        for etype, evalues in result.raw_data['entities'].items():
                            for val in evalues:
                                execute_db(
                                    "INSERT OR IGNORE INTO global_entities (entity_type, entity_value, associated_module, risk_level) VALUES (?, ?, ?, ?)",
                                    (etype, str(val), result.module_name, 'high')
                                )
            except Exception as ce:
                logger.error(f"Correlation Engine Error: {ce}")
            
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
