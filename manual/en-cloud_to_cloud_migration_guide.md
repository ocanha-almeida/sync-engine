# ☁️ Cloud-to-Cloud Migration Guide

The **Cloud-to-Cloud Migration** feature allows you to copy or transfer files directly between two separate cloud storage providers (for example, from Google Drive to Microsoft OneDrive, or from Dropbox to Mega).

The major advantage of this architecture is that **it consumes zero local hard drive space**. Sync Engine uses system RAM as a temporary streaming buffer, downloading and uploading chunks simultaneously.

---

## ⚠️ Prerequisites

To use this feature, you must have **at least two (2) remotes configured in Rclone**.
*Note:* These remotes do not need to be registered as active bidirectional sync profiles in Sync Engine (you can transfer files from a temporary network share, external bucket, or an infrequently used secondary account).

---

## 1. How to Start the Migration

1. Open your terminal and launch the interactive wizard:
   ```bash
   sync-engine config
   ```
2. In the **Extra Actions** menu, select **Direct Cloud-to-Cloud Migration**.
3. **Source:** The system lists all detected Rclone remotes. Enter the number corresponding to the source cloud provider.
   * *Subfolder:* You can optionally specify a target subdirectory (e.g., `Projects_2026`). To transfer the entire remote root, press **Enter** (leave blank).
4. **Destination:** Enter the number of the cloud provider that will receive the files.
   * *Subfolder:* Specify the destination directory (e.g., `Project_Backups`). Leave blank to copy directly into the remote root.

*Tip: You cannot select the exact same remote and subfolder as both source and destination.*

---

## 2. Transfer Modes (Filter Levels)

After specifying the source and destination paths, choose the filter level to enforce during the transfer:

*   **[1] TOTAL (Absolute copy):**
    The engine transfers **everything unconditionally**. Hidden folders, local trash remnants, and system cache files are copied without exception.
*   **[2] STANDARD (Security locks):**
    The engine applies baseline safety exclusions. It performs a fast pre-scan on the source and **automatically excludes** folders marked with `.nosync`, operating system metadata (`.DS_Store`, `Thumbs.db`), and cloud-locked folders such as "Personal Vault" or "Cofre Pessoal".
*   **[3] CUSTOM (Locks + config.json filters):**
    Enforces all standard security locks and additionally **inherits custom exclusion filters** defined in your account settings (if the source provider matches an active Sync Engine profile).

Finally, the prompt asks whether to apply a **Max Size Limit**. Entering `1G`, for example, skips any individual file larger than 1 Gigabyte. Enter `0` for **Unlimited**.

---

## 3. Progress Tracking and Audit Reports

Once the transfer begins, real-time statistics appear in the terminal (transfer progress, bandwidth speed, ETA, and remaining file counts).

*   **Interruptible and Safe:** If network connectivity drops or you need to shut down the machine, press `Ctrl+C` to abort safely.
*   **Resumable (Idempotent):** When re-running the migration later, the engine skips files that already exist identically on the destination, resuming transfer seamlessly from where it stopped.
*   **Audit Logging:** Upon completion, an execution report is saved to your default reports directory (e.g., `migracao_gdrive_para_onedrive_2026-10-09.txt`).

---

## 4. Practical Use Cases

### Example 1: Redundant Backup Mirroring (Full Clone)
You rely on Google Drive for daily work but want an automated secondary clone in OneDrive to safeguard against account lockouts.
**The Solution:**
1. Launch Cloud-to-Cloud Migration.
2. Select Google Drive as Source (root) and OneDrive as Destination (root).
3. Select mode **[2] STANDARD** to skip temporary caches and `.nosync` folders.
4. Set the size limit to `0` (unlimited). The engine mirrors the directory tree directly across cloud providers without consuming local disk space.

### Example 2: Specific Subfolder Transfer (Client Video Handoff)
A client shared access to a temporary Dropbox remote containing large raw video assets. You want to transfer these assets into a dedicated project folder inside your primary Google Drive.
**The Solution:**
1. Select the temporary Dropbox remote as Source and enter `Client_Deliverables` as the subfolder.
2. Select Google Drive as Destination and set the target path to `Video_Projects/Client_X`.
3. Choose mode **[1] TOTAL**.
4. Sync Engine streams the assets directly to the target subfolder, keeping your root structure clean.

### Example 3: Overnight Automation via Task Scheduler
You need to transfer 500 GB of assets without monitoring terminal output for several hours.
**The Solution:**
1. Rather than triggering an immediate interactive migration, navigate to **Task Scheduler (Cron)** in the main menu.
2. Create a new task and choose type **`3 (Cloud-to-Cloud Migration)`**.
3. Configure the source, destination, and schedule the run for off-peak hours (e.g., `02:00` AM).
4. The background daemon handles the transfer automatically at the scheduled time with no terminal window required.