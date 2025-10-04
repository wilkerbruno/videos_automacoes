#!/usr/bin/env python3
"""
Script de Atualização Automática - Social Media Automation
Executa todas as atualizações necessárias automaticamente
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

class SystemUpdater:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.errors = []
        self.warnings = []
        
    def print_header(self, text):
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
    
    def print_step(self, text):
        print(f"\n>> {text}")
    
    def print_success(self, text):
        print(f"✓ {text}")
    
    def print_error(self, text):
        print(f"✗ {text}")
        self.errors.append(text)
    
    def print_warning(self, text):
        print(f"⚠ {text}")
        self.warnings.append(text)
    
    def create_backup(self):
        """Criar backup dos arquivos existentes"""
        self.print_step("Criando backup dos arquivos existentes...")
        
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            files_to_backup = [
                'app.py',
                'services/video_processor.py',
                'static/js/app.js',
            ]
            
            for file_path in files_to_backup:
                source = self.project_root / file_path
                if source.exists():
                    dest = self.backup_dir / file_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    self.print_success(f"Backup: {file_path}")
            
            self.print_success(f"Backup salvo em: {self.backup_dir}")
            return True
            
        except Exception as e:
            self.print_error(f"Erro no backup: {e}")
            return False
    
    def create_directories(self):
        """Criar estrutura de diretórios"""
        self.print_step("Criando diretórios...")
        
        directories = [
            'services', 'static/css', 'static/js', 'templates',
            'models', 'utils', 'uploads', 'temp_videos', 'logs'
        ]
        
        for directory in directories:
            try:
                (self.project_root / directory).mkdir(parents=True, exist_ok=True)
                self.print_success(f"Diretório: {directory}")
            except Exception as e:
                self.print_error(f"Erro em {directory}: {e}")
    
    def create_youtube_service(self):
        """Criar YouTube service"""
        self.print_step("Criando YouTube service...")
        
        content = '''# services/youtube_service.py
import os
import logging
import pickle
from typing import Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class YouTubeService:
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    def __init__(self):
        self.credentials = None
        self.youtube = None
        self.token_file = 'youtube_token.pickle'
        
    def authenticate(self, credentials_path: Optional[str] = None) -> bool:
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not credentials_path:
                        credentials_path = os.getenv('YOUTUBE_CREDENTIALS_PATH', 'client_secret.json')
                    
                    if not os.path.exists(credentials_path):
                        logger.error(f"Credentials not found: {credentials_path}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            logger.info("YouTube authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: list, category_id: str = "22", 
                    privacy_status: str = "public") -> Dict[str, Any]:
        try:
            if not self.youtube:
                if not self.authenticate():
                    return {'success': False, 'error': 'Authentication failed'}
            
            body = {
                'snippet': {
                    'title': title[:100],
                    'description': description[:5000],
                    'tags': tags[:15] if tags else [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/*')
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'status': privacy_status
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_channel_info(self) -> Dict[str, Any]:
        try:
            if not self.youtube:
                if not self.authenticate():
                    return {'success': False, 'error': 'Authentication failed'}
            
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'success': True,
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                }
            
            return {'success': False, 'error': 'No channel found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_connection(self) -> bool:
        try:
            if not self.youtube:
                return self.authenticate()
            result = self.get_channel_info()
            return result.get('success', False)
        except:
            return False
    
    def is_authenticated(self) -> bool:
        return self.youtube is not None and self.credentials is not None
'''
        
        try:
            file_path = self.project_root / 'services' / 'youtube_service.py'
            file_path.write_text(content, encoding='utf-8')
            self.print_success("YouTube service criado")
            return True
        except Exception as e:
            self.print_error(f"Erro ao criar YouTube service: {e}")
            return False
    
    def update_gitignore(self):
        """Atualizar .gitignore"""
        self.print_step("Atualizando .gitignore...")
        
        content = '''# Environment
.env
venv/
env/

# YouTube
client_secret.json
*.pickle

# Uploads
uploads/
temp_videos/

# Logs
logs/
*.log

# Python
__pycache__/
*.pyc

# Database
*.db

# Backups
backup_*/
'''
        
        try:
            (self.project_root / '.gitignore').write_text(content, encoding='utf-8')
            self.print_success(".gitignore atualizado")
            return True
        except Exception as e:
            self.print_error(f"Erro: {e}")
            return False
    
    def install_dependencies(self):
        """Instalar dependências"""
        self.print_step("Instalando dependências...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            self.print_success("pip atualizado")
            
            req_file = self.project_root / 'requirements.txt'
            if req_file.exists():
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(req_file)])
                self.print_success("Dependências instaladas")
                return True
            else:
                self.print_warning("requirements.txt não encontrado")
                return False
                
        except Exception as e:
            self.print_error(f"Erro: {e}")
            return False
    
    def check_ffmpeg(self):
        """Verificar ffmpeg"""
        self.print_step("Verificando ffmpeg...")
        
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, check=True)
            self.print_success("ffmpeg instalado")
            return True
        except:
            self.print_warning("ffmpeg não encontrado - instale para remover metadados")
            return False
    
    def print_summary(self):
        """Imprimir resumo"""
        self.print_header("RESUMO DA ATUALIZAÇÃO")
        
        if not self.errors and not self.warnings:
            print("\n✓ Atualização concluída com sucesso!")
        else:
            if self.warnings:
                print(f"\n⚠ {len(self.warnings)} avisos")
            if self.errors:
                print(f"\n✗ {len(self.errors)} erros")
        
        print("\nPRÓXIMOS PASSOS:")
        print("1. Configure .env com suas chaves")
        print("2. Siga YOUTUBE_SETUP_GUIDE.md")
        print("3. Execute: python run.py")
        print("\nBackup em:", self.backup_dir)
    
    def run(self):
        """Executar atualização"""
        self.print_header("ATUALIZAÇÃO AUTOMÁTICA")
        print("Data:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        response = input("\nContinuar? (s/n): ").strip().lower()
        if response != 's':
            print("Cancelado.")
            return
        
        steps = [
            self.create_backup,
            self.create_directories,
            self.create_youtube_service,
            self.update_gitignore,
            self.check_ffmpeg,
            self.install_dependencies
        ]
        
        for step in steps:
            try:
                step()
            except Exception as e:
                self.print_error(f"Erro: {e}")
        
        self.print_summary()

def main():
    updater = SystemUpdater()
    updater.run()

if __name__ == '__main__':
    main()