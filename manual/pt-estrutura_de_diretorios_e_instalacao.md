# 📂 Estrutura de Diretórios e Instalação

O Sync Engine separa rigorosamente os arquivos de código (imutáveis) dos seus dados pessoais de configuração (bancos, logs e regras). Isso garante que, ao desinstalar ou atualizar a aplicação, as suas configurações permaneçam intactas.

Abaixo estão listados os caminhos padrão do Sync Engine em cada sistema operacional:

================================================================================
🐧 LINUX
================================================================================
• Pasta da Aplicação (Repositório / Scripts / Locales):
  `~/.local/share/sync-engine`
  (É aqui que os scripts `.py` e a pasta `locales/` são instalados

• Pasta de Configurações, Bancos e Logs:
  `~/.config/sync_engine`
  - `config.json` (banco central de configurações do sistema)
  - `sync.log` (registro global contínuo do motor)
  - `sync_metadata_*.db` (índices locais SQLite)
  - `excludes_*.txt` (filtros compilados por conta)

• Binário do Comando no Terminal (PATH):
  `~/.local/bin/sync-engine`

• Serviço do Sistema em Segundo Plano (Systemd User):
  `~/.config/systemd/user/sync-engine.service`


================================================================================
🪟 WINDOWS
================================================================================
• Pasta da Aplicação (Repositório / Scripts / Locales):
  `%LOCALAPPDATA%\sync-engine`
  (Geralmente mapeado em `C:\Users\<SeuUsuario>\AppData\Local\sync-engine`)

• Pasta de Configurações, Bancos e Logs:
  `%USERPROFILE%\.config\sync_engine` 
  - `config.json`
  - `sync.log`
  - `sync_metadata_*.db`
  - `excludes_*.txt`

• Inicialização Automática do Motor (Startup Shortcut):
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SyncEngine.lnk`