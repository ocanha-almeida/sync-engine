# 🧪 Safe Simulation Mode Guide (Dry-Run)

When setting up new accounts or configuring complex exclusion filters, it is natural to be cautious about triggering a synchronization run that might inadvertently delete or overwrite important files.

To eliminate this uncertainty, Sync Engine provides the **Safe Simulation Mode (Dry-Run)**. This utility executes a mock synchronization pass: it scans your local filesystem, inspects the cloud remote, and calculates precisely which files would be downloaded, uploaded, or deleted—without making **any actual modifications to your data**.

---

## 1. How to Run a Simulation

You can initiate a safe simulation in two ways:

* **Via Terminal CLI:** Run `sync-engine test` and press Enter.
* **Via Interactive Menu:** Launch `sync-engine config` and select **Test / Dry-Run (Safe Simulation)** under the Synchronization section.

The system will prompt you to choose one of your active profiles. Once selected, the engine begins a bidirectional inspection pass. Depending on the total number of files indexed on your remote, this scan may take anywhere from a few seconds to a few minutes.

---

## 2. Interpreting the Simulation Report

Unlike a standard live sync pass, a dry-run does not render an interactive progress bar. Instead, upon completion, it compiles an audit report named `[account_name]_ultimo_dry_run.txt` (or `[account_name]_last_dry_run.txt`) and saves it directly to your default reports directory.

The generated log uses Rclone's native status indicators for each simulated action:

* `+` (Plus sign): Files that **would be uploaded** or **downloaded**.
* `-` (Minus sign): Files that **would be deleted** (from the remote or local disk, based on where they were removed to maintain mirror parity).
* `*` (Asterisk): Files that **would be updated** or replaced (due to recent modifications or timestamp divergence).

*Note:* If you configured a size ceiling (`MAX_SIZE`) for the account profile, the report explicitly identifies any files bypassed during the simulation due to exceeding the limit.

---

## 3. Practical Use Cases

### Example 1: Testing a New Safety Filter
You edited the configuration for your "Work" account and added the filter rule `*.mp4` to prevent heavy raw video files from uploading to Google Drive. Before allowing the automated background daemon to run, you want to verify that the rule syntax is correct.

**The Solution:**
1. Run `sync-engine test` and select the "Work" account.
2. Once the simulation completes, open the generated report file.
3. Press `Ctrl+F` and search for `.mp4`. If the filter rule is functioning correctly, no video files will appear with a `+` prefix (staged for upload), confirming that the extension was completely ignored.

### Example 2: Pre-Download Audit on a New Machine
You installed Sync Engine on a new computer and linked an empty local directory to a large 500 GB cloud remote, but you want to verify the exact file tree before consuming local disk space.

**The Solution:**
1. Start the simulation via the interactive menu.
2. Inspect the generated report to review the entire directory tree scheduled for download.
3. If you spot an obsolete archive folder (e.g., `/Backups_2020`) that you do not want stored on the new machine, navigate to the filter settings menu, add an exclusion rule for it (`/Backups_2020`), and re-run the simulation to verify the updated scope.

### Example 3: Verifying the `.nosync` Folder Marker
You created an empty file named `.nosync` inside a local "Finances" directory to keep it private and prevent it from syncing to the cloud.

**The Solution:**
To confirm the directory is excluded without taking risks, run a simulation. The log will confirm that the folder subtree was bypassed, ensuring that sensitive data remains isolated before you trigger an immediate sync (`sync-engine now`) or start the background engine.