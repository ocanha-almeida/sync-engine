# ⚙️ Background Engine & Diagnostics Guide

The core of Sync Engine is its **Background Engine (Daemon)**. Unlike many corporate backup solutions, it is engineered with an architectural focus on security, privacy, and low resource overhead, running entirely invisibly on your local computer.

---

## 1. Architecture: The "User Space"

The most significant security design choice in Sync Engine is that the background motor operates strictly within the **User Space**.

* **Zero Administrative Privileges:** Sync Engine never prompts for Administrator credentials on Windows, nor does it require root (`sudo`) access on Linux to synchronize your files.
* **Data Isolation:** Because the process runs bound to your specific operating system user profile, it only accesses directories your user account is authorized to view. It cannot access or expose files belonging to other users on the shared machine.
* **Secure Startup:**
  * **On Linux:** Integrates natively as an isolated Systemd User Unit (`systemctl --user`), starting automatically only when you log into your desktop environment or user session.
  * **On Windows:** Configures a silent background startup entry pointing directly to `pythonw.exe` in your personal startup folder, ensuring no console or terminal windows interrupt your workflow.

---

## 2. Engine Management

You have complete control over the lifecycle of the background daemon through the **Background Motor** section in the main wizard (`sync-engine config`). The available operations include:

* **▶️ Start Service (Enable):** Installs (if running for the first time) and starts the background daemon. It registers the background motor to launch automatically with your operating system.
* **⏸️ Stop / Kill Service (Disable):** Immediately terminates active background synchronization tasks and unregisters auto-startup. This is ideal if you are tethering cellular data or wish to suspend network consumption temporarily.
* **📊 View Service Status (Status):** Displays a real-time status summary indicating whether the daemon is **Running (Active)** or **Stopped (Inactive)**, alongside the timestamp of the last completed check cycle (last wake-up event).

---

## 3. System Diagnostic (System Doctor)

If Sync Engine experiences unexpected latency, startup issues, or if background synchronization stalls, your first line of investigation should be the built-in diagnostic utility.

* **How to access:** In the main menu, navigate to **Maintenance** > **System Diagnostic (Doctor)**.

The System Doctor performs a thorough inspection of your environment and outputs a color-coded traffic light overview (Green, Yellow, Red) evaluating four critical pillars:

1. **System Dependencies:** Confirms that Python and the Rclone binary are installed and directly accessible through your system's `$PATH`.
2. **Database Integrity:** Tests read and write operations against your local SQLite database (`sync_metadata_*.db`), which stores fast file indexing tables.
3. **Remote Connections:** Dispatches a non-intrusive health ping to all registered cloud remotes to verify that OAuth tokens have not been revoked by the cloud provider.
4. **Local Directory Paths:** Verifies that all configured local directories (e.g., `~/gdrive`) still physically exist on your storage drive.

---

## 4. Updates and Uninstallation

The User Space architecture also ensures clean lifecycle maintenance:

* **Automated Updates (Update System):** Triggered directly from the maintenance menu, Sync Engine downloads the latest stable release package from the official GitHub repository and updates its codebase in-place. It preserves your accounts, filters, and configuration database (`config.json`) untouched.
* **Clean Uninstallation (Uninstall/Clean-up):** With a single confirmation, this routine unregisters system startup hooks, terminates running background workers, and provides explicit instructions on which specific local directories to delete (`~/.local/share/sync-engine` and `~/.config/sync_engine` on Linux, or `%LOCALAPPDATA%\sync-engine` and `%USERPROFILE%\.config\sync_engine` on Windows). This ensures no orphan registry keys or background daemons are left behind on your machine.