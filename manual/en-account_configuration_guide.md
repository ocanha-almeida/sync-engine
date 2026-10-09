# ⚙️ Account Configuration & Synchronization Guide

Sync Engine allows you to manage multiple cloud accounts simultaneously, each with its own isolated synchronization rules, file size limits, and exclusion filters. This guide explains how to add new cloud providers and fine-tune each account profile.

## 1. How to Register a New Account

To connect a new cloud remote, open your terminal and launch the primary wizard:

```bash
sync-engine config
```

1. From the main menu, select **Add new account**.
2. **Profile Name:** Choose a descriptive, friendly name to identify this profile (e.g., `Work`, `Personal`, `Photo_Backup`).
3. **Cloud Remote Selection:** The system automatically lists all remotes previously configured in your underlying Rclone installation. Enter the number corresponding to your desired provider.
4. **Local Folder:** Specify the absolute local filesystem path that will synchronize with this cloud remote.
   * *Tip:* Pressing **Enter** without typing a path automatically creates a dedicated folder in your user root named after the remote (e.g., `~/gdrive`).

Once saved, the wizard automatically redirects you to the configuration dashboard for this profile. The dashboard provides an overview of your settings:

```text
=== ⚙️  ACCOUNT: my_drive ===
=============================================
☁️  Cloud (Remote)  : my_gdrive:
📁 Local Folder    : ~/google_drive
🔄 Background Sync : ON
📦 Max Size Limit  : 0 (0 = Unlimited)
🛡️  Active Filters  : 19 rule(s)
🔌 Virtual Drive   : Inactive

1. ✏️  Change Local Folder path
2. 🔄 Toggle Background Sync
3. 📦 Change Max Size
4. 🛡️  Manage Filters

[Enter] Back/Exit
=============================================
Option: 
```

If the background motor is currently active, it will detect the new profile immediately and begin its first indexing pass silently.

---

## 2. Account Settings and Options

Through the account's interactive panel, you can adjust granular behavioral settings:

### ✏️ Change Local Folder path
Updates the local directory bound to the cloud remote.
* **Safe Physical Migration:** When changing the directory path, Sync Engine prompts you to physically transfer all existing files from the old location to the new path. This automated relocation prevents duplicate downloads and saves network bandwidth.

### 🔄 Toggle Background Sync
Enables or suspends automated background synchronization for this specific profile.
* **ON:** The account syncs continuously according to the global synchronization interval.
* **OFF [Paused]:** Pauses automated background operations for this profile. This is ideal for temporarily conserving bandwidth or system resources without deleting your account settings. Paused accounts can still be synchronized on-demand via the manual command:
  ```bash
  sync-engine now
  ```

### 📦 Change Max Size
Enforces an upper file-size ceiling for bidirectional transfers, skipping any file larger than the specified threshold.
* Accepts standard size notations such as `500M` (500 Megabytes) or `2G` (2 Gigabytes).
* Enter `0` for **Unlimited**.
* Files excluded by this rule are never deleted; they are simply bypassed during sync cycles. You can inspect skipped items anytime via the "Report of Files Over the Limit" option in the Maintenance menu.

### 🛡️ Manage Filters
Defines precise rules to prevent specific files, directories, or extensions from uploading to the cloud or downloading to your local machine.

When a new account is registered, Sync Engine **automatically populates default protection filters** to prevent sync lockups, OS collisions, or wasted bandwidth. These pre-configured defaults cover:
* **System & Hidden Metadata:** `desktop.ini`, `Thumbs.db`, `.DS_Store`, `$RECYCLE.BIN` (prevents OS icon index conflicts and external drive trash sync).
* **Development & Version Control:** `venv`, `.venv`, `__pycache__`, `.git`, `site-packages`, `node_modules` (prevents millions of tiny source-tree files from overwhelming cloud APIs).
* **Process Locks & Temporary Files:** `*.tmp`, `~$*`, `.~lock.*` (prevents attempting to sync Office or LibreOffice documents while actively open in an editor).
* **Incomplete Browser Downloads:** `*.crdownload`, `*.part` (avoids uploading partial files during active web downloads).
* **Cloud Trash & Vaults:** `Personal Vault`, `Cofre Pessoal`, `*.trashinfo`, `.Trash`.

> **💡 YOU ARE IN CONTROL:**
> Default filters are fully customizable. If you are a developer and **need** Sync Engine to back up your `node_modules` folders or `.git` repositories, open **Manage Filters** in your account dashboard, select the number corresponding to the rule, and choose **Delete**.

**Supported filter syntax for custom rules:**
* `(?i)*.tmp`: Case-insensitive extension matching.
* `venv`: Matches folders or files by exact name across all hierarchy levels.
* `Backup*`: Prefix wildcard matching (e.g., `Backup_2026`).
* `*.bak`: Standard file extension wildcard applied across all subfolders.
* `/Old_Files`: The leading slash (`/`) anchors the rule to the root of the sync tree, ignoring root-level `Old_Files` while allowing subfolders with the same name elsewhere.
* `.*`: Excludes dot-prefixed hidden files and directories across all levels.
* `/.*`: Excludes dot-prefixed hidden files exclusively at the root directory level, allowing hidden files inside subdirectories to sync normally.

---

## 3. Dynamic Exclusion Marker (`.nosync`)

If you need to isolate a directory quickly without opening the terminal to configure explicit rules, use the dynamic exclusion marker:

Place an empty file named `.nosync` inside any folder (either locally via your file manager or remotely via your cloud web portal). Sync Engine detects this marker during the next indexing pass and **isolates the entire directory**, safely halting synchronization for that subtree.

---

## 4. Integrated Virtual Drive (Mount)

Sync Engine allows you to mount any registered cloud account as a local Virtual Drive on demand. This feature runs alongside the background sync engine without interfering with bidirectional synchronization rules.

* **How to enable:** From the main configuration menu, choose **Mount Cloud as Virtual Drive**.
* **On Windows:** Enter an available drive letter (e.g., `X:`, `Y:`). The cloud remote mounts and appears directly under "This PC" as a network drive.
* **On Linux:** The cloud remote mounts directly onto a local filesystem mountpoint (defaults to your Desktop, but fully customizable).
* **Auto-Mount:** Enabling persistent auto-mount ensures the Virtual Drive reconnects silently in the background whenever Sync Engine starts on system boot.