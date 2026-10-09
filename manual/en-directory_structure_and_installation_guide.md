# 📂 Directory Structure and Installation Paths

Sync Engine strictly isolates application code (immutable scripts) from personal user configuration data (databases, logs, and exclusion rules). This architectural separation ensures that updating or reinstalling the application leaves your existing configurations, accounts, and sync history completely intact.

The default filesystem paths utilized by Sync Engine across each supported operating system are detailed below:

================================================================================
🐧 LINUX
================================================================================
• Application Directory (Repository / Scripts / Locales):
  `~/.local/share/sync-engine`
  (Where the core `.py` scripts and the `locales/` translation folder reside)

• Configuration, Databases, and Logs:
  `~/.config/sync_engine`
  - `config.json` (Central system configuration database)
  - `sync.log` (Continuous global background engine journal)
  - `sync_metadata_*.db` (Per-account local SQLite index databases)
  - `excludes_*.txt` (Compiled per-account exclusion filter rules)

• Terminal Command Binary (PATH Wrapper):
  `~/.local/bin/sync-engine`

• Background Daemon Service (Systemd User Unit):
  `~/.config/systemd/user/sync-engine.service`


================================================================================
🪟 WINDOWS
================================================================================
• Application Directory (Repository / Scripts / Locales):
  `%LOCALAPPDATA%\sync-engine`
  (Typically mapped to `C:\Users\<YourUser>\AppData\Local\sync-engine`)

• Configuration, Databases, and Logs:
  `%USERPROFILE%\.config\sync_engine`
  - `config.json`
  - `sync.log`
  - `sync_metadata_*.db`
  - `excludes_*.txt`

• Automated Background Startup (Startup Shortcut):
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SyncEngine.lnk`