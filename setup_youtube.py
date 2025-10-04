#!/usr/bin/env python3
"""
Script para configurar credenciais do YouTube automaticamente
"""

import json
import os
from pathlib import Path

def create_client_secret_file():
    """Criar arquivo client_secret.json com as credenciais"""
    
    # Suas credenciais
    client_id = "1002764123481-d3upmcb4ig7gr3fgepmm71sar53ais7r.apps.googleusercontent.com"
    client_secret = "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"
    
    # Estrutura correta para Desktop app
    client_config = {
        "installed": {
            "client_id": client_id,
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # Salvar arquivo
    with open('client_secret.json', 'w') as f:
        json.dump(client_config, f, indent=2)
    
    print("✓ client_secret.json criado com sucesso!")
    print(f"✓ Client ID: {client_id[:30]}...")
    
    return True

def update_env_file():
    """Atualizar arquivo .env"""
    
    env_content = """# Flask Configuration
SECRET_KEY=change-this-in-production-use-random-string
DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=524288000

# OpenAI Configuration (OBRIGATÓRIO)
OPENAI_API_KEY=your-openai-key-here

# YouTube Configuration
YOUTUBE_CLIENT_ID=1002764123481-d3upmcb4ig7gr3fgepmm71sar53ais7r.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=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
YOUTUBE_CREDENTIALS_PATH=client_secret.json
YOUTUBE_REDIRECT_URI=http://localhost:5000/oauth/youtube/callback

# Database Configuration
DATABASE_URL=sqlite:///social_media_automation.db

# Instagram (opcional)
INSTAGRAM_ACCESS_TOKEN=

# TikTok (opcional)
TIKTOK_ACCESS_TOKEN=

# Kawai (opcional)
KAWAI_API_KEY=
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ .env atualizado com sucesso!")
    print("\n⚠️  IMPORTANTE: Configure sua chave OpenAI no .env")

def clean_old_tokens():
    """Remover tokens antigos"""
    if os.path.exists('youtube_token.pickle'):
        os.remove('youtube_token.pickle')
        print("✓ Token antigo removido")
    else:
        print("• Nenhum token antigo encontrado")

def test_configuration():
    """Testar se a configuração está correta"""
    
    print("\n" + "="*50)
    print("VERIFICANDO CONFIGURAÇÃO")
    print("="*50)
    
    # Verificar client_secret.json
    if os.path.exists('client_secret.json'):
        with open('client_secret.json') as f:
            data = json.load(f)
            if 'installed' in data:
                print("✓ client_secret.json está correto (Desktop app)")
            else:
                print("✗ client_secret.json tem estrutura incorreta")
                return False
    else:
        print("✗ client_secret.json não encontrado")
        return False
    
    # Verificar .env
    if os.path.exists('.env'):
        print("✓ .env existe")
        with open('.env') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                if 'your-openai-key-here' in content:
                    print("⚠️  Configure sua chave OpenAI no .env")
                else:
                    print("✓ .env configurado")
    else:
        print("✗ .env não encontrado")
        return False
    
    return True

def main():
    print("="*50)
    print("CONFIGURAÇÃO DAS CREDENCIAIS DO YOUTUBE")
    print("="*50)
    
    # 1. Criar client_secret.json
    print("\n1. Criando client_secret.json...")
    create_client_secret_file()
    
    # 2. Atualizar .env
    print("\n2. Atualizando .env...")
    update_env_file()
    
    # 3. Limpar tokens antigos
    print("\n3. Limpando tokens antigos...")
    clean_old_tokens()
    
    # 4. Testar configuração
    if test_configuration():
        print("\n" + "="*50)
        print("CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*50)
        print("\nPRÓXIMOS PASSOS:")
        print("1. Edite .env e adicione sua chave OpenAI")
        print("2. Execute: python run.py")
        print("3. Acesse: http://localhost:5000")
        print("4. Vá em 'Contas' e clique em 'Conectar' no YouTube")
        print("\n⚠️  IMPORTANTE: As credenciais foram expostas aqui.")
        print("   Considere regenerar no Google Cloud Console depois.")
    else:
        print("\n✗ Houve problemas na configuração")

if __name__ == '__main__':
    main()