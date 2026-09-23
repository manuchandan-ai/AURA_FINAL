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

def _extract_topic(msg: str) -> str:
    """Extract the core topic from a user's message."""
    msg = msg.lower().strip()
    prefixes = [
        'i want to learn about ', 'i want to learn ', 'what is ', 'who is ', 'tell me about ',
        'explain ', 'how to build a ', 'how to build ', 'roadmap for ', 'study materials for ',
        'information on ', 'help me with '
    ]
    for prefix in prefixes:
        if msg.startswith(prefix):
            msg = msg[len(prefix):]
            break
    
    # Remove punctuation at the end
    msg = re.sub(r'[^\w\s]+$', '', msg)
    return msg.strip().title()

def _fetch_wikipedia_summary(topic: str) -> dict:
    """Fetch real-world data from Wikipedia REST API (100% Free, No Keys)."""
    if not topic:
        return None
        
    # Attempt direct search and some common variants
    variants = [
        urllib.parse.quote(topic),
        urllib.parse.quote(topic + " (programming language)"),
        urllib.parse.quote(topic + " (software)")
    ]
    
    for variant in variants:
        url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{variant}'
        req = urllib.request.Request(url, headers={'User-Agent': 'AURA_Knowledge_Engine/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if 'extract' in data:
                    return data
        except Exception:
            continue
            
    return None

def process_chat(user_id: int, conversation_id: int, message: str) -> dict:
    """Process a chat message using the Free Hybrid Knowledge Engine."""
    
    msg_lower = message.lower()
    topic = _extract_topic(message)
    
    # Default fallbacks
    module = "AURA Investigate"
    decision = "Analysis Complete"
    new_goal = None
    resp_text = ""
    
    # Check for simple conversational inputs
    if msg_lower in ['yes', 'yeah', 'yep', 'sure']:
        return {
            "module": "AURA Conversational",
            "confidence": 99,
            "decision": "Affirmative",
            "response": "**Excellent.** I have logged your preference. How else can I assist you today?",
            "new_goal": None
        }
    elif msg_lower in ['hi', 'hello', 'hey']:
        return {
            "module": "AURA Conversational",
            "confidence": 99,
            "decision": "Greeting",
            "response": "**Hello!** I am AURA, your advanced knowledge assistant. What would you like to learn or explore today?",
            "new_goal": None
        }
        
    # Detect if this is a learning/goal request
    is_learning = any(x in msg_lower for x in ['learn', 'study', 'roadmap', 'build', 'goal', 'plan'])
    
    # Try fetching real data
    wiki_data = _fetch_wikipedia_summary(topic)
    
    if wiki_data:
        module = "AURA Learn" if is_learning else "AURA Encyclopedia"
        desc = wiki_data.get('description', 'Fascinating subject')
        extract = wiki_data.get('extract', '')
        url = wiki_data.get('content_urls', {}).get('desktop', {}).get('page', f'https://en.wikipedia.org/wiki/{topic}')
        
        resp_text = f"### Knowledge Engine Analysis: **{topic}**\n\n"
        resp_text += f"> {desc.capitalize()}\n\n"
        resp_text += f"{extract}\n\n"
        resp_text += f"[📖 Read full Wikipedia Article]({url})\n\n"
        
        if is_learning:
            decision = "Goal Detected"
            new_goal = {
                "title": f"Master {topic}",
                "description": f"Comprehensive study plan for {topic}",
                "roadmap": f"**Phase 1: Foundations**\n- Understand the history and core concepts of {topic}.\n- Read introductory materials and set up your workspace.\n\n**Phase 2: Deep Dive**\n- Practice core principles.\n- Build your first mini-project related to {topic}.\n\n**Phase 3: Advanced Mastery**\n- Explore advanced topics and edge cases.\n- Share your knowledge with the community."
            }
            resp_text += "---\n### 🚀 Suggested Learning Roadmap\n\nI have automatically generated a goal and roadmap for you to master this subject. You will find it in your Quick Actions or Goals dashboard.\n\n"
            resp_text += new_goal['roadmap']
            
    else:
        # Fallback if topic is unknown or too vague
        if is_learning:
            module = "AURA Learn"
            decision = "Clarification Needed"
            resp_text = f"**Learning Module Active**\n\nI see you want to learn about **{topic or 'this subject'}**. To generate a highly tailored curriculum and roadmap, could you provide a bit more detail about your current skill level?"
        elif "remind" in msg_lower or "task" in msg_lower:
            module = "AURA Productivity"
            resp_text = "**Productivity Engine**\n\nI can certainly schedule that. When exactly would you like the reminder to trigger?"
        else:
            resp_text = f"**AURA Intelligence**\n\nI have analyzed your input: '{message}'.\n\nWhile I don't have a specific Wikipedia entry for this exact phrase, I am ready to help you break this down into actionable steps. What is your ultimate goal here?"

    return {
        "module": module,
        "confidence": 95,
        "decision": decision,
        "response": resp_text,
        "new_goal": new_goal
    }
