# 🔎 Sync Error Analyzer Guide

Rclone is an exceptionally powerful engine, but its raw output logs are often overwhelmingly technical, filled with hundreds of lines of stack traces, API transaction IDs, and remote server codes (`HTTP 403`, `Rate Limit Exceeded`, etc.) that can be confusing to interpret.

The **Sync Error Analyzer** in Sync Engine functions as an intelligent log interpreter. It scans error logs from past synchronization routines (both manual CLI triggers and automated background runs), strips away technical noise, and presents an actionable diagnostic report outlining exactly what failed and the precise steps required to fix it.

---

## 1. How to Launch the Analyzer

You can run the analyzer in two ways:
* **Via Terminal CLI:** Enter `sync-engine analyze` and press Enter.
* **Via Interactive Menu:** Launch `sync-engine config` and navigate to the **Sync Error Analyzer** option under the Maintenance section.

The system inspects your local logs and lists every account that encountered an error in recent cycles. Once you select an account, the engine parses the raw log and compiles its diagnosis.

---

## 2. Common Issues Translated

The Analyzer translates dozens of cloud communication, network, and file-system failures into clear guidance. Below are the most frequent scenarios identified by the engine:

### 🔴 Expired Security Tokens (Most Critical)
Providers like Microsoft OneDrive and Google Drive rely on OAuth refresh tokens for authenticated sessions. Due to security timeout policies or prolonged idle intervals, these access tokens periodically expire. Instead of displaying cryptic authentication codes, the Analyzer reports:
> *🚨 Expired Token Detected! The cloud provider terminated communication for security reasons.*

When this occurs, the tool offers an interactive terminal prompt asking if you want to open your web browser. Confirming the prompt initiates a one-click re-authorization flow on the provider's official portal, immediately renewing the token and restoring your connection.

### 🟡 Files in Use (File Locked by Another Process)
If the engine attempts to sync an open spreadsheet, an active database, or a binary file currently held exclusively by an operating system process, the transfer fails.
* **The Diagnosis:** The Analyzer isolates and lists the specific locked file paths and advises you to close the programs accessing them before the next synchronization cycle runs.

### 🟠 Bandwidth Ceilings or Exhausted Storage (Rate Limit / Quota Reached)
When uploading substantial volumes of data in short bursts, providers such as Google Drive may enforce rolling daily upload caps (typically 750 GB/day).
* **The Diagnosis:** The Analyzer clearly distinguishes between a temporary cloud API "Rate Limit" (which clears automatically within 24 hours) and an account storage pool that is completely full.

---

## 3. Practical Use Cases

### Example 1: Resolving a Silent Background Halt
You notice from your status overview that your "Work" account has not synced for two days, despite a stable internet connection.
1. Run `sync-engine analyze` in your terminal.
2. The tool parses the latest background log generated silently by the daemon.
3. The Analyzer identifies the root cause: *"Attention: Synchronization paused because the OneDrive OAuth token has expired."*
4. It presents a browser link. You authenticate, and Sync Engine restores normal synchronization immediately.

### Example 2: The Missing Video Upload
You spent the entire afternoon editing a high-resolution video project, but later discover the master export never appeared on the team's cloud folder.
1. Open the interactive wizard and launch the **Sync Error Analyzer**.
2. The diagnostic output states: *"Failed to transfer 'Master_Export.mp4' - File was locked by another process."*
3. You realize your video editing software is still running minimized in the background. Closing the software frees the file handle, allowing the engine to sync it on the next cycle.

### Example 3: Handling Remote Naming Restrictions
You trigger an immediate sync, but instead of completing with a green success status, the terminal reports an error with dozens of unparsed paths.
1. Rather than combing through complex terminal logs, run the Analyzer.
2. The tool reports: *"Invalid Character Error: The remote provider rejected 5 files containing question marks (?) in their filenames."*
3. With the root cause clearly identified, you immediately run the **Filename Cleaner (`clean`)** command on the affected directory to sanitize the filenames.