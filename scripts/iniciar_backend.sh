#!/bin/bash
# Inicia apenas o backend (para testes de API, desenvolvimento)
# Uso: ./scripts/iniciar_backend.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR/backend" || exit 1

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip3 install -r requirements.txt
fi

echo "🚀 Backend em http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
