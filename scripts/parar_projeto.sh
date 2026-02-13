#!/bin/bash
# Script para parar todos os processos do ProPosing
# Funciona com rodar_macos.sh, rodar_web.sh e iniciar_backend.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${YELLOW}🛑 Parando ProPosing...${NC}"

for PID_FILE in .backend.pid .backend_macos_pid; do
  if [ -f "$PID_FILE" ]; then
    BACKEND_PID=$(cat "$PID_FILE")
    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
      echo -e "${YELLOW}   Parando backend (PID: $BACKEND_PID)...${NC}"
      kill "$BACKEND_PID" 2>/dev/null || true
      sleep 1
      ps -p "$BACKEND_PID" > /dev/null 2>&1 && kill -9 "$BACKEND_PID" 2>/dev/null || true
      echo -e "${GREEN}   ✅ Backend parado${NC}"
    fi
    rm -f "$PID_FILE"
  fi
done

if [ -f ".flutter_macos_pid" ]; then
  FLUTTER_PID=$(cat ".flutter_macos_pid")
  if ps -p "$FLUTTER_PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}   Parando Flutter (PID: $FLUTTER_PID)...${NC}"
    kill "$FLUTTER_PID" 2>/dev/null || true
    echo -e "${GREEN}   ✅ Flutter parado${NC}"
  fi
  rm -f ".flutter_macos_pid"
fi

if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}   Parando processo na porta 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}   ✅ Porta 8000 liberada${NC}"
fi

if pgrep -f "flutter run" > /dev/null; then
    echo -e "${YELLOW}   Parando Flutter...${NC}"
    pkill -f "flutter run" 2>/dev/null || true
    echo -e "${GREEN}   ✅ Flutter parado${NC}"
fi

echo -e "${GREEN}✅ Todos os processos parados${NC}"
