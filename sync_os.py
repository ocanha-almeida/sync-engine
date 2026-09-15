import os
import platform
import subprocess
import shutil
import time
from sync_config import logger

SISTEMA = platform.system()

def manage_service(action, log_file):
    if SISTEMA == "Windows":
        manage_windows(action, log_file)
    elif SISTEMA == "Linux":
        manage_linux(action, log_file)

def manage_windows(action, log_file):
    if action == "start":
        print("\n⚙️ Ligando Motor em segundo plano...")
        try:
            subprocess.Popen(["pythonw", "sync_engine.py"], creationflags=subprocess.CREATE_NO_WINDOW)
            print("✅ Sucesso! O motor agora está rodando de forma invisível na sua sessão.")
        except Exception as e:
            print(f"❌ Falha ao iniciar: {e}")
    
    elif action == "stop":
        print("\n🛑 Parando o Motor...")
        subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"], capture_output=True)
        print("✅ Sucesso! O motor foi completamente desabilitado.")
    
    elif action == "status":
        res = subprocess.run(["tasklist", "/FI", "IMAGENAME eq pythonw.exe"], capture_output=True, text=True)
        estado = "RODANDO" if "pythonw.exe" in res.stdout else "PARADO"
        print(f"\n📊 Status do Processo de Fundo (Windows): {estado}")
        print(f"\n📝 Últimos registros de Log ({log_file}):")
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Get-Content '{log_file}' -Tail 10 -ErrorAction SilentlyContinue"])
    
    elif action == "reload":
        manage_windows("stop", log_file)
        time.sleep(1)
        manage_windows("start", log_file)

def manage_linux(action, log_file):
    service_name = "sync-engine.service"
    if action == "start":
        subprocess.run(["systemctl", "--user", "start", service_name])
        subprocess.run(["systemctl", "--user", "enable", service_name])
        print("✅ Motor Linux (Systemd) ligado.")
    elif action == "stop":
        subprocess.run(["systemctl", "--user", "stop", service_name])
        subprocess.run(["systemctl", "--user", "disable", service_name])
        print("✅ Motor Linux parado e desabilitado.")
    elif action == "status":
        subprocess.run(["systemctl", "--user", "status", service_name])
        print(f"\n📝 Logs: {log_file}")
        subprocess.run(["tail", "-n", "10", log_file])
    elif action == "reload":
        subprocess.run(["systemctl", "--user", "restart", service_name])

def send_notification(title, message, urgency="normal"):
    if SISTEMA == "Windows":
        try:
            safe_title = title.replace("'", "").replace('"', '')
            safe_msg = message.replace("'", "").replace('"', '')
            ps_cmd = f"Add-Type -AssemblyName System.Windows.Forms; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.Visible = $true; $notify.ShowBalloonTip(5000, '{safe_title}', '{safe_msg}', [System.Windows.Forms.ToolTipIcon]::Info); Start-Sleep -Seconds 5; $notify.Dispose()"
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass
    elif SISTEMA == "Linux":
        try:
            env = os.environ.copy()
            env["DISPLAY"] = ":0"
            env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"
            subprocess.run(["notify-send", title, message, "--urgency", urgency, "--app-name", "Sync Engine", "--icon", "folder-remote"], env=env, check=False)
        except: pass

def run_doctor_os():
    if SISTEMA == "Windows":
        print("🟢 Windows: Operando nativamente via Startup Mode e Tasklist.")
    else:
        if shutil.which("systemctl"): print("🟢 Systemd: Disponível (Linux).")
        else: print("🔴 Systemd: NÃO ENCONTRADO!")
```