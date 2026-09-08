import os
import subprocess
import shutil
import time

def manage_service(action, log_file):
    TASK_NAME = "SyncEngine_Background"
    try:
        if action == "start":
            print("\n⚙️ Ligando e ativando o Motor em segundo plano...")
            subprocess.run(["schtasks", "/Run", "/TN", TASK_NAME], capture_output=True)
            print("✅ Sucesso! O motor agora está rodando de forma invisível.")
        elif action == "stop":
            print("\n🛑 Desligando o Motor...")
            subprocess.run(["schtasks", "/End", "/TN", TASK_NAME], capture_output=True)
            print("✅ Sucesso! O motor foi parado.")
        elif action == "status":
            print(f"\n📊 Status da Tarefa Agendada ({TASK_NAME}):\n")
            subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"])
            print(f"\n📝 Últimos registros de Log ({log_file}):")
            # Equivalente ao "tail -n 10" usando powershell
            subprocess.run(["powershell", "-NoProfile", "-Command", f"Get-Content '{log_file}' -Tail 10"])
        elif action == "reload":
            print("🔄 Reiniciando serviço (Task Scheduler)...")
            subprocess.run(["schtasks", "/End", "/TN", TASK_NAME], capture_output=True)
            time.sleep(1)
            subprocess.run(["schtasks", "/Run", "/TN", TASK_NAME], capture_output=True)
    except Exception as e:
        print(f"Erro ao interagir com o Agendador de Tarefas: {e}")

def send_notification(title, message, urgency="normal"):
    try:
        # Limpa aspas que poderiam quebrar o comando do powershell
        safe_title = title.replace("'", "").replace('"', '')
        safe_msg = message.replace("'", "").replace('"', '')
        
        # Chama as bibliotecas de interface do Windows (Balão de Notificação nativo)
        ps_cmd = f"Add-Type -AssemblyName System.Windows.Forms; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.Visible = $true; $notify.ShowBalloonTip(5000, '{safe_title}', '{safe_msg}', [System.Windows.Forms.ToolTipIcon]::Info); Start-Sleep -Seconds 5; $notify.Dispose()"
        
        # Executa sem abrir janelas pretas piscando na tela do usuário
        subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception: 
        pass

def run_update_installer(extract_dir):
    install_script = os.path.join(extract_dir, "install.ps1")
    if os.path.exists(install_script):
        print("\n🛑 Parando o motor atual antes de atualizar...")
        manage_service("stop", "")
        
        print("\n🚀 Iniciando instalador (O Windows pedirá permissão de Administrador na tela):")
        # Invoca o script .ps1 pedindo elevação (UAC) com "RunAs"
        ps_cmd = f'Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File \\"{install_script}\\"" -Verb RunAs -Wait'
        subprocess.run(["powershell", "-Command", ps_cmd])
        
        print("\n✅ Atualização concluída com sucesso!")
        print("⚠️  Aviso: Não se esqueça de rodar 'sync-engine start' para religar o motor.")
    else:
        print("\n❌ Erro: Arquivo install.ps1 não encontrado no pacote baixado.")

def run_doctor_os(config_dir):
    if shutil.which("schtasks"): 
        print("🟢 Agendador de Tarefas: Disponível (Auto-start suportado).")
    else: 
        print("🔴 Agendador de Tarefas: NÃO ENCONTRADO! (O motor de fundo falhará).")

    if shutil.which("powershell"): 
        print("🟢 PowerShell: Disponível (Notificações e update suportados).")
    else: 
        print("🟡 PowerShell: Ausente ou o PATH do sistema está quebrado.")
        
    if os.access(config_dir, os.W_OK): 
        print("🟢 Permissões: Acesso total à pasta de configurações.")
    else: 
        print("🔴 Permissões: Sem acesso de escrita na pasta do usuário!")