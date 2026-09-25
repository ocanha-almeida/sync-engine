#!/bin/bash

INSTALL_DIR="$HOME/.local/share/sync-engine"
BIN_DIR="$HOME/.local/bin"
SERVICE_FILE="$HOME/.config/systemd/user/sync-engine.service"
CONFIG_DIR="$HOME/.config/sync_engine"

# ==========================================
# UNINSTALL / PURGE ROUTINES
# ==========================================
if [ "$1" == "uninstall" ] || [ "$1" == "purge" ]; then
    echo "🗑️ Starting Sync Engine removal..."
    echo "   Iniciando a remoção do Sync Engine..."
    
    # 1. Para e desabilita o serviço se estiver rodando
    if systemctl --user is-active --quiet sync-engine.service 2>/dev/null; then
        systemctl --user stop sync-engine.service
        systemctl --user disable sync-engine.service
        echo "🛑 Background service stopped and disabled."
        echo "   Serviço de segundo plano parado e desabilitado."
    fi

    # 2. Remove o arquivo do systemd e limpa a memória
    if [ -f "$SERVICE_FILE" ]; then
        rm -f "$SERVICE_FILE"
        systemctl --user daemon-reload
        echo "✅ Systemd service file removed."
        echo "   Arquivo de serviço do Systemd removido."
    fi

    # 3. Remove o atalho do terminal
    if [ -L "$BIN_DIR/sync-engine" ] || [ -f "$BIN_DIR/sync-engine" ]; then
        rm -f "$BIN_DIR/sync-engine"
        echo "✅ 'sync-engine' command removed."
        echo "   Comando 'sync-engine' removido."
    fi

    # 4. Remove a pasta de instalação (módulos python)
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        echo "✅ Core engine files removed ($INSTALL_DIR)."
        echo "   Arquivos principais do motor removidos ($INSTALL_DIR)."
    fi

    # 5. Executa a destruição das configurações se o modo for PURGE
    if [ "$1" == "purge" ]; then
        if [ -d "$CONFIG_DIR" ]; then
            rm -rf "$CONFIG_DIR"
            echo "🔥 PURGE: Database, logs, and configurations annihilated ($CONFIG_DIR)."
            echo "   PURGE: Banco de dados, logs e configurações aniquilados ($CONFIG_DIR)."
        fi
        echo "💀 Total removal (Purge) completed successfully!"
        echo "   Remoção total (Purge) concluída com sucesso!"
    else
        echo "🎉 Standard uninstallation completed!"
        echo "   Desinstalação padrão concluída!"
        echo "Note: Your reports and settings in $CONFIG_DIR were kept."
        echo "Nota: Seus relatórios e configurações em $CONFIG_DIR foram mantidos."
        echo "Tip: To delete absolutely everything, run: ./install-linux.sh purge"
        echo "Dica: Para apagar absolutamente tudo, execute: ./install-linux.sh purge"
    fi
    exit 0
fi

# ==========================================
# INSTALLATION ROUTINE
# ==========================================
echo "🚀 Starting Sync Engine installation (Linux)..."
echo "   Iniciando a instalação do Sync Engine (Linux)..."

# Cria as pastas necessárias silenciosamente
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# MUDANÇA V6.0: Copia todos os arquivos Python da pasta atual (módulos e motor)
cp *.py "$INSTALL_DIR/"
cp -r locales "$INSTALL_DIR/" 2>/dev/null

# Aplica as permissões e recria o atalho global de forma forçada
chmod +x "$INSTALL_DIR/sync_engine.py"
ln -sf "$INSTALL_DIR/sync_engine.py" "$BIN_DIR/sync-engine"

echo "✅ Files installed in $INSTALL_DIR"
echo "   Arquivos instalados em $INSTALL_DIR"
echo "✅ 'sync-engine' command linked to $BIN_DIR"
echo "   Comando 'sync-engine' vinculado em $BIN_DIR"

# Verifica se a pasta do atalho está na memória do terminal
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  CRITICAL WARNING: The $BIN_DIR directory is not in your PATH."
    echo "    AVISO CRÍTICO: O diretório $BIN_DIR não está no seu PATH."
    echo "To make the 'sync-engine' command work from anywhere,"
    echo "Para que o comando 'sync-engine' funcione de qualquer lugar,"
    echo "add the following line to the end of your ~/.bashrc or ~/.zshrc file:"
    echo "adicione a seguinte linha ao final do seu arquivo ~/.bashrc ou ~/.zshrc:"
    echo ""
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then run: source ~/.bashrc"
    echo "Depois, execute: source ~/.bashrc"
fi

# Ativa o Linger para iniciar o motor junto com o boot do PC
loginctl enable-linger $USER
echo "✅ Linger enabled (The engine will start before login)."
echo "   Linger ativado (O motor iniciará antes do login)."

echo "🎉 Installation complete!"
echo "   Instalação concluída!"

read -p $'\nPress Enter to close... / Pressione Enter para fechar...'
