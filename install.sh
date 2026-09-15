#!/usr/bin/env bash

echo "🚀 Iniciando a instalação do Sync Engine (Linux User Mode)..."

INSTALL_DIR="$HOME/.local/share/sync-engine"
BIN_DIR="$HOME/.local/bin"
SERVICE_FILE="$HOME/.config/systemd/user/sync-engine.service"

echo "🛑 Parando serviços antigos..."
systemctl --user stop sync-engine.service 2>/dev/null
systemctl --user disable sync-engine.service 2>/dev/null

echo "🧹 Limpando módulos antigos..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$HOME/.config/systemd/user"

echo "📦 Copiando novos módulos (Arquitetura 6.0)..."
cp *.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/sync_engine.py"

echo "🔗 Criando atalho no terminal..."
ln -sf "$INSTALL_DIR/sync_engine.py" "$BIN_DIR/sync-engine"

echo "⚙️ Configurando serviço invisível (Systemd)..."
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Sync Engine Background Motor
After=network.target

[Service]
ExecStart=/usr/bin/env python3 $INSTALL_DIR/sync_engine.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable sync-engine.service

echo "🎉 Instalação concluída com sucesso!"
echo "💡 Certifique-se de que $BIN_DIR está no seu PATH (geralmente já está no Ubuntu)."
echo "Execute 'sync-engine' para abrir o painel!"