import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'
]

def test_auth():
    creds = None
    
    # Remove token antigo
    if os.path.exists('youtube_token.pickle'):
        os.remove('youtube_token.pickle')
        print("Token antigo removido")
    
    # Nova autenticação
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    
    # Salvar token
    with open('youtube_token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    # Testar API
    youtube = build('youtube', 'v3', credentials=creds)
    request = youtube.channels().list(part='snippet', mine=True)
    response = request.execute()
    
    if response['items']:
        print(f"✓ Autenticação bem-sucedida!")
        print(f"Canal: {response['items'][0]['snippet']['title']}")
        return True
    else:
        print("✗ Nenhum canal encontrado")
        return False

if __name__ == '__main__':
    try:
        test_auth()
    except Exception as e:
        print(f"Erro: {e}")