#!/bin/bash

# --- Script para parar o aplicativo macOS ---

BACKEND_PID_FILE=".backend_macos_pid"
FLUTTER_PID_FILE=".flutter_macos_pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_message() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                    🛑 Parando ProPosing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Encerrar Flutter
if [ -f "$FLUTTER_PID_FILE" ]; then
    FLUTTER_PID=$(cat "$FLUTTER_PID_FILE")
    log_message "Encerrando aplicativo Flutter (PID: $FLUTTER_PID)..."
    kill "$FLUTTER_PID" 2>/dev/null
    rm -f "$FLUTTER_PID_FILE"
    log_success "Aplicativo Flutter encerrado"
else
    log_warning "Nenhum processo Flutter encontrado (PID file não existe)"
fi

# Encerrar Backend
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    log_message "Encerrando backend (PID: $BACKEND_PID)..."
    kill "$BACKEND_PID" 2>/dev/null
    rm -f "$BACKEND_PID_FILE"
    log_success "Backend encerrado"
else
    log_warning "Nenhum processo Backend encontrado (PID file não existe)"
fi

echo ""
log_success "ProPosing encerrado com sucesso!"
echo ""
