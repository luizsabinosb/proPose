#!/bin/bash
# Script para iniciar o backend com configurações corretas

echo "🚀 Iniciando BodyVision Backend..."

# Navega para o diretório backend
cd "$(dirname "$0")"

# Verifica se está no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Erro: Execute este script a partir do diretório backend/"
    exit 1
fi

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Verifica se as dependências estão instaladas
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Descobre o IP local
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig en0 2>/dev/null | grep "inet " | awk '{print $2}')

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="localhost"
fi

echo ""
echo "✅ Backend configurado!"
echo "🌐 Servidor iniciando em:"
echo "   - Local: http://localhost:8000"
echo "   - Rede:  http://${LOCAL_IP}:8000"
echo "📚 Documentação: http://localhost:8000/docs"
echo "🔗 Use o IP acima no Flutter se usar dispositivo físico"
echo ""
echo "⚠️  Para parar o servidor, pressione Ctrl+C"
echo ""

# Inicia servidor aceitando conexões externas
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

