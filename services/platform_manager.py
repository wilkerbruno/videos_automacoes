# services/platform_manager.py
import logging
from typing import Dict, List, Any, Optional
import os
from services.youtube_service import YouTubeService




logger = logging.getLogger(__name__)

class PlatformManager:
    def __init__(self):
        self.connected_platforms = set()
    
    async def post_to_platforms(self, post_data):
        # Mock implementation
        return {'success': True}
    
    async def connect_platform(self, platform, credentials):
        # Mock implementation
        return {'success': True}
    
    def get_all_platform_status(self):
        # Mock implementation
        return {}
    
    class YouTubeManager:
        def __init__(self):
            self.youtube_service = YouTubeService()
        
    async def connect(self, credentials: Dict) -> Dict:
        """Connect to YouTube API"""
        return await self.youtube_service.connect(credentials)
    
    async def post(self, post_data: Dict) -> Dict:
        """Post video to YouTube"""
        try:
            platform_content = post_data.get('platform_specific', {}).get('youtube', {})
            
            # Get video file path
            files = post_data.get('files', [])
            if not files:
                return {'success': False, 'error': 'No video files provided'}
            
            # Use the processed video path for YouTube
            video_path = None
            for file_info in files:
                processed_videos = file_info.get('processed_videos', {})
                if 'youtube' in processed_videos:
                    video_path = processed_videos['youtube']['path']
                    break
                elif file_info.get('original_path'):
                    video_path = file_info['original_path']
                    break
            
            if not video_path or not os.path.exists(video_path):
                return {'success': False, 'error': 'Video file not found'}
            
            # Prepare metadata
            metadata = {
                'title': platform_content.get('title', post_data.get('title', 'Untitled')),
                'description': platform_content.get('description', post_data.get('description', '')),
                'hashtags': platform_content.get('hashtags', post_data.get('hashtags', [])),
                'category': post_data.get('category', 'entertainment')
            }
            
            # Upload to YouTube
            result = await self.youtube_service.upload_video(video_path, metadata)
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_supported_features(self) -> List[str]:
        return ['video_upload', 'shorts', 'scheduling', 'analytics', 'live_streaming']


    # OAuth Setup Instructions for YouTube
"""
To enable actual YouTube video uploads, you need to set up OAuth 2.0:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Web application"
   - Add redirect URI: http://localhost:5000/oauth/youtube/callback
   
5. Download the client_secrets.json file

6. Add these environment variables to your .env:
   YOUTUBE_CLIENT_ID=your_client_id_here
   YOUTUBE_CLIENT_SECRET=your_client_secret_here
   
7. Implement OAuth flow to get access_token and refresh_token

For now, the system is using API Key only which allows reading but not uploading.
Video uploads require OAuth authentication with write permissions.
"""