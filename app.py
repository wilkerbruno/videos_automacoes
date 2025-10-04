#!/usr/bin/env python3
"""
Social Media Automation System - Main Flask Application
Sistema de automação para múltiplas plataformas de mídia social
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import asyncio
import json
from services.youtube_service import YouTubeService
# Import custom modules
from services.ai_service import AIContentGenerator
from services.platform_manager import PlatformManager
from services.video_processor import VideoProcessor
from services.scheduler import PostScheduler
from services.analytics import AnalyticsService
from models.database import DatabaseManager
from utils.config import Config
from utils.validators import ValidationService
from utils.logger import setup_logging

import asyncio
import logging
from typing import Dict, List, Optional, Any

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class SocialMediaApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        
        # Enable CORS for all routes
        CORS(self.app)
        
        # Initialize services
        self.db = DatabaseManager()
        self.ai_service = AIContentGenerator()
        self.platform_manager = PlatformManager()
        self.video_processor = VideoProcessor()
        self.scheduler = PostScheduler()
        self.analytics = AnalyticsService()
        self.validator = ValidationService()
        
        # Setup routes
        self.setup_routes()
        
        # Setup error handlers
        self.setup_error_handlers()
        
        logger.info("Social Media Automation System initialized successfully")

    def setup_routes(self):
        """Setup all application routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main application page"""
            return render_template('index.html')

        @self.app.route('/api/upload', methods=['POST'])
        def upload_video():
            """Handle video upload and processing"""
            try:
                # Validate request
                if not request.files:
                    return jsonify({'error': 'No files provided'}), 400

                files = []
                for key in request.files:
                    if key.startswith('video_'):
                        files.append(request.files[key])

                if not files:
                    return jsonify({'error': 'No video files found'}), 400

                # Get form data
                title = request.form.get('title', '').strip()
                category = request.form.get('category', '').strip()
                platforms = request.form.get('platforms', '[]')
                generate_content = request.form.get('generateContent') == 'true'
                schedule_time = request.form.get('scheduleTime')

                # Validate required fields
                if not title:
                    return jsonify({'error': 'Title is required'}), 400

                # Parse platforms
                try:
                    platforms = json.loads(platforms)
                except:
                    return jsonify({'error': 'Invalid platforms data'}), 400

                if not platforms:
                    return jsonify({'error': 'At least one platform must be selected'}), 400

                # Process files
                processed_files = []
                for file in files:
                    if not self.validator.validate_video_file(file):
                        return jsonify({'error': f'Invalid file: {file.filename}'}), 400

                    # Save file
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Process video
                    processed_video = self.video_processor.process_video(filepath, platforms)
                    if processed_video['success']:
                        processed_files.append({
                            'original_path': filepath,
                            'processed_videos': processed_video['processed'],
                            'thumbnail': processed_video.get('thumbnail'),
                            'analysis': processed_video['analysis']
                        })
                    else:
                        return jsonify({'error': f'Video processing failed: {processed_video.get("error")}'}), 500

                # Generate AI content if requested
                hashtags = []
                description = ""
                ai_content = {}
                
                if generate_content:
                    try:
                        
                        ai_content = asyncio.run(
                        self.ai_service.generate_viral_content(
                        title=title,
                        category=category,
                        platforms=platforms,
                        video_duration=processed_files[0]['analysis']['duration'] if processed_files else None
                        )
                    )
                        
                        hashtags = ai_content.get('hashtags', [])
                        description = ai_content.get('description', '')
                        
                    except Exception as e:
                        logger.warning(f"AI content generation failed: {e}")
                        # Continue without AI content

                # Create post data
                post_data = {
                    'id': self.db.generate_id(),
                    'title': ai_content.get('optimized_title', title),
                    'category': category,
                    'description': description,
                    'hashtags': hashtags,
                    'platforms': platforms,
                    'files': processed_files,
                    'status': 'scheduled' if schedule_time else 'ready',
                    'created_at': datetime.now().isoformat(),
                    'schedule_time': schedule_time,
                    'ai_content': ai_content,
                    'viral_score': ai_content.get('viral_score', 0)
                }

                # Save to database
                if not self.db.save_post(post_data):
                    return jsonify({'error': 'Failed to save post'}), 500

                # Handle posting/scheduling
                if schedule_time:
                    # Validate schedule time
                    if not self.validator.validate_schedule_time(schedule_time):
                        return jsonify({'error': 'Invalid schedule time'}), 400
                    
                    # Schedule for later
                    if self.scheduler.schedule_post(post_data, schedule_time):
                        response_message = 'Post scheduled successfully'
                    else:
                        return jsonify({'error': 'Failed to schedule post'}), 500
                else:
                    # Post immediately
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        results = loop.run_until_complete(
                            self.platform_manager.post_to_platforms(post_data)
                        )
                        
                        loop.close()
                        
                        post_data['results'] = results
                        self.db.update_post(post_data['id'], {'status': 'posted', 'results': results})
                        response_message = 'Posted successfully to platforms'
                        
                    except Exception as e:
                        logger.error(f"Platform posting failed: {e}")
                        return jsonify({'error': f'Failed to post to platforms: {str(e)}'}), 500

                return jsonify({
                    'success': True,
                    'message': response_message,
                    'post_id': post_data['id'],
                    'viral_score': post_data['viral_score'],
                    'data': {
                        'title': post_data['title'],
                        'description': post_data['description'],
                        'hashtags': post_data['hashtags'],
                        'platforms': post_data['platforms'],
                        'status': post_data['status']
                    }
                })

            except Exception as e:
                logger.error(f"Upload error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-content', methods=['POST'])
        def generate_content():
            """Generate AI content for posts"""
            try:
                data = request.get_json()
                title = data.get('title')
                category = data.get('category')
                platforms = data.get('platforms', [])

                if not title:
                    return jsonify({'error': 'Title is required'}), 400

                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                content = loop.run_until_complete(
                    self.ai_service.generate_viral_content(title, category, platforms)
                )
                
                loop.close()
                
                return jsonify({'success': True, 'content': content})

            except Exception as e:
                logger.error(f"Content generation error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/analyze-viral-potential', methods=['POST'])
        def analyze_viral_potential():
            """Analyze viral potential of content"""
            try:
                data = request.get_json()
                
                # Run async analysis
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                analysis = loop.run_until_complete(
                    self.ai_service.analyze_viral_potential(data)
                )
                
                loop.close()
                
                return jsonify({
                    'success': True,
                    'viral_score': analysis.get('viral_score', 50),
                    'strengths': analysis.get('strengths', []),
                    'improvements': analysis.get('improvements', []),
                    'trending_elements': analysis.get('trending_elements', {}),
                    'optimal_timing': analysis.get('optimal_posting_times', [])
                })
                
            except Exception as e:
                logger.error(f"Viral analysis error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/schedule', methods=['POST'])
        def schedule_post():
            """Schedule a post for later"""
            try:
                data = request.get_json()
                post_id = data.get('post_id')
                schedule_time = data.get('schedule_time')

                if not post_id or not schedule_time:
                    return jsonify({'error': 'Post ID and schedule time are required'}), 400

                # Validate schedule time
                if not self.validator.validate_schedule_time(schedule_time):
                    return jsonify({'error': 'Invalid schedule time'}), 400

                post = self.db.get_post(post_id)
                if not post:
                    return jsonify({'error': 'Post not found'}), 404

                # Schedule the post
                if self.scheduler.schedule_post(post, schedule_time):
                    self.db.update_post(post_id, {
                        'status': 'scheduled',
                        'schedule_time': schedule_time
                    })
                    return jsonify({'success': True, 'message': 'Post scheduled successfully'})
                else:
                    return jsonify({'error': 'Failed to schedule post'}), 500

            except Exception as e:
                logger.error(f"Schedule error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/schedule', methods=['GET'])
        def get_scheduled_posts():
            """Get scheduled posts with optional filtering"""
            try:
                platform = request.args.get('platform')
                date = request.args.get('date')

                filters = {}
                if platform:
                    filters['platform'] = platform
                if date:
                    filters['date'] = date

                posts = self.db.get_scheduled_posts(filters)
                return jsonify({'success': True, 'posts': posts})

            except Exception as e:
                logger.error(f"Get scheduled posts error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/schedule/<post_id>', methods=['DELETE'])
        def cancel_scheduled_post(post_id):
            """Cancel a scheduled post"""
            try:
                post = self.db.get_post(post_id)
                if not post:
                    return jsonify({'error': 'Post not found'}), 404

                if post['status'] != 'scheduled':
                    return jsonify({'error': 'Post is not scheduled'}), 400

                if self.scheduler.cancel_scheduled_post(post_id):
                    self.db.update_post(post_id, {'status': 'cancelled'})
                    return jsonify({'success': True, 'message': 'Post cancelled successfully'})
                else:
                    return jsonify({'error': 'Failed to cancel post'}), 500

            except Exception as e:
                logger.error(f"Cancel post error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/accounts/connect', methods=['POST'])
        def connect_account():
            """Connect social media account"""
            try:
                data = request.get_json()
                platform = data.get('platform')
                credentials = {k: v for k, v in data.items() if k != 'platform'}

                if not platform:
                    return jsonify({'error': 'Platform is required'}), 400

                # Validate credentials format
                if not self.validator.validate_platform_credentials(platform, credentials):
                    return jsonify({'error': 'Invalid credentials format'}), 400

                # Test connection
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                connection_result = loop.run_until_complete(
                    self.platform_manager.connect_platform(platform, credentials)
                )
                
                loop.close()
                
                if connection_result['success']:
                    # Save credentials securely
                    if self.db.save_platform_credentials(platform, credentials):
                        return jsonify({
                            'success': True,
                            'message': f'{platform.capitalize()} connected successfully'
                        })
                    else:
                        return jsonify({'error': 'Failed to save credentials'}), 500
                else:
                    return jsonify({
                        'success': False,
                        'message': connection_result.get('error', 'Connection failed')
                    }), 400

            except Exception as e:
                logger.error(f"Connect account error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/accounts/status', methods=['GET'])
        def get_account_status():
            """Get connection status for all platforms"""
            try:
                status = self.platform_manager.get_all_platform_status()
                return jsonify({'success': True, 'accounts': status})

            except Exception as e:
                logger.error(f"Get account status error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/analytics', methods=['GET'])
        def get_analytics():
            """Get analytics data"""
            try:
                date_range = request.args.get('range', '30d')
                period = request.args.get('period', '30d')  # Alternative parameter name
                
                analytics_data = self.analytics.get_analytics(date_range or period)
                return jsonify({'success': True, **analytics_data})

            except Exception as e:
                logger.error(f"Get analytics error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/post', methods=['POST'])
        def post_to_platforms():
            """Post content to selected platforms"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['title', 'platforms']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'{field} is required'}), 400

                # Validate post data
                validation_result = self.validator.validate_post_data(data)
                if not validation_result['valid']:
                    return jsonify({
                        'error': 'Validation failed',
                        'details': validation_result['errors']
                    }), 400

                # Post to platforms
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(
                    self.platform_manager.post_to_platforms(data)
                )
                
                loop.close()
                
                # Save post to database
                post_data = {
                    'id': self.db.generate_id(),
                    'status': 'posted',
                    'results': results,
                    'created_at': datetime.now().isoformat(),
                    **data
                }
                
                if self.db.save_post(post_data):
                    return jsonify({
                        'success': True,
                        'message': 'Posted to platforms',
                        'post_id': post_data['id'],
                        'results': results
                    })
                else:
                    return jsonify({'error': 'Failed to save post data'}), 500

            except Exception as e:
                logger.error(f"Post to platforms error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/posts', methods=['GET'])
        def get_posts():
            """Get posts with optional filtering"""
            try:
                status = request.args.get('status')
                platform = request.args.get('platform')
                limit = int(request.args.get('limit', 50))
                offset = int(request.args.get('offset', 0))
                
                filters = {}
                if status:
                    filters['status'] = status
                if platform:
                    filters['platform'] = platform
                
                posts = self.db.get_posts(filters, limit, offset)
                return jsonify({'success': True, 'posts': posts})
                
            except Exception as e:
                logger.error(f"Get posts error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/posts/<post_id>', methods=['GET'])
        def get_post(post_id):
            """Get specific post"""
            try:
                post = self.db.get_post(post_id)
                if post:
                    return jsonify({'success': True, 'post': post})
                else:
                    return jsonify({'error': 'Post not found'}), 404
                    
            except Exception as e:
                logger.error(f"Get post error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/posts/<post_id>', methods=['PUT'])
        def update_post(post_id):
            """Update post"""
            try:
                data = request.get_json()
                
                if self.db.update_post(post_id, data):
                    return jsonify({'success': True, 'message': 'Post updated successfully'})
                else:
                    return jsonify({'error': 'Failed to update post'}), 500
                    
            except Exception as e:
                logger.error(f"Update post error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/posts/<post_id>', methods=['DELETE'])
        def delete_post(post_id):
            """Delete post"""
            try:
                if self.db.delete_post(post_id):
                    return jsonify({'success': True, 'message': 'Post deleted successfully'})
                else:
                    return jsonify({'error': 'Failed to delete post'}), 500
                    
            except Exception as e:
                logger.error(f"Delete post error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/content-templates', methods=['GET'])
        def get_content_templates():
            """Get available content templates"""
            try:
                from services.content_templates import ContentTemplateManager
                template_manager = ContentTemplateManager()
                
                category = request.args.get('category')
                suggestions = template_manager.suggest_templates(category or 'entertainment')
                
                return jsonify({
                    'success': True,
                    'templates': {
                        f'template_{i}': {
                            'id': f'template_{i}',
                            'name': suggestion['template_name'].replace('_', ' ').title(),
                            'description': f'Perfect for {suggestion["template_name"]} content',
                            'viral_score': suggestion['score'],
                            'best_platforms': suggestion['best_platforms'],
                            'category': 'viral' if suggestion['score'] > 80 else 'standard',
                            'title_example': suggestion['title_example'],
                            'description_example': suggestion['description_preview'],
                            'variables': ['timeframe', 'topic', 'result'],
                            'avg_views': '1.5M',
                            'avg_engagement': f'{suggestion["score"] * 0.15:.1f}%'
                        } for i, suggestion in enumerate(suggestions)
                    }
                })
                
            except Exception as e:
                logger.error(f"Get templates error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-from-template', methods=['POST'])
        def generate_from_template():
            """Generate content from template"""
            try:
                data = request.get_json()
                template_id = data.get('template_id')
                variables = data.get('variables', {})
                platforms = data.get('platforms', [])
                
                from services.content_templates import ContentTemplateManager
                template_manager = ContentTemplateManager()
                
                # Map template_id to actual template type
                template_mapping = {
                    'template_0': 'before_after',
                    'template_1': 'tutorial',
                    'template_2': 'reaction',
                    'template_3': 'behind_scenes'
                }
                
                template_type = template_mapping.get(template_id, 'before_after')
                
                result = template_manager.generate_content_from_template(
                    template_type, variables, platforms
                )
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'content': {
                            'title': list(result['content'].values())[0]['title'] if result['content'] else 'Generated Title',
                            'platforms': platforms,
                            'platform_specific': result['content']
                        }
                    })
                else:
                    return jsonify({'error': result.get('error', 'Template generation failed')}), 500
                
            except Exception as e:
                logger.error(f"Template generation error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/system/status', methods=['GET'])
        def get_system_status():
            """Get system health status"""
            try:
                from services.monitoring import SystemMonitor
                monitor = SystemMonitor()
                
                # Run monitoring check
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                loop.run_until_complete(monitor.monitor_all_services())
                status = monitor.get_system_status()
                
                loop.close()
                
                return jsonify({
                    'success': True,
                    'status': status
                })
                
            except Exception as e:
                logger.error(f"System status error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'services': {
                    'database': self.db.is_healthy(),
                    'ai_service': self.ai_service.is_healthy(),
                    'scheduler': self.scheduler.is_healthy() if hasattr(self.scheduler, 'is_healthy') else True,
                    'video_processor': self.video_processor.is_healthy() if hasattr(self.video_processor, 'is_healthy') else True
                }
            })

        @self.app.route('/api/health/<service>', methods=['GET'])
        def service_health(service):
            """Individual service health check"""
            try:
                service_map = {
                    'ai': self.ai_service,
                    'database': self.db,
                    'scheduler': self.scheduler,
                    'video': self.video_processor,
                    'analytics': self.analytics
                }
                
                if service not in service_map:
                    return jsonify({'error': 'Service not found'}), 404
                
                service_obj = service_map[service]
                is_healthy = service_obj.is_healthy() if hasattr(service_obj, 'is_healthy') else True
                
                return jsonify({
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'service': service,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'unhealthy',
                    'service': service,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500

    def setup_error_handlers(self):
        """Setup global error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404

        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({'error': 'Method not allowed'}), 405

        @self.app.errorhandler(413)
        def request_entity_too_large(error):
            return jsonify({'error': 'File too large'}), 413

        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({'error': 'Internal server error'}), 500

        @self.app.errorhandler(Exception)
        def handle_exception(error):
            logger.error(f"Unhandled exception: {error}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
        
        # Temporary OAuth Helper (add this endpoint to your app.py)
        @self.app.route('/oauth/youtube/start')
        def start_youtube_oauth():
            """Start YouTube OAuth flow"""
            from urllib.parse import urlencode
            
            client_id = os.getenv('YOUTUBE_CLIENT_ID')
            if not client_id:
                return jsonify({'error': 'YouTube OAuth not configured'}), 400
            
            params = {
                'client_id': client_id,
                'redirect_uri': 'http://localhost:5000/oauth/youtube/callback',
                'scope': 'https://www.googleapis.com/auth/youtube.upload',
                'response_type': 'code',
                'access_type': 'offline'
            }
            
            auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
            return jsonify({'auth_url': auth_url})

        @self.app.route('/oauth/youtube/callback')
        def youtube_oauth_callback():
            """Handle YouTube OAuth callback"""
            code = request.args.get('code')
            if not code:
                return jsonify({'error': 'Authorization code not received'}), 400
            

             # Exchange code for tokens (implement this)
            # Store tokens securely for the user
            # Return success message
            
            return "YouTube authorization successful! You can close this window."

    def init_app_context(self):
        """Initialize application context and services"""
        try:
            # Create required directories
            os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs('temp_videos', exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            
            # Initialize database
            self.db.init_database()
            
            # Start scheduler if not already running
            if hasattr(self.scheduler, 'start'):
                self.scheduler.start()
            
            logger.info("Application context initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize app context: {e}")
            raise

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        try:
            # Initialize app context
            self.init_app_context()
            
            logger.info(f"Starting Social Media Automation System on {host}:{port}")
            logger.info(f"Debug mode: {debug}")
            logger.info(f"Upload folder: {self.app.config['UPLOAD_FOLDER']}")
            
            # Run the application
            self.app.run(host=host, port=port, debug=debug, threaded=True)
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise
        finally:
            # Cleanup
            try:
                if hasattr(self.scheduler, 'stop'):
                    self.scheduler.stop()
                logger.info("Application shutdown complete")
            except:
                pass

def create_app():
    """Application factory"""
    return SocialMediaApp()

if __name__ == '__main__':
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create and run application
        app = create_app()
        
        # Get configuration from environment
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        exit(1)