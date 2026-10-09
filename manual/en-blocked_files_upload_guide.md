# 📦 Uploading Blocked Files Guide (Bypass MAX_SIZE)

When you configure an upper file size limit (`MAX_SIZE`) on a Sync Engine account profile (for example, skipping files larger than 500 MB), the engine conserves network bandwidth and cloud storage by bypassing any file that exceeds that threshold.

However, what should you do when you **need** to transfer a specific oversized file that was excluded?

Because Sync Engine is built on a modular and flexible architecture, you do not need to dismantle your synchronization setup to handle this. Below are four reliable methods to upload blocked files, arranged from the most integrated to the most technical.

---

## 1. Virtual Drive Mount (The Native & Elegant Solution)

Sync Engine's **Virtual Drive (Mount)** feature operates completely independently of the background synchronization daemon. It mounts your remote as an interactive disk volume directly within your operating system, communicating directly with cloud endpoints without being constrained by bidirectional sync rules, exclusion patterns, or account file-size caps.

* **How to use it:**
  1. Open the interactive wizard: `sync-engine config`.
  2. Navigate to **Extra Actions** and select **Mount Cloud as Virtual Drive**.
  3. Mount your desired cloud remote (e.g., Drive letter `X:` on Windows or a local directory on Linux).
  4. Open your native file manager, locate the large file, and drag and drop it directly into the mounted Virtual Drive.
* **System Behavior:** The file uploads immediately through the mount stream. During subsequent sync passes, the background engine continues to bypass the local copy in your sync folder, while the remote copy remains safe in the cloud.

---

## 2. Web Browser Upload (The Universal Solution)

This is the fastest, zero-configuration workaround—ideal if you want to upload a one-off asset without configuring a mount point or launching terminal commands.

* **How to use it:**
  1. Open your web browser.
  2. Sign in to your cloud provider's web portal (Google Drive, OneDrive, Dropbox, etc.).
  3. Drag and drop the oversized file from your local storage directly into the desired cloud destination directory.
* **System Behavior:** The file uploads directly via HTTPS. When Sync Engine wakes up for its next inspection pass, it detects the remote file but **will neither attempt to download nor delete it**, because the `MAX_SIZE` rule tells the engine to ignore files that exceed the threshold.

---

## 3. Temporary Limit Adjustment (The Interactive Menu Solution)

If you have dozens of heavy files distributed across various subdirectories and do not want to hunt them down manually to upload via a browser, you can leverage the engine's built-in indexing logic.

* **How to use it:**
  1. Run `sync-engine config`, list your accounts, and open the profile you wish to adjust.
  2. Select **Change Max Size** and temporarily set it to `0` (Unlimited).
  3. Return to the main menu and trigger an on-demand **Manual Sync** (`sync-engine now`) in Normal (Safe) mode. The engine inspects your directories and uploads all previously skipped files automatically.
  4. Once the transfer completes, return to the account panel and restore your original file size limit (e.g., `500M`).

---

## 4. Direct Rclone Command (For Advanced Users)

Because Sync Engine manages authenticated credentials via the underlying Rclone configuration, you can bypass the Sync Engine wrapper entirely and dispatch a targeted transfer via your system terminal.

* **How to use it:**
  1. Open a system terminal window.
  2. Run a targeted copy command specifying the local file path and the remote target destination.
  
  *Example:*
  ```bash
  rclone copy /path/to/local/large_video.mp4 AccountName:/Target/Directory/
  ```
* **System Behavior:** The file transfers directly through Rclone, bypassing Sync Engine's active profile exclusion rules and size restrictions.

---

## Practical Use Cases

### Example 1: Delivering a Master Video Export (Using Virtual Drive Mount)
You maintain a 1 GB limit on your OneDrive account to keep project caches and intermediate renders from filling your cloud quota. Today, you exported a final master video that weighs 5 GB.  
**The Solution:** Instead of modifying your profile rules, mount OneDrive as Drive `Z:`. Copy the final export directly into `Z:`, grab the shareable link for your client, and dismount when finished. Your 1 GB limit continues safeguarding your routine syncs, while your client delivery goes through seamlessly.

### Example 2: Ad-Hoc Archive Sharing (Using Web Interface)
Your `_last_size_report.txt` audit report reveals that a multi-gigabyte `.zip` archive was skipped due to size limits.  
**The Solution:** Open Google Drive in your web browser, navigate to your target backup directory, and upload the `.zip` archive directly. Sync Engine will continue operating silently in the background, ignoring the archive so it does not take up disk space on smaller secondary machines linked to the same cloud profile.

### Example 3: Scheduled Batch Offload (Using Temporary Limit Adjustment)
During business hours, your team enforces a 100 MB upload cap to prevent heavy transfers from congesting office network bandwidth. By Friday evening, multiple large client projects have piled up locally and need to be offloaded.  
**The Solution:** Open `sync-engine config`, set **Max Size** to `0` (unlimited), and exit. Because your Task Scheduler is already set to execute an off-peak forced sync overnight, the system transfers all queued assets automatically during the early morning hours. On Monday morning, you restore the limit to 100 MB.