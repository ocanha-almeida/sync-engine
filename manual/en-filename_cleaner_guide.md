# 🧹 Filename Cleaner & Collision Checker Guide

Cloud storage providers (such as Google Drive, Microsoft OneDrive, and Dropbox) enforce strict naming conventions for stored files. If Sync Engine attempts to push a file containing characters rejected by the remote cloud filesystem, the transfer fails and synchronization for that entire directory tree is halted.

The **Filename Cleaner & Collision Checker** is a preventive and corrective maintenance utility designed to scan local directories for incompatible naming schemes, safely sanitize offending paths, and generate a detailed audit log.

---

## 1. What Does the Cleaner Resolve?

The Cleaner addresses two primary naming failure categories that commonly interrupt cloud sync operations:

1. **Special and Prohibited Characters:**  
   Operating systems like Linux or macOS frequently allow filenames with characters strictly forbidden on Windows or cloud object stores. The Cleaner identifies and sanitizes illegal characters including: `?`, `*`, `:`, `<`, `>`, `"`, `|`, `\`, `/`, as well as problematic Unicode glyphs (e.g., star symbols `★`, curly smart quotes, or unusual forward/backward slashes).

2. **Case-Sensitivity Collisions:**  
   On Linux and macOS file systems, two distinct files can coexist in the same directory under identical names with different casing (e.g., `Report.pdf` and `report.pdf`). However, Windows and many cloud storage backends are case-insensitive, which leads to silent file overwrites or severe synchronization lockups (name collisions). The Cleaner detects these structural duplicates before they corrupt cloud directories.

*Note:* The Cleaner is fully filter-aware and **respects your existing exclusion rules**. If a directory contains a `.nosync` marker file or matches a rule in your account's exclusion list, it is bypassed and left untouched.

---

## 2. How to Use the Tool

You can run the Cleaner in two ways:

* **Via Terminal CLI:** Run `sync-engine clean` and press Enter.
* **Via Interactive Menu:** Launch `sync-engine config` and select **Cleaner and Collision Checker** under the Maintenance section.

When launched, the tool displays all registered account profiles along with a manual scan option:

* **[Registered Accounts]:** The system automatically resolves the account's local sync directory path and loads its active exclusion filters.
* **Enter a manual path:** Allows you to input any local directory path (e.g., `C:\Downloads` or `~/Documents`) to sanitize folders that are not part of Sync Engine's configured sync profiles.

Once the process finishes, a complete execution report detailing all renamed files is written to your default reports directory (saved as `_ultimo_relatorio_higienizador.txt`).

---

## 3. Practical Use Cases

### Example 1: Post-Extraction Sanitization (Web or macOS Archives)
You downloaded a `.zip` archive containing legacy course materials or assets exported from macOS and extracted it into your synchronized Google Drive folder. Several files contain names such as `Lesson 01: Introduction.pdf` or `Archive 2024/2025.txt`.  
**The Risk:** Synchronization will abort as soon as Rclone encounters colons (`:`) or slashes (`/`).  
**The Solution:**
1. Open your terminal and run `sync-engine clean`.
2. Select your Google Drive account profile.
3. The Cleaner scans the directory hierarchy, replaces or removes prohibited characters, and verifies that the folder is safe for cloud transfer.
4. Normal synchronization resumes automatically.

### Example 2: Red Collision Alert (Background Engine Paused)
While running Sync Engine as a background daemon on Linux, you notice an alert notification or encounter the following warning when running `sync-engine now`:
> *🚨 ALERT: Case-Sensitivity Conflicts or Invalid Characters detected!*  
> *Sync for 'Work' paused. Use Option 9 to fix.*  
**The Cause:** The background monitor detected a collision hazard (such as `Photo.JPG` and `photo.jpg` residing in the same folder). To prevent data loss or remote corruption, it suspended automated synchronization for that profile.  
**The Solution:**
1. Run the cleaner directly: `sync-engine clean`.
2. Select the "Work" profile.
3. The utility pinpoints the conflicting filenames and safely renames the duplicate file to avoid data loss. With the naming conflict resolved, the background engine clears the safety lock and resumes sync automatically.

### Example 3: Standalone External Drive / USB Sanitization
A colleague provided a USB flash drive containing improperly formatted file names (including non-standard emojis, stars, and trailing spaces), and you need to copy them to a shared corporate network share that rejects non-compliant paths.  
**The Solution:**
1. You do not need to register the external drive as a Sync Engine account profile.
2. Run `sync-engine clean` and select **Enter a manual path**.
3. Enter the mount point or drive path (e.g., `E:\Client_Files` or `/media/usb`).
4. The Cleaner operates independently, sanitizing all problematic filenames across the external volume within seconds.