"""
AI Content Generation Service
Serviço para geração de hashtags e descrições virais usando OpenAI GPT
"""

import openai
import logging
import asyncio
from typing import Dict, List, Optional
import json
import re
from dataclasses import dataclass
from utils.config import Config

logger = logging.getLogger(__name__)

@dataclass
class ContentRequest:
    title: str
    category: str
    platforms: List[str]
    target_audience: Optional[str] = None
    tone: Optional[str] = "engaging"
    language: str = "pt-BR"

@dataclass
class GeneratedContent:
    hashtags: List[str]
    description: str
    platform_specific: Dict[str, Dict[str, any]]
    engagement_tips: List[str]

class AIContentGenerator:
    def __init__(self):
        """Initialize the AI content generator"""
        self.client = openai.AsyncOpenAI(
            api_key=Config.OPENAI_API_KEY
        )
        self.model = Config.OPENAI_MODEL or "gpt-4-turbo-preview"
        self.max_retries = 3
        self.is_initialized = False
        
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
                'story_length': 15  # seconds
            },
            'tiktok': {
                'caption_max': 150,
                'hashtag_max': 5,
                'optimal_hashtags': 3,
                'video_length': 60  # seconds
            },
            'kawai': {
                'caption_max': 500,
                'hashtag_max': 10,
                'optimal_hashtags': 8
            }
        }
        
        self._initialize()

    def _initialize(self):
        """Initialize the service"""
        try:
            if not Config.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured")
                return
            
            self.is_initialized = True
            logger.info("AI Content Generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")

    async def generate_content(
        self, 
        title: str, 
        category: str = "", 
        platforms: List[str] = None,
        target_audience: str = None,
        tone: str = "engaging"
    ) -> Dict[str, any]:
        """
        Generate viral content for social media platforms
        
        Args:
            title: Video title
            category: Content category/niche
            platforms: List of target platforms
            target_audience: Target audience description
            tone: Content tone (engaging, professional, funny, etc.)
            
        Returns:
            Dictionary with generated content
        """
        try:
            if not self.is_initialized:
                raise Exception("AI service not properly initialized")

            platforms = platforms or ['youtube', 'instagram', 'tiktok', 'kawai']
            
            request = ContentRequest(
                title=title,
                category=category,
                platforms=platforms,
                target_audience=target_audience,
                tone=tone
            )

            # Generate content using multiple approaches
            content = await self._generate_comprehensive_content(request)
            
            logger.info(f"Successfully generated content for: {title}")
            return content

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return self._get_fallback_content(title, category, platforms)

    async def _generate_comprehensive_content(self, request: ContentRequest) -> Dict[str, any]:
        """Generate comprehensive content using AI"""
        
        # Build the AI prompt
        prompt = self._build_content_prompt(request)
        
        for attempt in range(self.max_retries):
            try:
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
                    temperature=0.8,
                    response_format={"type": "json_object"}
                )
                
                content_text = response.choices[0].message.content
                content_data = json.loads(content_text)
                
                # Process and validate the response
                processed_content = self._process_ai_response(content_data, request)
                return processed_content
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                
            except Exception as e:
                logger.warning(f"AI generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                
                await asyncio.sleep(1)  # Brief delay before retry

    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI content generation"""
        return """Você é um especialista em marketing digital e criação de conteúdo viral para redes sociais. 
        Sua missão é criar hashtags e descrições que maximizem o engajamento e alcance.

        Você deve sempre responder em formato JSON válido com a seguinte estrutura:
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
        }

        Diretrizes importantes:
        - Use hashtags populares e relevantes
        - Misture hashtags gerais e específicas
        - Crie descrições envolventes que geram curiosidade
        - Considere tendências atuais
        - Adapte o conteúdo para cada plataforma
        - Use linguagem brasileira natural
        - Foque em engajamento e viralização"""

    def _build_content_prompt(self, request: ContentRequest) -> str:
        """Build the content generation prompt"""
        platform_info = []
        for platform in request.platforms:
            constraints = self.platform_constraints.get(platform, {})
            platform_info.append(f"- {platform.upper()}: máx {constraints.get('hashtag_max', 15)} hashtags")

        prompt = f"""Gere conteúdo viral para o seguinte vídeo:

