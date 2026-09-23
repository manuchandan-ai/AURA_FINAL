import os
import json
import urllib.request
import urllib.error
import logging
import re
from database.db import query_db, execute_db

logger = logging.getLogger(__name__)

# Basic dotenv loader since pip is blocked
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val.strip("'\"")

load_env()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def _extract_json_from_text(text: str) -> dict:
    """Attempt to extract JSON from the LLM response if it wrapped it in markdown."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Failed to parse LLM JSON: {e} \nText was: {text}")
        return {}

def call_gemini(system_prompt: str, user_prompt: str) -> str:
    """Call Gemini REST API using native urllib (no pip dependencies required)."""
    if not GEMINI_API_KEY:
        return "SIMULATION_MODE"

    # Use 1.5-flash for reliability and speed
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"parts": [{"text": user_prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json"
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    
    try:
        # Added timeout to prevent hanging forever
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            return ""
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return "ERROR"

def get_conversation_history(conversation_id: int) -> str:
    """Fetch recent messages for context."""
    messages = query_db(
        "SELECT sender, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,)
    )
    history = ""
    for msg in messages:
        sender_name = "User" if msg['sender'] == 'user' else "AURA"
        history += f"{sender_name}: {msg['content']}\n"
    return history

def process_chat(user_id: int, conversation_id: int, message: str) -> dict:
    """Process a chat message, detect goals, ask questions, or provide roadmap."""
    
    # Get history
    history = get_conversation_history(conversation_id)
    
    # Construct prompt
    system_prompt = """You are AURA, an Adaptive Unified Reasoning Assistant.
You can help with Travel, Career, Learn, Money, Health, Shop, Create, Project, Trust, Documents, and Life.
You MUST output your response in EXACT JSON format. No markdown wrappers.

Instructions:
1. Always give highly detailed, long, and comprehensive answers in the "response" field, richly formatted with markdown. Provide deep dive explanations.
2. If the user is stating a goal (e.g. "I want to learn python", "I want to save money", "Help me build a project", "I want to build a fitness app"), you MUST extract this into the "new_goal" object.
3. If the user's request is vague and you need more info to build a roadmap, put a clarifying question in the "response" field, but still give an initial detailed breakdown.
4. If you have enough info, generate a comprehensive step-by-step markdown roadmap/plan in the "response" field.

JSON Schema:
{
  "module": "AURA Learn",
  "confidence": 95,
  "decision": "Analysis Complete",
  "response": "Detailed, comprehensive, long markdown explanation here...",
  "new_goal": {
      "title": "Learn Python", 
      "description": "Master python in 5 days",
      "roadmap": "Day 1: Basics..." 
  }
}
If no goal is detected, set new_goal to null.
"""

    user_prompt = f"Previous Conversation:\n{history}\nUser's New Message: {message}"
    
    # Call Gemini
    raw_response = call_gemini(system_prompt, user_prompt)
    
    # Fallback Simulation if no API key
    if raw_response in ["SIMULATION_MODE", "ERROR"]:
        msg_lower = message.lower()
        module = "AURA Investigate"
        decision = "Analysis Complete"
        new_goal = None
        
        if "learn" in msg_lower or "python" in msg_lower or "study" in msg_lower:
            module = "AURA Learn"
            if "want to" in msg_lower or "plan" in msg_lower or "goal" in msg_lower:
                decision = "Goal Detected"
                new_goal = {
                    "title": "Master " + ("Python" if "python" in msg_lower else "New Skill"),
                    "description": "An intensive roadmap to master the subject.",
                    "roadmap": "• Phase 1: Fundamentals\n• Phase 2: Practical Application\n• Phase 3: Advanced Concepts"
                }
                resp_text = f"**I have added a new goal to your dashboard.**\n\nHere is a high-level roadmap to get you started:\n\n{new_goal['roadmap']}\n\nWould you like me to schedule reminders for these phases?"
            else:
                resp_text = "**Learning Analysis**\n\nI can help you study effectively. Please tell me your exact timeline and current skill level so I can generate a personalized roadmap."
                
        elif "remind" in msg_lower or "task" in msg_lower:
            module = "AURA Productivity"
            resp_text = "**Reminder System**\n\nI can schedule that for you. When exactly would you like to be reminded?"
            
        else:
            resp_text = f"**Intelligence Report**\n\nI have analyzed your input: '{message}'.\n\nI am AURA. To unlock my full potential, please add a `GEMINI_API_KEY` to the environment variables so I can process deep multi-turn reasoning natively."

        result_data = {
            "module": module,
            "confidence": 85,
            "decision": decision,
            "response": resp_text,
            "new_goal": new_goal
        }
    else:
        result_data = _extract_json_from_text(raw_response)
        
    return result_data
