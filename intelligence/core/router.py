"""AURA Router.

Determines which module should handle an input based on intent, content, and file type.
"""

from intelligence.preprocessing.text_cleaner import clean_text

def route_input(text: str = None, filename: str = None, url: str = None) -> str:
    """Determine the optimal AURA module for the given input.
    
    Args:
        text: Input text.
        filename: Name of the uploaded file.
        url: Input URL.
        
    Returns:
        str: The slug of the target module (e.g., 'trust', 'verify').
    """
    cleaned_text = clean_text(text) if text else ""
    
    # 1. URL Routing
    # If a URL is provided, it's most likely a safety/phishing check (Trust)
    if url:
        return 'trust'
        
    # 2. File Routing
    if filename:
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Identity documents, PDFs usually go to Verify
        if ext in ['pdf', 'doc', 'docx']:
            if any(keyword in cleaned_text for keyword in ['id', 'passport', 'certificate', 'resume']):
                return 'verify'
            return 'investigate' # Default document fallback
            
        # Images could be Find, Heritage, or Verify
        if ext in ['jpg', 'jpeg', 'png']:
            if any(keyword in cleaned_text for keyword in ['lost', 'found', 'missing']):
                return 'find'
            if any(keyword in cleaned_text for keyword in ['old', 'monument', 'artifact', 'statue']):
                return 'heritage'
            if any(keyword in cleaned_text for keyword in ['face', 'id', 'license']):
                return 'verify'
            return 'investigate' # General image fallback
            
    # 3. Text/Keyword Routing
    if cleaned_text:
        # Trust keywords
        if any(keyword in cleaned_text for keyword in ['scam', 'phishing', 'fake', 'suspicious', 'hack', 'click here', 'safe']):
            return 'trust'
            
        # Verify keywords
        if any(keyword in cleaned_text for keyword in ['verify', 'authentic', 'real or fake', 'certificate']):
            return 'verify'
            
        # Find keywords
        if any(keyword in cleaned_text for keyword in ['lost', 'found', 'missing', 'stolen']):
            return 'find'
            
        # Life keywords
        if any(keyword in cleaned_text for keyword in ['career', 'study', 'job', 'salary', 'university', 'college']):
            return 'life'
            
        # Heritage keywords
        if any(keyword in cleaned_text for keyword in ['history', 'monument', 'temple', 'artifact', 'ancient']):
            return 'heritage'
            
    # Default fallback
    return 'investigate'
