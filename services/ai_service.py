# services/ai_service.py - Improved version with better content generation

import openai
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import os

logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
            self.is_initialized = False
        else:
            try:
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
                self.is_initialized = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
                self.is_initialized = False
        
        self.model = os.getenv('OPENAI_MODEL', "gpt-4")
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
                logger.warning("OpenAI not available, using fallback content")
                return self._get_fallback_content(title, category, platforms or [])

            platforms = platforms or ['youtube', 'instagram', 'tiktok', 'kawai']
            
            # Create optimized prompt
            prompt = self._create_viral_prompt(title, category, platforms, video_duration, video_description)
            
            logger.info(f"Generating AI content for: {title}")
            
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
                        timeout=30
                    )
                    
                    content = response.choices[0].message.content.strip()
                    logger.debug(f"Raw AI response: {content}")
                    
                    # Try to parse as JSON
                    try:
                        content_data = json.loads(content)
                        result = self._process_ai_response(content_data, title, category, platforms)
                        logger.info(f"AI content generated successfully (attempt {attempt + 1})")
                        return result
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
                        # Try to extract content from malformed JSON
                        extracted = self._extract_content_from_text(content, title, category, platforms)
                        if extracted:
                            return extracted
                        
                        if attempt == self.max_retries - 1:
                            logger.error("All attempts failed, using fallback")
                            return self._get_fallback_content(title, category, platforms)
                        
                        continue
                
                except Exception as e:
                    logger.warning(f"API call failed on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries - 1:
                        return self._get_fallback_content(title, category, platforms)
                    
                    await asyncio.sleep(1)  # Brief delay before retry
            
            return self._get_fallback_content(title, category, platforms)
                
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return self._get_fallback_content(title, category, platforms)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI content generation"""
        return """Você é um especialista em marketing digital e criação de conteúdo viral para redes sociais brasileiras. 
        Sua especialidade é criar hashtags e descrições que maximizem o engajamento e alcance no Brasil.

        IMPORTANTE: Responda SEMPRE em formato JSON válido com esta estrutura EXATA:
        {
            "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
            "description": "descrição principal do conteúdo",
            "platform_specific": {
                "youtube": {
                    "title": "título otimizado para YouTube",
                    "description": "descrição específica para YouTube",
                    "hashtags": ["yt1", "yt2", "yt3"]
                },
                "instagram": {
                    "caption": "legenda para Instagram",
                    "hashtags": ["ig1", "ig2", "ig3"],
                    "story_text": "texto para story"
                },
                "tiktok": {
                    "caption": "legenda curta para TikTok",
                    "hashtags": ["tt1", "tt2", "tt3"]
                },
                "kawai": {
                    "caption": "legenda kawai",
                    "hashtags": ["kw1", "kw2", "kw3"]
                }
            },
            "engagement_tips": ["dica1", "dica2", "dica3"],
            "viral_score": 85
        }

        Foque em:
        - Hashtags trending no Brasil
        - Linguagem que conecta com o público brasileiro
        - Gatilhos emocionais
        - Call-to-actions eficazes
        - Adaptação para cada plataforma"""

    def _create_viral_prompt(self, title: str, category: str, platforms: List[str], 
                           duration: int, description: str) -> str:
        """Create an optimized prompt for viral content generation"""
        return f"""
        Crie conteúdo viral otimizado para: "{title}"
        
        DETALHES:
        - Categoria/Nicho: {category or 'Entretenimento'}
        - Plataformas de destino: {', '.join(platforms)}
        - Duração do vídeo: {duration or 'Não especificado'}s
        - Descrição adicional: {description or 'Não fornecida'}
        
        REQUISITOS:
        1. Gere hashtags TRENDING e relevantes para o Brasil
        2. Crie descrições envolventes com hooks e CTAs
        3. Adapte o conteúdo para cada plataforma específica
        4. Use linguagem brasileira natural e cativante
        5. Inclua elementos virais (curiosidade, emoção, urgência)
        6. Considere as limitações de cada plataforma
        
        PLATAFORMAS:
        - YouTube: Títulos até 100 chars, descrições até 5000 chars, até 15 hashtags
        - Instagram: Legendas até 2200 chars, até 30 hashtags
        - TikTok: Legendas até 150 chars, até 5 hashtags
        - Kawai: Legendas até 500 chars, até 10 hashtags
        
        Responda APENAS com o JSON válido, sem texto adicional.
        """

    def _extract_content_from_text(self, text: str, title: str, category: str, platforms: List[str]) -> Optional[Dict]:
        """Try to extract content from malformed response"""
        try:
            # Look for JSON-like patterns in the text
            import re
            
            # Try to find hashtags
            hashtag_pattern = r'[#＃]\w+'
            hashtags = re.findall(hashtag_pattern, text)
            hashtags = [tag.replace('#', '').replace('＃', '') for tag in hashtags[:15]]
            
            # Try to find description-like content
            description_match = re.search(r'["\']description["\']:\s*["\']([^"\']*)["\']', text, re.IGNORECASE)
            description = description_match.group(1) if description_match else f"Conteúdo incrível sobre {title}!"
            
            if hashtags:
                return {
                    'hashtags': hashtags,
                    'description': description,
                    'platform_specific': self._generate_platform_specific(title, description, hashtags, platforms),
                    'engagement_tips': [
                        'Use emojis para chamar atenção',
                        'Poste no horário de pico (18h-20h)',
                        'Responda aos comentários rapidamente'
                    ],
                    'optimized_title': title,
                    'viral_score': 70,
                    'extracted_from_text': True
                }
        except:
            pass
        
        return None

    def _generate_platform_specific(self, title: str, description: str, hashtags: List[str], platforms: List[str]) -> Dict:
        """Generate platform-specific content"""
        platform_content = {}
        
        for platform in platforms:
            constraints = self.platform_constraints.get(platform, {})
            
            if platform == 'youtube':
                platform_content[platform] = {
                    'title': title[:constraints.get('title_max', 100)],
                    'description': f"{description}\n\n🔔 Se inscreva no canal!\n👍 Deixe seu like!\n💬 Comente o que achou!",
                    'hashtags': hashtags[:constraints.get('hashtag_max', 15)]
                }
            
            elif platform == 'instagram':
                platform_content[platform] = {
                    'caption': f"{description}\n\n📸 Siga para mais conteúdo!\n❤️ Duplo toque se curtiu!\n💬 Conta nos comentários!",
                    'hashtags': hashtags[:constraints.get('hashtag_max', 30)],
                    'story_text': f"Novo post no feed! {title[:50]}..."
                }
            
            elif platform == 'tiktok':
                short_desc = description[:100] + "..." if len(description) > 100 else description
                platform_content[platform] = {
                    'caption': f"{short_desc} #fyp #viral",
                    'hashtags': ['fyp', 'viral'] + hashtags[:3]
                }
            
            elif platform == 'kawai':
                platform_content[platform] = {
                    'caption': f"{description} ✨💖",
                    'hashtags': hashtags[:constraints.get('hashtag_max', 10)]
                }
        
        return platform_content

    def _process_ai_response(self, content_data: Dict, title: str, category: str, platforms: List[str]) -> Dict:
        """Process and validate AI response"""
        try:
            # Validate and clean hashtags
            hashtags = content_data.get('hashtags', [])
            if isinstance(hashtags, list):
                # Clean hashtags - remove # if present, limit length
                hashtags = [tag.replace('#', '').strip()[:30] for tag in hashtags if tag and isinstance(tag, str)]
                hashtags = [tag for tag in hashtags if tag and len(tag) > 1][:20]
            else:
                hashtags = []
            
            # Validate description
            description = content_data.get('description', '')
            if not isinstance(description, str) or not description.strip():
                description = f"Confira este conteúdo incrível sobre {title}! 🔥"
            
            # Validate platform specific content
            platform_specific = content_data.get('platform_specific', {})
            if not isinstance(platform_specific, dict):
                platform_specific = self._generate_platform_specific(title, description, hashtags, platforms)
            else:
                # Ensure all requested platforms are covered
                for platform in platforms:
                    if platform not in platform_specific:
                        platform_specific[platform] = self._generate_platform_specific(title, description, hashtags, [platform]).get(platform, {})
            
            # Validate engagement tips
            engagement_tips = content_data.get('engagement_tips', [])
            if not isinstance(engagement_tips, list):
                engagement_tips = [
                    'Use emojis para aumentar o engajamento',
                    'Poste no horário de pico da sua audiência',
                    'Responda aos comentários para aumentar a interação'
                ]
            
            # Validate viral score
            viral_score = content_data.get('viral_score', 75)
            if not isinstance(viral_score, (int, float)) or viral_score < 0 or viral_score > 100:
                viral_score = 75
            
            return {
                'hashtags': hashtags,
                'description': description,
                'platform_specific': platform_specific,
                'engagement_tips': engagement_tips[:5],  # Limit to 5 tips
                'optimized_title': title,
                'viral_score': int(viral_score),
                'generated_at': datetime.now().isoformat(),
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            return self._get_fallback_content(title, category, platforms)

    def _get_fallback_content(self, title: str, category: str, platforms: List[str]) -> Dict:
        """Fallback content when AI generation fails"""
        
        # Category-specific hashtags
        category_hashtags = {
            'entretenimento': ['entretenimento', 'diversao', 'viral', 'brasil', 'trending'],
            'educacao': ['educacao', 'aprender', 'conhecimento', 'dicas', 'tutorial'],
            'tecnologia': ['tecnologia', 'tech', 'inovacao', 'digital', 'futuro'],
            'lifestyle': ['lifestyle', 'vida', 'inspiracao', 'motivacao', 'bem_estar'],
            'humor': ['humor', 'engracado', 'comedia', 'risadas', 'diversao'],
            'musica': ['musica', 'som', 'ritmo', 'melodia', 'artista'],
            'esportes': ['esportes', 'fitness', 'exercicio', 'saude', 'acao'],
            'games': ['games', 'gaming', 'jogos', 'gameplay', 'gamer']
        }
        
        # Get category-specific hashtags or default ones
        base_hashtags = category_hashtags.get(category.lower(), ['viral', 'trending', 'brasil', 'conteudo'])
        
        # Add some general viral hashtags
        viral_hashtags = ['viral', 'trending', 'foryou', 'brasil', 'incrivel', 'top']
        
        # Combine and deduplicate
        all_hashtags = list(dict.fromkeys(base_hashtags + viral_hashtags))
        
        # Create engaging description
        description = f"🔥 {title} 🔥\n\nConteúdo incrível que você precisa ver! 💫\n\n👍 Curta se gostou!\n💬 Comente aqui embaixo!\n🔄 Compartilhe com os amigos!"
        
        # Generate platform-specific content
        platform_specific = {}
        for platform in platforms:
            if platform == 'youtube':
                platform_specific[platform] = {
                    'title': title,
                    'description': f"{description}\n\n🔔 Se inscreva no canal para mais conteúdo!\n🔥 Ative o sininho para não perder nenhum vídeo!",
                    'hashtags': all_hashtags[:10]
                }
            elif platform == 'instagram':
                platform_specific[platform] = {
                    'caption': f"{description}\n\n📸 Siga @seuperfil para mais!\n❤️ Salve este post!",
                    'hashtags': all_hashtags[:25],
                    'story_text': f"Novo post! {title[:50]}... Corre lá no feed! 🔥"
                }
            elif platform == 'tiktok':
                platform_specific[platform] = {
                    'caption': f"{title} 🔥 #fyp #viral #trending",
                    'hashtags': ['fyp', 'viral', 'trending'] + all_hashtags[:3]
                }
            elif platform == 'kawai':
                platform_specific[platform] = {
                    'caption': f"{title} ✨💖 Que fofo! Curtiu? 🥰",
                    'hashtags': all_hashtags[:8]
                }
        
        return {
            'hashtags': all_hashtags[:15],
            'description': description,
            'platform_specific': platform_specific,
            'engagement_tips': [
                'Use emojis para chamar atenção visual',
                'Poste no horário de pico (18h-20h)',
                'Faça perguntas para incentivar comentários',
                'Responda aos comentários rapidamente',
                'Use hashtags trending do momento'
            ],
            'optimized_title': title,
            'viral_score': 65,
            'fallback': True,
            'category': category,
            'generated_at': datetime.now().isoformat()
        }

    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        return self.is_initialized and self.client is not None

    async def analyze_viral_potential(self, content: Dict) -> Dict:
        """Analyze viral potential of content"""
        try:
            if not self.is_healthy():
                return self._get_basic_analysis(content)
            
            title = content.get('title', '')
            description = content.get('description', '')
            hashtags = content.get('hashtags', [])
            category = content.get('category', '')
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analise o potencial viral deste conteúdo brasileiro:
            
            Título: {title}
            Descrição: {description}
            Hashtags: {', '.join(hashtags)}
            Categoria: {category}
            
            Avalie de 0-100 e forneça:
            1. Score viral
            2. Pontos fortes
            3. Pontos de melhoria
            4. Elementos trending
            5. Melhor horário para postar
            
            Responda em JSON:
            {
                "viral_score": 85,
                "strengths": ["ponto1", "ponto2"],
                "improvements": ["melhoria1", "melhoria2"],
                "trending_elements": ["elemento1", "elemento2"],
                "optimal_times": ["18:00", "20:00"],
                "audience_appeal": "alto/medio/baixo"
            }
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um analista de conteúdo viral especialista no mercado brasileiro."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            try:
                analysis_data = json.loads(response.choices[0].message.content)
                return {
                    "viral_score": analysis_data.get("viral_score", 60),
                    "strengths": analysis_data.get("strengths", [])[:5],
                    "improvements": analysis_data.get("improvements", [])[:5],
                    "trending_elements": analysis_data.get("trending_elements", []),
                    "optimal_posting_times": analysis_data.get("optimal_times", ["18:00-20:00"]),
                    "audience_appeal": analysis_data.get("audience_appeal", "medio"),
                    "analysis_date": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                return self._get_basic_analysis(content)
                
        except Exception as e:
            logger.error(f"Viral analysis failed: {e}")
            return self._get_basic_analysis(content)

    def _get_basic_analysis(self, content: Dict) -> Dict:
        """Basic analysis when AI is not available"""
        title = content.get('title', '')
        hashtags = content.get('hashtags', [])
        description = content.get('description', '')
        
        score = 50
        strengths = []
        improvements = []
        
        # Basic scoring logic
        if len(title) > 10:
            score += 10
            strengths.append("Título com boa extensão")
        
        if any(word in title.lower() for word in ['incrível', 'viral', 'chocante', 'surpreendente']):
            score += 15
            strengths.append("Título possui palavras impactantes")
        
        if len(hashtags) >= 5:
            score += 10
            strengths.append("Boa quantidade de hashtags")
        
        if len(hashtags) < 3:
            improvements.append("Adicione mais hashtags relevantes")
        
        if len(description) < 100:
            improvements.append("Expanda a descrição do conteúdo")
        
        if 'viral' in [tag.lower() for tag in hashtags]:
            score += 10
            strengths.append("Usa hashtags virais")
        
        if not strengths:
            strengths = ["Conteúdo tem potencial básico"]
        
        if not improvements:
            improvements = ["Continue criando conteúdo consistente"]
        
        return {
            "viral_score": min(score, 100),
            "strengths": strengths,
            "improvements": improvements,
            "trending_elements": hashtags[:5],
            "optimal_posting_times": ["18:00-20:00", "12:00-14:00", "21:00-22:00"],
            "audience_appeal": "medio",
            "analysis_date": datetime.now().isoformat()
        }

    async def optimize_content_for_virality(self, content: Dict) -> Dict:
        """Optimize content for maximum viral potential"""
        try:
            # First analyze current content
            analysis = await self.analyze_viral_potential(content)
            
            if not self.is_healthy():
                return {**analysis, "optimization_tips": self._get_basic_optimization_tips()}
            
            # Generate optimization suggestions
            optimization_prompt = f"""
            Com base nesta análise de conteúdo:
            - Score atual: {analysis.get('viral_score', 50)}
            - Pontos fortes: {', '.join(analysis.get('strengths', []))}
            - Melhorias: {', '.join(analysis.get('improvements', []))}
            
            Conteúdo original:
            - Título: {content.get('title', '')}
            - Hashtags: {', '.join(content.get('hashtags', []))}
            
            Forneça otimizações específicas em JSON:
            {
                "optimized_hashtags": ["hashtag1", "hashtag2"],
                "title_suggestions": ["titulo1", "titulo2"],
                "optimization_tips": ["tip1", "tip2"],
                "trending_elements": {"hashtags": [], "topics": []},
                "optimal_timing": {"days": ["segunda", "terca"], "hours": ["18:00", "20:00"]}
            }
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em otimização de conteúdo viral para redes sociais brasileiras."},
                    {"role": "user", "content": optimization_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            try:
                optimization_data = json.loads(response.choices[0].message.content)
                return {
                    **analysis,
                    "optimized_hashtags": optimization_data.get("optimized_hashtags", []),
                    "title_suggestions": optimization_data.get("title_suggestions", []),
                    "optimization_tips": optimization_data.get("optimization_tips", []),
                    "trending_elements": optimization_data.get("trending_elements", {}),
                    "optimal_timing": optimization_data.get("optimal_timing", {})
                }
            except json.JSONDecodeError:
                return {**analysis, "optimization_tips": self._get_basic_optimization_tips()}
                
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            analysis = await self.analyze_viral_potential(content)
            return {**analysis, "optimization_tips": self._get_basic_optimization_tips()}

    def _get_basic_optimization_tips(self) -> List[str]:
        """Basic optimization tips when AI is not available"""
        return [
            "Use hashtags trending do momento",
            "Crie títulos com gatilhos emocionais",
            "Poste no horário de pico (18h-20h)",
            "Adicione emojis para chamar atenção",
            "Faça perguntas para incentivar interação",
            "Use palavras de impacto no título",
            "Mantenha consistência nas postagens",
            "Responda comentários rapidamente",
            "Crie conteúdo que gere discussão",
            "Use tendências atuais do Brasil"
        ]