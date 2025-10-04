python -c "
import json
import os

# Verificar arquivo
if not os.path.exists('client_secret.json'):
    print('✗ client_secret.json não encontrado')
    exit(1)

# Verificar estrutura
with open('client_secret.json') as f:
    data = json.load(f)
    
if 'installed' in data:
    print('✓ Tipo correto: Desktop app')
    print(f'✓ Client ID: {data[\"installed\"][\"client_id\"][:20]}...')
elif 'web' in data:
    print('✗ ERRO: Tipo incorreto (web)')
    print('Recrie a credencial como Desktop app!')
else:
    print('✗ Estrutura inválida')
"