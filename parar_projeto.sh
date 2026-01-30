#!/bin/bash
# Script para parar todos os processos do BodyVision

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PID_FILE="$PROJECT_DIR/.backend.pid"

echo -e "${YELLOW}🛑 Parando BodyVision...${NC}"

# Para backend
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}   Parando backend (PID: $BACKEND_PID)...${NC}"
        kill "$BACKEND_PID" 2>/dev/null || true
        sleep 1
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            kill -9 "$BACKEND_PID" 2>/dev/null || true
        fi
        echo -e "${GREEN}   ✅ Backend parado${NC}"
    fi
    rm -f "$BACKEND_PID_FILE"
fi

# Para processos na porta 8000
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}   Parando processo na porta 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}   ✅ Porta 8000 liberada${NC}"
fi

# Para processos do Flutter
if pgrep -f "flutter run" > /dev/null; then
    echo -e "${YELLOW}   Parando Flutter...${NC}"
    pkill -f "flutter run" 2>/dev/null || true
    echo -e "${GREEN}   ✅ Flutter parado${NC}"
fi

echo -e "${GREEN}✅ Todos os processos parados${NC}"
