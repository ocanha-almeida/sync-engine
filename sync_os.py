import os
import sys
import subprocess
import platform
import shutil

SISTEMA = platform.system()

def _get_cflags():
    """Garante compatibilidade de flags de console invisível no Windows."""
    return getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if SISTEMA == "Windows" else 0

def _setup_linux_service():
    """Gera o arquivo de serviço dinamicamente se ele não existir."""
    service_dir = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(service_dir, exist_ok=True)
    service_file = os.path.join(service_dir, "sync-engine.service")
    bin_path = os.path.expanduser("~/.local/bin/sync-engine")
    
    unit_content = f"""[Unit]
Description=Sync Engine Background Motor
After=network.target

[Service]
Type=simple
ExecStart={bin_path}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
"""
    with open(service_file, "w", encoding="utf-8") as f:
        f.write(unit_content)
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)

def manage_service(action, log_file):
    # Importa a função de tradução aqui para evitar problemas de importação circular no boot do sistema
    from sync_config import T 

    if SISTEMA == "Linux":
        service_name = "sync-engine.service"
        if action in ["start", "reload"]: _setup_linux_service()
            
        if action == "start":
            res = subprocess.run(["systemctl", "--user", "enable", "--now", service_name], capture_output=True, text=True)
            if res.returncode == 0: print(f"✅ {T('Linux Motor (Systemd) started and enabled.')}")
            else: print(f"❌ {T('Error starting motor:')} {res.stderr.strip()}")
        elif action == "stop":
            subprocess.run(["systemctl", "--user", "disable", "--now", service_name], capture_output=True)
            print(f"🛑 {T('Linux Motor (Systemd) stopped and disabled.')}")
        elif action == "status":
            print("\n" + "="*45)
            subprocess.run(["systemctl", "--user", "status", service_name])
            print("="*45)
            
            res_s = subprocess.run(["pgrep", "-f", "rclone bisync"], capture_output=True, text=True)
            if res_s.stdout.strip():
                print(f"⚡ {T('ACTIVITY:')} {T('Synchronization in progress right now!')}")
            else:
                print(f"💤 {T('ACTIVITY:')} {T('Idle (Waiting for next cycle)')}")
            print("="*45)
            
        elif action == "reload":
            res = subprocess.run(["systemctl", "--user", "is-enabled", service_name], capture_output=True, text=True)
            if "enabled" not in res.stdout:
                print(f"\n⚠️ {T('The motor was disabled. Changes saved, but the motor will remain off.')}")
                return
            subprocess.run(["systemctl", "--user", "restart", service_name], capture_output=True)
            print(f"🔄 {T('Linux Motor (Systemd) restarted.')}")
            
    elif SISTEMA == "Windows":
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_path = os.path.join(startup_dir, "SyncEngine.lnk")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Obtém o caminho absoluto do interpretador atual
        python_exe = sys.executable
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        script_path = os.path.join(base_dir, "sync_engine.py")

        if action == "start":
            ps_script = f"$WshShell = New-Object -comObject WScript.Shell; $Shortcut =$WshShell.CreateShortcut('{shortcut_path}'); $Shortcut.TargetPath = '{pythonw_exe}';$Shortcut.Arguments = '`\"{script_path}`\"'; $Shortcut.WorkingDirectory = '{base_dir}'; $Shortcut.WindowStyle = 0; $Shortcut.Save()"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], creationflags=_get_cflags())
            subprocess.Popen([pythonw_exe, "sync_engine.py"], cwd=base_dir, creationflags=_get_cflags())
            print(f"✅ {T('Windows Motor started and Automatic Startup enabled!')}")

        elif action == "stop":
            if os.path.exists(shortcut_path):
                try: os.remove(shortcut_path)
                except: pass
            ps_kill = "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" | Where-Object { $_.CommandLine -like '*sync_engine*' } \vert{} ForEach-Object { Stop-Process -Id$_.ProcessId -Force }"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], creationflags=_get_cflags())
            print(f"🛑 {T('Windows Motor stopped and Automatic Startup disabled.')}")

        elif action == "status":
            if os.path.exists(shortcut_path):
                print(f"\n📊 {T('Status (Startup): Automatic ENABLED.')}")
            else:
                print(f"\n📊 {T('Status (Startup): Automatic DISABLED.')}")
            
            ps_check_motor = "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" | Where-Object { $_.CommandLine -like '*sync_engine*' } | Select-Object -ExpandProperty ProcessId"
            res_m = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check_motor], capture_output=True, text=True, creationflags=_get_cflags())
            
            ps_check_sync = "Get-CimInstance Win32_Process -Filter \"Name='rclone.exe'\" | Where-Object { $_.CommandLine -like '*bisync*' } | Select-Object -ExpandProperty ProcessId"
            res_s = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check_sync], capture_output=True, text=True, creationflags=_get_cflags())
            
            print("="*45)
            if res_m.stdout.strip():
                print(f"🟢 {T('MOTOR:')} {T('RUNNING (Active in Background)')}")
            else:
                print(f"🔴 {T('MOTOR:')} {T('STOPPED')}")
                
            if res_s.stdout.strip():
                print(f"⚡ {T('ACTIVITY:')} {T('Synchronization in progress right now!')}")
            else:
                print(f"💤 {T('ACTIVITY:')} {T('Idle (Waiting for next cycle)')}")
            print("="*45)

        elif action == "reload":
            is_enabled = os.path.exists(shortcut_path)
            print(f"\n🔄 {T('Reloading the invisible motor in memory...')}")
            ps_kill = "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" | Where-Object { $_.CommandLine -like '*sync_engine*' } \vert{} ForEach-Object { Stop-Process -Id$_.ProcessId -Force }"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], creationflags=_get_cflags())
            import time; time.sleep(1)
            subprocess.Popen([pythonw_exe, "sync_engine.py"], cwd=base_dir, creationflags=_get_cflags())
            if not is_enabled:
                print(f"⚠️ {T('The motor was restarted in memory, but Automatic Startup REMAINS DISABLED.')}")

def send_notification(title, message, urgency="normal"):
    if SISTEMA == "Linux":
        try:
            env = os.environ.copy()
            if "DBUS_SESSION_BUS_ADDRESS" not in env:
                env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"
            subprocess.run(["notify-send", title, message, "--urgency", urgency, "--app-name", "Sync Engine"], env=env, check=False)
        except Exception: pass
    elif SISTEMA == "Windows":
        try:
            safe_title, safe_msg = title.replace("'", ""), message.replace("'", "")
            ps_cmd = f"Add-Type -AssemblyName System.Windows.Forms; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.Visible = $true; $notify.ShowBalloonTip(5000, '{safe_title}', '{safe_msg}', [System.Windows.Forms.ToolTipIcon]::Info); Start-Sleep -Seconds 5; $notify.Dispose()"
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        except Exception: pass

def run_doctor_os():
    from sync_config import T 
    if SISTEMA == "Linux":
        if shutil.which("systemctl"): print(f"🟢 Systemd: {T('Supported.')}")
        else: print(f"🔴 Systemd: {T('Missing.')}")
    elif SISTEMA == "Windows":
        print(f"🟢 Windows Startup Folder: {T('Supported.')}")