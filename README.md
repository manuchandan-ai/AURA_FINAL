# AURA — Adaptive Unified Reasoning Assistant

A multimodal AI/ML intelligence and decision-support platform with a shared adaptive intelligence core.

## Overview

AURA is designed to help users understand, identify, authenticate, investigate, match, correlate, predict, decide, explain, and adapt to real-world problems through a unified intelligence pipeline.

## Modules

| Module | Purpose |
|--------|--------|
| **AURA Trust** | Digital safety & suspicious content analysis |
| **AURA Verify** | Document & information verification |
| **AURA Find** | Lost/found object matching |
| **AURA Life** | Student & career intelligence |
| **AURA Investigate** | Evidence & event analysis |
| **AURA Heritage** | Historical/heritage object analysis |
| **AURA Access** | Accessibility layer |

## Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3
- **Backend:** Python, Flask
- **Database:** SQLite
- **AI/ML:** NumPy, Pandas, scikit-learn, OpenCV, Pillow, NLTK, pytesseract

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AURA_FINAL

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Run the application
python app/app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project Structure

```
AURA_FINAL/
├── app/              # Flask application
├── intelligence/     # Shared intelligence core
├── modules/          # AURA modules (Trust, Verify, etc.)
├── models/           # Trained ML models
├── datasets/         # Training datasets
├── database/         # SQLite database & schema
├── frontend/         # Templates & static assets
├── evaluation/       # ML evaluation scripts
├── tests/            # Test suite
└── docs/             # Documentation
```

## License

Academic project — BCA AIML Internship
