<div align="right">
  <span>🇺🇸 English</span> | <a href="README-pt.md">🇧🇷 Português</a>
</div>

# 🔄 Sync Engine - Multi-Account Rclone Manager

An intelligent, interactive, and secure bidirectional cloud sync engine built on top of the powerful `rclone bisync`. Designed exclusively for Linux, it transforms Rclone's complexity into a seamless experience through a comprehensive CLI wizard.

Born from the need to overcome the limitations of traditional cloud clients for Linux, this project heavily focuses on automatic background synchronization, native protection against accidental deletions, strict bandwidth/size limits, and surgical bidirectional folder blocking.

## ✨ Key Features

*   **Smart Bidirectional Blocking (`.nosync`):** Create an empty file named `.nosync` inside any folder (whether on your local machine **or directly in the cloud**) and the engine will instantly ignore it. Remote scanning ensures unwanted cloud directories are never accidentally downloaded, without needing to edit global config files.
*   **Interactive CLI Wizard:** A 13-option menu to manage accounts, filters, services, and generate reports.
*   **Native Filename Cleaner (`clean`):** Scans your local folders for special characters that cause cloud upload errors. It shows a safe preview, strictly respects your filter rules and `.nosync` flags, requires user confirmation, and generates a detailed modification report.
*   **Error Analyzer (`analyze`):** Forget confusing logs. The engine reads Rclone failure reports and translates common issues (like *eTag Mismatches* or stuck *Lock Files*) into human-readable diagnostics and actionable solutions.
*   **Auto-Updater (`update`):** Checks for, downloads, and installs the latest version of the script directly from the GitHub repository with a single command.
*   **Multi-Account Support:** Connect Google Drive, OneDrive, Dropbox, S3, or any other provider supported by Rclone simultaneously.
*   **Advanced Filters:** Define global exclusions using wildcards, file size limits (`MAX_SIZE`), and bandwidth limits (`BW_LIMIT`).
*   **Background Service (Systemd):** Runs silently at the user level (no root required for daily syncing).
*   **Exportable Reports:** Generate safe Dry-Run simulations, manual sync logs, and lists of files blocked by size limits, saved as plain text in the folder of your choice.
*   **Desktop Notifications:** Native Linux alerts (via `notify-send`) for successful syncs or errors.
*   **Auto-Healing (Auto-Resync):** The script detects critical API failures (like broken Rclone history) and performs a deep resync automatically to recover.

---

## ⚙️ Prerequisites and Installation

Built for Linux ecosystems (tested on Debian/Ubuntu/Mint based distributions).

### Dependencies
The installation script will automatically install:
*   `rclone` (The core transfer engine)
*   `sqlite3` (For fast metadata indexing and `.nosync` logic)
*   `libnotify-bin` (For desktop notifications)
*   *Note: Requires native system `python3`.*

### Installation Steps

1. **Clone this repository:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Run the automatic installer (requires sudo):**
   ```bash
   sudo ./install.sh
   ```

