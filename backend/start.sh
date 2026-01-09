#!/bin/bash
# Script para iniciar o backend

echo "🚀 Iniciando BodyVision Backend..."

# Verifica se está no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Erro: Execute este script a partir do diretório backend/"
    exit 1
fi

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verifica se as dependências estão instaladas
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Inicia servidor
echo "🌐 Iniciando servidor em http://0.0.0.0:8000"
echo "📚 Documentação: http://localhost:8000/docs"
echo "🔗 Aceitando conexões externas (para Flutter em dispositivos físicos)"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

