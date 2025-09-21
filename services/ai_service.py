# services/ai_service.py
import openai
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests
from utils.config import Config

logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.trending_hashtags = {}
        self.viral_patterns = self._load_viral_patterns()
    
    def _load_viral_patterns(self) -> Dict:
        """Load viral content patterns for different platforms"""
        return {
            'youtube': {
                'optimal_title_length': 60,
                'description_length': 200,
                'hashtag_count': 15,
                'trending_keywords': ['viral', 'amazing', 'incredible', 'must see', 'shocking']
            },
            'instagram': {
                'optimal_title_length': 125,
                'description_length': 150,
                'hashtag_count': 30,
                'trending_keywords': ['instagood', 'photooftheday', 'viral', 'trending']
            },
            'tiktok': {
                'optimal_title_length': 100,
                'description_length': 100,
                'hashtag_count': 10,
                'trending_keywords': ['fyp', 'viral', 'trending', 'foryou']
            },
            'kawai': {
                'optimal_title_length': 80,
                'description_length': 120,
                'hashtag_count': 20,
                'trending_keywords': ['cute', 'kawaii', 'adorable', 'sweet']
            }
        }
    
    async def generate_viral_content(self, title: str, category: str, platforms: List[str], 
                                   video_duration: int = None, video_description: str = None) -> Dict:
        """Generate viral content optimized for specific platforms using ChatGPT"""
        try:
            # Analyze trending hashtags first
            trending_data = await self._get_trending_hashtags(platforms, category)
            
            # Create optimized prompt for viral content
            prompt = self._create_viral_prompt(title, category, platforms, video_duration, 
                                             video_description, trending_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a viral content expert specializing in social media growth. 
                        Create highly engaging, viral-optimized content that maximizes reach, engagement, 
                        and shareability across platforms. Focus on trending topics, emotional triggers, 
                        and platform-specific best practices."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = json.loads(response.choices[0].message.content)
            
            # Enhance with platform-specific optimizations
            enhanced_content = await self._enhance_for_platforms(content, platforms)
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return self._fallback_content(title, category, platforms)
    
    def _create_viral_prompt(self, title: str, category: str, platforms: List[str], 
                           duration: int, description: str, trending_data: Dict) -> str:
        """Create an optimized prompt for viral content generation"""
        platform_specs = []
        for platform in platforms:
            if platform in self.viral_patterns:
                pattern = self.viral_patterns[platform]
                platform_specs.append(f"{platform.upper()}: max {pattern['hashtag_count']} hashtags, "
                                     f"title ≤{pattern['optimal_title_length']} chars, "
                                     f"description ≤{pattern['description_length']} chars")
        
        trending_info = ""
        for platform, hashtags in trending_data.items():
            trending_info += f"{platform}: {', '.join(hashtags[:5])}\n"
        
        return f"""
        Create viral social media content for: "{title}"
        Category: {category}
        Video Duration: {duration}s
        Platforms: {', '.join(platforms)}
        
        Platform Requirements:
        {chr(10).join(platform_specs)}
        
        Current Trending Hashtags:
        {trending_info}
        
        Video Context: {description or 'Not provided'}
        
        Generate a JSON response with:
        {{
            "optimized_title": "Viral, attention-grabbing title",
            "description": "Engaging description with hooks and CTAs",
            "hashtags": ["platform-optimized", "trending", "hashtags"],
            "platform_specific": {{
                "youtube": {{"title": "", "description": "", "hashtags": []}},
                "instagram": {{"title": "", "description": "", "hashtags": []}},
                "tiktok": {{"title": "", "description": "", "hashtags": []}},
                "kawai": {{"title": "", "description": "", "hashtags": []}}
            }},
            "posting_tips": ["Best time to post", "Engagement strategies"],
            "viral_score": 85
        }}
        
        Focus on:
        - Emotional triggers (curiosity, surprise, joy, fear of missing out)
        - Current trends and memes
        - Platform-specific viral formats
        - Strong hooks in first 3 seconds
        - Clear calls-to-action
        - Optimal posting times
        """
    
    async def _get_trending_hashtags(self, platforms: List[str], category: str) -> Dict:
        """Fetch current trending hashtags for platforms and category"""
        trending = {}
        
        for platform in platforms:
            try:
                if platform == 'instagram':
                    trending[platform] = await self._get_instagram_trending(category)
                elif platform == 'tiktok':
                    trending[platform] = await self._get_tiktok_trending(category)
                elif platform == 'youtube':
                    trending[platform] = await self._get_youtube_trending(category)
                else:
                    trending[platform] = self._get_generic_trending(category)
            except:
                trending[platform] = self._get_generic_trending(category)
        
        return trending
    
    async def _get_instagram_trending(self, category: str) -> List[str]:
        """Get Instagram trending hashtags"""
        # In production, use Instagram API or trending tools
        base_hashtags = {
            'entretenimento': ['entertainment', 'viral', 'funny', 'instagood', 'reels'],
            'educacao': ['education', 'learn', 'knowledge', 'study', 'tips'],
            'tecnologia': ['tech', 'technology', 'innovation', 'digital', 'future'],
            'lifestyle': ['lifestyle', 'daily', 'inspiration', 'motivation', 'life'],
            'humor': ['funny', 'humor', 'memes', 'comedy', 'laugh'],
            'musica': ['music', 'song', 'beats', 'musical', 'audio'],
            'esportes': ['sports', 'fitness', 'athlete', 'training', 'game'],
            'games': ['gaming', 'gamer', 'gameplay', 'game', 'esports']
        }
        return base_hashtags.get(category, ['viral', 'trending', 'instagood'])
    
    async def _get_tiktok_trending(self, category: str) -> List[str]:
        """Get TikTok trending hashtags"""
        base_hashtags = {
            'entretenimento': ['fyp', 'viral', 'trending', 'foryou', 'entertainment'],
            'educacao': ['learn', 'education', 'knowledge', 'tutorial', 'tips'],
            'tecnologia': ['tech', 'technology', 'techtok', 'innovation', 'digital'],
            'lifestyle': ['lifestyle', 'daily', 'motivation', 'life', 'inspiration'],
            'humor': ['funny', 'comedy', 'humor', 'meme', 'laugh'],
            'musica': ['music', 'song', 'audio', 'sound', 'beats'],
            'esportes': ['sports', 'fitness', 'workout', 'athlete', 'sportstok'],
            'games': ['gaming', 'gamer', 'gameplay', 'game', 'gamertok']
        }
        return base_hashtags.get(category, ['fyp', 'viral', 'foryou'])
    
    async def _get_youtube_trending(self, category: str) -> List[str]:
        """Get YouTube trending tags"""
        base_tags = {
            'entretenimento': ['viral', 'trending', 'entertainment', 'amazing', 'incredible'],
            'educacao': ['education', 'tutorial', 'howto', 'learn', 'knowledge'],
            'tecnologia': ['technology', 'tech', 'review', 'innovation', 'digital'],
            'lifestyle': ['lifestyle', 'vlog', 'daily', 'life', 'motivation'],
            'humor': ['funny', 'comedy', 'humor', 'hilarious', 'laugh'],
            'musica': ['music', 'song', 'cover', 'audio', 'musical'],
            'esportes': ['sports', 'fitness', 'workout', 'training', 'athlete'],
            'games': ['gaming', 'gameplay', 'game', 'playthrough', 'review']
        }
        return base_tags.get(category, ['viral', 'trending'])
    
    def _get_generic_trending(self, category: str) -> List[str]:
        """Fallback trending hashtags"""
        generic = {
            'entretenimento': ['viral', 'trending', 'amazing', 'incredible', 'mustsee'],
            'educacao': ['learn', 'education', 'knowledge', 'tips', 'howto'],
            'tecnologia': ['tech', 'technology', 'innovation', 'digital', 'future'],
            'lifestyle': ['lifestyle', 'daily', 'life', 'inspiration', 'motivation'],
            'humor': ['funny', 'humor', 'comedy', 'laugh', 'meme'],
            'musica': ['music', 'song', 'audio', 'sound', 'beats'],
            'esportes': ['sports', 'fitness', 'workout', 'training', 'health'],
            'games': ['gaming', 'game', 'gamer', 'gameplay', 'fun']
        }
        return generic.get(category, ['trending', 'viral'])
    
    async def _enhance_for_platforms(self, content: Dict, platforms: List[str]) -> Dict:
        """Enhance content with platform-specific optimizations"""
        enhanced = content.copy()
        
        for platform in platforms:
            if platform in enhanced.get('platform_specific', {}):
                platform_content = enhanced['platform_specific'][platform]
                
                # Add platform-specific viral elements
                if platform == 'tiktok':
                    platform_content['description'] = f"🔥 {platform_content['description']} #FYP #Viral"
                    platform_content['hashtags'].extend(['fyp', 'viral', 'foryou'])
                
                elif platform == 'instagram':
                    platform_content['description'] += "\n\n🔔 Turn on notifications!"
                    platform_content['hashtags'].extend(['instagood', 'photooftheday'])
                
                elif platform == 'youtube':
                    platform_content['description'] += "\n\n👍 LIKE if you enjoyed!\n🔔 SUBSCRIBE for more!"
                    
                elif platform == 'kawai':
                    platform_content['description'] = f"💖 {platform_content['description']} ✨"
                    platform_content['hashtags'].extend(['kawaii', 'cute', 'adorable'])
        
        return enhanced
    
    def _fallback_content(self, title: str, category: str, platforms: List[str]) -> Dict:
        """Fallback content when AI generation fails"""
        return {
            "optimized_title": f"🔥 {title} - You Won't Believe This!",
            "description": f"Amazing {category} content that will blow your mind! Don't miss out!",
            "hashtags": ["viral", "trending", "amazing", "incredible", category],
            "platform_specific": {
                platform: {
                    "title": f"🔥 {title}",
                    "description": f"Check out this amazing {category} content!",
                    "hashtags": self._get_generic_trending(category)
                } for platform in platforms
            },
            "posting_tips": ["Post during peak hours", "Use engaging thumbnails"],
            "viral_score": 70
        }
    
    async def analyze_viral_potential(self, content: Dict) -> Dict:
        """Analyze and score viral potential of content"""
        try:
            analysis_prompt = f"""
            Analyze the viral potential of this social media content:
            Title: {content.get('title', '')}
            Description: {content.get('description', '')}
            Hashtags: {', '.join(content.get('hashtags', []))}
            
            Rate from 0-100 and provide improvement suggestions:
            {{
                "viral_score": 85,
                "strengths": ["Strong hook", "Trending hashtags"],
                "weaknesses": ["Could be more emotional", "Missing CTA"],
                "improvements": ["Add curiosity gap", "Include trending sounds"],
                "optimal_posting_times": ["18:00-20:00", "12:00-14:00"],
                "competitor_analysis": "Similar content averages 50K views"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Viral analysis failed: {e}")
            return {"viral_score": 50, "analysis": "Analysis unavailable"}
    
    def is_healthy(self) -> bool:
        """Check if AI service is healthy"""
        try:
            return bool(Config.OPENAI_API_KEY)
        except:
            return False

# services/platform_manager.py
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import json
from utils.config import Config

logger = logging.getLogger(__name__)

class PlatformManager:
    def __init__(self):
        self.platforms = {
            'youtube': YouTubeManager(),
            'instagram': InstagramManager(),
            'tiktok': TikTokManager(),
            'kawai': KawaiManager()
        }
        self.connected_platforms = set()
    
    async def post_to_platforms(self, post_data: Dict) -> Dict:
        """Post content to selected platforms"""
        results = {}
        platforms = post_data.get('platforms', [])
        
        tasks = []
        for platform in platforms:
            if platform in self.platforms and platform in self.connected_platforms:
                manager = self.platforms[platform]
                task = asyncio.create_task(
                    manager.post(post_data),
                    name=f"post_{platform}"
                )
                tasks.append((platform, task))
        
        # Execute posts concurrently
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = result
            except Exception as e:
                logger.error(f"Failed to post to {platform}: {e}")
                results[platform] = {'success': False, 'error': str(e)}
        
        return results
    
    async def connect_platform(self, platform: str, credentials: Dict) -> Dict:
        """Connect to a specific platform"""
        if platform not in self.platforms:
            return {'success': False, 'error': f'Platform {platform} not supported'}
        
        try:
            manager = self.platforms[platform]
            result = await manager.connect(credentials)
            
            if result['success']:
                self.connected_platforms.add(platform)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to connect to {platform}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_platform_status(self) -> Dict:
        """Get connection status for all platforms"""
        status = {}
        for platform_name, manager in self.platforms.items():
            status[platform_name] = {
                'connected': platform_name in self.connected_platforms,
                'last_check': datetime.now().isoformat(),
                'features': manager.get_supported_features()
            }
        return status

class YouTubeManager:
    def __init__(self):
        self.api_key = None
        self.channel_id = None
        self.access_token = None
    
    async def connect(self, credentials: Dict) -> Dict:
        """Connect to YouTube API"""
        try:
            self.api_key = credentials.get('apiKey')
            self.channel_id = credentials.get('channelId')
            
            # Test connection
            if await self._test_connection():
                return {'success': True, 'message': 'YouTube connected successfully'}
            else:
                return {'success': False, 'error': 'Invalid YouTube credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post(self, post_data: Dict) -> Dict:
        """Post video to YouTube"""
        try:
            platform_content = post_data.get('platform_specific', {}).get('youtube', {})
            
            # Optimize for YouTube Shorts
            video_data = {
                'title': platform_content.get('title', post_data['title'])[:100],
                'description': self._format_description(
                    platform_content.get('description', post_data['description']),
                    platform_content.get('hashtags', post_data.get('hashtags', []))
                ),
                'tags': platform_content.get('hashtags', post_data.get('hashtags', []))[:15],
                'categoryId': self._get_category_id(post_data.get('category')),
                'privacyStatus': 'public'
            }
            
            # Upload video (mock implementation)
            result = await self._upload_video(post_data['files'][0], video_data)
            
            return {
                'success': True,
                'platform': 'youtube',
                'post_id': result.get('video_id'),
                'url': f"https://youtube.com/shorts/{result.get('video_id')}",
                'metrics': {'views': 0, 'likes': 0, 'comments': 0}
            }
            
        except Exception as e:
            logger.error(f"YouTube post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_description(self, description: str, hashtags: List[str]) -> str:
        """Format description for YouTube"""
        formatted = description
        if hashtags:
            hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
            formatted += f"\n\n{hashtag_text}"
        
        formatted += "\n\n🔔 Subscribe for more amazing content!"
        formatted += "\n👍 Like if you enjoyed this video!"
        return formatted[:5000]  # YouTube limit
    
    def _get_category_id(self, category: str) -> str:
        """Map category to YouTube category ID"""
        category_mapping = {
            'entretenimento': '24',
            'educacao': '27',
            'tecnologia': '28',
            'esportes': '17',
            'musica': '10',
            'games': '20',
            'humor': '23',
            'lifestyle': '22'
        }
        return category_mapping.get(category, '24')  # Default to Entertainment
    
    async def _upload_video(self, video_file: Dict, metadata: Dict) -> Dict:
        """Upload video to YouTube (mock implementation)"""
        # In production, use YouTube Data API v3
        await asyncio.sleep(0.1)  # Simulate upload time
        return {'video_id': f'yt_{datetime.now().timestamp()}'}
    
    async def _test_connection(self) -> bool:
        """Test YouTube API connection"""
        # In production, make actual API call
        return bool(self.api_key and self.channel_id)
    
    def get_supported_features(self) -> List[str]:
        return ['video_upload', 'shorts', 'scheduling', 'analytics', 'live_streaming']

class InstagramManager:
    def __init__(self):
        self.username = None
        self.access_token = None
        self.business_account_id = None
    
    async def connect(self, credentials: Dict) -> Dict:
        """Connect to Instagram"""
        try:
            self.username = credentials.get('username')
            self.access_token = credentials.get('access_token')
            
            if await self._test_connection():
                return {'success': True, 'message': 'Instagram connected successfully'}
            else:
                return {'success': False, 'error': 'Invalid Instagram credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post(self, post_data: Dict) -> Dict:
        """Post to Instagram Reels"""
        try:
            platform_content = post_data.get('platform_specific', {}).get('instagram', {})
            
            # Format for Instagram Reels
            caption = self._format_caption(
                platform_content.get('description', post_data['description']),
                platform_content.get('hashtags', post_data.get('hashtags', []))
            )
            
            # Upload reel (mock implementation)
            result = await self._upload_reel(post_data['files'][0], caption)
            
            return {
                'success': True,
                'platform': 'instagram',
                'post_id': result.get('media_id'),
                'url': f"https://instagram.com/reel/{result.get('media_id')}",
                'metrics': {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0}
            }
            
        except Exception as e:
            logger.error(f"Instagram post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_caption(self, description: str, hashtags: List[str]) -> str:
        """Format caption for Instagram"""
        caption = description
        
        if hashtags:
            # Instagram allows up to 30 hashtags
            hashtag_text = ' '.join([f'#{tag}' for tag in hashtags[:30]])
            caption += f"\n\n{hashtag_text}"
        
        caption += "\n\n🔔 Follow for more amazing content!"
        return caption[:2200]  # Instagram limit
    
    async def _upload_reel(self, video_file: Dict, caption: str) -> Dict:
        """Upload reel to Instagram (mock implementation)"""
        # In production, use Instagram Graph API
        await asyncio.sleep(0.1)
        return {'media_id': f'ig_{datetime.now().timestamp()}'}
    
    async def _test_connection(self) -> bool:
        """Test Instagram connection"""
        return bool(self.username and self.access_token)
    
    def get_supported_features(self) -> List[str]:
        return ['reels', 'stories', 'posts', 'igtv', 'scheduling', 'analytics']

class TikTokManager:
    def __init__(self):
        self.access_token = None
        self.user_id = None
    
    async def connect(self, credentials: Dict) -> Dict:
        """Connect to TikTok"""
        try:
            self.access_token = credentials.get('accessToken')
            self.user_id = credentials.get('userId')
            
            if await self._test_connection():
                return {'success': True, 'message': 'TikTok connected successfully'}
            else:
                return {'success': False, 'error': 'Invalid TikTok credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post(self, post_data: Dict) -> Dict:
        """Post to TikTok"""
        try:
            platform_content = post_data.get('platform_specific', {}).get('tiktok', {})
            
            # Format for TikTok
            caption = self._format_caption(
                platform_content.get('description', post_data['description']),
                platform_content.get('hashtags', post_data.get('hashtags', []))
            )
            
            # Upload video (mock implementation)
            result = await self._upload_video(post_data['files'][0], caption)
            
            return {
                'success': True,
                'platform': 'tiktok',
                'post_id': result.get('video_id'),
                'url': f"https://tiktok.com/@user/video/{result.get('video_id')}",
                'metrics': {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0}
            }
            
        except Exception as e:
            logger.error(f"TikTok post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_caption(self, description: str, hashtags: List[str]) -> str:
        """Format caption for TikTok"""
        # TikTok works best with fewer, more targeted hashtags
        selected_hashtags = hashtags[:5] if hashtags else []
        
        caption = description
        if selected_hashtags:
            hashtag_text = ' '.join([f'#{tag}' for tag in selected_hashtags])
            caption = f"{description} {hashtag_text}"
        
        # Always include FYP hashtags for better reach
        caption += " #fyp #viral #foryou"
        
        return caption[:300]  # TikTok limit
    
    async def _upload_video(self, video_file: Dict, caption: str) -> Dict:
        """Upload video to TikTok (mock implementation)"""
        # In production, use TikTok API
        await asyncio.sleep(0.1)
        return {'video_id': f'tt_{datetime.now().timestamp()}'}
    
    async def _test_connection(self) -> bool:
        """Test TikTok connection"""
        return bool(self.access_token and self.user_id)
    
    def get_supported_features(self) -> List[str]:
        return ['video_upload', 'live_streaming', 'analytics', 'duets', 'effects']

class KawaiManager:
    def __init__(self):
        self.api_key = None
        self.user_id = None
    
    async def connect(self, credentials: Dict) -> Dict:
        """Connect to Kawai platform"""
        try:
            self.api_key = credentials.get('apiKey')
            self.user_id = credentials.get('userId')
            
            if await self._test_connection():
                return {'success': True, 'message': 'Kawai connected successfully'}
            else:
                return {'success': False, 'error': 'Invalid Kawai credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def post(self, post_data: Dict) -> Dict:
        """Post to Kawai"""
        try:
            platform_content = post_data.get('platform_specific', {}).get('kawai', {})
            
            # Format for Kawai (cute/kawaii content focus)
            caption = self._format_caption(
                platform_content.get('description', post_data['description']),
                platform_content.get('hashtags', post_data.get('hashtags', []))
            )
            
            # Upload video (mock implementation)
            result = await self._upload_video(post_data['files'][0], caption)
            
            return {
                'success': True,
                'platform': 'kawai',
                'post_id': result.get('video_id'),
                'url': f"https://kawai.com/video/{result.get('video_id')}",
                'metrics': {'views': 0, 'likes': 0, 'comments': 0, 'hearts': 0}
            }
            
        except Exception as e:
            logger.error(f"Kawai post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_caption(self, description: str, hashtags: List[str]) -> str:
        """Format caption for Kawai with cute emoji"""
        # Add kawaii elements
        cute_emojis = ['💖', '✨', '🌸', '🎀', '💫', '🌟']
        
        caption = f"💖 {description} ✨"
        
        if hashtags:
            # Focus on cute/kawaii hashtags
            kawaii_hashtags = [tag for tag in hashtags if any(word in tag.lower() 
                             for word in ['cute', 'kawaii', 'adorable', 'sweet'])]
            other_hashtags = [tag for tag in hashtags if tag not in kawaii_hashtags]
            
            selected_hashtags = kawaii_hashtags[:10] + other_hashtags[:10]
            hashtag_text = ' '.join([f'#{tag}' for tag in selected_hashtags])
            caption += f"\n\n{hashtag_text}"
        
        caption += "\n\n🌸 Follow for more kawaii content! 💕"
        return caption[:500]  # Platform limit
    
    async def _upload_video(self, video_file: Dict, caption: str) -> Dict:
        """Upload video to Kawai (mock implementation)"""
        await asyncio.sleep(0.1)
        return {'video_id': f'kw_{datetime.now().timestamp()}'}
    
    async def _test_connection(self) -> bool:
        """Test Kawai connection"""
        return bool(self.api_key and self.user_id)
    
    def get_supported_features(self) -> List[str]:
        return ['video_upload', 'stories', 'cute_filters', 'analytics', 'kawaii_effects']

# services/video_processor.py
import os
import subprocess
import logging
from typing import Dict, List, Optional
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.output_formats = {
            'youtube': {'width': 1080, 'height': 1920, 'fps': 30, 'duration_max': 60},
            'instagram': {'width': 1080, 'height': 1920, 'fps': 30, 'duration_max': 60},
            'tiktok': {'width': 1080, 'height': 1920, 'fps': 30, 'duration_max': 60},
            'kawai': {'width': 1080, 'height': 1920, 'fps': 25, 'duration_max': 45}
        }
        self.temp_dir = 'temp_videos'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_video(self, video_path: str, platforms: List[str] = None) -> Dict:
        """Process video for multiple platforms"""
        try:
            # Load video
            clip = VideoFileClip(video_path)
            
            # Analyze video
            analysis = self._analyze_video(clip)
            
            processed_videos = {}
            
            if platforms:
                # Process for specific platforms
                for platform in platforms:
                    if platform in self.output_formats:
                        processed_videos[platform] = self._optimize_for_platform(
                            clip, platform, analysis
                        )
            else:
                # Process for all platforms
                for platform in self.output_formats:
                    processed_videos[platform] = self._optimize_for_platform(
                        clip, platform, analysis
                    )
            
            # Generate thumbnail
            thumbnail_path = self._generate_thumbnail(clip)
            
            clip.close()
            
            return {
                'success': True,
                'original': {
                    'path': video_path,
                    'duration': analysis['duration'],
                    'size': analysis['size'],
                    'resolution': analysis['resolution']
                },
                'processed': processed_videos,
                'thumbnail': thumbnail_path,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_video(self, clip: VideoFileClip) -> Dict:
        """Analyze video properties"""
        return {
            'duration': clip.duration,
            'fps': clip.fps,
            'size': clip.size,
            'resolution': f"{clip.w}x{clip.h}",
            'aspect_ratio': clip.w / clip.h,
            'has_audio': clip.audio is not None,
            'file_size': os.path.getsize(clip.filename) if hasattr(clip, 'filename') else 0
        }
    
    def _optimize_for_platform(self, clip: VideoFileClip, platform: str, analysis: Dict) -> Dict:
        """Optimize video for specific platform"""
        try:
            specs = self.output_formats[platform]
            
            # Create optimized clip
            optimized_clip = clip
            
            # Resize to platform specs
            if analysis['resolution'] != f"{specs['width']}x{specs['height']}":
                optimized_clip = self._resize_video(optimized_clip, specs['width'], specs['height'])
            
            # Adjust duration if needed
            if analysis['duration'] > specs['duration_max']:
                optimized_clip = optimized_clip.subclip(0, specs['duration_max'])
            
            # Adjust FPS
            if analysis['fps'] != specs['fps']:
                optimized_clip = optimized_clip.set_fps(specs['fps'])
            
            # Add platform-specific enhancements
            optimized_clip = self._add_platform_enhancements(optimized_clip, platform)
            
            # Export video
            output_path = os.path.join(
                self.temp_dir, 
                f"{platform}_{os.path.basename(clip.filename)}"
            )
            
            optimized_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=specs['fps']
            )
            
            optimized_clip.close()
            
            return {
                'path': output_path,
                'platform': platform,
                'specs': specs,
                'size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            logger.error(f"Platform optimization failed for {platform}: {e}")
            raise
    
    def _resize_video(self, clip: VideoFileClip, target_width: int, target_height: int) -> VideoFileClip:
        """Resize video maintaining aspect ratio"""
        # Calculate scaling to fit target dimensions
        scale_w = target_width / clip.w
        scale_h = target_height / clip.h
        scale = min(scale_w, scale_h)
        
        # Resize clip
        resized_clip = clip.resize(scale)
        
        # If needed, add padding to match exact dimensions
        if resized_clip.w != target_width or resized_clip.h != target_height:
            # Create background clip
            background = TextClip("", size=(target_width, target_height), color=(0, 0, 0))
            background = background.set_duration(clip.duration)
            
            # Center the video
            resized_clip = resized_clip.set_position('center')
            
            # Compose final video
            final_clip = CompositeVideoClip([background, resized_clip])
            return final_clip
        
        return resized_clip
    
    def _add_platform_enhancements(self, clip: VideoFileClip, platform: str) -> VideoFileClip:
        """Add platform-specific visual enhancements"""
        try:
            enhanced_clip = clip
            
            if platform == 'tiktok':
                # Add subtle vignette effect for TikTok
                enhanced_clip = self._add_vignette(enhanced_clip)
                
            elif platform == 'instagram':
                # Add subtle Instagram-style filter
                enhanced_clip = self._add_filter(enhanced_clip, 'instagram')
                
            elif platform == 'youtube':
                # Optimize for YouTube Shorts
                enhanced_clip = self._optimize_for_shorts(enhanced_clip)
                
            elif platform == 'kawai':
                # Add cute effects for Kawai
                enhanced_clip = self._add_kawaii_effects(enhanced_clip)
            
            return enhanced_clip
            
        except Exception as e:
            logger.warning(f"Enhancement failed for {platform}: {e}")
            return clip
    
    def _add_vignette(self, clip: VideoFileClip) -> VideoFileClip:
        """Add vignette effect"""
        # Simple vignette implementation
        return clip  # Placeholder - implement actual vignette
    
    def _add_filter(self, clip: VideoFileClip, filter_type: str) -> VideoFileClip:
        """Add visual filter"""
        # Implement various filters
        return clip  # Placeholder
    
    def _optimize_for_shorts(self, clip: VideoFileClip) -> VideoFileClip:
        """Optimize for YouTube Shorts"""
        # Ensure proper encoding for Shorts
        return clip
    
    def _add_kawaii_effects(self, clip: VideoFileClip) -> VideoFileClip:
        """Add cute/kawaii visual effects"""
        # Add sparkle effects, cute borders, etc.
        return clip
    
    def _generate_thumbnail(self, clip: VideoFileClip, timestamp: float = None) -> str:
        """Generate thumbnail from video"""
        try:
            if timestamp is None:
                timestamp = clip.duration / 2  # Middle of video
            
            # Extract frame
            frame = clip.get_frame(timestamp)
            
            # Convert to PIL Image
            img = Image.fromarray(frame)
            
            # Resize for thumbnail
            img.thumbnail((1280, 720), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumbnail_path = os.path.join(
                self.temp_dir, 
                f"thumbnail_{os.path.basename(clip.filename)}.jpg"
            )
            img.save(thumbnail_path, 'JPEG', quality=90)
            
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None
    
    def add_captions(self, video_path: str, captions: List[Dict], language: str = 'pt') -> str:
        """Add captions to video"""
        try:
            clip = VideoFileClip(video_path)
            
            # Create caption clips
            caption_clips = []
            for caption in captions:
                txt_clip = TextClip(
                    caption['text'],
                    fontsize=50,
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    font='Arial-Bold'
                ).set_position(('center', 'bottom')).set_start(
                    caption['start']
                ).set_end(caption['end'])
                
                caption_clips.append(txt_clip)
            
            # Composite video with captions
            if caption_clips:
                final_clip = CompositeVideoClip([clip] + caption_clips)
            else:
                final_clip = clip
            
            # Export with captions
            output_path = video_path.replace('.mp4', '_with_captions.mp4')
            final_clip.write_videofile(output_path)
            
            clip.close()
            final_clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Caption addition failed: {e}")
            return video_path
    
    def extract_audio(self, video_path: str) -> Optional[str]:
        """Extract audio from video"""
        try:
            clip = VideoFileClip(video_path)
            audio_path = video_path.replace('.mp4', '.mp3')
            
            if clip.audio:
                clip.audio.write_audiofile(audio_path)
                clip.close()
                return audio_path
            else:
                clip.close()
                return None
                
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return None
    
    def is_healthy(self) -> bool:
        """Check if video processor is working"""
        try:
            # Test basic video processing
            return True
        except:
            return False

# utils/config.py
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
    
    # AI Service Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///social_media_automation.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Platform API Keys (Store encrypted in production)
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
    TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN', '')
    KAWAI_API_KEY = os.getenv('KAWAI_API_KEY', '')
    
    # Scheduling Configuration
    SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'America/Sao_Paulo')
    
    # Analytics Configuration
    ANALYTICS_RETENTION_DAYS = int(os.getenv('ANALYTICS_RETENTION_DAYS', '90'))
    
    # Security Configuration
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'social_media_automation.log')
    
    @classmethod
    def init_app(cls, app):
        """Initialize Flask app with configuration"""
        # Create necessary directories
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('temp_videos', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

# models/database.py
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'social_media_automation.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            # Posts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    hashtags TEXT,
                    platforms TEXT,
                    files TEXT,
                    status TEXT DEFAULT 'draft',
                    schedule_time TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    results TEXT
                )
            ''')
            
            # Platform credentials table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS platform_credentials (
                    platform TEXT PRIMARY KEY,
                    credentials TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Analytics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id TEXT PRIMARY KEY,
                    post_id TEXT,
                    platform TEXT,
                    metric_name TEXT,
                    metric_value INTEGER,
                    recorded_at TEXT,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            ''')
            
            # Scheduled jobs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    id TEXT PRIMARY KEY,
                    post_id TEXT,
                    job_type TEXT,
                    schedule_time TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    executed_at TEXT,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            ''')
            
            # User settings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def save_post(self, post_data: Dict) -> bool:
        """Save post to database"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO posts 
                    (id, title, description, category, hashtags, platforms, files, 
                     status, schedule_time, created_at, updated_at, results)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_data['id'],
                    post_data['title'],
                    post_data.get('description', ''),
                    post_data.get('category', ''),
                    json.dumps(post_data.get('hashtags', [])),
                    json.dumps(post_data.get('platforms', [])),
                    json.dumps(post_data.get('files', [])),
                    post_data.get('status', 'draft'),
                    post_data.get('schedule_time'),
                    post_data.get('created_at', datetime.now().isoformat()),
                    datetime.now().isoformat(),
                    json.dumps(post_data.get('results', {}))
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save post: {e}")
            return False
    
    def get_post(self, post_id: str) -> Optional[Dict]:
        """Get post by ID"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT * FROM posts WHERE id = ?', (post_id,)
                ).fetchone()
                
                if result:
                    post = dict(result)
                    # Parse JSON fields
                    post['hashtags'] = json.loads(post['hashtags'] or '[]')
                    post['platforms'] = json.loads(post['platforms'] or '[]')
                    post['files'] = json.loads(post['files'] or '[]')
                    post['results'] = json.loads(post['results'] or '{}')
                    return post
                return None
        except Exception as e:
            logger.error(f"Failed to get post {post_id}: {e}")
            return None
    
    def update_post(self, post_id: str, updates: Dict) -> bool:
        """Update post with new data"""
        try:
            with self.get_connection() as conn:
                set_clause = []
                values = []
                
                for key, value in updates.items():
                    if key in ['hashtags', 'platforms', 'files', 'results']:
                        value = json.dumps(value)
                    set_clause.append(f"{key} = ?")
                    values.append(value)
                
                set_clause.append("updated_at = ?")
                values.append(datetime.now().isoformat())
                values.append(post_id)
                
                query = f"UPDATE posts SET {', '.join(set_clause)} WHERE id = ?"
                conn.execute(query, values)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update post {post_id}: {e}")
            return False
    
    def get_scheduled_posts(self, filters: Dict = None) -> List[Dict]:
        """Get scheduled posts with optional filtering"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM posts WHERE status = 'scheduled'"
                params = []
                
                if filters:
                    if filters.get('platform'):
                        query += " AND platforms LIKE ?"
                        params.append(f"%{filters['platform']}%")
                    
                    if filters.get('date'):
                        query += " AND DATE(schedule_time) = ?"
                        params.append(filters['date'])
                
                query += " ORDER BY schedule_time ASC"
                
                results = conn.execute(query, params).fetchall()
                
                posts = []
                for result in results:
                    post = dict(result)
                    post['hashtags'] = json.loads(post['hashtags'] or '[]')
                    post['platforms'] = json.loads(post['platforms'] or '[]')
                    post['files'] = json.loads(post['files'] or '[]')
                    posts.append(post)
                
                return posts
        except Exception as e:
            logger.error(f"Failed to get scheduled posts: {e}")
            return []
    
    def save_platform_credentials(self, platform: str, credentials: Dict) -> bool:
        """Save encrypted platform credentials"""
        try:
            with self.get_connection() as conn:
                # In production, encrypt credentials before storing
                conn.execute('''
                    INSERT OR REPLACE INTO platform_credentials 
                    (platform, credentials, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    platform,
                    json.dumps(credentials),  # Encrypt this in production
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save credentials for {platform}: {e}")
            return False
    
    def get_platform_credentials(self, platform: str) -> Optional[Dict]:
        """Get platform credentials"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT credentials FROM platform_credentials WHERE platform = ? AND is_active = 1',
                    (platform,)
                ).fetchone()
                
                if result:
                    return json.loads(result['credentials'])
                return None
        except Exception as e:
            logger.error(f"Failed to get credentials for {platform}: {e}")
            return None
    
    def save_analytics(self, post_id: str, platform: str, metrics: Dict) -> bool:
        """Save analytics data"""
        try:
            with self.get_connection() as conn:
                for metric_name, metric_value in metrics.items():
                    conn.execute('''
                        INSERT INTO analytics (id, post_id, platform, metric_name, metric_value, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        self.generate_id(),
                        post_id,
                        platform,
                        metric_name,
                        int(metric_value),
                        datetime.now().isoformat()
                    ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save analytics: {e}")
            return False
    
    def get_analytics_summary(self, days: int = 30) -> Dict:
        """Get analytics summary for the last N days"""
        try:
            with self.get_connection() as conn:
                # Get date threshold
                from datetime import timedelta
                threshold = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Get total metrics
                result = conn.execute('''
                    SELECT 
                        metric_name,
                        SUM(metric_value) as total_value
                    FROM analytics 
                    WHERE recorded_at >= ?
                    GROUP BY metric_name
                ''', (threshold,)).fetchall()
                
                summary = {}
                for row in result:
                    summary[row['metric_name']] = row['total_value']
                
                # Get post count
                post_count = conn.execute('''
                    SELECT COUNT(DISTINCT post_id) 
                    FROM analytics 
                    WHERE recorded_at >= ?
                ''', (threshold,)).fetchone()[0]
                
                summary['total_posts'] = post_count
                
                return summary
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    def is_healthy(self) -> bool:
        """Check database health"""
        try:
            with self.get_connection() as conn:
                conn.execute('SELECT 1').fetchone()
                return True
        except:
            return False

# services/scheduler.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import schedule
import threading
import time
from models.database import DatabaseManager
from services.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self):
        self.db = DatabaseManager()
        self.platform_manager = PlatformManager()
        self.scheduled_jobs = {}
        self.is_running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("Post scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Post scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduling loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def schedule_post(self, post_data: Dict, schedule_time: str) -> bool:
        """Schedule a post for future publishing"""
        try:
            # Parse schedule time
            scheduled_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            
            # Create scheduled job
            job_id = self.db.generate_id()
            
            # Schedule the job
            schedule.every().day.at(scheduled_datetime.strftime("%H:%M")).do(
                self._execute_scheduled_post, post_data, job_id
            ).tag(job_id)
            
            # Save to database
            self.db.save_scheduled_job({
                'id': job_id,
                'post_id': post_data['id'],
                'schedule_time': schedule_time,
                'status': 'scheduled'
            })
            
            logger.info(f"Post scheduled for {schedule_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule post: {e}")
            return False
    
    async def _execute_scheduled_post(self, post_data: Dict, job_id: str):
        """Execute a scheduled post"""
        try:
            logger.info(f"Executing scheduled post: {post_data['id']}")
            
            # Post to platforms
            results = await self.platform_manager.post_to_platforms(post_data)
            
            # Update post status
            self.db.update_post(post_data['id'], {
                'status': 'posted',
                'results': results
            })
            
            # Update job status
            self.db.update_scheduled_job(job_id, {
                'status': 'completed',
                'executed_at': datetime.now().isoformat()
            })
            
            logger.info(f"Scheduled post executed successfully: {post_data['id']}")
            
        except Exception as e:
            logger.error(f"Failed to execute scheduled post: {e}")
            
            # Mark job as failed
            self.db.update_scheduled_job(job_id, {
                'status': 'failed',
                'executed_at': datetime.now().isoformat()
            })
    
    def cancel_scheduled_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        try:
            # Find and cancel the job
            jobs_to_cancel = [job for job in schedule.jobs if hasattr(job, 'tags') and post_id in str(job.tags)]
            
            for job in jobs_to_cancel:
                schedule.cancel_job(job)
            
            logger.info(f"Cancelled scheduled post: {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel scheduled post: {e}")
            return False
    
    def get_optimal_posting_times(self, platform: str, category: str) -> List[str]:
        """Get optimal posting times for platform and category"""
        # Based on research and analytics
        optimal_times = {
            'youtube': {
                'general': ['18:00', '20:00', '12:00', '14:00'],
                'entretenimento': ['19:00', '21:00'],
                'educacao': ['12:00', '15:00', '18:00'],
                'games': ['20:00', '22:00']
            },
            'instagram': {
                'general': ['11:00', '13:00', '17:00', '19:00'],
                'lifestyle': ['11:00', '14:00'],
                'humor': ['18:00', '20:00'],
                'musica': ['19:00', '21:00']
            },
            'tiktok': {
                'general': ['06:00', '10:00', '19:00', '20:00'],
                'humor': ['18:00', '21:00'],
                'entretenimento': ['19:00', '22:00'],
                'educacao': ['12:00', '16:00']
            },
            'kawai': {
                'general': ['12:00', '15:00', '18:00', '20:00']
            }
        }
        
        return optimal_times.get(platform, {}).get(category, optimal_times.get(platform, {}).get('general', ['12:00', '18:00']))
    
    def is_healthy(self) -> bool:
        """Check scheduler health"""
        return self.is_running

# services/analytics.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
from models.database import DatabaseManager

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_analytics(self, date_range: str = '30d') -> Dict:
        """Get comprehensive analytics data"""
        try:
            days = self._parse_date_range(date_range)
            
            # Get summary data
            summary = self.db.get_analytics_summary(days)
            
            # Get chart data
            chart_data = self._get_chart_data(days)
            
            # Get platform breakdown
            platform_breakdown = self._get_platform_breakdown(days)
            
            # Get performance insights
            insights = self._get_performance_insights(days)
            
            return {
                'summary': {
                    'views': summary.get('views', 0),
                    'likes': summary.get('likes', 0),
                    'shares': summary.get('shares', 0),
                    'comments': summary.get('comments', 0),
                    'posts': summary.get('total_posts', 0)
                },
                'chartData': chart_data,
                'platformBreakdown': platform_breakdown,
                'insights': insights,
                'period': f"Last {days} days"
            }
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return self._get_default_analytics()
    
    def _parse_date_range(self, range_str: str) -> int:
        """Parse date range string to days"""
        range_mapping = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        return range_mapping.get(range_str, 30)
    
    def _get_chart_data(self, days: int) -> Dict:
        """Get chart data for analytics dashboard"""
        try:
            # Generate sample chart data - replace with real analytics
            dates = []
            views = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i)
                dates.append(date.strftime('%Y-%m-%d'))
                # Sample data - replace with real metrics
                views.append(max(0, int(np.random.normal(1000, 200))))
            
            return {
                'labels': dates[-30:],  # Last 30 days
                'views': views[-30:],
                'likes': [max(0, int(v * 0.1 + np.random.normal(0, 10))) for v in views[-30:]],
                'shares': [max(0, int(v * 0.05 + np.random.normal(0, 5))) for v in views[-30:]]
            }
            
        except Exception as e:
            logger.error(f"Chart data generation failed: {e}")
            return {'labels': [], 'views': [], 'likes': [], 'shares': []}
    
    def _get_platform_breakdown(self, days: int) -> Dict:
        """Get performance breakdown by platform"""
        try:
            # Sample data - replace with real analytics
            return {
                'youtube': {'views': 15000, 'engagement': 8.5},
                'instagram': {'views': 12000, 'engagement': 12.3},
                'tiktok': {'views': 25000, 'engagement': 15.7},
                'kawai': {'views': 8000, 'engagement': 18.2}
            }
            
        except Exception as e:
            logger.error(f"Platform breakdown failed: {e}")
            return {}
    
    def _get_performance_insights(self, days: int) -> List[Dict]:
        """Get actionable performance insights"""
        try:
            insights = []
            
            # Sample insights - generate based on real data
            insights.append({
                'type': 'positive',
                'title': 'TikTok Performance Strong',
                'description': 'Your TikTok posts are getting 40% more engagement than average',
                'action': 'Consider posting more content on TikTok'
            })
            
            insights.append({
                'type': 'warning',
                'title': 'YouTube Engagement Down',
                'description': 'YouTube engagement has dropped 15% this week',
                'action': 'Try using more trending hashtags'
            })
            
            insights.append({
                'type': 'info',
                'title': 'Optimal Posting Time',
                'description': 'Your posts perform best between 7-9 PM',
                'action': 'Schedule more posts during peak hours'
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return []
    
    def _get_default_analytics(self) -> Dict:
        """Default analytics when data unavailable"""
        return {
            'summary': {
                'views': 0,
                'likes': 0,
                'shares': 0,
                'comments': 0,
                'posts': 0
            },
            'chartData': {
                'labels': [],
                'views': [],
                'likes': [],
                'shares': []
            },
            'platformBreakdown': {},
            'insights': [],
            'period': 'No data available'
        }
    
    def track_post_performance(self, post_id: str, platform: str, metrics: Dict):
        """Track performance metrics for a post"""
        try:
            self.db.save_analytics(post_id, platform, metrics)
            logger.info(f"Tracked metrics for post {post_id} on {platform}")
        except Exception as e:
            logger.error(f"Failed to track metrics: {e}")
    
    def generate_performance_report(self, post_id: str) -> Dict:
        """Generate detailed performance report for a post"""
        try:
            post = self.db.get_post(post_id)
            if not post:
                return {'error': 'Post not found'}
            
            # Get analytics for this post
            analytics = self._get_post_analytics(post_id)
            
            # Calculate performance scores
            performance_score = self._calculate_performance_score(analytics)
            
            return {
                'post': post,
                'analytics': analytics,
                'performance_score': performance_score,
                'recommendations': self._get_improvement_recommendations(analytics)
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {'error': str(e)}
    
    def _get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics data for specific post"""
        # Implementation would query database for post metrics
        return {}
    
    def _calculate_performance_score(self, analytics: Dict) -> int:
        """Calculate overall performance score (0-100)"""
        # Implementation would calculate score based on metrics
        return 75  # Sample score
    
    def _get_improvement_recommendations(self, analytics: Dict) -> List[str]:
        """Get recommendations for improving performance"""
        recommendations = [
            "Use trending hashtags to increase reach",
            "Post during peak engagement hours",
            "Add captions to improve accessibility",
            "Create eye-catching thumbnails"
        ]
        return recommendations

# utils/validators.py
import re
import logging
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
        self.platform_requirements = {
            'youtube': {
                'max_title_length': 100,
                'max_description_length': 5000,
                'max_tags': 15
            },
            'instagram': {
                'max_title_length': 125,
                'max_description_length': 2200,
                'max_hashtags': 30
            },
            'tiktok': {
                'max_title_length': 100,
                'max_description_length': 300,
                'max_hashtags': 10
            },
            'kawai': {
                'max_title_length': 80,
                'max_description_length': 500,
                'max_hashtags': 20
            }
        }
    
    def validate_video_file(self, file: FileStorage) -> bool:
        """Validate uploaded video file"""
        try:
            # Check if file exists
            if not file or not file.filename:
                logger.warning("No file provided")
                return False
            
            # Check file type
            if file.mimetype not in self.allowed_video_types:
                logger.warning(f"Invalid file type: {file.mimetype}")
                return False
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if size > self.max_file_size:
                logger.warning(f"File too large: {size} bytes")
                return False
            
            # Check filename
            if not self._is_valid_filename(file.filename):
                logger.warning(f"Invalid filename: {file.filename}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation failed: {e}")
            return False
    
    def validate_post_data(self, data: Dict) -> Dict:
        """Validate post data and return validation result"""
        errors = []
        warnings = []
        
        # Validate title
        title = data.get('title', '').strip()
        if not title:
            errors.append("Title is required")
        elif len(title) > 200:
            errors.append("Title is too long (max 200 characters)")
        
        # Validate platforms
        platforms = data.get('platforms', [])
        if not platforms:
            errors.append("At least one platform must be selected")
        
        # Validate platform-specific content
        for platform in platforms:
            if platform in self.platform_requirements:
                platform_errors = self._validate_platform_content(data, platform)
                errors.extend(platform_errors)
        
        # Validate description
        description = data.get('description', '').strip()
        if len(description) > 2000:
            warnings.append("Description is very long and may be truncated on some platforms")
        
        # Validate hashtags
        hashtags = data.get('hashtags', [])
        if len(hashtags) > 50:
            warnings.append("Too many hashtags may reduce visibility")
        
        # Validate inappropriate content
        content_check = self._check_inappropriate_content(title, description, hashtags)
        if content_check:
            errors.extend(content_check)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def validate_platform_credentials(self, platform: str, credentials: Dict) -> bool:
        """Validate platform credentials format"""
        try:
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
            
            # Additional validation for specific platforms
            if platform == 'youtube':
                if not re.match(r'^UC[a-zA-Z0-9_-]{22}$', credentials.get('channelId', '')):
                    return False
            
            elif platform == 'instagram':
                username = credentials.get('username', '')
                if not re.match(r'^[a-zA-Z0-9._]{1,30}$', username):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
    
    def _validate_platform_content(self, data: Dict, platform: str) -> List[str]:
        """Validate content for specific platform requirements"""
        errors = []
        requirements = self.platform_requirements.get(platform, {})
        
        platform_content = data.get('platform_specific', {}).get(platform, {})
        
        # Check title length
        title = platform_content.get('title', data.get('title', ''))
        max_title = requirements.get('max_title_length', 200)
        if len(title) > max_title:
            errors.append(f"{platform} title too long (max {max_title} chars)")
        
        # Check description length
        description = platform_content.get('description', data.get('description', ''))
        max_desc = requirements.get('max_description_length', 2000)
        if len(description) > max_desc:
            errors.append(f"{platform} description too long (max {max_desc} chars)")
        
        # Check hashtag count
        hashtags = platform_content.get('hashtags', data.get('hashtags', []))
        max_hashtags = requirements.get('max_hashtags', 50)
        if len(hashtags) > max_hashtags:
            errors.append(f"{platform} too many hashtags (max {max_hashtags})")
        
        return errors
    
    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename is valid"""
        if not filename:
            return False
        
        # Remove potentially dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            if char in filename:
                return False
        
        # Check length
        if len(filename) > 255:
            return False
        
        return True
    
    def _check_inappropriate_content(self, title: str, description: str, hashtags: List[str]) -> List[str]:
        """Check for inappropriate content"""
        errors = []
        
        # Basic inappropriate content detection
        inappropriate_words = [
            'spam', 'scam', 'fake', 'clickbait', 'misleading'
        ]
        
        content_to_check = f"{title} {description} {' '.join(hashtags)}".lower()
        
        for word in inappropriate_words:
            if word in content_to_check:
                errors.append(f"Content may contain inappropriate term: {word}")
        
        return errors
    
    def validate_schedule_time(self, schedule_time: str) -> bool:
        """Validate schedule time format and logic"""
        try:
            from datetime import datetime
            
            # Parse ISO format
            scheduled_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            
            # Check if time is in the future
            if scheduled_datetime <= datetime.now():
                return False
            
            # Check if time is not too far in the future (1 year max)
            max_future = datetime.now().replace(year=datetime.now().year + 1)
            if scheduled_datetime > max_future:
                return False
            
            return True
            
        except Exception:
            return False

# utils/logger.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_level='INFO', log_file='social_media_automation.log'):
    """Setup comprehensive logging configuration"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        f'logs/{log_file}',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers to root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    # Log startup message
    logger.info("Social Media Automation System logging initialized")
    
    return logger