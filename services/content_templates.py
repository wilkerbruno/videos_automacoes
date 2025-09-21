# services/content_templates.py
import logging
from typing import Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContentTemplateManager:
    def __init__(self):
        self.templates = self._load_viral_templates()
    
    def _load_viral_templates(self) -> Dict:
        """Load proven viral content templates"""
        return {
            'before_after': {
                'title_templates': [
                    "The {timeframe} transformation that shocked everyone",
                    "From {before_state} to {after_state} in {timeframe}",
                    "This {timeframe} journey will inspire you",
                    "You won't believe this {timeframe} change"
                ],
                'description_templates': [
                    "Here's my {timeframe} transformation journey. The results speak for themselves! What started as {challenge} became {success}. Swipe to see the difference!",
                    "I documented my entire {timeframe} process. The before and after will shock you! Here's exactly what I did..."
                ],
                'hashtag_templates': {
                    'tiktok': ['transformation', 'beforeafter', 'progress', 'journey', 'fyp'],
                    'instagram': ['transformation', 'beforeandafter', 'progress', 'journey', 'motivational'],
                    'youtube': ['transformation', 'before', 'after', 'results', 'journey']
                }
            },
            
            'tutorial': {
                'title_templates': [
                    "How to {skill} in {timeframe} (Step by Step)",
                    "The {skill} method nobody talks about",
                    "Master {skill} with this simple trick",
                    "{skill} tutorial that actually works"
                ],
                'description_templates': [
                    "Learn {skill} the right way! This step-by-step tutorial covers everything you need to know. Save this post for later!",
                    "I'm sharing the exact method I use for {skill}. Follow along and you'll master it too!"
                ],
                'hashtag_templates': {
                    'tiktok': ['tutorial', 'howto', 'learn', 'educational', 'tips'],
                    'instagram': ['tutorial', 'howto', 'learnsomething', 'educational', 'tips'],
                    'youtube': ['tutorial', 'howto', 'learn', 'educational', 'guide']
                }
            },
            
            'reaction': {
                'title_templates': [
                    "My reaction to {topic} (you need to see this)",
                    "Reacting to {topic} for the first time",
                    "This {topic} reaction will shock you",
                    "Watch my face when I see {topic}"
                ],
                'description_templates': [
                    "I couldn't believe what I was seeing! My genuine reaction to {topic}. What would your reaction be?",
                    "First time seeing {topic} and I was NOT prepared! Comment your reaction below!"
                ],
                'hashtag_templates': {
                    'tiktok': ['reaction', 'reacting', 'firsttime', 'shocked', 'omg'],
                    'instagram': ['reaction', 'reacting', 'surprised', 'omg', 'unbelievable'],
                    'youtube': ['reaction', 'reacting', 'review', 'surprised', 'firsttime']
                }
            },
            
            'behind_scenes': {
                'title_templates': [
                    "Behind the scenes of {project}",
                    "What really happens when {activity}",
                    "The truth about {topic} nobody shows you",
                    "Here's what {profession} don't want you to see"
                ],
                'description_templates': [
                    "Ever wondered what really goes on behind the scenes? Here's the unfiltered truth about {topic}!",
                    "Pulling back the curtain on {topic}. This is what it's really like!"
                ],
                'hashtag_templates': {
                    'tiktok': ['behindthescenes', 'bts', 'reality', 'truth', 'insider'],
                    'instagram': ['behindthescenes', 'bts', 'reallife', 'authentic', 'insider'],
                    'youtube': ['behindthescenes', 'bts', 'making', 'process', 'truth']
                }
            }
        }
    
    def generate_content_from_template(self, template_type: str, variables: Dict, platforms: List[str]) -> Dict:
        """Generate content from template"""
        try:
            if template_type not in self.templates:
                raise ValueError(f"Template type '{template_type}' not found")
            
            template = self.templates[template_type]
            content = {}
            
            for platform in platforms:
                platform_content = self._fill_template(template, variables, platform)
                content[platform] = platform_content
            
            return {
                'success': True,
                'content': content,
                'template_used': template_type,
                'variables_applied': variables
            }
            
        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fill_template(self, template: Dict, variables: Dict, platform: str) -> Dict:
        """Fill template with variables for specific platform"""
        import random
        
        # Choose random title template
        title_templates = template['title_templates']
        title_template = random.choice(title_templates)
        
        # Fill title variables
        filled_title = title_template
        for key, value in variables.items():
            filled_title = filled_title.replace(f'{{{key}}}', str(value))
        
        # Choose random description template
        description_templates = template['description_templates']
        description_template = random.choice(description_templates)
        
        # Fill description variables
        filled_description = description_template
        for key, value in variables.items():
            filled_description = filled_description.replace(f'{{{key}}}', str(value))
        
        # Get platform-specific hashtags
        hashtag_templates = template.get('hashtag_templates', {})
        platform_hashtags = hashtag_templates.get(platform, [])
        
        # Add category-specific hashtags if provided
        category = variables.get('category', '')
        if category:
            platform_hashtags.append(category)
        
        return {
            'title': filled_title,
            'description': filled_description,
            'hashtags': platform_hashtags,
            'template_type': template.__class__.__name__
        }
    
    def suggest_templates(self, category: str, content_type: str = None) -> List[Dict]:
        """Suggest best templates based on category and content type"""
        suggestions = []
        
        # Template scoring based on category
        category_scores = {
            'entretenimento': {
                'reaction': 90,
                'behind_scenes': 85,
                'before_after': 75,
                'tutorial': 60
            },
            'educacao': {
                'tutorial': 95,
                'before_after': 80,
                'behind_scenes': 70,
                'reaction': 60
            },
            'lifestyle': {
                'before_after': 95,
                'behind_scenes': 85,
                'tutorial': 80,
                'reaction': 70
            },
            'tecnologia': {
                'tutorial': 90,
                'behind_scenes': 80,
                'reaction': 75,
                'before_after': 65
            }
        }
        
        scores = category_scores.get(category, {})
        
        for template_name, template_data in self.templates.items():
            score = scores.get(template_name, 50)
            
            suggestions.append({
                'template_name': template_name,
                'score': score,
                'title_example': template_data['title_templates'][0],
                'description_preview': template_data['description_templates'][0][:100] + '...',
                'best_platforms': self._get_best_platforms_for_template(template_name)
            })
        
        # Sort by score
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return suggestions
    
    def _get_best_platforms_for_template(self, template_name: str) -> List[str]:
        """Get best platforms for each template type"""
        platform_preferences = {
            'before_after': ['instagram', 'tiktok', 'youtube'],
            'tutorial': ['youtube', 'instagram', 'tiktok'],
            'reaction': ['tiktok', 'youtube', 'instagram'],
            'behind_scenes': ['instagram', 'tiktok', 'youtube']
        }
        
        return platform_preferences.get(template_name, ['tiktok', 'instagram', 'youtube'])
    
    def create_custom_template(self, template_data: Dict) -> bool:
        """Create a custom template"""
        try:
            template_name = template_data.get('name')
            if not template_name or template_name in self.templates:
                return False
            
            # Validate template structure
            required_fields = ['title_templates', 'description_templates', 'hashtag_templates']
            for field in required_fields:
                if field not in template_data:
                    return False
            
            self.templates[template_name] = {
                'title_templates': template_data['title_templates'],
                'description_templates': template_data['description_templates'],
                'hashtag_templates': template_data['hashtag_templates'],
                'created_at': datetime.now().isoformat(),
                'custom': True
            }
            
            logger.info(f"Created custom template: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom template: {e}")
            return False