3. **Configure your cloud accounts (Run as standard user, DO NOT use sudo):**
   ```bash
   rclone config
   ```
   *(Follow Rclone's instructions to set up your cloud remotes).*

---

## 💻 CLI Command Reference

Sync Engine can be operated via the interactive wizard or direct terminal shortcuts.

Basic usage: `sync-engine [COMMAND]`

| Command | Description |
| :--- | :--- |
| `config` | Opens the Interactive Wizard (Main menu). |
| `now` | 🚀 Forces an immediate Sync (displays progress bar). |
| `test` | 🧪 Starts Dry-Run mode (Safe simulation, alters nothing). |
| `clean` | 🧹 Starts the filename cleaner (Generates report & respects filters). |
| `analyze` | 🔎 Analyzes the last manual sync log to provide error diagnostics. |
| `doctor` | 🩺 Runs a system health check (dependencies and permissions). |
| `update` | 🔄 Downloads and installs the latest version from GitHub. |
| `start` / `stop` | TURNS ON or OFF the invisible `systemd` background service. |
| `status` | Displays the current service status and recent logs. |
| `version` (`-v`)| Shows the current engine version. |

---

## 🛠️ Interactive Wizard Guide (`sync-engine config`)

The interactive menu is divided into 4 main sections:

1. **Account Configuration (Options 1 to 3):** Add, list, or remove local folder links to your clouds. Removing an account triggers intelligent garbage collection (removes databases and residual filters).
2. **Global Settings (Options 4 & 5):** Change sync intervals (e.g., `300s`), bandwidth limits (e.g., `10M`), max file size caps (e.g., `2G`), and set the export folder for reports (e.g., `/tmp`).
3. **Extra Actions (Options 6 to 9):** Shortcuts for immediate execution (`now`), simulation (`test`), diagnostics (`doctor`), and the **Size Report**, which lists files blocked by the size limit rule in a readable format (e.g., `[3.07 GB] /videos/class.mp4`).
4. **Engine Control (Options 10 to 12):** Friendly interface to start, stop, and check the engine status (same effect as the direct CLI commands).

---

## 🎯 Filters and Exclusions Guide

To prevent the synchronization of unwanted folders or files, you can use two methods:

### Method 1: The `.nosync` Flag (Recommended)
Simply create an empty file named exactly `.nosync` inside any directory (locally or via your cloud's web interface). 
On the next engine cycle, that folder and all its contents will be instantly ignored and safely blocked from Rclone.
*Linux terminal example:* `touch ~/MyProjects/Tests/.nosync`

### Method 2: Global Filters (Menu 5 - Manage Filters)
Applies broad rules to all folders within an account. Supports advanced syntaxes:
*   **Exact match:** `venv` or `.git` (Blocks any folder/file with that exact name, at any level).
*   **Text wildcard (`*`):** `*.tmp` (Blocks all files ending with `.tmp`).
*   **Character wildcard (`?`):** `cam_?.dav` (Blocks `cam_1.dav`, `cam_A.dav`, etc).
*   **Root Anchor (`/`):** `/Backups` (Blocks the "Backups" folder, but *only* if it is in the root of your cloud/main folder. A folder named `Photos/Backups` will still sync normally).

---

## 💡 Automatic Continuous Server (Linger)

By default Linux security rules, user-level services only start when you type your password at the login screen. 

To turn your PC into a true "server", **the installation script automatically enables the Linger feature** (`loginctl enable-linger`). This allows the sync engine to start immediately after system boot, even if the machine is left at the lock screen.

*Note: When uninstalling Sync Engine, Linger is not deactivated from your user account. We chose to keep it active as it is a valuable permission should you wish to run other applications and background services in the future.*

---

## 💡 Usage Tips & Workflows

*   **Ephemeral Report Folders:** In **Option 4** of the wizard, you can change the generated reports folder (Dry-Run and Size) to `/tmp`. Linux will magically clear out your old reports on every reboot.
*   **Multiple Clouds:** Create an account in the menu pointing to Google Drive (`~/GDrive`) and another for OneDrive (`~/OneDrive`). The engine will handle both in parallel with independent rules and SQLite databases.

---

## ⚠️ Known Limitations

1. **Not Real-Time (Inotify):** The script does not actively monitor every disk click. It operates in cyclical scanning windows (default: every 5 minutes). 
2. **Ignores Symlinks:** To prevent accidental infinite loops, the engine does not copy or follow system shortcuts (preventing structural crashes between Linux and the Cloud).
3. **Initial Resync Time:** On the very first sync of an account (or if the process is force-killed leading to a fatal error), the engine will need to run a deep scan (`--resync`). This is handled automatically but takes more time than a standard incremental sync.
4. **Personal Vaults:** Some clouds require native decryption keys (e.g., OneDrive's *Personal Vault*). The Sync Engine blocks "Cofre Pessoal" and "Personal Vault" by default via global filters to prevent API read permission failures.

---

## 🗑️ Uninstallation

To completely remove Sync Engine from your system (clearing the root executable, shortcuts, and `systemd` services), use the native installer routine:

```bash
sudo ./install.sh uninstall
```
*(Your `config.json` rules and `.db` metadata will be kept in `~/.config/sync_engine/` for safety. You can manually delete this folder if you don't plan to reinstall the tool).*
