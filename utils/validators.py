# utils/validators.py
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
import mimetypes
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        self.allowed_video_types = {
            'video/mp4', 'video/quicktime', 'video/x-msvideo', 
            'video/webm', 'video/x-matroska'
        }
        self.max_file_size = 500 * 1024 * 1024  # 500MB
    
    def validate_video_file(self, file: FileStorage) -> bool:
        """Validate uploaded video file"""
        try:
            if not file or not file.filename:
                return False
            
            # Check file type
            if file.mimetype not in self.allowed_video_types:
                return False
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if size > self.max_file_size:
                return False
            
            return True
        except:
            return False
    
    def validate_post_data(self, data: Dict) -> Dict:
        """Validate post data"""
        errors = []
        
        if not data.get('title'):
            errors.append("Title is required")
        
        if not data.get('platforms'):
            errors.append("At least one platform must be selected")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def validate_platform_credentials(self, platform: str, credentials: Dict) -> bool:
        """Validate platform credentials"""
        required_fields = {
            'youtube': ['apiKey', 'channelId'],
            'instagram': ['username', 'access_token'],
            'tiktok': ['accessToken', 'userId'],
            'kawai': ['apiKey', 'userId']
        }
        
        if platform not in required_fields:
            return False
        
        for field in required_fields[platform]:
            if field not in credentials or not credentials[field]:
                return False
        
        return True
    
    def validate_schedule_time(self, schedule_time: str) -> bool:
        """Validate schedule time"""
        try:
            scheduled_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            return scheduled_datetime > datetime.now()
        except:
            return False