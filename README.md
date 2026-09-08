<div align="right">
  <span>🇺🇸 English</span> | <a href="README-pt.md">🇧🇷 Português</a>
</div>

# 🔄 Sync Engine - Multi-Account Rclone Manager

An intelligent, interactive, and secure bidirectional cloud sync engine built on top of the powerful `rclone bisync`. Designed for Linux and Windows, it transforms Rclone's complexity into a seamless experience through a comprehensive CLI wizard.

Born from the need to overcome the limitations of traditional cloud clients, this project heavily focuses on automatic background synchronization, native protection against accidental deletions, strict bandwidth/size limits, and surgical bidirectional folder blocking.

## ✨ Key Features

*   **Smart Bidirectional Blocking (`.nosync`):** Create an empty file named `.nosync` inside any folder (whether on your local machine **or directly in the cloud**) and the engine will instantly ignore it. Remote scanning ensures unwanted cloud directories are never accidentally downloaded.
*   **Interactive CLI Wizard:** A complete menu to manage accounts, filters, services, and generate reports.
*   **Native Filename Cleaner (`clean`):** Scans your local folders for special characters that cause cloud upload errors. It shows a safe preview, strictly respects your filter rules, requires user confirmation, and generates a detailed report.
*   **Error Analyzer (`analyze`):** Forget confusing logs. The engine reads Rclone failure reports and translates common issues (like *eTag Mismatches* or stuck *Lock Files*) into human-readable diagnostics and actionable solutions.
*   **Auto-Updater (`update`):** Checks for, downloads, and installs the latest version of the script directly from the GitHub repository with a single command.
*   **Multi-Account Support:** Connect Google Drive, OneDrive, Dropbox, S3, or any other provider supported by Rclone simultaneously.
*   **Advanced Filters:** Define global exclusions using wildcards, file size limits (`MAX_SIZE`), and bandwidth limits (`BW_LIMIT`).
*   **Background Service (Systemd / Task Scheduler):** Runs silently at the user level, allowing auto-start without requiring administrative privileges for daily tasks.
*   **Exportable Reports:** Generate safe Dry-Run simulations, manual sync logs, and lists of files blocked by size limits, saved as plain text.
*   **Desktop Notifications:** Native alerts for successful syncs or errors (supported on Linux via `notify-send` and Windows via PowerShell balloons).
*   **Auto-Healing & Auto-Unlocker:** The script detects critical API failures and stuck lock files, automatically breaking the locks and performing deep resyncs to recover.

---

## ⚙️ Prerequisites and Installation

The project is cross-platform, running natively as a background service on both **Linux** and **Windows 10/11** ecosystems.

### Dependencies
The core tools required by the engine are:
*   `python3` (The core runtime)
*   `rclone` (The core transfer engine)
*   `sqlite3` (For fast metadata indexing)

**🐧 On Linux:**
Don't worry, all dependencies are automatically downloaded and configured by our `install.sh` script.

