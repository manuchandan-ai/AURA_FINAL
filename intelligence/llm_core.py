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

def call_free_ai(system_prompt: str, user_prompt: str) -> str:
    """Call Local Ollama API (No API Key Required)."""
    url = 'http://localhost:11434/api/chat'
    payload = {
        'model': 'qwen3:8b',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'stream': False,
        'format': 'json'
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    
    try:
        # 120 second timeout since local models on CPU can take time
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['message']['content']
    except Exception as e:
        logger.error(f"Ollama API Error: {e}")
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
    """Process a chat message using the Free AI Engine."""
    
    history = get_conversation_history(conversation_id)
    
    system_prompt = """You are AURA, an Adaptive Unified Reasoning Assistant.
You can help with Travel, Career, Learn, Money, Health, Shop, Create, Project, Trust, Documents, and Life.
You MUST output your response in EXACT JSON format. No markdown wrappers.

Instructions:
1. Always give highly detailed, long, and comprehensive answers in the "response" field, richly formatted with markdown. Provide deep dive explanations.
2. If the user is stating a goal (e.g. "I want to learn python", "I want to save money", "Help me build a project", "I want to build a fitness app"), you MUST extract this into the "new_goal" object.
3. If the user's request is vague and you need more info to build a roadmap, put a clarifying question in the "response" field, but still give an initial detailed breakdown.
4. If you have enough info, generate a comprehensive step-by-step markdown roadmap/plan in the "response" field.
5. If the user asks a simple question, answer it thoroughly.

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
    
    raw_response = call_free_ai(system_prompt, user_prompt)
    
    if raw_response == "ERROR":
        return {
            "module": "AURA System",
            "confidence": 100,
            "decision": "API Unavailable",
            "response": "**System Alert**\n\nThe local Ollama Engine is currently unreachable or timed out. Please ensure Ollama is running in the background with the `qwen3:8b` model installed.",
            "new_goal": None
        }
        
    return _extract_json_from_text(raw_response)
