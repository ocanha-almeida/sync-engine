# 🚀 Manual Synchronization Guide (Force Sync Now)

While Sync Engine stands out for its quiet, automated background execution, there are times when you need immediate control. The **Manual Synchronization** feature is designed for on-demand execution, offering real-time visual feedback (Rclone's native progress statistics) and assertive conflict resolution tools.

## 1. How to Start a Manual Sync

You can trigger an on-demand synchronization in two ways:

* **Via Terminal CLI (Shortcut):** Type `sync-engine now` and press Enter.
* **Via Interactive Menu:** Launch `sync-engine config` and select **Force Sync Now** under the Synchronization section.

When triggered, the system asks whether you want to sync **All accounts sequentially (Batch)** or target a **specific account**.

---

## 2. Execution Modes

After selecting your target account, two execution modes are available. The system logs your selected mode and the complete execution details in `_ultima_sincronizacao_manual.txt` (or `_last_manual_sync.txt`).

### [1] Normal Sync (Safe)
This is the default safe mode. It evaluates differences between your local filesystem and the cloud remote, transferring only files that were newly created, modified, or deleted.
* **Best used for:** Routine synchronization runs where you want visual feedback on progress (e.g., tracking the upload progress of newly added assets).
* **Safety mechanisms:** If the engine detects that the same file was modified locally and remotely at the same time, or if dangerous structural divergence occurs, it preemptively halts execution to prevent data loss.

### [2] ⚠️ FORCE Sync (--force)
Forced mode bypasses safety locks triggered by concurrent modifications.
* **Best used for:** Situations where safe (Normal) sync repeatedly halts due to "both paths modified" warnings (*Path1 and Path2 modified*), and you want the engine to resolve the deadlock automatically.
* **Safety notice:** Use with care. The engine forces synchronization and prioritizes files with the most recent modification timestamp.

---

## 3. Built-In Protection and Self-Healing

During manual synchronization, Sync Engine acts as a safeguard by running three automated checks without requiring manual flags:

* **Pre-Sync Collision Inspection:** Before contacting the cloud remote, the engine scans your local folder. If it detects filenames differing only by letter case (e.g., `Report.pdf` and `report.pdf`) or containing invalid characters (`?`, `*`, `"`), it triggers a **Conflict Alert**. This prevents corrupting the remote file tree.
* **Automatic Lock Breaking (Auto-Unlock):** If a previous run was interrupted abruptly (such as by a sudden power loss or terminal closure), leaving behind an orphaned lock file, Sync Engine inspects the log, breaks the lock file, and restarts the transfer cleanly.
* **Healing Scan:** If cached listing indexes (*Path1/Path2 listings*) are missing or corrupted, the system detects the discrepancy and automatically triggers a `--resync` pass to rebuild the listing baseline from scratch.

---

## 4. Practical Use Cases

### Example 1: Emergency Upload with Visual Progress
You just copied 15 GB of media to your local folder and need to shut down your laptop for travel, but you want to ensure everything reached Google Drive first.
1. Open your terminal and run `sync-engine now`.
2. Select your account profile.
3. Choose option **[1] Normal Sync (Safe)**.
4. The terminal displays real-time progress statistics, including upload speed, current files, and ETA. Once the terminal displays the green completion message, you can safely shut down your machine.

### Example 2: Resolving a Stalled Sync Profile
You notice that an account stopped updating in the background. Running the "Sync Error Analyzer" points to an *eTag* mismatch or stale lock state.
1. Run `sync-engine now` and select the affected account.
2. Choose option **[2] ⚠️ FORCE Sync (--force)**.
3. The engine clears residual lock states, overrides conflicts based on the newest timestamp, and outputs an audit log detailing what was updated.

### Example 3: Catching Naming Conflicts on Newly Extracted Files
You extracted an older `.zip` archive into your synchronized directory containing non-standard or illegal characters. Running `sync-engine now` triggers a red warning:
> *🚨 ALERT: Case-Sensitivity Conflicts or Invalid Characters detected!*

The engine suspends execution before any files are uploaded. To fix this, cancel the sync prompt (press Enter), return to the main menu, and run the **Cleaner and Collision Checker** (`sync-engine clean`). The cleaner sanitizes invalid paths automatically, allowing you to re-run your manual sync safely.