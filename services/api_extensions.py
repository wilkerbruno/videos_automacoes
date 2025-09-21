# services/api_extensions.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime  # Added missing import
import asyncio
import json
import logging

# Import services
from services.viral_optimizer import ViralContentOptimizer
from services.content_templates import ContentTemplateManager
from services.monitoring import SystemMonitor
from services.webhook_handler import WebhookHandler

logger = logging.getLogger(__name__)

# Create blueprint for extended API endpoints
api_bp = Blueprint('api_extensions', __name__, url_prefix='/api')

# Initialize services
viral_optimizer = ViralContentOptimizer()
template_manager = ContentTemplateManager()
system_monitor = SystemMonitor()
webhook_handler = WebhookHandler()

@api_bp.route('/analyze-viral-potential', methods=['POST'])
def analyze_viral_potential():
    """Analyze viral potential of content"""
    try:
        data = request.get_json()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analysis = loop.run_until_complete(
            viral_optimizer.optimize_content_for_virality(data)
        )
        
        loop.close()
        
        return jsonify({
            'success': True,
            'viral_score': analysis.get('viral_score', 50),
            'strengths': analysis.get('optimization_tips', [])[:5],
            'improvements': analysis.get('optimization_tips', [])[5:],
            'trending_elements': analysis.get('trending_elements', {}),
            'optimal_timing': analysis.get('optimal_timing', {})
        })
    
    except Exception as e:
        logger.error(f"Viral analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/regenerate-viral-content', methods=['POST'])
def regenerate_viral_content():
    """Regenerate content with viral optimizations"""
    try:
        data = request.get_json()
        analysis = data.get('analysis', {})
        
        # Apply improvements to generate better content
        optimized_content = {
            'title': 'Optimized Viral Title',
            'platform_specific': {
                'tiktok': {
                    'title': 'TikTok Optimized Title',
                    'description': 'Viral TikTok description',
                    'hashtags': ['fyp', 'viral', 'trending']
                },
                'instagram': {
                    'title': 'Instagram Optimized Title',
                    'description': 'Engaging Instagram description',
                    'hashtags': ['instagood', 'viral', 'trending']
                }
            }
        }
        
        return jsonify({
            'success': True,
            'content': optimized_content
        })
    
    except Exception as e:
        logger.error(f"Content regeneration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/content-templates', methods=['GET'])
def get_content_templates():
    """Get available content templates"""
    try:
        templates = {
            'viral_template_1': {
                'id': 'viral_template_1',
                'name': 'Before & After Transformation',
                'description': 'Perfect for showcasing transformations and progress',
                'viral_score': 92,
                'best_platforms': ['instagram', 'tiktok', 'youtube'],
                'category': 'viral',
                'title_example': 'This 30-day transformation will shock you!',
                'description_example': 'I documented my entire journey...',
                'variables': ['timeframe', 'transformation_type', 'result'],
                'avg_views': '2.5M',
                'avg_engagement': '15.2%'
            },
            'educational_template_1': {
                'id': 'educational_template_1',
                'name': 'Step-by-Step Tutorial',
                'description': 'Great for educational and how-to content',
                'viral_score': 85,
                'best_platforms': ['youtube', 'instagram', 'tiktok'],
                'category': 'educational',
                'title_example': 'Master {skill} in {timeframe} (Complete Guide)',
                'description_example': 'Learn {skill} the right way with this comprehensive guide...',
                'variables': ['skill', 'timeframe', 'difficulty'],
                'avg_views': '1.8M',
                'avg_engagement': '12.8%'
            }
        }
        
        return jsonify({'success': True, 'templates': templates})
    
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/generate-from-template', methods=['POST'])
def generate_from_template():
    """Generate content from template"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        variables = data.get('variables', {})
        platforms = data.get('platforms', [])
        
        # Generate content using template
        content = template_manager.generate_content_from_template(
            template_id, variables, platforms
        )
        
        return jsonify(content)
    
    except Exception as e:
        logger.error(f"Template generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        # Run async monitoring
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(system_monitor.monitor_all_services())
        
        status = system_monitor.get_system_status()
        loop.close()
        
        return jsonify({
            'success': True,
            'status': status
        })
    
    except Exception as e:
        logger.error(f"System status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/webhooks/<platform>', methods=['POST'])
def handle_platform_webhook(platform):
    """Handle platform webhooks"""
    try:
        payload = request.get_json() or {}
        signature = request.headers.get('X-Signature-256') or request.headers.get('X-Hub-Signature-256')
        
        # Verify signature if provided
        if signature and hasattr(current_app, 'config'):
            secret = current_app.config.get(f'{platform.upper()}_WEBHOOK_SECRET')
            if secret and not webhook_handler.verify_signature(request.data, signature, secret):
                return jsonify({'error': 'Invalid signature'}), 401
        
        # Process webhook
        result = webhook_handler.handle_webhook(platform, payload)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health/ai', methods=['GET'])
def ai_service_health():
    """AI service health check"""
    try:
        from services.ai_service import AIContentGenerator
        ai_service = AIContentGenerator()
        
        return jsonify({
            'status': 'healthy' if ai_service.is_healthy() else 'unhealthy',
            'service': 'ai_content_generator',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'ai_content_generator',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/health/video', methods=['GET'])
def video_processor_health():
    """Video processor health check"""
    try:
        from services.video_processor import VideoProcessor
        processor = VideoProcessor()
        
        return jsonify({
            'status': 'healthy' if processor.is_healthy() else 'unhealthy',
            'service': 'video_processor',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'video_processor',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/health/scheduler', methods=['GET'])
def scheduler_health():
    """Scheduler health check"""
    try:
        from services.scheduler import PostScheduler
        scheduler = PostScheduler()
        
        return jsonify({
            'status': 'healthy' if scheduler.is_healthy() else 'unhealthy',
            'service': 'post_scheduler',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'post_scheduler',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/trending-hashtags/<platform>', methods=['GET'])
def get_trending_hashtags(platform):
    """Get trending hashtags for specific platform"""
    try:
        category = request.args.get('category', 'entertainment')
        
        # Mock trending hashtags - in production, fetch from real APIs
        trending_data = {
            'tiktok': {
                'entertainment': ['fyp', 'viral', 'trending', 'foryou', 'comedy'],
                'education': ['learn', 'tutorial', 'knowledge', 'tips', 'howto'],
                'lifestyle': ['lifestyle', 'daily', 'routine', 'selfcare', 'motivation']
            },
            'instagram': {
                'entertainment': ['instagood', 'viral', 'reels', 'trending', 'fun'],
                'education': ['education', 'learning', 'knowledge', 'tips', 'tutorial'],
                'lifestyle': ['lifestyle', 'inspiration', 'daily', 'selfcare', 'wellness']
            },
            'youtube': {
                'entertainment': ['shorts', 'viral', 'trending', 'youtube', 'entertainment'],
                'education': ['education', 'tutorial', 'learning', 'howto', 'knowledge'],
                'lifestyle': ['lifestyle', 'vlog', 'daily', 'inspiration', 'motivation']
            }
        }
        
        hashtags = trending_data.get(platform, {}).get(category, ['trending', 'viral'])
        
        return jsonify({
            'success': True,
            'platform': platform,
            'category': category,
            'hashtags': hashtags,
            'updated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trending hashtags error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/optimize-posting-time', methods=['POST'])
def optimize_posting_time():
    """Get optimal posting times for platforms and content"""
    try:
        data = request.get_json()
        platforms = data.get('platforms', [])
        category = data.get('category', 'entertainment')
        timezone = data.get('timezone', 'America/Sao_Paulo')
        
        optimal_times = {
            'youtube': {
                'entertainment': ['14:00', '18:00', '20:00'],
                'education': ['12:00', '15:00', '19:00'],
                'lifestyle': ['11:00', '16:00', '19:00']
            },
            'instagram': {
                'entertainment': ['11:00', '13:00', '17:00', '19:00'],
                'education': ['12:00', '14:00', '18:00'],
                'lifestyle': ['10:00', '14:00', '17:00']
            },
            'tiktok': {
                'entertainment': ['06:00', '10:00', '19:00', '21:00'],
                'education': ['12:00', '16:00', '20:00'],
                'lifestyle': ['08:00', '12:00', '18:00']
            }
        }
        
        result = {}
        for platform in platforms:
            if platform in optimal_times:
                result[platform] = optimal_times[platform].get(category, optimal_times[platform]['entertainment'])
        
        return jsonify({
            'success': True,
            'optimal_times': result,
            'timezone': timezone,
            'category': category
        })
        
    except Exception as e:
        logger.error(f"Optimize posting time error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/content-insights', methods=['POST'])
def get_content_insights():
    """Get AI-powered content insights and recommendations"""
    try:
        data = request.get_json()
        content_type = data.get('type', 'video')
        category = data.get('category', 'entertainment')
        platforms = data.get('platforms', [])
        
        insights = {
            'recommendations': [
                f"For {category} content on {', '.join(platforms)}, consider using trending audio",
                "Add captions to improve accessibility and engagement",
                "Use the first 3 seconds to create a strong hook",
                "Include a clear call-to-action in your description"
            ],
            'trending_topics': [
                "Transformation stories",
                "Behind the scenes content",
                "Quick tutorials",
                "Day in my life vlogs"
            ],
            'engagement_tips': [
                "Ask questions in your captions to encourage comments",
                "Use trending hashtags (but don't overdo it)",
                "Post consistently at optimal times",
                "Respond to comments quickly to boost engagement"
            ],
            'viral_elements': [
                "Emotional storytelling",
                "Relatable situations",
                "Surprising twists or reveals",
                "Visual appeal and quality"
            ]
        }
        
        return jsonify({
            'success': True,
            'insights': insights,
            'category': category,
            'platforms': platforms
        })
        
    except Exception as e:
        logger.error(f"Content insights error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/performance-prediction', methods=['POST'])
def predict_performance():
    """Predict content performance using AI analysis"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        description = data.get('description', '')
        hashtags = data.get('hashtags', [])
        platforms = data.get('platforms', [])
        category = data.get('category', 'entertainment')
        
        # Mock performance prediction - in production, use ML models
        base_score = 50
        
        # Title analysis
        if len(title) > 0:
            if any(word in title.lower() for word in ['amazing', 'incredible', 'shocking']):
                base_score += 15
            if '?' in title or '!' in title:
                base_score += 10
                
        # Hashtag analysis
        if len(hashtags) > 5:
            base_score += 10
        if any(tag in ['viral', 'trending', 'fyp'] for tag in hashtags):
            base_score += 15
            
        # Platform analysis
        platform_multipliers = {
            'tiktok': 1.2,
            'instagram': 1.1,
            'youtube': 1.0,
            'kawai': 0.9
        }
        
        predictions = {}
        for platform in platforms:
            platform_score = min(100, int(base_score * platform_multipliers.get(platform, 1.0)))
            predictions[platform] = {
                'score': platform_score,
                'estimated_views': f"{platform_score * 1000:,}",
                'estimated_engagement': f"{platform_score * 0.15:.1f}%",
                'confidence': 'high' if platform_score > 70 else 'medium' if platform_score > 50 else 'low'
            }
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'overall_score': base_score,
            'recommendations': [
                "Add more emotional triggers to your title",
                "Include trending hashtags for better discoverability",
                "Consider posting during peak hours"
            ]
        })
        
    except Exception as e:
        logger.error(f"Performance prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bulk-schedule', methods=['POST'])
def bulk_schedule_posts():
    """Schedule multiple posts at once"""
    try:
        data = request.get_json()
        posts = data.get('posts', [])
        
        if not posts:
            return jsonify({'error': 'No posts provided'}), 400
        
        scheduled_posts = []
        errors = []
        
        for i, post in enumerate(posts):
            try:
                # Validate post data
                if not post.get('title') or not post.get('schedule_time'):
                    errors.append(f"Post {i+1}: Missing title or schedule_time")
                    continue
                
                # Here you would integrate with your actual scheduler
                post_id = f"bulk_{datetime.now().timestamp()}_{i}"
                scheduled_posts.append({
                    'id': post_id,
                    'title': post['title'],
                    'schedule_time': post['schedule_time'],
                    'platforms': post.get('platforms', []),
                    'status': 'scheduled'
                })
                
            except Exception as e:
                errors.append(f"Post {i+1}: {str(e)}")
        
        return jsonify({
            'success': len(errors) == 0,
            'scheduled_posts': scheduled_posts,
            'errors': errors,
            'total_scheduled': len(scheduled_posts)
        })
        
    except Exception as e:
        logger.error(f"Bulk schedule error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handler for the blueprint
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"API extension error: {error}")
    return jsonify({'error': 'Internal server error'}), 500