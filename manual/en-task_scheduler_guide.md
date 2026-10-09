# ⏰ Task Scheduler Guide

Sync Engine features a native Task Scheduler inspired by Linux's Cron system, but presented with a fully interactive command-line interface. This eliminates the need to configure complex rules in the *Windows Task Scheduler* or manually edit *crontab* files on Linux to automate routines at specific times.

Everything is managed directly within the Sync Engine interactive wizard and executed seamlessly in the background.

---

## ⚠️ Fundamental Requirement

For any scheduled task to run at its designated time, the Sync Engine **Background Engine** must be **ON (Active)**.

The scheduler does not wake up a suspended computer from sleep or launch the terminal application on its own. It operates as an internal timer within the background daemon, checking at every cycle whether any scheduled job matches the current system time.

---

## 1. Supported Task Types

When creating a new scheduled job, you can choose from three distinct execution modes:

1. **Normal Sync (Safe):** Runs a standard, safe bidirectional synchronization routine for the selected account.
2. **FORCED Sync (--force):** Bypasses conflict locks and forces synchronization (ideal for resolving conflicting modified files automatically and keeping remotes aligned).
3. **Cloud-to-Cloud Migration:** Initiates a direct server-to-server copy between two cloud providers (e.g., OneDrive to Google Drive) running entirely in the background via RAM streaming.

---

## 2. How to Create a New Scheduled Task

1. Open your terminal and start the interactive wizard:
   ```bash
   sync-engine config
   ```
2. Navigate to the synchronization menu and select **Task Scheduler (Cron)**.
3. Select **➕ Add new scheduled task**.
4. **Choose the Task Type:** Enter `1`, `2`, or `3` according to your requirements (Normal sync, Forced sync, or Cloud Migration).
5. **Select the Target:**
   * For synchronization tasks (`1` or `2`), select the account to synchronize.
   * For cloud migration (`3`), specify the source path and destination path.
6. **Set the Execution Date:**
   * Enter a specific date using the `DD/MM/YYYY` format (e.g., `25/12/2026`).
   * *Tip:* Press **Enter** to leave the field blank if you want the task to run repeatedly as **Daily**.
7. **Set the Execution Time:** Enter the exact run time using 24-hour notation `HH:MM` (e.g., `14:30`, `23:00`).

Once saved, the job will appear immediately in the scheduler overview panel.

---

## 3. Management and Automatic Cleanup

* **Deleting Tasks:** To delete an entry, open the Task Scheduler menu and enter the number corresponding to the item marked with "❌ Delete".
* **Automatic Cleanup:** Tasks assigned to a single, specific calendar date are executed once and automatically purged from the task list the following day to avoid clutter. Recurring **Daily** tasks remain permanently active, updating their "Last Run" status upon each completed execution.

---

## 4. Practical Use Cases

### Example 1: End-of-Day Batch Upload (Daily Sync)
You edit large 4K video projects or heavy design assets locally throughout the working day. If background synchronization runs every 5 minutes, constant uploads might saturate office network bandwidth.  
**The Solution:**
1. Turn off continuous Background Sync for your work account in the Account panel (set to **OFF**).
2. Open the Task Scheduler and configure a **Normal Sync** task.
3. Leave the date blank to make it **Daily** and set the time to `23:00`.  
**Result:** The engine stays dormant during work hours. At 23:00, it uploads the entire day's output in a single batch.

### Example 2: Off-Peak Cloud Mirroring (Scheduled Migration)
You use Google Drive for daily collaboration, but maintain a secondary exact copy on OneDrive for redundancy. Full cloud-to-cloud transfers consume significant API calls and bandwidth, which should not impact daytime work.  
**The Solution:**
1. Create a task with type **Cloud-to-Cloud Migration**.
2. Specify the source (e.g., `gdrive:/Work`) and destination (`onedrive:/Backup`).
3. Set the date for the upcoming Saturday (e.g., `10/10/2026`) and set the time to `02:00` AM.  
**Result:** While you sleep on Saturday morning, Sync Engine transfers files directly across cloud infrastructures without consuming local disk space.

### Example 3: Automated Conflict Resolution (Forced Sync)
A specialized database or note-taking application frequently generates temporary lock files, triggering safety alerts that halt automated sync due to simultaneous edits (*Path1 and Path2 modified*).  
**The Solution:**
1. Create a task with type **FORCED Sync**.
2. Leave the date blank (**Daily**) and configure the execution for `12:00` (lunch break).  
**Result:** Every day at noon, Sync Engine runs an aggressive synchronization run. Any pending lock collision is broken and remotes are resynchronized without manual intervention.