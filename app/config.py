"""AURA Configuration."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project (AURA_FINAL/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'aura-dev-secret-key-change-in-production')

    # Database
    DATABASE = os.path.join(BASE_DIR, 'database', 'aura.db')

    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'pdf', 'doc', 'docx', 'txt'}

    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # AURA
    AURA_VERSION = '1.0.0'
    AURA_NAME = 'AURA'
    AURA_FULL_NAME = 'Adaptive Unified Reasoning Assistant'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Configuration map
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
