# services/webhook_handler.py
import logging
import hmac
import hashlib
import json
from flask import request, jsonify
from typing import Dict, Any
from models.database import DatabaseManager

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        self.db = DatabaseManager()
        self.handlers = {
            'youtube': self.handle_youtube_webhook,
            'instagram': self.handle_instagram_webhook,
            'tiktok': self.handle_tiktok_webhook,
            'kawai': self.handle_kawai_webhook
        }
    
    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def handle_webhook(self, platform: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route webhook to appropriate handler"""
        try:
            if platform not in self.handlers:
                return {'error': f'Unsupported platform: {platform}'}
            
            return self.handlers[platform](payload)
        
        except Exception as e:
            logger.error(f"Webhook handling failed for {platform}: {e}")
            return {'error': str(e)}
    
    def handle_youtube_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YouTube webhook notifications"""
        try:
            event_type = payload.get('eventType')
            
            if event_type == 'video.published':
                self.process_video_published(payload, 'youtube')
            elif event_type == 'video.metrics.updated':
                self.process_metrics_update(payload, 'youtube')
            elif event_type == 'video.comment.added':
                self.process_new_comment(payload, 'youtube')
            
            return {'status': 'processed', 'platform': 'youtube'}
        
        except Exception as e:
            logger.error(f"YouTube webhook error: {e}")
            return {'error': str(e)}
    
    def handle_instagram_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Instagram webhook notifications"""
        try:
            object_type = payload.get('object')
            
            if object_type == 'instagram':
                for entry in payload.get('entry', []):
                    for change in entry.get('changes', []):
                        field = change.get('field')
                        
                        if field == 'media':
                            self.process_media_update(change['value'], 'instagram')
                        elif field == 'comments':
                            self.process_comment_update(change['value'], 'instagram')
            
            return {'status': 'processed', 'platform': 'instagram'}
        
        except Exception as e:
            logger.error(f"Instagram webhook error: {e}")
            return {'error': str(e)}
    
    def handle_tiktok_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TikTok webhook notifications"""
        try:
            event_type = payload.get('event_type')
            
            if event_type == 'video_publish':
                self.process_video_published(payload, 'tiktok')
            elif event_type == 'video_analytics_update':
                self.process_metrics_update(payload, 'tiktok')
            
            return {'status': 'processed', 'platform': 'tiktok'}
        
        except Exception as e:
            logger.error(f"TikTok webhook error: {e}")
            return {'error': str(e)}
    
    def handle_kawai_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Kawai webhook notifications"""
        try:
            action = payload.get('action')
            
            if action == 'video.uploaded':
                self.process_video_published(payload, 'kawai')
            elif action == 'stats.updated':
                self.process_metrics_update(payload, 'kawai')
            
            return {'status': 'processed', 'platform': 'kawai'}
        
        except Exception as e:
            logger.error(f"Kawai webhook error: {e}")
            return {'error': str(e)}
    
    def process_video_published(self, payload: Dict, platform: str):
        """Process video published notification"""
        try:
            video_id = payload.get('video_id') or payload.get('media_id')
            post_id = payload.get('post_id')  # Our internal post ID
            
            if post_id:
                # Update post status in database
                self.db.update_post(post_id, {
                    'status': 'published',
                    f'{platform}_video_id': video_id,
                    f'{platform}_published_at': payload.get('published_at')
                })
                
                logger.info(f"Video published on {platform}: {video_id}")
        
        except Exception as e:
            logger.error(f"Failed to process video published for {platform}: {e}")
    
    def process_metrics_update(self, payload: Dict, platform: str):
        """Process metrics update notification"""
        try:
            video_id = payload.get('video_id') or payload.get('media_id')
            metrics = payload.get('metrics', {})
            
            # Find post by platform video ID
            post = self.find_post_by_video_id(video_id, platform)
            
            if post:
                # Save updated metrics
                self.db.save_analytics(post['id'], platform, metrics)
                logger.info(f"Metrics updated for {platform} video: {video_id}")
        
        except Exception as e:
            logger.error(f"Failed to process metrics update for {platform}: {e}")
    
    def process_new_comment(self, payload: Dict, platform: str):
        """Process new comment notification"""
        try:
            video_id = payload.get('video_id') or payload.get('media_id')
            comment = payload.get('comment', {})
            
            # Find post and save comment for analysis
            post = self.find_post_by_video_id(video_id, platform)
            
            if post:
                self.save_comment(post['id'], platform, comment)
                logger.info(f"New comment on {platform} video: {video_id}")
        
        except Exception as e:
            logger.error(f"Failed to process comment for {platform}: {e}")
    
    def find_post_by_video_id(self, video_id: str, platform: str) -> Dict:
        """Find post by platform-specific video ID"""
        # This would require extending the database schema
        # For now, return None
        return None
    
    def save_comment(self, post_id: str, platform: str, comment: Dict):
        """Save comment for analysis"""
        # This would save comments to analyze sentiment, engagement, etc.
        pass