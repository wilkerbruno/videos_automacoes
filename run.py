# run.py
#!/usr/bin/env python3
"""
Social Media Automation System - Production Runner
"""

import os
import sys
from dotenv import load_dotenv
from app import create_app

app = create_app()
# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from services.scheduler import PostScheduler
from utils.config import Config
import logging

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application runner"""
    try:
        # Create Flask app
        social_app = create_app()
        
        # Initialize configuration
        Config.init_app(social_app.app)
        
        # Start scheduler
        scheduler = PostScheduler()
        scheduler.start()
        
        # Create required directories
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('temp_videos', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        logger.info("Starting Social Media Automation System")
        logger.info(f"Debug mode: {Config.DEBUG}")
        logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
        
        # Run the application
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        social_app.run(
            host=host,
            port=port,
            debug=Config.DEBUG
        )
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'scheduler' in locals():
            scheduler.stop()

if __name__ == '__main__':
    main()
    app.run()