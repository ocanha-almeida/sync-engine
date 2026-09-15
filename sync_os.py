import os
import subprocess
import platform
import shutil

SISTEMA = platform.system()

def manage_service(action, log_file):
    if SISTEMA == "Linux":
        service_name = "sync-engine.service"
        if action == "start":
            subprocess.run(["systemctl", "--user", "enable", "--now", service_name])
            print("✅ Motor Linux (Systemd) iniciado e habilitado.")
        elif action == "stop":
            subprocess.run(["systemctl", "--user", "disable", "--now", service_name])
            print("🛑 Motor Linux (Systemd) parado.")
        elif action == "status":
            subprocess.run(["systemctl", "--user", "status", service_name])
        elif action == "reload":
            subprocess.run(["systemctl", "--user", "restart", service_name])
            
    elif SISTEMA == "Windows":
        # No Windows, agora usamos a pasta Startup do usuário em vez do Agendador
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_path = os.path.join(startup_dir, "SyncEngine.lnk")
        
        if action == "start":
            # Como a inicialização é por atalho no boot, o 'start' avisa para reiniciar
            print("✅ Motor Windows (Startup) configurado. Reinicie o PC ou execute o script manualmente para iniciar o ciclo de fundo.")
        elif action == "stop":
            print("🛑 Para parar o motor no Windows, finalize o processo 'pythonw.exe' no Gerenciador de Tarefas.")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print("✅ Inicialização automática desabilitada.")
        elif action == "status":
            if os.path.exists(shortcut_path):
                print("\n📊 Status: Inicialização Automática (Startup) ATIVADA no Windows.")
            else:
                print("\n📊 Status: Inicialização Automática DESATIVADA.")

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
            safe_title = title.replace("'", "")
            safe_msg = message.replace("'", "")
            ps_cmd = f"Add-Type -AssemblyName System.Windows.Forms; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.Visible = $true; $notify.ShowBalloonTip(5000, '{safe_title}', '{safe_msg}', [System.Windows.Forms.ToolTipIcon]::Info); Start-Sleep -Seconds 5; $notify.Dispose()"
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception: pass

def run_doctor_os():
    if SISTEMA == "Linux":
        if shutil.which("systemctl"): print("🟢 Systemd: Suportado.")
        else: print("🔴 Systemd: Ausente.")
    elif SISTEMA == "Windows":
        print("🟢 Windows Startup Folder: Suportado.")