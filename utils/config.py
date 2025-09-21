# utils/config.py
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Config:
    """Configuration class for Social Media Automation System"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 500 * 1024 * 1024))  # 500MB
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv'}
    
    # AI Service Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.8))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///social_media_automation.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Platform API Keys (Store encrypted in production)
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID', '')
    YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', '')
    
    INSTAGRAM_APP_ID = os.getenv('INSTAGRAM_APP_ID', '')
    INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET', '')
    INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
    
    TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY', '')
    TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET', '')
    TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN', '')
    
    KAWAI_API_KEY = os.getenv('KAWAI_API_KEY', '')
    KAWAI_SECRET = os.getenv('KAWAI_SECRET', '')
    
    # Webhook Secrets
    YOUTUBE_WEBHOOK_SECRET = os.getenv('YOUTUBE_WEBHOOK_SECRET', '')
    INSTAGRAM_WEBHOOK_SECRET = os.getenv('INSTAGRAM_WEBHOOK_SECRET', '')
    TIKTOK_WEBHOOK_SECRET = os.getenv('TIKTOK_WEBHOOK_SECRET', '')
    KAWAI_WEBHOOK_SECRET = os.getenv('KAWAI_WEBHOOK_SECRET', '')
    
    # Scheduler Configuration
    SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'America/Sao_Paulo')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # Security Configuration
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'social_media_automation.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Analytics Configuration
    ANALYTICS_RETENTION_DAYS = int(os.getenv('ANALYTICS_RETENTION_DAYS', 90))
    
    # External Services
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
    
    # Advanced Features
    ENABLE_AI_CONTENT_OPTIMIZATION = os.getenv('ENABLE_AI_CONTENT_OPTIMIZATION', 'True').lower() == 'true'
    ENABLE_VIRAL_ANALYSIS = os.getenv('ENABLE_VIRAL_ANALYSIS', 'True').lower() == 'true'
    ENABLE_AUTO_SCHEDULING = os.getenv('ENABLE_AUTO_SCHEDULING', 'True').lower() == 'true'
    ENABLE_PERFORMANCE_TRACKING = os.getenv('ENABLE_PERFORMANCE_TRACKING', 'True').lower() == 'true'
    
    # Video Processing Configuration
    VIDEO_PROCESSING_QUALITY = os.getenv('VIDEO_PROCESSING_QUALITY', 'high')  # low, medium, high
    MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', 300))  # 5 minutes in seconds
    SUPPORTED_VIDEO_FORMATS = ['mp4', 'mov', 'avi', 'mkv', 'webm']
    
    # Platform-specific Settings
    PLATFORM_SETTINGS = {
        'youtube': {
            'max_title_length': 100,
            'max_description_length': 5000,
            'max_tags': 15,
            'video_formats': ['mp4'],
            'max_file_size': 256 * 1024 * 1024,  # 256MB
            'resolution': (1920, 1080)
        },
        'instagram': {
            'max_title_length': 125,
            'max_description_length': 2200,
            'max_hashtags': 30,
            'video_formats': ['mp4', 'mov'],
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'resolution': (1080, 1920)
        },
        'tiktok': {
            'max_title_length': 100,
            'max_description_length': 300,
            'max_hashtags': 10,
            'video_formats': ['mp4', 'mov'],
            'max_file_size': 75 * 1024 * 1024,  # 75MB
            'resolution': (1080, 1920)
        },
        'kawai': {
            'max_title_length': 80,
            'max_description_length': 500,
            'max_hashtags': 20,
            'video_formats': ['mp4'],
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'resolution': (1080, 1920)
        }
    }
    
    # Monitoring Configuration
    MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'True').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 300))  # 5 minutes
    ALERT_EMAIL_ENABLED = os.getenv('ALERT_EMAIL_ENABLED', 'False').lower() == 'true'
    
    # Performance Thresholds
    CPU_THRESHOLD = float(os.getenv('CPU_THRESHOLD', 80.0))
    MEMORY_THRESHOLD = float(os.getenv('MEMORY_THRESHOLD', 85.0))
    DISK_THRESHOLD = float(os.getenv('DISK_THRESHOLD', 90.0))
    RESPONSE_TIME_THRESHOLD = float(os.getenv('RESPONSE_TIME_THRESHOLD', 5.0))
    
    @classmethod
    def init_app(cls, app):
        """Initialize Flask app with configuration"""
        # Create necessary directories
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('temp_videos', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Set Flask configuration
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        
        # Additional Flask configurations
        app.config['JSON_SORT_KEYS'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = cls.DEBUG
        
    @classmethod
    def validate_config(cls):
        """Validate required configuration values"""
        required_configs = []
        warnings = []
        
        # Check required API keys
        if not cls.OPENAI_API_KEY:
            required_configs.append('OPENAI_API_KEY is required for AI content generation')
        
        # Check platform configurations
        platform_keys = {
            'YouTube': cls.YOUTUBE_API_KEY,
            'Instagram': cls.INSTAGRAM_ACCESS_TOKEN,
            'TikTok': cls.TIKTOK_ACCESS_TOKEN,
            'Kawai': cls.KAWAI_API_KEY
        }
        
        missing_platforms = [name for name, key in platform_keys.items() if not key]
        if missing_platforms:
            warnings.append(f'Missing API keys for: {", ".join(missing_platforms)}')
        
        # Check database configuration
        if not cls.DATABASE_URL:
            required_configs.append('DATABASE_URL is required')
        
        # Check security settings
        if cls.SECRET_KEY == 'your-secret-key-change-this-in-production':
            warnings.append('Please change the default SECRET_KEY in production')
        
        if cls.JWT_SECRET_KEY == 'jwt-secret-key-change-this':
            warnings.append('Please change the default JWT_SECRET_KEY in production')
        
        return {
            'valid': len(required_configs) == 0,
            'required': required_configs,
            'warnings': warnings
        }
    
    @classmethod
    def get_platform_config(cls, platform):
        """Get configuration for specific platform"""
        return cls.PLATFORM_SETTINGS.get(platform, {})
    
    @classmethod
    def is_platform_enabled(cls, platform):
        """Check if platform is properly configured"""
        platform_keys = {
            'youtube': cls.YOUTUBE_API_KEY,
            'instagram': cls.INSTAGRAM_ACCESS_TOKEN,
            'tiktok': cls.TIKTOK_ACCESS_TOKEN,
            'kawai': cls.KAWAI_API_KEY
        }
        return bool(platform_keys.get(platform))
    
    @classmethod
    def get_enabled_platforms(cls):
        """Get list of enabled platforms"""
        enabled = []
        if cls.is_platform_enabled('youtube'):
            enabled.append('youtube')
        if cls.is_platform_enabled('instagram'):
            enabled.append('instagram')
        if cls.is_platform_enabled('tiktok'):
            enabled.append('tiktok')
        if cls.is_platform_enabled('kawai'):
            enabled.append('kawai')
        return enabled

# Development Configuration
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'

# Testing Configuration
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    UPLOAD_FOLDER = 'test_uploads'

# Production Configuration
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}