# services/ai_service.py
import openai
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests
from utils.config import Config
import asyncio

logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
            self.is_initialized = False
        else:
            self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            self.is_initialized = True
        
        self.model = Config.OPENAI_MODEL or "gpt-4"
        self.max_retries = 3
        
        # Platform-specific constraints
        self.platform_constraints = {
            'youtube': {
                'title_max': 100,
                'description_max': 5000,
                'hashtag_max': 15,
                'optimal_hashtags': 10
            },
            'instagram': {
                'caption_max': 2200,
                'hashtag_max': 30,
                'optimal_hashtags': 25,
                'story_length': 15
            },
            'tiktok': {
                'caption_max': 150,
                'hashtag_max': 5,
                'optimal_hashtags': 3,
                'video_length': 60
            },
            'kawai': {
                'caption_max': 500,
                'hashtag_max': 10,
                'optimal_hashtags': 8
            }
        }

    async def generate_viral_content(self, title: str, category: str = "", 
                                   platforms: List[str] = None,
                                   video_duration: int = None, 
                                   video_description: str = None) -> Dict[str, any]:
        """Generate viral content for social media platforms"""
        try:
            if not self.is_initialized or not self.client:
                return self._get_fallback_content(title, category, platforms or [])

            platforms = platforms or ['youtube', 'instagram', 'tiktok', 'kawai']
            
            # Create optimized prompt
            prompt = self._create_viral_prompt(title, category, platforms, video_duration, video_description)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            try:
                content_data = json.loads(response.choices[0].message.content)
                return self._process_ai_response(content_data, title, category, platforms)
            except json.JSONDecodeError:
                logger.warning("AI returned non-JSON response, using fallback")
                return self._get_fallback_content(title, category, platforms)
                
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return self._get_fallback_content(title, category, platforms)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI content generation"""
        return """Você é um especialista em marketing digital e criação de conteúdo viral para redes sociais. 
        Sua missão é criar hashtags e descrições que maximizem o engajamento e alcance.

        Responda SEMPRE em formato JSON válido com esta estrutura:
        {
            "hashtags": ["lista", "de", "hashtags"],
            "description": "descrição principal do conteúdo",
            "platform_specific": {
                "youtube": {"title": "título otimizado", "description": "descrição específica"},
                "instagram": {"caption": "legenda", "story_text": "texto para story"},
                "tiktok": {"caption": "legenda curta", "trending_sounds": ["som1", "som2"]},
                "kawai": {"caption": "legenda kawai", "mood": "emoji mood"}
            },
            "engagement_tips": ["dica1", "dica2", "dica3"]
        }"""

    def _create_viral_prompt(self, title: str, category: str, platforms: List[str], 
                           duration: int, description: str) -> str:
        """Create an optimized prompt for viral content generation"""
        return f"""
        Crie conteúdo viral para: "{title}"
        Categoria: {category or 'Geral'}
        Plataformas: {', '.join(platforms)}
        Duração do vídeo: {duration or 'Não especificado'}s
        
        Gere hashtags relevantes e trending, descrições envolventes com hooks e CTAs.
        Adapte o conteúdo para cada plataforma específica.
        Foque em gatilhos emocionais e tendências atuais do Brasil.
        """

    def _process_ai_response(self, content_data: Dict, title: str, category: str, platforms: List[str]) -> Dict:
        """Process and validate AI response"""
        return {
            'hashtags': content_data.get('hashtags', [])[:20],
            'description': content_data.get('description', ''),
            'platform_specific': content_data.get('platform_specific', {}),
            'engagement_tips': content_data.get('engagement_tips', []),
            'optimized_title': title,
            'viral_score': 75,
            'generated_at': datetime.now().isoformat()
        }

    def _get_fallback_content(self, title: str, category: str, platforms: List[str]) -> Dict:
        """Fallback content when AI generation fails"""
        basic_hashtags = ['viral', 'trending', 'brasil', category] if category else ['viral', 'trending', 'brasil']
        
        return {
            'hashtags': basic_hashtags,
            'description': f"🔥 {title} 🔥\n\nConteúdo incrível que você precisa ver! 💫\n\n👍 Curta se gostou!\n💬 Comente aqui!\n🔄 Compartilhe!",
            'platform_specific': {
                platform: {
                    'title': title,
                    'description': f"Confira este conteúdo incrível de {category}!",
                    'hashtags': basic_hashtags[:10]
                } for platform in platforms
            },
            'engagement_tips': [
                'Use emojis para chamar atenção',
                'Poste no horário de pico',
                'Responda aos comentários'
            ],
            'optimized_title': title,
            'viral_score': 60,
            'fallback': True
        }

    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        return self.is_initialized and self.client is not None

    async def analyze_viral_potential(self, content: Dict) -> Dict:
        """Analyze viral potential of content"""
        try:
            if not self.is_healthy():
                return {"viral_score": 50, "analysis": "AI service unavailable"}
            
            # Simplified analysis
            title = content.get('title', '')
            description = content.get('description', '')
            hashtags = content.get('hashtags', [])
            
            score = 50
            
            # Basic scoring
            if len(title) > 10 and any(word in title.lower() for word in ['incrível', 'viral', 'chocante']):
                score += 15
            
            if len(hashtags) >= 5:
                score += 10
            
            if 'viral' in hashtags or 'trending' in hashtags:
                score += 15
            
            return {
                "viral_score": min(score, 100),
                "strengths": ["Título envolvente", "Hashtags relevantes"] if score > 60 else [],
                "improvements": ["Adicione mais hashtags", "Melhore o título"] if score < 70 else [],
                "trending_elements": {"hashtags": hashtags[:5]},
                "optimal_posting_times": ["18:00-20:00", "12:00-14:00"]
            }
            
        except Exception as e:
            logger.error(f"Viral analysis failed: {e}")
            return {"viral_score": 50, "analysis": f"Analysis failed: {e}"}