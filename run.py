# run.py - Corrigido para funcionar com a estrutura atual
#!/usr/bin/env python3
"""
Social Media Automation System - Production Runner
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask


# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import after setting path
from app import SocialMediaApp
from utils.config import Config
import logging

# Setup logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'social_media_automation.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application runner"""
    try:
        # Validate configuration
        validation = Config.validate_config()
        if not validation['valid']:
            logger.error("Configuration validation failed:")
            for error in validation['required']:
                logger.error(f"  - {error}")
            return
        
        if validation['warnings']:
            logger.warning("Configuration warnings:")
            for warning in validation['warnings']:
                logger.warning(f"  - {warning}")
        
        # Create and configure the app
        social_app = SocialMediaApp()
        
        # Get configuration from environment
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        logger.info("Starting Social Media Automation System")
        logger.info(f"Host: {host}, Port: {port}, Debug: {debug}")
        logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
        
        # Validate enabled platforms
        enabled_platforms = Config.get_enabled_platforms()
        logger.info(f"Enabled platforms: {', '.join(enabled_platforms) if enabled_platforms else 'None'}")
        
        if not enabled_platforms:
            logger.warning("No platforms are properly configured. Please check your API keys.")
        
        # Run the application
        social_app.run(
            host=host,
            port=port,
            debug=debug
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()