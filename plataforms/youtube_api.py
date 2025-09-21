from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import json
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')

# Configurar CORS
CORS(app)

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

# Criar pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configurações OAuth2
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'
]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_authenticated_service():
    """Obtém serviço YouTube autenticado"""
    credentials = None
    
    # Carregar credenciais salvas
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    
    # Se não há credenciais válidas, retorna None
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Salvar credenciais atualizadas
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
        else:
            return None
    
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def create_oauth_flow():
    """Cria flow OAuth2"""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES
        )
        flow.redirect_uri = url_for('oauth_callback', _external=True)
        return flow
    except Exception as e:
        logger.error(f"Erro ao criar flow OAuth: {e}")
        return None

@app.route('/')
def index():
    """Página inicial com informações da API"""
    return jsonify({
        'message': '🚀 API YouTube Upload em Python',
        'version': '1.0.0',
        'endpoints': {
            'GET /status': 'Status da API',
            'GET /auth': 'Iniciar autenticação',
            'GET /auth/callback': 'Callback OAuth2',
            'POST /upload': 'Upload de vídeo',
            'GET /videos': 'Listar vídeos',
            'PUT /video/<video_id>': 'Atualizar vídeo',
            'DELETE /video/<video_id>': 'Deletar vídeo'
        }
    })

@app.route('/status')
def status():
    """Verifica status da API e autenticação"""
    youtube = get_authenticated_service()
    is_authenticated = youtube is not None
    
    return jsonify({
        'status': 'API YouTube Upload funcionando',
        'authenticated': is_authenticated,
        'timestamp': datetime.now().isoformat(),
        'python_version': '3.x',
        'framework': 'Flask'
    })

@app.route('/auth')
def auth():
    """Inicia processo de autenticação OAuth2"""
    flow = create_oauth_flow()
    if not flow:
        return jsonify({'error': 'Erro ao inicializar autenticação. Verifique client_secrets.json'}), 500
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/auth/callback')
def oauth_callback():
    """Callback OAuth2"""
    try:
        state = session.get('state')
        flow = create_oauth_flow()
        if not flow:
            return jsonify({'error': 'Erro na configuração OAuth'}), 500
        
        flow.fetch_token(authorization_response=request.url)
        
        # Salvar credenciais
        credentials = flow.credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
        
        return jsonify({
            'message': '✅ Autenticado com sucesso!',
            'authenticated': True
        })
    
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return jsonify({'error': 'Erro na autenticação', 'details': str(e)}), 400

@app.route('/upload', methods=['POST'])
def upload_video():
    """Upload de vídeo para o YouTube"""
    try:
        # Verificar autenticação
        youtube = get_authenticated_service()
        if not youtube:
            return jsonify({'error': 'Não autenticado. Acesse /auth primeiro.'}), 401
        
        # Verificar se arquivo foi enviado
        if 'video' not in request.files:
            return jsonify({'error': 'Arquivo de vídeo é obrigatório'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Obter metadados do formulário
        title = request.form.get('title', 'Vídeo sem título')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '')
        privacy = request.form.get('privacy', 'private')
        category_id = request.form.get('categoryId', '22')
        
        # Processar tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Configurar metadados do vídeo
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tag_list,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy,
                'embeddable': True,
                'publicStatsViewable': True
            }
        }
        
        # Configurar upload
        media = MediaFileUpload(
            filepath,
            chunksize=-1,
            resumable=True,
            mimetype=None
        )
        
        logger.info(f"Iniciando upload do vídeo: {title}")
        
        # Fazer upload
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = insert_request.execute()
        
        # Remover arquivo temporário
        try:
            os.remove(filepath)
        except:
            pass
        
        # Resposta de sucesso
        video_info = {
            'videoId': response['id'],
            'title': response['snippet']['title'],
            'url': f"https://www.youtube.com/watch?v={response['id']}",
            'uploadDate': datetime.now().isoformat(),
            'privacyStatus': response['status']['privacyStatus']
        }
        
        return jsonify({
            'success': True,
            'message': '✅ Vídeo enviado com sucesso!',
            'video': video_info
        })
    
    except HttpError as e:
        # Limpar arquivo em caso de erro
        try:
            if 'filepath' in locals():
                os.remove(filepath)
        except:
            pass
        
        logger.error(f"Erro HTTP no upload: {e}")
        return jsonify({
            'error': 'Erro no upload do vídeo',
            'details': str(e)
        }), 500
    
    except Exception as e:
        # Limpar arquivo em caso de erro
        try:
            if 'filepath' in locals():
                os.remove(filepath)
        except:
            pass
        
        logger.error(f"Erro no upload: {e}")
        return jsonify({
            'error': 'Erro interno no upload',
            'details': str(e)
        }), 500

