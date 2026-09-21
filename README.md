<div align="right">
  <span>🇺🇸 English</span> | <a href="README-pt.md">🇧🇷 Português</a>
</div>

# 🔄 Sync Engine - Multi-Account Rclone Manager (v7.0)

An intelligent, interactive, and secure bidirectional cloud sync engine built on top of the powerful `rclone bisync`. Designed for Linux and Windows, it transforms Rclone's complexity into a seamless experience through a comprehensive CLI wizard.

Born from the need to overcome the limitations of traditional cloud clients, this project heavily focuses on automatic background synchronization, native protection against accidental deletions, strict bandwidth/size limits, and surgical bidirectional folder blocking.

## ✨ Key Features (Updated v7.0)

*   **Cloud-to-Cloud Migration:** Transfer files directly between distinct providers (e.g., OneDrive to Google Drive) using your system's RAM, preserving local disk space and intelligently ignoring blocked folders (`.nosync`).
*   **Virtual Drive Mount:** Turn any cloud into a "virtual flash drive" seamlessly integrated into your OS (Native Systemd support on Linux and Network Drive on Windows).
*   **Granular Account Configuration:** Exclusion rules and maximum file size limits (`MAX_SIZE`) are now defined individually for each connected cloud.
*   **Error Analyzer & Auto-Reconnect (`analyze`):** Forget confusing logs. The engine translates Rclone failures into readable diagnostics. Version 7.0 automatically detects expired security tokens and triggers your browser for instant 1-click renewal.
*   **Smart Bidirectional Blocking (`.nosync`):** Create an empty file named `.nosync` inside any folder (locally or directly in the cloud) and the engine will instantly ignore it.
*   **Isolated & Standardized Reports:** All history logs are generated with timestamps in the header and isolated by account in your chosen folder.
*   **Native Filename Cleaner (`clean`):** Scans your local folders for special characters that cause cloud upload errors, shows a safe preview, and generates a detailed report.
*   **Auto-Healing & Auto-Unlocker:** The script detects critical API failures and stuck lock files, automatically breaking the locks and performing deep resyncs (`--resync`) to recover.
*   **Safe Auto-Uninstall:** The engine now has a clean self-destruct routine (Option 18) protected by a text challenge (CAPTCHA).
*   **Background Service:** Runs silently at the user level, allowing auto-start without requiring administrative privileges for daily tasks.

---

## ⚙️ Prerequisites and Installation

The project is cross-platform, running natively as a background service on both **Linux** and **Windows 10/11** ecosystems.

### Dependencies
The core tools required by the engine are:
*   `python3` (The core runtime)
*   `rclone` (The core transfer engine)
*   `sqlite3` (For fast metadata indexing)

**🐧 On Linux:**
Don't worry, all dependencies are automatically downloaded and configured by our `install-linux.sh` script. Virtual drive support utilizes the native system `fuse` package.

**🪟 On Windows:**
You must manually download and install these tools before running the installer. Make sure to select **"Add to PATH"** during installation:
1.  **Python 3:** [Download Windows Installer](https://www.python.org/downloads/windows/)
2.  **Rclone:** [Download Rclone](https://rclone.org/downloads/) *(Extract the `.exe` and place it in a folder in your PATH, e.g., `C:\Windows`)*
3.  **SQLite3:** [Download SQLite Tools](https://www.sqlite.org/download.html) *(Extract the `.exe` and place it in your PATH)*
4.  **WinFsp:** [Download WinFsp](https://winfsp.dev/) *(Required **ONLY** if you plan to use the Virtual Drive Mount feature - Menu Option 13).*

### Step-by-Step Installation

1. **Clone this repository to your computer:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Run the correct installer for your OS:**
   * 🐧 **On Linux:** Double-click the `install-linux.sh` file and choose "Run in Terminal", or run `bash ./install-linux.sh` via CLI.
   * 🪟 **On Windows:** Simply double-click the `install-windows.cmd` file located in the cloned folder.

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
| `test` | 🧪 Starts interactive Dry-Run mode per account (Safe simulation). |
| `clean` | 🧹 Starts the filename cleaner (Generates report & respects filters). |
| `analyze` | 🔎 Analyzes recent manual/auto reports and provides actionable solutions. |
| `doctor` | 🩺 Runs a system health check (dependencies and permissions). |
| `update` | 🔄 Downloads and installs the latest version from GitHub. |
| `start` / `stop` / `reload` | Turns ON, OFF, or RELOADS the invisible background service. |
| `status` | Displays current service status and recent memory logs. |

---

## 🛠️ Interactive Wizard Guide (`sync-engine config`)

The interactive menu has been expanded to support v7.0's granular management:

1. **Account Configuration (Options 1 to 3):** Add, list, or remove local folder links to your clouds. Removing an account triggers intelligent garbage collection.
2. **Global Settings (Option 4):** Change sync intervals, global bandwidth limits (`BW_LIMIT`), set the absolute folder path for saved reports, and toggle case-sensitivity blocking.
3. **Account Filters & Limits (Option 5):** Choose a specific account to assign custom max size limits and manage its exclusion list.
4. **Extra Actions & Reports (Options 6 to 13):** Shortcuts for immediate execution (`now`), simulation (`test`), large file reports, cleaner, error analyzer, system doctor, **Cloud-to-Cloud Migration**, and **Virtual Drive Mount**.
5. **Engine Control (Options 14 to 18):** Friendly interface to start, stop, check status, update, or trigger the system-wide **Auto-Uninstall**.

---

## 🎯 Filters and Exclusions Guide

To prevent the synchronization of unwanted folders or files, use the following syntaxes when adding a filter via **Option 5**:

*   **Case Insensitive:** `(?i)*.tmp` *(Ignores both `log.tmp` and `LOG.TMP` on any OS).*
*   **Exact Match:** `venv` or `.git`
*   **Start of Filename:** `Prefix*` *(e.g., `Backup*` blocks any file/folder starting with that word).*
*   **Text Wildcard (`*`):** `*.bak`
*   **Root Anchor (`/`):** `/Backups` *(Blocks the "Backups" folder, but *only* if it is exactly at the root of your sync directory).*
*   **Root Hidden Files (Linux):** `/.*` *(Blocks hidden files/folders like `.bashrc` or `.config`, but *only* if they are located at the root level).*
*   **Universal Blocker:** Just create an empty file named `.nosync` inside any folder you wish to permanently block.

---

## 💡 Automatic Continuous Server (Linger / Logon)

To turn your PC into a true "server":
*   **On Linux:** The installation script automatically enables the Linger feature (`loginctl enable-linger`). This allows the sync engine to start immediately after system boot, even if the machine is left at the lock screen.
*   **On Windows:** An invisible task is created in the Task Scheduler linked to the user's *Logon* trigger, ensuring a clean and silent start as soon as the desktop loads.

---

## 🗑️ Uninstallation

To completely remove Sync Engine from your system (clearing the root executable, system shortcuts, and turning off background services):
1. Open your terminal and type `sync-engine config`
2. Select **Option 18 (Uninstall Sync Engine)**
3. The system will prompt you with a random text challenge (CAPTCHA) to confirm the deletion.
4. You will be asked if you want to keep or permanently delete your configuration history and old reports.
5. The software will safely self-destruct in 3 seconds.