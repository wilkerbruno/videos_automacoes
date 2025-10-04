# services/youtube_service.py
import os
import logging
import pickle
from typing import Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeService:
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    def __init__(self):
        self.credentials = None
        self.youtube = None
        self.token_file = 'youtube_token.pickle'
        
    def authenticate(self, credentials_path: Optional[str] = None) -> bool:
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not credentials_path:
                        credentials_path = os.getenv('YOUTUBE_CREDENTIALS_PATH', 'client_secret.json')
                    
                    if not os.path.exists(credentials_path):
                        logger.error(f"Credentials not found: {credentials_path}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: list, category_id: str = "22", 
                    privacy_status: str = "public") -> Dict[str, Any]:
        try:
            if not self.youtube:
                if not self.authenticate():
                    return {'success': False, 'error': 'Authentication failed'}
            
            body = {
                'snippet': {
                    'title': title[:100],
                    'description': description[:5000],
                    'tags': tags[:15] if tags else [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/*')
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'status': privacy_status
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_channel_info(self) -> Dict[str, Any]:
        try:
            if not self.youtube:
                if not self.authenticate():
                    return {'success': False, 'error': 'Authentication failed'}
            
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'success': True,
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                }
            
            return {'success': False, 'error': 'No channel found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_connection(self) -> bool:
        try:
            if not self.youtube:
                return self.authenticate()
            result = self.get_channel_info()
            return result.get('success', False)
        except:
            return False
    
    def is_authenticated(self) -> bool:
        return self.youtube is not None and self.credentials is not None