@app.route('/videos')
def list_videos():
    """Lista vídeos do canal"""
    try:
        youtube = get_authenticated_service()
        if not youtube:
            return jsonify({'error': 'Não autenticado'}), 401
        
        # Buscar vídeos do canal
        search_response = youtube.search().list(
            part='snippet',
            forMine=True,
            type='video',
            maxResults=50
        ).execute()
        
        videos = []
        for item in search_response['items']:
            video_info = {
                'videoId': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'publishedAt': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video_info)
        
        return jsonify({
            'success': True,
            'count': len(videos),
            'videos': videos
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao listar vídeos',
            'details': str(e)
        }), 500

@app.route('/video/<video_id>', methods=['PUT'])
def update_video(video_id):
    """Atualiza metadados de um vídeo"""
    try:
        youtube = get_authenticated_service()
        if not youtube:
            return jsonify({'error': 'Não autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON obrigatórios'}), 400
        
        # Construir corpo da requisição
        body = {'id': video_id}
        
        if any(key in data for key in ['title', 'description', 'tags']):
            body['snippet'] = {}
            if 'title' in data:
                body['snippet']['title'] = data['title']
            if 'description' in data:
                body['snippet']['description'] = data['description']
            if 'tags' in data:
                body['snippet']['tags'] = [tag.strip() for tag in data['tags'].split(',')]
        
        if 'privacy' in data:
            body['status'] = {'privacyStatus': data['privacy']}
        
        # Atualizar vídeo
        response = youtube.videos().update(
            part=','.join([key for key in body.keys() if key != 'id']),
            body=body
        ).execute()
        
        return jsonify({
            'success': True,
            'message': '✅ Vídeo atualizado com sucesso!',
            'video': {
                'videoId': response['id'],
                'title': response.get('snippet', {}).get('title'),
                'url': f"https://www.youtube.com/watch?v={response['id']}"
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao atualizar vídeo',
            'details': str(e)
        }), 500

@app.route('/video/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Deleta um vídeo"""
    try:
        youtube = get_authenticated_service()
        if not youtube:
            return jsonify({'error': 'Não autenticado'}), 401
        
        youtube.videos().delete(id=video_id).execute()
        
        return jsonify({
            'success': True,
            'message': '✅ Vídeo deletado com sucesso!'
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao deletar vídeo',
            'details': str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handler para arquivo muito grande"""
    return jsonify({
        'error': 'Arquivo muito grande',
        'details': 'Limite máximo de 2GB'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """Handler para erro interno"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'details': str(e)
    }), 500

if __name__ == '__main__':
    print("🚀 Iniciando API YouTube Upload em Python...")
    print("📝 Endpoints disponíveis:")
    print("   GET  /                 - Informações da API")
    print("   GET  /status           - Status da API")
    print("   GET  /auth             - Iniciar autenticação")
    print("   POST /upload           - Upload de vídeo")
    print("   GET  /videos           - Listar vídeos")
    print("   PUT  /video/<id>       - Atualizar vídeo")
    print("   DELETE /video/<id>     - Deletar vídeo")
    print()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)