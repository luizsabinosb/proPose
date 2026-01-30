#!/bin/bash
# Script para iniciar o projeto BodyVision completo
# Executa backend e Flutter automaticamente

set -e  # Para em caso de erro

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
INTERFACE_DIR="$PROJECT_DIR/interface"
BACKEND_PID_FILE="$PROJECT_DIR/.backend.pid"

# Função para limpar processos ao sair
cleanup() {
    echo -e "\n${YELLOW}🛑 Parando processos...${NC}"
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}   Parando backend (PID: $BACKEND_PID)...${NC}"
            kill "$BACKEND_PID" 2>/dev/null || true
            sleep 1
            # Força kill se ainda estiver rodando
            if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                kill -9 "$BACKEND_PID" 2>/dev/null || true
            fi
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # Mata processos do Flutter se necessário
    pkill -f "flutter run" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Processos parados${NC}"
    exit 0
}

# Registra função de cleanup
trap cleanup SIGINT SIGTERM EXIT

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║     BodyVision - Iniciando Projeto        ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Verifica se está no diretório correto
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$INTERFACE_DIR" ]; then
    echo -e "${RED}❌ Erro: Execute este script da raiz do projeto BodyVision${NC}"
    exit 1
fi

# ============================================
# 1. Verificar e preparar Backend
# ============================================
echo -e "\n${YELLOW}📦 Preparando Backend...${NC}"

cd "$BACKEND_DIR"

# Verifica ambiente virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}   Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativa ambiente virtual
source venv/bin/activate

# Verifica dependências
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}   Instalando dependências do backend...${NC}"
    pip install -r requirements.txt --quiet
fi

# Verifica se backend já está rodando
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}   ⚠️  Porta 8000 já está em uso${NC}"
    read -p "   Deseja parar o processo existente? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        echo -e "${RED}   ❌ Não é possível iniciar. Porta 8000 ocupada.${NC}"
        exit 1
    fi
fi

# ============================================
# 2. Iniciar Backend
# ============================================
echo -e "\n${GREEN}🚀 Iniciando Backend...${NC}"

# Descobre IP local
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig en0 2>/dev/null | grep "inet " | awk '{print $2}' || echo "localhost")

# Inicia backend em background
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/.backend.log" 2>&1 &
BACKEND_PID=$!

# Salva PID
echo $BACKEND_PID > "$BACKEND_PID_FILE"

# Aguarda backend iniciar
echo -e "${YELLOW}   Aguardando backend iniciar...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Backend iniciado com sucesso!${NC}"
        echo -e "${BLUE}   🌐 Local: http://localhost:8000${NC}"
        echo -e "${BLUE}   🌐 Rede:  http://${LOCAL_IP}:8000${NC}"
        echo -e "${BLUE}   📚 Docs:  http://localhost:8000/docs${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}   ❌ Backend não iniciou após 30 segundos${NC}"
        echo -e "${YELLOW}   Verifique os logs: cat $PROJECT_DIR/.backend.log${NC}"
        exit 1
    fi
    sleep 1
done

# ============================================
# 3. Verificar e preparar Flutter
# ============================================
echo -e "\n${YELLOW}📱 Preparando Flutter...${NC}"

cd "$INTERFACE_DIR"

# Verifica se Flutter está instalado
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}   ❌ Flutter não encontrado${NC}"
    echo -e "${YELLOW}   💡 Instale Flutter: https://flutter.dev/docs/get-started/install${NC}"
    echo -e "${YELLOW}   💡 Ou adicione ao PATH: export PATH=\"\$PATH:$INTERFACE_DIR/flutter/bin\"${NC}"
    exit 1
fi

# Verifica dependências Flutter
if [ ! -d ".dart_tool" ] && [ ! -f "pubspec.lock" ]; then
    echo -e "${YELLOW}   Instalando dependências do Flutter...${NC}"
    flutter pub get
fi

# Atualiza IP no api_client.dart se necessário
API_CLIENT_FILE="$INTERFACE_DIR/lib/data/api/api_client.dart"
if [ -f "$API_CLIENT_FILE" ]; then
    # Verifica se precisa atualizar IP (opcional - comentado para não forçar)
    # sed -i.bak "s|http://[0-9.]*:8000|http://${LOCAL_IP}:8000|g" "$API_CLIENT_FILE"
    echo -e "${GREEN}   ✅ API Client configurado${NC}"
fi

# ============================================
# 4. Iniciar Flutter
# ============================================
echo -e "\n${GREEN}🚀 Iniciando Interface Flutter...${NC}"
echo -e "${BLUE}   💡 Use Ctrl+C para parar tudo${NC}"
echo -e "${BLUE}   💡 Backend continuará rodando em: http://localhost:8000${NC}"
echo ""

# Lista dispositivos disponíveis
echo -e "${YELLOW}📱 Dispositivos disponíveis:${NC}"
flutter devices

echo ""
echo -e "${YELLOW}Escolha o dispositivo (ou Enter para web/Chrome):${NC}"
read -p "> " DEVICE_CHOICE

# Inicia Flutter
if [ -z "$DEVICE_CHOICE" ]; then
    # Tenta Chrome primeiro, depois primeiro dispositivo disponível
    if flutter devices | grep -q "Chrome"; then
        flutter run -d chrome
    else
        flutter run
    fi
else
    flutter run -d "$DEVICE_CHOICE"
fi
