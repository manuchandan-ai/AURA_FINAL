"""AURA Life Module — Student and Career Intelligence."""

import re
import logging
from typing import Dict, Any, List

from intelligence.core.base import AuraModule, AnalysisResult
from intelligence.preprocessing.text_cleaner import clean_text

logger = logging.getLogger(__name__)

class AuraLife(AuraModule):
    """Provides insights and guidance for career and academic paths."""
    
    def __init__(self):
        super().__init__()
        
        # Mock knowledge base for Stage 10
        self.career_db = {
            'aiml': {
                'title': 'AI/ML Engineer',
                'salary_range': '$90,000 - $160,000+',
                'growth': 'Very High (35% YoY)',
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'Data Structures', 'Statistics']
            },
            'webdev': {
                'title': 'Full Stack Developer',
                'salary_range': '$70,000 - $130,000+',
                'growth': 'High (15% YoY)',
                'skills': ['JavaScript', 'React', 'Node.js', 'Python', 'Databases']
            },
            'data': {
                'title': 'Data Scientist',
                'salary_range': '$85,000 - $150,000+',
                'growth': 'High (22% YoY)',
                'skills': ['Python', 'SQL', 'Machine Learning', 'Data Visualization', 'Math']
            },
            'python': {
                'title': 'Python Developer (Intensive Roadmap)',
                'salary_range': '$80,000 - $140,000+',
                'growth': 'Very High',
                'skills': ['Python Syntax', 'OOP', 'Django/Flask', 'Data Structures', 'Algorithms'],
                'roadmap': "Day 1: Basics (Variables, Data Types, Control Flow)<br>Day 2: Functions, Modules & Error Handling<br>Day 3: Object Oriented Programming (OOP)<br>Day 4: File Handling & Libraries (Requests, OS)<br>Day 5: Mini Project (API integration or Web Scraper)",
                'links': "<a href='https://docs.python.org/3/tutorial/index.html' target='_blank' class='text-info'>Official Python Tutorial</a> | <a href='https://www.freecodecamp.org/learn/scientific-computing-with-python/' target='_blank' class='text-info'>freeCodeCamp Python</a>"
            }
        }
        
    @property
    def module_name(self) -> str:
        return "AURA Life"
        
    @property
    def module_slug(self) -> str:
        return "life"
        
    def _match_intent(self, text: str) -> str:
        """Determine what the user is asking about."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ['python', 'learn python']):
            return 'python'
        if any(w in text_lower for w in ['ai', 'ml', 'artificial intelligence', 'machine learning']):
            return 'aiml'
        if any(w in text_lower for w in ['web', 'frontend', 'backend', 'full stack', 'developer']):
            return 'webdev'
        if any(w in text_lower for w in ['data', 'analytics', 'scientist', 'big data']):
            return 'data'
            
        return 'general'

    def analyze(self, text: str = None, file_path: str = None, url: str = None) -> AnalysisResult:
        """Analyze the career/study inquiry and return intelligence."""
        signals = []
        input_text = text or ""
        
        if not input_text:
            return AnalysisResult(
                module_name=self.module_name,
                confidence=0.0,
                decision="Error: No query provided",
                explanation="Please provide a career or academic question."
            )
            
        intent = self._match_intent(input_text)
        
        if intent == 'general':
            confidence = 40.0
            decision = "General Career Guidance"
            signals.append({'name': 'Broad Inquiry', 'type': 'info'})
            explanation = "Your query is quite broad. AURA Life specializes in tech careers like AI/ML, Web Development, and Data Science. Try asking specifically about those paths."
            raw_data = {}
        else:
            confidence = 92.5
            career_info = self.career_db[intent]
            decision = f"Path Match: {career_info['title']}"
            
            signals.append({'name': 'Specific Career Path', 'type': 'success'})
            signals.append({'name': f"Growth: {career_info['growth']}", 'type': 'primary'})
            
            explanation = (
                f"You asked about the <strong>{career_info['title']}</strong> path.<br><br>"
                f"<strong>Estimated Salary Range:</strong> {career_info['salary_range']}<br>"
                f"<strong>Growth Demand:</strong> {career_info['growth']}<br><br>"
                f"<strong>Core Skills to Master:</strong> {', '.join(career_info['skills'])}.<br><br>"
            )
            
            if 'roadmap' in career_info:
                explanation += f"<strong>Intensive Study Roadmap:</strong><br>{career_info['roadmap']}<br><br>"
            
            if 'links' in career_info:
                explanation += f"<strong>Study Materials:</strong><br>{career_info['links']}"
                
            raw_data = career_info
            
        return AnalysisResult(
            module_name=self.module_name,
            confidence=confidence,
            decision=decision,
            explanation=explanation,
            signals=signals,
            raw_data=raw_data
        )
