#!/bin/bash

INSTALL_DIR="$HOME/.local/share/sync-engine"
BIN_DIR="$HOME/.local/bin"
SERVICE_FILE="$HOME/.config/systemd/user/sync-engine.service"
CONFIG_DIR="$HOME/.config/sync_engine"

# ==========================================
# ROTINAS DE REMOÇÃO (UNINSTALL / PURGE)
# ==========================================
if [ "$1" == "uninstall" ] || [ "$1" == "purge" ]; then
    echo "🗑️ Iniciando a remoção do Sync Engine..."
    
    # 1. Para e desabilita o serviço se estiver rodando
    if systemctl --user is-active --quiet sync-engine.service 2>/dev/null; then
        systemctl --user stop sync-engine.service
        systemctl --user disable sync-engine.service
        echo "🛑 Serviço de background parado e desabilitado."
    fi

    # 2. Remove o arquivo do systemd e limpa a memória
    if [ -f "$SERVICE_FILE" ]; then
        rm -f "$SERVICE_FILE"
        systemctl --user daemon-reload
        echo "✅ Arquivo de serviço do Systemd removido."
    fi

    # 3. Remove o atalho do terminal
    if [ -L "$BIN_DIR/sync-engine" ] || [ -f "$BIN_DIR/sync-engine" ]; then
        rm -f "$BIN_DIR/sync-engine"
        echo "✅ Comando 'sync-engine' removido."
    fi

    # 4. Remove a pasta de instalação (módulos python)
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        echo "✅ Arquivos principais do motor removidos ($INSTALL_DIR)."
    fi

    # 5. Executa a destruição das configurações se o modo for PURGE
    if [ "$1" == "purge" ]; then
        if [ -d "$CONFIG_DIR" ]; then
            rm -rf "$CONFIG_DIR"
            echo "🔥 PURGE: Banco de dados, logs e configurações foram aniquilados ($CONFIG_DIR)."
        fi
        echo "💀 Remoção total (Purge) concluída com sucesso!"
    else
        echo "🎉 Desinstalação padrão concluída!"
        echo "Nota: Seus relatórios e configurações em $CONFIG_DIR foram mantidos."
        echo "Dica: Para apagar absolutamente tudo, use o comando: ./install.sh purge"
    fi
    exit 0
fi

# ==========================================
# ROTINA DE INSTALAÇÃO
# ==========================================
echo "🚀 Iniciando a instalação do Sync Engine (Linux)..."

# Cria as pastas necessárias silenciosamente
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# MUDANÇA V6.0: Copia todos os arquivos Python da pasta atual (módulos e motor)
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

# ... código anterior do install.sh ...

# Ativa o Linger para iniciar o motor junto com o boot do PC
loginctl enable-linger $USER
echo "✅ Linger ativado (O motor iniciará antes do login)."

echo "🎉 Instalação concluída!"

read -p $'\nPressione Enter para fechar...'