TÍTULO: {request.title}
CATEGORIA: {request.category or 'Geral'}
PLATAFORMAS: {', '.join(request.platforms)}
TOM: {request.tone}
PÚBLICO-ALVO: {request.target_audience or 'Geral'}

Limitações por plataforma:
{chr(10).join(platform_info)}

Instruções específicas:
1. Crie hashtags que sejam trending e relevantes para {request.category}
2. Misture hashtags populares (#viral, #fyp) com específicas do nicho
3. A descrição deve gerar curiosidade e incentivar interação
4. Use emojis estrategicamente
5. Considere tendências atuais do Brasil
6. Adapte o conteúdo para cada plataforma específica
7. Inclua call-to-actions sutis mas efetivos

Priorize conteúdo que:
- Gere comentários e compartilhamentos
- Use palavras-chave populares
- Tenha apelo emocional
- Seja relevante para o momento atual"""

        return prompt

    def _process_ai_response(self, content_data: Dict, request: ContentRequest) -> Dict[str, any]:
        """Process and validate AI response"""
        try:
            # Validate required fields
            required_fields = ['hashtags', 'description', 'platform_specific', 'engagement_tips']
            for field in required_fields:
                if field not in content_data:
                    logger.warning(f"Missing field in AI response: {field}")
                    content_data[field] = self._get_default_field_value(field)

            # Clean and validate hashtags
            hashtags = self._clean_hashtags(content_data.get('hashtags', []))
            
            # Optimize hashtags for each platform
            platform_hashtags = {}
            for platform in request.platforms:
                constraints = self.platform_constraints.get(platform, {})
                max_tags = constraints.get('hashtag_max', 15)
                platform_hashtags[platform] = hashtags[:max_tags]

            # Process platform-specific content
            platform_specific = self._process_platform_specific(
                content_data.get('platform_specific', {}), 
                request
            )

            return {
                'hashtags': hashtags,
                'description': content_data.get('description', ''),
                'platform_hashtags': platform_hashtags,
                'platform_specific': platform_specific,
                'engagement_tips': content_data.get('engagement_tips', []),
                'generated_at': asyncio.get_event_loop().time(),
                'request_data': {
                    'title': request.title,
                    'category': request.category,
                    'platforms': request.platforms
                }
            }

        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            return self._get_fallback_content(request.title, request.category, request.platforms)

    def _clean_hashtags(self, hashtags: List[str]) -> List[str]:
        """Clean and validate hashtags"""
        cleaned = []
        for tag in hashtags:
            if isinstance(tag, str):
                # Remove # if present, clean up
                clean_tag = re.sub(r'^#', '', tag.strip())
                clean_tag = re.sub(r'[^a-zA-Z0-9_áàâãéêíóôõúüç]', '', clean_tag)
                
                if clean_tag and len(clean_tag) >= 3:
                    cleaned.append(clean_tag)
        
        return cleaned[:30]  # Limit total hashtags

    def _process_platform_specific(self, platform_data: Dict, request: ContentRequest) -> Dict:
        """Process platform-specific content"""
        processed = {}
        
        for platform in request.platforms:
            platform_content = platform_data.get(platform, {})
            constraints = self.platform_constraints.get(platform, {})
            
            # Apply platform constraints
            if platform == 'youtube':
                processed[platform] = {
                    'title': self._truncate_text(
                        platform_content.get('title', request.title), 
                        constraints.get('title_max', 100)
                    ),
                    'description': self._truncate_text(
                        platform_content.get('description', ''), 
                        constraints.get('description_max', 5000)
                    )
                }
            elif platform == 'instagram':
                processed[platform] = {
                    'caption': self._truncate_text(
                        platform_content.get('caption', ''), 
                        constraints.get('caption_max', 2200)
                    ),
                    'story_text': platform_content.get('story_text', '')
                }
            elif platform == 'tiktok':
                processed[platform] = {
                    'caption': self._truncate_text(
                        platform_content.get('caption', ''), 
                        constraints.get('caption_max', 150)
                    ),
                    'trending_sounds': platform_content.get('trending_sounds', [])
                }
            elif platform == 'kawai':
                processed[platform] = {
                    'caption': self._truncate_text(
                        platform_content.get('caption', ''), 
                        constraints.get('caption_max', 500)
                    ),
                    'mood': platform_content.get('mood', '💖')
                }
        
        return processed

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'

    def _get_default_field_value(self, field: str):
        """Get default value for missing fields"""
        defaults = {
            'hashtags': ['viral', 'trending', 'fyp'],
            'description': 'Conteúdo incrível que você precisa ver!',
            'platform_specific': {},
            'engagement_tips': ['Use emojis', 'Faça perguntas', 'Poste no horário certo']
        }
        return defaults.get(field, [])

    def _get_fallback_content(self, title: str, category: str, platforms: List[str]) -> Dict[str, any]:
        """Get fallback content when AI generation fails"""
        logger.info("Using fallback content generation")
        
        # Generate basic hashtags based on category and title
        basic_hashtags = self._generate_basic_hashtags(title, category)
        
        # Generate basic description
        basic_description = f"🔥 {title} 🔥\n\nNão perca este conteúdo incrível! 💫\n\n👆 Curta se você gostou!\n💬 Comenta aqui embaixo!\n🔄 Compartilha com os amigos!"
        
        platform_specific = {}
        for platform in platforms:
            platform_specific[platform] = {
                'caption': basic_description[:self.platform_constraints.get(platform, {}).get('caption_max', 500)]
            }

        return {
            'hashtags': basic_hashtags,
            'description': basic_description,
            'platform_hashtags': {p: basic_hashtags[:self.platform_constraints.get(p, {}).get('hashtag_max', 15)] for p in platforms},
            'platform_specific': platform_specific,
            'engagement_tips': [
                'Poste no horário de pico da sua audiência',
                'Use emojis para chamar atenção',
                'Faça perguntas para gerar comentários',
                'Responda aos comentários rapidamente'
            ],
            'generated_at': asyncio.get_event_loop().time(),
            'fallback': True
        }

    def _generate_basic_hashtags(self, title: str, category: str) -> List[str]:
        """Generate basic hashtags based on title and category"""
        hashtags = ['viral', 'trending', 'fyp', 'brasil']
        
        # Category-based hashtags
        category_tags = {
            'entretenimento': ['entretenimento', 'diversao', 'viral', 'engracado'],
            'educacao': ['educacao', 'aprender', 'conhecimento', 'dicas'],
            'tecnologia': ['tech', 'tecnologia', 'inovacao', 'digital'],
            'lifestyle': ['lifestyle', 'vida', 'motivacao', 'inspiracao'],
            'humor': ['humor', 'engracado', 'comedia', 'riso'],
            'musica': ['musica', 'som', 'audio', 'ritmo'],
            'esportes': ['esportes', 'fitness', 'atleta', 'treino'],
            'games': ['games', 'gaming', 'jogos', 'gamer']
        }
        
        if category.lower() in category_tags:
            hashtags.extend(category_tags[category.lower()])
        
        # Extract keywords from title
        title_words = re.findall(r'\w+', title.lower())
        for word in title_words:
            if len(word) >= 4 and word not in hashtags:
                hashtags.append(word)
        
        return hashtags[:20]

    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        return self.is_initialized

    async def test_connection(self) -> bool:
        """Test AI service connection"""
        try:
            if not self.is_initialized:
                return False
            
            # Test with a simple request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI service test failed: {e}")
            return False