# 🌍 Global Settings Guide

While individual Account panels configure isolated rules for each cloud provider, the **Global Settings** menu dictates the behavior of the Sync Engine's core system. The parameters defined here apply system-wide, directly influencing network consumption and local machine performance.

To access these options, start the wizard (`sync-engine config`) and select **Global Settings**.

---

## 1. System Language (Language Selector)

Sync Engine includes native multi-language support.
*   **The "Auto (System Default)" Option:** This is the recommended default setting. The engine detects your operating system's language and loads the corresponding dictionary (e.g., if your Windows installation is in Portuguese, Sync Engine loads `pt.json`). If your operating system's language is not yet supported, it automatically falls back to English (the base codebase language).
*   **Manual Selection:** You can enforce any available language from the list, regardless of your operating system's regional settings. The change takes effect immediately upon restarting the application.

## 2. Global Bandwidth Limit (BW_LIMIT)

When synchronizing large files (such as high-resolution videos or database dumps), Sync Engine can saturate your available upload bandwidth, slowing down internet access for other applications.
*   **How to configure:** You can define a global transfer speed ceiling that Rclone must respect. Accepted units include `500K` (500 Kilobytes per second) or `2M` (2 Megabytes per second).
*   **Usage Insight:** Set this to `0` (Zero) for unlimited speed during off-hours, overnight runs, or weekends to accelerate migrations. During business hours, apply a limit such as `1M` or `2M` to ensure background transfers do not interfere with video conferences or regular web browsing.

## 3. Global Sync Interval

This setting defines how frequently the Background Engine wakes up to inspect your configured folders for file modifications.
*   **How to configure:** The interval is defined in minutes (e.g., `5`, `15`, `60`).
*   **Performance Insight:** 
    *   A `5`-minute interval provides near-real-time mirroring, but increases CPU utilization and issues more frequent API requests to cloud provider endpoints.
    *   For shared servers or free-tier cloud accounts with strict API thresholds, an interval between `15` and `30` minutes is recommended to avoid temporary provider blocks (Rate Limiting).

## 4. Case-Sensitivity Protection

Enables or disables global safeguards against files with structurally identical names differing only by character casing (e.g., `report.pdf` versus `Report.pdf`).
*   **Usage Insight:** Keep this option **Enabled (ON)** if your cloud remotes are accessed across heterogeneous operating systems (such as mixed Linux/macOS and Windows environments). Disabling this check marginally speeds up pre-sync indexing runs, but removes your primary defense against cloud directory collisions and cross-platform sync corruption.

---

## 🚨 PANIC MODE: How to Manually Restore the Language

**The Scenario:** While exploring configuration menus, you accidentally switched the language to an unfamiliar writing system such as Japanese (`jp`) or Chinese (`zh`). Because you cannot read the terminal prompts, navigating back through "Global Settings > Language" using the interactive wizard has become unfeasible.

Sync Engine stores all your preferences persistently in a plain text configuration file. You can easily reset the language by applying "Panic Mode":

### Step-by-Step Recovery:
1.  **Completely close Sync Engine** and terminate any related terminal sessions.
2.  Navigate to your Sync Engine configuration directory. Typical default paths include:
    *   **On Linux:** `~/.config/sync_engine/` (or the installation path `~/.local/share/sync-engine/`).
    *   **On Windows:** `%USERPROFILE%\.config\sync_engine\` (or `C:\Users\YourUser\.config\sync_engine\`).
3.  Locate the file named **`config.json`**.
4.  **🛑 CRITICAL STEP:** Before opening, create a **safety backup** of this file (e.g., duplicate it and name it `config_backup.json`). This ensures your account definitions and exclusion rules remain safe if a formatting error occurs.
5.  Open the original `config.json` file in a plain text editor (Notepad on Windows, or Gedit/Nano/VS Code on Linux).
6.  Locate the line specifying the language code (found near the top of the file); it will look similar to:
    ```json
    "language": "zh",
    ```
7.  Change only the value between quotes to `auto`. The line must read:
    ```json
    "language": "auto",
    ```
8.  Save the file (`Ctrl+S`) and close the editor. Upon restarting Sync Engine in your terminal, the interface will automatically resume using your operating system's native language.

### ⚠️ DANGER WARNING (Structural Integrity)
The `config.json` file is the application's central configuration database.
*   **NEVER remove the double quotation marks (`""`)** enclosing keys and values.
*   **NEVER remove the trailing comma (`,`)** at the end of a line if one is present.
*   If the JSON syntax structure is broken (such as an omitted comma or unmatched bracket), **Sync Engine will fail to launch (Crash)** or, as a safety fallback, overwrite the unparseable file with a clean template, which will result in the **immediate loss of all saved accounts, custom paths, and active filter rules**. Modify only the text inside the quotation marks, save, and exit.