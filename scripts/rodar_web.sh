#!/bin/bash
# Script para rodar ProPosing na web (Chrome)
# Requer: backend rodando + localhost (ou HTTPS) para câmera funcionar

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
INTERFACE_DIR="$PROJECT_DIR/interface"
BACKEND_PID_FILE="$PROJECT_DIR/.backend.pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$PROJECT_DIR"

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend não está rodando. Iniciando...${NC}"
    cd "$BACKEND_DIR"
    pip3 install -q -r requirements.txt 2>/dev/null || true
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/.backend.log" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    echo -e "${GREEN}   Backend iniciado (PID: $(cat "$BACKEND_PID_FILE"))${NC}"
    sleep 3
    cd "$PROJECT_DIR"
fi

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend não respondeu. Verifique: cat .backend.log${NC}"
    exit 1
fi

echo -e "${BLUE}🌐 Iniciando ProPosing na web...${NC}"
echo -e "${BLUE}   Câmera requer localhost ou HTTPS${NC}"
echo ""

cd "$INTERFACE_DIR"
flutter pub get
flutter run -d chrome
