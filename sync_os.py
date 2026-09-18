import os
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
    if SISTEMA == "Linux":
        service_name = "sync-engine.service"
        if action in ["start", "reload"]: _setup_linux_service()
            
        if action == "start":
            res = subprocess.run(["systemctl", "--user", "enable", "--now", service_name], capture_output=True, text=True)
            if res.returncode == 0: print("✅ Motor Linux (Systemd) iniciado e habilitado.")
            else: print(f"❌ Erro ao iniciar o motor: {res.stderr.strip()}")
        elif action == "stop":
            subprocess.run(["systemctl", "--user", "disable", "--now", service_name], capture_output=True)
            print("🛑 Motor Linux (Systemd) parado e desabilitado.")
        elif action == "status":
            subprocess.run(["systemctl", "--user", "status", service_name])
        elif action == "reload":
            subprocess.run(["systemctl", "--user", "restart", service_name], capture_output=True)
            print("🔄 Motor Linux (Systemd) reiniciado.")
            
    elif SISTEMA == "Windows":
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_path = os.path.join(startup_dir, "SyncEngine.lnk")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if action == "start":
            # Cria atalho invisível e inicia o processo sem piscar tela
            ps_script = f"$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '`\"{base_dir}\\sync_engine.py`\"'; $Shortcut.WorkingDirectory = '{base_dir}'; $Shortcut.WindowStyle = 0; $Shortcut.Save()"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], creationflags=_get_cflags())
            subprocess.Popen(["pythonw", "sync_engine.py"], cwd=base_dir, creationflags=_get_cflags())
            print("✅ Motor Windows iniciado imediatamente e habilitado no Startup.")
            
        elif action == "stop":
            # Apaga o atalho de inicialização
            if os.path.exists(shortcut_path): os.remove(shortcut_path)
            
            # Caça e aniquila APENAS o processo invisível (pythonw.exe), poupando o menu atual!
            ps_kill = "Get-WmiObject Win32_Process -Filter \"Name='pythonw.exe'\" | Where-Object { $_.CommandLine -match 'sync_engine' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], creationflags=_get_cflags())
            print("🛑 Motor Windows parado e desabilitado do Startup.")
            
        elif action == "status":
            if os.path.exists(shortcut_path): print("\n📊 Status (Startup): Inicialização Automática ATIVADA.")
            else: print("\n📊 Status (Startup): Inicialização Automática DESATIVADA.")
            
            # NOVIDADE: Adicionado o filtro Name='pythonw.exe' igual fizemos no Stop!
            ps_check = "Get-WmiObject Win32_Process -Filter \"Name='pythonw.exe'\" | Where-Object { $_.CommandLine -match 'sync_engine' }"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", f"({ps_check}).ProcessId"], capture_output=True, text=True, creationflags=_get_cflags())
            
            if res.stdout.strip(): print("🟢 Status (Memória): O motor invisível está RODANDO agora.")
            else: print("🔴 Status (Memória): O motor invisível está PARADO agora.")
        elif action == "reload":
            print("\n🔄 Recarregando o motor invisível...")
            manage_service("stop", log_file)
            import time; time.sleep(1) # Pausa de 1 segundo para garantir a liberação da memória
            manage_service("start", log_file)

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
    if SISTEMA == "Linux":
        if shutil.which("systemctl"): print("🟢 Systemd: Suportado.")
        else: print("🔴 Systemd: Ausente.")
    elif SISTEMA == "Windows":
        print("🟢 Windows Startup Folder: Suportado.")
