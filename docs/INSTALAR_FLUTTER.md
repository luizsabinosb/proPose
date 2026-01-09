# 📱 Como Instalar Flutter no macOS

## 🚀 Método Rápido (Recomendado)

### 1. Baixar Flutter

```bash
# Navegar para o diretório onde quer instalar
cd ~

# Baixar Flutter SDK
git clone https://github.com/flutter/flutter.git -b stable

# OU baixar ZIP: https://docs.flutter.dev/get-started/install/macos
```

### 2. Adicionar ao PATH

```bash
# Editar arquivo de configuração do shell
nano ~/.zshrc  # ou ~/.bash_profile se usar bash

# Adicionar estas linhas no final:
export PATH="$PATH:$HOME/flutter/bin"
export PATH="$PATH:$HOME/flutter/bin/cache/dart-sdk/bin"

# Salvar (Ctrl+O, Enter, Ctrl+X)

# Recarregar configuração
source ~/.zshrc
```

### 3. Verificar Instalação

```bash
flutter doctor
```

Este comando verifica se tudo está instalado corretamente.

---

## 📦 Instalação via Homebrew (Alternativa)

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Flutter
brew install --cask flutter

# Verificar
flutter doctor
```

---

## ✅ Verificar se Funcionou

```bash
flutter --version
```

Deve mostrar algo como:
```
Flutter 3.x.x • channel stable
```

---

## 🔧 Próximos Passos

Após instalar Flutter:

1. **Configurar Xcode** (necessário para iOS):
   ```bash
   sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
   sudo xcodebuild -license accept
   ```

2. **Instalar ferramentas necessárias:**
   ```bash
   flutter doctor -v
   ```
   
   Siga as instruções para instalar o que faltar.

3. **Testar no projeto:**
   ```bash
   cd interface
   flutter pub get
   flutter run
   ```

---

## ⚠️ Requisitos

- **macOS 10.14 (Mojave) ou superior**
- **Xcode** (para desenvolvimento iOS)
- **Android Studio** (opcional, para Android)

---

## 💡 Alternativa: Testar Só o Backend

**Se não quiser instalar Flutter agora**, você pode:

1. ✅ Testar apenas o **backend** (funciona perfeitamente!)
2. ✅ Usar a **documentação Swagger** em `http://localhost:8000/docs`
3. ✅ Testar endpoints com **curl** ou **Postman**
4. ✅ Instalar Flutter depois quando quiser testar a interface

**O backend é independente e funciona sozinho!** 🚀

---

**Precisa de ajuda?** Verifique: https://docs.flutter.dev/get-started/install/macos