**🪟 On Windows:**
You must manually download and install these tools before running the installer. Make sure to select **"Add to PATH"** during installation:
1.  **Python 3:** [Download Windows Installer](https://www.python.org/downloads/windows/)
2.  **Rclone:** [Download Rclone](https://rclone.org/downloads/) *(Extract the `.exe` and place it in a folder in your PATH, e.g., `C:\Windows`)*
3.  **SQLite3:** [Download SQLite Tools](https://www.sqlite.org/download.html) *(Extract the `.exe` and place it in your PATH)*

### Step-by-Step Installation

1. **Clone this repository to your computer:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Run the correct installer for your OS:**
   * 🐧 **On Linux:** Open your terminal and run:
     ```bash
     sudo ./install.sh
     ```
   * 🪟 **On Windows:** Open the cloned folder, right-click the `install.ps1` file, and select **"Run with PowerShell"**. *(A blue screen will ask for Administrator privileges; just confirm it).*

3. **Configure your cloud accounts:**
   On either Windows or Linux, open a terminal and run (as a standard user, DO NOT use sudo/admin):
   ```bash
   rclone config
   ```
   *(Follow Rclone's instructions to set up your cloud remotes).*

---

## 💻 CLI Command Reference

Sync Engine can be operated via the interactive wizard or direct terminal shortcuts. Basic usage: `sync-engine [COMMAND]`

| Command | Description |
| :--- | :--- |
| `config` | Opens the Interactive Wizard (Main menu). |
| `now` | 🚀 Forces an immediate Sync (displays progress bar). |
| `test` | 🧪 Starts Dry-Run mode (Safe simulation, alters nothing). |
| `clean` | 🧹 Starts the filename cleaner (Generates report & respects filters). |
| `analyze` | 🔎 Analyzes the last manual sync log to provide error diagnostics. |
| `doctor` | 🩺 Runs a system health check (dependencies and permissions). |
| `update` | 🔄 Downloads and installs the latest version from GitHub. |
| `start` / `stop` | TURNS ON or OFF the invisible background service. |
| `status` | Displays the current service status and recent logs. |
| `version` (`-v`)| Shows the current engine version. |

---

## 🛠️ Interactive Wizard Guide (`sync-engine config`)

The interactive menu is divided into 4 main sections:

1. **Account Configuration (Options 1 to 3):** Add, list, or remove local folder links to your clouds. Removing an account triggers intelligent garbage collection.
2. **Global Settings (Options 4 & 5):** Change sync intervals, bandwidth limits, max file size caps, and set the export folder for reports.
3. **Extra Actions (Options 6 to 11):** Shortcuts for immediate execution (`now`), simulation (`test`), diagnostics (`doctor`), error analysis (`analyze`), and the **Size Report**.
4. **Engine Control (Options 12 to 15):** Friendly interface to start, stop, check the engine status, or run the updater.

---

## 🎯 Filters and Exclusions Guide

To prevent the synchronization of unwanted folders or files, you can use two methods:

### Method 1: The `.nosync` Flag (Recommended)
Simply create an empty file named exactly `.nosync` inside any directory (locally or via your cloud's web interface). 
On the next engine cycle, that folder and all its contents will be instantly ignored and safely blocked.

### Method 2: Global Filters (Menu 5 - Manage Filters)
Applies broad rules to all folders within an account. Supports advanced syntaxes:
*   **Exact match:** `venv` or `.git`
*   **Text wildcard (`*`):** `*.tmp`
*   **Character wildcard (`?`):** `cam_?.dav`
*   **Root Anchor (`/`):** `/Backups` (Blocks the "Backups" folder, but *only* if it is in the root of your cloud/main folder).

---

## 💡 Automatic Continuous Server (Linger / Logon)

To turn your PC into a true "server":
*   **On Linux:** The installation script automatically enables the Linger feature (`loginctl enable-linger`). This allows the sync engine to start immediately after system boot, even if the machine is left at the lock screen. *(Note: Linger is not deactivated during uninstallation, as it is a valuable permission).*
*   **On Windows:** A task is created in the Task Scheduler linked to the user's *Logon* trigger, ensuring it runs invisibly as soon as the desktop loads.

---

## ⚠️ Known Limitations

1. **Not Real-Time (Inotify):** The script does not actively monitor every disk click. It operates in cyclical scanning windows (default: every 5 minutes). 
2. **Ignores Symlinks:** To prevent accidental infinite loops, the engine does not copy or follow system shortcuts.
3. **Initial Resync Time:** On the very first sync of an account (or if the history breaks), the engine will need to run a deep scan (`--resync`). This is handled automatically.
4. **Personal Vaults:** Some clouds require native decryption keys (e.g., OneDrive's *Personal Vault*). The Sync Engine blocks these by default via global filters to prevent API read permission failures.

---

## 🗑️ Uninstallation

To completely remove Sync Engine from your system (clearing the root executable, shortcuts, and background services):

*   **On Linux:** `sudo ./install.sh uninstall`
*   **On Windows:** Run `.\install.ps1 uninstall` in your PowerShell terminal, or use the prompt provided by the script context.

*(Your `config.json` rules and `.db` metadata will be kept in `~/.config/sync_engine/` for safety).*