# tests/test_app.py
import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from app import create_app
from services.ai_service import AIContentGenerator
from services.platform_manager import PlatformManager
from services.video_processor import VideoProcessor
from models.database import DatabaseManager

class TestSocialMediaApp:
    
    @pytest.fixture
    def app(self):
        """Create test application"""
        app = create_app()
        app.app.config['TESTING'] = True
        app.app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        return app.app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def sample_video_file(self):
        """Create sample video file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(b'fake video content')
            return f.name
    
    def test_index_route(self, client):
        """Test main index route"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    @patch('services.video_processor.VideoProcessor.process_video')
    @patch('services.ai_service.AIContentGenerator.generate_viral_content')
    def test_upload_video(self, mock_ai, mock_video, client, sample_video_file):
        """Test video upload functionality"""
        mock_video.return_value = {
            'success': True,
            'processed': {'youtube': {'path': '/fake/path'}},
            'analysis': {'duration': 30}
        }
        
        mock_ai.return_value = {
            'optimized_title': 'Test Title',
            'description': 'Test Description',
            'hashtags': ['test', 'video']
        }
        
        with open(sample_video_file, 'rb') as video_file:
            data = {
                'video_0': video_file,
                'title': 'Test Video',
                'category': 'entertainment',
                'platforms': json.dumps(['youtube', 'tiktok']),
                'generateContent': 'true'
            }
            
            response = client.post('/api/upload', data=data, content_type='multipart/form-data')
            
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
    
    def test_upload_no_file(self, client):
        """Test upload without file"""
        response = client.post('/api/upload', data={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_connect_account(self, client):
        """Test account connection"""
        data = {
            'platform': 'youtube',
            'apiKey': 'test_key',
            'channelId': 'UC1234567890123456789012'
        }
        
        with patch('services.platform_manager.PlatformManager.connect_platform') as mock_connect:
            mock_connect.return_value = {'success': True}
            
            response = client.post('/api/accounts/connect', 
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data['success'] is True
    
    def test_get_analytics(self, client):
        """Test analytics endpoint"""
        with patch('services.analytics.AnalyticsService.get_analytics') as mock_analytics:
            mock_analytics.return_value = {
                'summary': {'views': 1000, 'likes': 100},
                'chartData': {'labels': [], 'views': []},
                'insights': []
            }
            
            response = client.get('/api/analytics?range=30d')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'summary' in data

class TestAIService:
    
    @pytest.fixture
    def ai_service(self):
        return AIContentGenerator()
    
    @pytest.mark.asyncio
    @patch('openai.OpenAI')
    async def test_generate_viral_content(self, mock_openai, ai_service):
        """Test viral content generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            'optimized_title': 'Amazing Viral Title',
            'description': 'Engaging description',
            'hashtags': ['viral', 'trending'],
            'viral_score': 85
        })
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        result = await ai_service.generate_viral_content(
            title='Test Title',
            category='entertainment',
            platforms=['tiktok', 'youtube']
        )
        
        assert 'optimized_title' in result
        assert result['viral_score'] == 85
    
    @pytest.mark.asyncio
    async def test_get_trending_hashtags(self, ai_service):
        """Test trending hashtag retrieval"""
        platforms = ['tiktok', 'instagram']
        category = 'entertainment'
        
        result = await ai_service._get_trending_hashtags(platforms, category)
        
        assert isinstance(result, dict)
        assert 'tiktok' in result
        assert 'instagram' in result
        assert len(result['tiktok']) > 0

class TestPlatformManager:
    
    @pytest.fixture
    def platform_manager(self):
        return PlatformManager()
    
    @pytest.mark.asyncio
    async def test_post_to_platforms(self, platform_manager):
        """Test posting to multiple platforms"""
        post_data = {
            'title': 'Test Post',
            'description': 'Test Description',
            'platforms': ['youtube', 'tiktok'],
            'files': [{'path': '/fake/path'}]
        }
        
        with patch.object(platform_manager.platforms['youtube'], 'post') as mock_youtube:
            with patch.object(platform_manager.platforms['tiktok'], 'post') as mock_tiktok:
                mock_youtube.return_value = {'success': True, 'post_id': 'yt123'}
                mock_tiktok.return_value = {'success': True, 'post_id': 'tt123'}
                
                # Add platforms to connected set
                platform_manager.connected_platforms.add('youtube')
                platform_manager.connected_platforms.add('tiktok')
                
                results = await platform_manager.post_to_platforms(post_data)
                
                assert 'youtube' in results
                assert 'tiktok' in results
                assert results['youtube']['success'] is True
                assert results['tiktok']['success'] is True

class TestVideoProcessor:
    
    @pytest.fixture
    def video_processor(self):
        return VideoProcessor()
    
    def test_video_analysis(self, video_processor, sample_video_file=None):
        """Test video analysis"""
        # Mock video clip
        with patch('moviepy.editor.VideoFileClip') as mock_clip:
            mock_instance = Mock()
            mock_instance.duration = 30.0
            mock_instance.fps = 30
            mock_instance.size = (1080, 1920)
            mock_instance.w = 1080
            mock_instance.h = 1920
            mock_instance.audio = Mock()
            mock_clip.return_value = mock_instance
            
            analysis = video_processor._analyze_video(mock_instance)
            
            assert analysis['duration'] == 30.0
            assert analysis['fps'] == 30
            assert analysis['resolution'] == '1080x1920'