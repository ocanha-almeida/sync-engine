#!/bin/bash

# Garante que o script seja executado como root (sudo)
if [ "$EUID" -ne 0 ]; then
  echo "❌ Por favor, execute como root: sudo ./install.sh"
  echo "💡 Para desinstalar, use: sudo ./install.sh uninstall"
  exit 1
fi

# ==========================================
# ROTINA DE DESINSTALAÇÃO
# ==========================================
if [ "$1" == "uninstall" ] || [ "$1" == "--uninstall" ]; then
  echo "=== Desinstalador do Sync Engine ==="
  
  echo "🛑 Parando processos do motor em execução..."
  pkill -f sync_engine.py 2>/dev/null
  
  echo "🗑️ Removendo atalho global..."
  rm -f /usr/local/bin/sync-engine

  echo "🗑️ Removendo diretório de executáveis..."
  rm -rf /opt/sync-engine

  echo "🗑️ Removendo serviço do systemd..."
  rm -f /etc/systemd/user/sync-engine.service

  echo ""
  echo "✅ Desinstalação do sistema concluída com sucesso!"
  echo "💡 Dica: Seus bancos de dados (.db) e exclusões foram mantidos por segurança."
  echo "   Se quiser apagar TUDO definitivamente, rode no seu usuário comum:"
  echo "   rm -rf ~/.config/sync_engine"
  exit 0
fi

# ==========================================
# ROTINA DE INSTALAÇÃO
# ==========================================
echo "=== Instalador do Sync Engine ==="

# 1. Instala dependências nativas
echo "Verificando dependências (Rclone e SQLite)..."
apt-get update -qq
apt-get install -y rclone sqlite3 libnotify-bin > /dev/null

# 2. Cria a pasta no /opt e copia o executável
echo "Instalando executável em /opt/sync-engine/..."
mkdir -p /opt/sync-engine
cp sync_engine.py /opt/sync-engine/
chmod +x /opt/sync-engine/sync_engine.py

# 3. Cria o Serviço de Sistema (Desligado por padrão)
echo "Configurando serviço Systemd Multi-Usuário..."
mkdir -p /etc/systemd/user/
cat << 'EOF' > /etc/systemd/user/sync-engine.service
[Unit]
Description=Motor de Sincronizacao Multi-Contas
After=network-online.target

[Service]
Type=simple
ExecStart=/opt/sync-engine/sync_engine.py
Restart=always
RestartSec=15

[Install]
WantedBy=default.target
EOF

# 4. Cria um atalho global (symlink)
echo "Criando atalho global 'sync-engine'..."
ln -sf /opt/sync-engine/sync_engine.py /usr/local/bin/sync-engine

echo ""
echo "✅ Instalação concluída com sucesso!"
echo "==============================================================="
echo "Para começar, NÃO use o 'sudo'. Faça o seguinte com seu usuário comum:"
echo ""
echo "  PASSO 1: Autentique sua nuvem (Google Drive, OneDrive, etc)"
echo "           Execute o comando abaixo e siga as instruções na tela:"
echo "           rclone config"
echo ""
echo "  PASSO 2: Configure o Motor de Sincronização"
echo "           Após criar a sua conta no Rclone, digite:"
echo "           sync-engine config"
echo "==============================================================="
echo "Veja o manual abaixo para mais detalhes:"
echo ""

# Exibe o manual usando o usuário real que chamou o script
if [ -n "$SUDO_USER" ]; then
    su - $SUDO_USER -c "/usr/local/bin/sync-engine --help"
else
    /usr/local/bin/sync-engine --help
fi