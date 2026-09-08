import os
import subprocess
import shutil

def manage_service(action, log_file):
    SERVICE = "sync-engine.service"
    try:
        if action == "start":
            print("\n⚙️ Ligando e ativando o Motor em segundo plano...")
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
            subprocess.run(["systemctl", "--user", "enable", "--now", SERVICE], check=False)
            print("✅ Sucesso! O motor agora está rodando de forma invisível.")
        elif action == "stop":
            print("\n🛑 Desligando o Motor...")
            subprocess.run(["systemctl", "--user", "disable", "--now", SERVICE], check=False)
            print("✅ Sucesso! O motor foi parado.")
        elif action == "status":
            print(f"\n📊 Status do Serviço ({SERVICE}):\n")
            subprocess.run(["systemctl", "--user", "status", SERVICE, "--no-pager"])
            print(f"\n📝 Últimos registros de Log ({log_file}):")
            subprocess.run(["tail", "-n", "10", log_file])
        elif action == "reload":
            check = subprocess.run(["systemctl", "--user", "is-active", SERVICE], capture_output=True, text=True)
            if check.stdout.strip() == "active":
                print("🔄 Serviço detectado. Reiniciando automaticamente...")
                subprocess.run(["systemctl", "--user", "restart", SERVICE], check=False)
    except Exception as e:
        print(f"Erro ao interagir com o sistema: {e}")

def send_notification(title, message, urgency="normal"):
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"
        subprocess.run(["notify-send", title, message, "--urgency", urgency, "--app-name", "Sync Engine", "--icon", "folder-remote"], env=env, check=False)
    except Exception: 
        pass

def run_update_installer(extract_dir):
    install_script = os.path.join(extract_dir, "install.sh")
    if os.path.exists(install_script):
        os.chmod(install_script, 0o755)
        print("\n🛑 Parando o motor atual antes de atualizar...")
        manage_service("stop", "")
        
        print("\n🚀 Iniciando instalador (Pode ser solicitada a senha sudo):")
        subprocess.run(["sudo", "./install.sh"], cwd=extract_dir)
        
        print("\n✅ Atualização concluída com sucesso!")
        print("⚠️  Aviso: Não se esqueça de rodar 'sync-engine start' para religar o motor.")
    else:
        print("\n❌ Erro: Arquivo install.sh não encontrado no pacote baixado.")

def run_doctor_os(config_dir):
    if shutil.which("systemctl"): 
        print("🟢 Systemd: Disponível (Auto-start suportado).")
    else: 
        print("🔴 Systemd: NÃO ENCONTRADO! (O motor de fundo não funcionará).")

    if shutil.which("notify-send"): 
        print("🟢 Notificações (libnotify): Instalado.")
    else: 
        print("🟡 Notificações: Ausente (Instale 'libnotify-bin' se quiser alertas).")
        
    if os.access(config_dir, os.W_OK): 
        print("🟢 Permissões: Acesso total à pasta de configurações.")
    else: 
        print("🔴 Permissões: Sem acesso de escrita na pasta de configurações!")