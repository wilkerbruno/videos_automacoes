import os
import logging
import asyncio
from typing import Dict, List, Optional
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = None
        self.channel_id = None
        self.access_token = None
        self.refresh_token = None
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
    
    async def connect(self, credentials: Dict) -> Dict:
        """Connect to YouTube API"""
        try:
            self.api_key = credentials.get('apiKey')
            self.channel_id = credentials.get('channelId')
            self.access_token = credentials.get('accessToken')  # OAuth token for uploads
            
            # Test connection by getting channel info
            if await self._test_connection():
                return {'success': True, 'message': 'YouTube connected successfully'}
            else:
                return {'success': False, 'error': 'Invalid YouTube credentials or insufficient permissions'}
                
        except Exception as e:
            logger.error(f"YouTube connection error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _test_connection(self) -> bool:
        """Test YouTube API connection"""
        try:
            if not self.api_key or not self.channel_id:
                return False
            
            url = f"{self.base_url}/channels"
            params = {
                'part': 'snippet',
                'id': self.channel_id,
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return len(data.get('items', [])) > 0
                    else:
                        logger.error(f"YouTube API test failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"YouTube connection test error: {e}")
            return False
    
    async def upload_video(self, video_file_path: str, metadata: Dict) -> Dict:
        """Upload video to YouTube"""
        try:
            if not self.access_token:
                return {
                    'success': False, 
                    'error': 'OAuth access token required for video uploads. Please complete OAuth authentication.'
                }
            
            # Prepare video metadata
            video_metadata = {
                'snippet': {
                    'title': metadata.get('title', '')[:100],  # YouTube limit
                    'description': metadata.get('description', '')[:5000],  # YouTube limit
                    'tags': metadata.get('hashtags', [])[:15],  # YouTube limit
                    'categoryId': self._get_category_id(metadata.get('category', 'entertainment')),
                    'defaultLanguage': 'pt',
                    'defaultAudioLanguage': 'pt'
                },
                'status': {
                    'privacyStatus': 'public',  # or 'private', 'unlisted'
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video using resumable upload
            upload_result = await self._resumable_upload(video_file_path, video_metadata)
            
            if upload_result['success']:
                return {
                    'success': True,
                    'platform': 'youtube',
                    'video_id': upload_result['video_id'],
                    'url': f"https://youtube.com/watch?v={upload_result['video_id']}",
                    'message': 'Video uploaded successfully to YouTube'
                }
            else:
                return {
                    'success': False,
                    'error': upload_result.get('error', 'Upload failed')
                }
                
        except Exception as e:
            logger.error(f"YouTube upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _resumable_upload(self, video_file_path: str, metadata: Dict) -> Dict:
        """Perform resumable upload to YouTube"""
        try:
            # Step 1: Initiate resumable upload session
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json; charset=UTF-8',
                'X-Upload-Content-Type': 'video/*'
            }
            
            # Get file size
            file_size = os.path.getsize(video_file_path)
            headers['X-Upload-Content-Length'] = str(file_size)
            
            params = {'uploadType': 'resumable', 'part': 'snippet,status'}
            
            async with aiohttp.ClientSession() as session:
                # Initiate upload
                async with session.post(
                    self.upload_url, 
                    params=params,
                    headers=headers,
                    json=metadata
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"YouTube upload initiation failed: {response.status} - {error_text}")
                        return {'success': False, 'error': f'Upload initiation failed: {error_text}'}
                    
                    upload_url = response.headers.get('Location')
                    if not upload_url:
                        return {'success': False, 'error': 'No upload URL received from YouTube'}
                
                # Step 2: Upload video file
                chunk_size = 8 * 1024 * 1024  # 8MB chunks
                
                with open(video_file_path, 'rb') as video_file:
                    uploaded = 0
                    
                    while uploaded < file_size:
                        chunk_data = video_file.read(chunk_size)
                        if not chunk_data:
                            break
                        
                        chunk_end = min(uploaded + len(chunk_data) - 1, file_size - 1)
                        
                        upload_headers = {
                            'Content-Range': f'bytes {uploaded}-{chunk_end}/{file_size}',
                            'Content-Type': 'video/*'
                        }
                        
                        async with session.put(
                            upload_url,
                            headers=upload_headers,
                            data=chunk_data
                        ) as chunk_response:
                            
                            if chunk_response.status == 200:
                                # Upload complete
                                result = await chunk_response.json()
                                video_id = result.get('id')
                                
                                if video_id:
                                    logger.info(f"YouTube video uploaded successfully: {video_id}")
                                    return {'success': True, 'video_id': video_id}
                                else:
                                    return {'success': False, 'error': 'No video ID returned'}
                            
                            elif chunk_response.status == 308:
                                # Resume incomplete, continue
                                range_header = chunk_response.headers.get('Range', '')
                                if range_header:
                                    uploaded = int(range_header.split('-')[1]) + 1
                                else:
                                    uploaded += len(chunk_data)
                            
                            else:
                                error_text = await chunk_response.text()
                                logger.error(f"YouTube chunk upload failed: {chunk_response.status} - {error_text}")
                                return {'success': False, 'error': f'Chunk upload failed: {error_text}'}
            
            return {'success': False, 'error': 'Upload completed but no success response received'}
            
        except Exception as e:
            logger.error(f"YouTube resumable upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_category_id(self, category: str) -> str:
        """Map category to YouTube category ID"""
        category_mapping = {
            'entretenimento': '24',  # Entertainment
            'educacao': '27',        # Education
            'tecnologia': '28',      # Science & Technology
            'esportes': '17',        # Sports
            'musica': '10',         # Music
            'games': '20',          # Gaming
            'humor': '23',          # Comedy
            'lifestyle': '22',      # People & Blogs
            'noticias': '25',       # News & Politics
            'viagem': '19',         # Travel & Events
            'carros': '2',          # Autos & Vehicles
            'pets': '15'            # Pets & Animals
        }
        return category_mapping.get(category, '24')  # Default to Entertainment
    
    async def get_video_analytics(self, video_id: str) -> Dict:
        """Get analytics for uploaded video"""
        try:
            if not self.api_key:
                return {'error': 'API key required'}
            
            url = f"{self.base_url}/videos"
            params = {
                'part': 'statistics,snippet',
                'id': video_id,
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        
                        if items:
                            stats = items[0].get('statistics', {})
                            return {
                                'views': int(stats.get('viewCount', 0)),
                                'likes': int(stats.get('likeCount', 0)),
                                'comments': int(stats.get('commentCount', 0)),
                                'shares': int(stats.get('shareCount', 0))
                            }
            
            return {'error': 'Video not found or no access'}
            
        except Exception as e:
            logger.error(f"YouTube analytics error: {e}")
            return {'error': str(e)}
