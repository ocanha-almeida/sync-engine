#!/bin/bash
echo "🚀 Iniciando a instalação do Sync Engine (Linux)..."

INSTALL_DIR="$HOME/.local/share/sync-engine"
BIN_DIR="$HOME/.local/bin"

# Cria as pastas necessárias silenciosamente
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# ⚠️ MUDANÇA V6.0: Copia todos os arquivos Python da pasta atual (módulos e motor)
cp *.py "$INSTALL_DIR/"

# Aplica as permissões e recria o atalho global de forma forçada
chmod +x "$INSTALL_DIR/sync_engine.py"
ln -sf "$INSTALL_DIR/sync_engine.py" "$BIN_DIR/sync-engine"

echo "✅ Arquivos instalados em $INSTALL_DIR"
echo "✅ Comando 'sync-engine' vinculado em $BIN_DIR"

# Verifica se a pasta do atalho está na memória do terminal
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  AVISO CRÍTICO: O diretório $BIN_DIR não está no seu PATH."
    echo "Para que o comando 'sync-engine' funcione de qualquer lugar,"
    echo "adicione a seguinte linha ao final do seu arquivo ~/.bashrc ou ~/.zshrc:"
    echo ""
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Depois, rode: source ~/.bashrc"
fi

echo "🎉 Instalação concluída!"