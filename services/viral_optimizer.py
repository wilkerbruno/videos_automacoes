# services/viral_optimizer.py
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re
from services.ai_service import AIContentGenerator
from models.database import DatabaseManager
import asyncio

logger = logging.getLogger(__name__)

class ViralContentOptimizer:
    def __init__(self):
        self.ai_service = AIContentGenerator()
        self.db = DatabaseManager()
        self.viral_patterns = self._load_viral_patterns()
        self.trending_topics = {}
        self.performance_weights = {
            'views': 0.4,
            'likes': 0.25,
            'shares': 0.2,
            'comments': 0.1,
            'saves': 0.05
        }
    
    def _load_viral_patterns(self) -> Dict:
        """Load patterns that make content go viral"""
        return {
            'hooks': [
                "You won't believe what happened",
                "This will blow your mind",
                "Wait for it...",
                "Plot twist:",
                "This is why",
                "The secret to",
                "Nobody talks about this",
                "This changed everything"
            ],
            'emotional_triggers': [
                'surprising', 'shocking', 'amazing', 'incredible', 'unbelievable',
                'heartwarming', 'inspiring', 'mind-blowing', 'game-changing'
            ],
            'viral_formats': [
                'before_after', 'transformation', 'reaction', 'tutorial',
                'behind_scenes', 'day_in_life', 'challenge', 'trend'
            ],
            'call_to_actions': [
                "Tag someone who needs to see this",
                "Share if you agree",
                "Comment your thoughts below",
                "Save this for later",
                "Which one are you?",
                "Rate this 1-10"
            ]
        }
    
    async def optimize_content_for_virality(self, post_data: Dict) -> Dict:
        """Optimize content using viral best practices"""
        try:
            optimized_content = {}
            
            for platform in post_data.get('platforms', []):
                platform_optimization = await self._optimize_for_platform_virality(
                    post_data, platform
                )
                optimized_content[platform] = platform_optimization
            
            # Add viral score
            viral_score = self._calculate_viral_potential(optimized_content)
            
            return {
                'optimized_content': optimized_content,
                'viral_score': viral_score,
                'optimization_tips': self._get_optimization_tips(optimized_content),
                'trending_elements': await self._add_trending_elements(post_data)
            }
            
        except Exception as e:
            logger.error(f"Viral optimization failed: {e}")
            return {'error': str(e)}
    
    async def _optimize_for_platform_virality(self, post_data: Dict, platform: str) -> Dict:
        """Optimize content for specific platform's viral algorithms"""
        base_content = post_data.get('platform_specific', {}).get(platform, {})
        title = base_content.get('title', post_data.get('title', ''))
        description = base_content.get('description', post_data.get('description', ''))
        
        if platform == 'tiktok':
            return await self._optimize_tiktok_virality(title, description, post_data)
        elif platform == 'instagram':
            return await self._optimize_instagram_virality(title, description, post_data)
        elif platform == 'youtube':
            return await self._optimize_youtube_virality(title, description, post_data)
        elif platform == 'kawai':
            return await self._optimize_kawai_virality(title, description, post_data)
        
        return base_content
    
    async def _optimize_tiktok_virality(self, title: str, description: str, post_data: Dict) -> Dict:
        """Optimize for TikTok's algorithm"""
        # TikTok loves hooks, trends, and engagement
        viral_title = self._add_viral_hook(title, 'tiktok')
        
        # Add trending hashtags
        trending_hashtags = await self._get_trending_hashtags('tiktok', post_data.get('category'))
        
        # Optimize description for engagement
        viral_description = f"{description}\n\n{self._get_random_cta()}"
        
        # Add TikTok-specific viral elements
        viral_description += "\n#fyp #viral #foryou #trending"
        
        return {
            'title': viral_title,
            'description': viral_description[:300],  # TikTok limit
            'hashtags': trending_hashtags[:10],
            'posting_strategy': 'Post during 6-10am or 7-9pm for maximum reach',
            'engagement_tactics': [
                'Ask viewers to duet or stitch',
                'Use trending sounds',
                'Jump on current challenges'
            ]
        }
    
    async def _optimize_instagram_virality(self, title: str, description: str, post_data: Dict) -> Dict:
        """Optimize for Instagram's algorithm"""
        viral_title = self._add_viral_hook(title, 'instagram')
        
        # Instagram loves storytelling and community
        story_elements = self._add_story_elements(description)
        
        # Add engagement-driving elements
        viral_description = f"{story_elements}\n\n💫 {self._get_random_cta()}"
        viral_description += "\n\n🔥 Follow for more amazing content!"
        
        trending_hashtags = await self._get_trending_hashtags('instagram', post_data.get('category'))
        
        return {
            'title': viral_title,
            'description': viral_description[:2200],
            'hashtags': trending_hashtags[:30],
            'posting_strategy': 'Post at 11am, 1pm, or 5pm for best engagement',
            'engagement_tactics': [
                'Use Instagram Stories for behind-the-scenes',
                'Create carousel posts for higher engagement',
                'Use location tags and mentions'
            ]
        }
    
    async def _optimize_youtube_virality(self, title: str, description: str, post_data: Dict) -> Dict:
        """Optimize for YouTube Shorts algorithm"""
        # YouTube loves curiosity gaps and clear value propositions
        viral_title = self._create_curiosity_gap_title(title)
        
        # Optimize description for search and engagement
        seo_description = self._add_seo_elements(description, post_data.get('category'))
        
        trending_hashtags = await self._get_trending_hashtags('youtube', post_data.get('category'))
        
        return {
            'title': viral_title[:100],  # YouTube limit
            'description': f"{seo_description}\n\n🔔 Subscribe for more!\n👍 Like if this helped you!",
            'hashtags': trending_hashtags[:15],
            'posting_strategy': 'Upload at 2-4pm or 8-10pm for maximum views',
            'engagement_tactics': [
                'Create compelling thumbnails',
                'Use end screens to promote other videos',
                'Pin engaging comments'
            ]
        }
    
    async def _optimize_kawai_virality(self, title: str, description: str, post_data: Dict) -> Dict:
        """Optimize for Kawai platform"""
        # Kawai loves cute, positive, and heartwarming content
        kawaii_title = f"💖 {title} ✨"
        
        # Add kawaii elements and positive vibes
        kawaii_description = f"🌸 {description} 💕\n\nSpread the kawaii love! 🎀"
        
        kawaii_hashtags = ['kawaii', 'cute', 'adorable', 'sweet', 'lovely', 'precious']
        
        return {
            'title': kawaii_title,
            'description': kawaii_description,
            'hashtags': kawaii_hashtags + (post_data.get('hashtags', [])[:14]),
            'posting_strategy': 'Post during afternoon hours for cute content',
            'engagement_tactics': [
                'Use cute filters and effects',
                'Add heartwarming captions',
                'Engage with kawaii community'
            ]
        }
    
    def _add_viral_hook(self, title: str, platform: str) -> str:
        """Add viral hooks to titles"""
        hooks = self.viral_patterns['hooks']
        
        # Choose appropriate hook based on platform
        if platform == 'tiktok':
            selected_hooks = [h for h in hooks if 'wait' in h.lower() or 'won\'t believe' in h.lower()]
        elif platform == 'youtube':
            selected_hooks = [h for h in hooks if 'secret' in h.lower() or 'why' in h.lower()]
        else:
            selected_hooks = hooks
        
        if selected_hooks:
            import random
            hook = random.choice(selected_hooks)
            return f"{hook}: {title}"
        
        return title
    
    def _create_curiosity_gap_title(self, title: str) -> str:
        """Create titles with curiosity gaps"""
        curiosity_patterns = [
            f"The {title} Secret Nobody Tells You",
            f"What Happens When You {title}? (Shocking)",
            f"Why {title} Changes Everything",
            f"{title}: The Truth Will Surprise You",
            f"This {title} Method Will Blow Your Mind"
        ]
        
        import random
        return random.choice(curiosity_patterns)
    
    def _add_story_elements(self, description: str) -> str:
        """Add storytelling elements to description"""
        story_starters = [
            "Here's what happened when...",
            "I never expected this to...",
            "This completely changed my perspective on...",
            "The moment I realized..."
        ]
        
        import random
        starter = random.choice(story_starters)
        return f"{starter} {description}"
    
    def _add_seo_elements(self, description: str, category: str) -> str:
        """Add SEO-friendly elements to description"""
        seo_keywords = {
            'entretenimento': ['entertaining', 'fun', 'amazing', 'incredible'],
            'educacao': ['learn', 'tutorial', 'how to', 'educational'],
            'tecnologia': ['tech', 'technology', 'innovation', 'digital'],
            'lifestyle': ['lifestyle', 'daily', 'routine', 'tips']
        }
        
        keywords = seo_keywords.get(category, ['amazing', 'incredible'])
        
        # Add keywords naturally to description
        enhanced_description = f"{description}\n\nIn this {' '.join(keywords[:2])} video, you'll discover..."
        return enhanced_description
    
    def _get_random_cta(self) -> str:
        """Get random call-to-action"""
        import random
        return random.choice(self.viral_patterns['call_to_actions'])
    
    async def _get_trending_hashtags(self, platform: str, category: str) -> List[str]:
        """Get current trending hashtags"""
        # This would integrate with real trending APIs
        base_trending = {
            'tiktok': ['fyp', 'viral', 'trending', 'foryou'],
            'instagram': ['instagood', 'photooftheday', 'viral', 'trending'],
            'youtube': ['shorts', 'viral', 'trending', 'youtube'],
            'kawai': ['kawaii', 'cute', 'adorable', 'sweet']
        }
        
        category_hashtags = {
            'entretenimento': ['entertainment', 'fun', 'amazing'],
            'educacao': ['education', 'learn', 'knowledge'],
            'tecnologia': ['tech', 'technology', 'innovation'],
            'lifestyle': ['lifestyle', 'daily', 'motivation']
        }
        
        trending = base_trending.get(platform, [])
        trending.extend(category_hashtags.get(category, []))
        
        return trending
    
    async def _add_trending_elements(self, post_data: Dict) -> Dict:
        """Add current trending elements"""
        # This would analyze current trends and add relevant elements
        return {
            'trending_sounds': ['Popular sound 1', 'Viral audio 2'],
            'trending_effects': ['Trending filter 1', 'Popular effect 2'],
            'trending_challenges': ['#Challenge1', '#TrendingChallenge'],
            'optimal_timing': self._get_optimal_posting_times(post_data.get('platforms', []))
        }
    
    def _get_optimal_posting_times(self, platforms: List[str]) -> Dict:
        """Get optimal posting times for platforms"""
        times = {}
        for platform in platforms:
            if platform == 'tiktok':
                times[platform] = ['06:00', '10:00', '19:00', '20:00']
            elif platform == 'instagram':
                times[platform] = ['11:00', '13:00', '17:00', '19:00']
            elif platform == 'youtube':
                times[platform] = ['14:00', '16:00', '20:00', '22:00']
            elif platform == 'kawai':
                times[platform] = ['12:00', '15:00', '18:00', '20:00']
        
        return times
    
    def _calculate_viral_potential(self, content: Dict) -> int:
        """Calculate viral potential score (0-100)"""
        score = 50  # Base score
        
        for platform, platform_content in content.items():
            title = platform_content.get('title', '')
            description = platform_content.get('description', '')
            hashtags = platform_content.get('hashtags', [])
            
            # Check for viral elements
            if any(hook.lower() in title.lower() for hook in self.viral_patterns['hooks']):
                score += 10
            
            if any(trigger in description.lower() for trigger in self.viral_patterns['emotional_triggers']):
                score += 8
            
            if any(cta in description for cta in self.viral_patterns['call_to_actions']):
                score += 5
            
            # Check hashtag relevance
            if len(hashtags) >= 5:
                score += 5
            
            # Platform-specific scoring
            if platform == 'tiktok' and '#fyp' in hashtags:
                score += 7
            elif platform == 'instagram' and '#instagood' in hashtags:
                score += 5
        
        return min(score, 100)
    
    def _get_optimization_tips(self, content: Dict) -> List[str]:
        """Get personalized optimization tips"""
        tips = []
        
        for platform, platform_content in content.items():
            title = platform_content.get('title', '')
            description = platform_content.get('description', '')
            
            if len(title) > 80:
                tips.append(f"Consider shortening your {platform} title for better mobile visibility")
            
            if '?' not in title and '!' not in title:
                tips.append(f"Add excitement or curiosity to your {platform} title with punctuation")
            
            if not any(cta in description for cta in self.viral_patterns['call_to_actions']):
                tips.append(f"Add a clear call-to-action to your {platform} description")
        
        # General tips
        tips.extend([
            "Post during peak engagement hours for your audience",
            "Use trending sounds or music when possible",
            "Create eye-catching thumbnails or first frames",
            "Engage with comments quickly to boost algorithm favor"
        ])
        
        return tips[:5]  # Return top 5 tips