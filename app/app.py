"""AURA Application Entry Point.

Usage:
    python app/app.py
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  AURA — Adaptive Unified Reasoning Assistant")
    print("  Version:", app.config.get('AURA_VERSION', '1.0.0'))
    print("  http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
