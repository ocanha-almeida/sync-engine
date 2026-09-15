#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import re
import urllib.request
import zipfile
import tempfile
import shutil
import ssl

# ==========================================
# ÂNCORA DE DIRETÓRIO E IMPORTAÇÃO DOS MÓDULOS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)

from sync_config import load_config, save_config, get_report_dir, VERSION, CONFIG_DIR, LOG_FILE, logger, clean_log_file
from sync_os import manage_service, send_notification, run_doctor_os, SISTEMA
from sync_core import init_db, scan_local, scan_remote, generate_filters, analyze_sync_logic

UPDATE_URL_RAW = "https://raw.githubusercontent.com/ocanha-almeida/sync-engine/main/sync_engine.py"
UPDATE_URL_ZIP = "https://github.com/ocanha-almeida/sync-engine/archive/refs/heads/main.zip"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPressione Enter para continuar...")

# ==========================================
# ROTINAS DE EXECUÇÃO
# ==========================================
def run_sync(local_dir, remote_name, filter_file, bw_limit, max_size, report_dir, profile_name):
    safe_profile = "".join([c for c in profile_name.lower().replace(" ", "_") if c.isalnum() or c=='_'])
    log_file = os.path.join(report_dir, f"ultimo_ciclo_auto_{safe_profile}.txt")
    
    cmd = ["rclone", "bisync", local_dir, f"{remote_name}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", f"--log-file={log_file}"]
    
    if bw_limit != "0": cmd.append(f"--bwlimit={bw_limit}")
    if max_size != "0": cmd.append(f"--max-size={max_size}")

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(log_file, "r", encoding="utf-8") as f: log_text = f.read()
    
    if result.returncode != 0 and "prior lock file found" in log_text.lower():
        lock_match = re.search(r'prior lock file found:\s*([^\r\n]+)', log_text, re.IGNORECASE)
        if lock_match:
            subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(log_file, "r", encoding="utf-8") as f: log_text = f.read()

    has_transfers, err_msg = analyze_sync_logic(log_text)
    
    if result.returncode == 0:
        clean_log_file(log_file)
        return True, has_transfers, ""
    elif "resync" in log_text.lower() or "not found" in log_text.lower():
        cmd.append("--resync")
        resync_result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(log_file, "r", encoding="utf-8") as f: resync_log = f.read()
        has_resync, _ = analyze_sync_logic(resync_log)
        clean_log_file(log_file)
        return resync_result.returncode == 0, has_resync, ""
    else:
        clean_log_file(log_file)
        return False, False, err_msg

def run_now():
    clear_screen()
    print("="*45 + "\n🚀 SINCRONIZAÇÃO IMEDIATA E REPARO (NOW)\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: print("\nNenhuma conta configurada."); pause(); return

    report_dir = get_report_dir(config)
    MANUAL_SYNC_REPORT_FILE = os.path.join(report_dir, "ultima_sincronizacao_manual.txt")
    with open(MANUAL_SYNC_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("="*45 + "\n🚀 RELATÓRIO DE SINCRONIZAÇÃO MANUAL\n" + "="*45 + "\n\n")

    for acc in ACCOUNTS:
        print(f"\n🔄 Conta atual: {acc['PROFILE_NAME']}")
        local_dir = os.path.expanduser(acc["LOCAL_DIR"])
        os.makedirs(local_dir, exist_ok=True)
        
        print("\n  [1] Sincronização Normal (Segura)")
        print("  [2] ⚠️  FORÇAR Sincronização (--force)")
        print("  [3] Pular esta conta")
        
        escolha = input("\nAção (1-3) [Enter = Pular]: ").strip()
        if escolha == '' or escolha == '3': continue
            
        db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
        db_connection = init_db(db_path)
        scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
        try:
            scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
        except RuntimeError:
            print(f"❌ Erro de conexão com {acc['REMOTE_NAME']}. Sincronização abortada."); continue
            
        generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
        db_connection.close()

        cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-P", "-v", f"--log-file={MANUAL_SYNC_REPORT_FILE}"]
        if escolha == '2': cmd.append("--force")
        
        subprocess.run(cmd)
        
        with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()
        if "prior lock file found" in log_text.lower():
            lock_match = re.search(r'prior lock file found:\s*([^\r\n]+)', log_text, re.IGNORECASE)
            if lock_match:
                print(f"\n⚠️  Quebrando cadeado automaticamente...")
                subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()])
                subprocess.run(cmd)
                with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()

        if "resync" in log_text.lower() or "not found" in log_text.lower():
            print(f"\n⚠️ Acionando varredura de cura (--resync)...")
            cmd.append("--resync"); subprocess.run(cmd)
            
        clean_log_file(MANUAL_SYNC_REPORT_FILE)
        print(f"\n✅ Concluído: {acc['PROFILE_NAME']}")
    
    print(f"\n📂 Relatório salvo em: {MANUAL_SYNC_REPORT_FILE}"); pause()

def run_update():
    clear_screen()
    print("="*45 + "\n🔄 VERIFICADOR DE ATUALIZAÇÕES\n" + "="*45)
    print(f"Versão local:  {VERSION}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(UPDATE_URL_RAW, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'^VERSION\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            remote_version = match.group(1) if match else None
    except Exception as e:
        print(f"❌ Erro de rede: {e}"); pause(); return

    if not remote_version:
        print("❌ Não foi possível identificar a versão no servidor."); pause(); return

    print(f"Versão remota: {remote_version}\n")
    if remote_version == VERSION:
        print("✅ Você já está utilizando a versão mais recente!"); pause(); return
        
    print("🎉 Uma nova versão está disponível!")
    resp = input("Deseja baixar e instalar a atualização agora? (S/N) [N]: ").strip().lower()
    if resp != 's': return
        
    print("\n📥 Baixando pacote de atualização...")
    try:
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "update.zip")
        req = urllib.request.Request(UPDATE_URL_ZIP, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("📦 Extraindo arquivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(tmp_dir)
        
        extract_dir = os.path.join(tmp_dir, "sync-engine-main")
        if SISTEMA == "Windows":
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "install.ps1"], cwd=extract_dir)
        else:
            subprocess.run(["bash", "install.sh"], cwd=extract_dir)
            
        shutil.rmtree(tmp_dir)
        print("\n✅ Atualização concluída com sucesso!"); pause()
    except Exception as e:
        print(f"\n❌ Erro durante o processo de atualização: {e}"); pause()

def run_config_wizard():
    while True:
        config = load_config()
        clear_screen()
        print(f"=== Assistente Sync Engine (v{VERSION}) ===\n" + "="*45)
        print("\n--- Configuração de Contas ---")
        print("1. Adicionar nova conta")
        print("2. Listar contas atuais")
        print("3. Remover uma conta")
        
        print("\n--- Configurações Globais ---")
        print("4. Editar Intervalo, Limites e Pastas")
        print("5. Gerenciar Filtros de Exclusão")
        
        print("\n--- Ações Extras ---")
        print("6. 🚀 Forçar Sincronização Agora")
        print("7. 🩺 Diagnóstico do Sistema (Doctor)")
        
        print("\n--- Motor de Segundo Plano ---")
        print("8. ▶️ Ligar Serviço")
        print("9. ⏹️ Desligar Serviço")
        print("10. ℹ️ Checar Status do Motor")
        print("11. 🔄 Atualizar Versão do Aplicativo")
        
        print("\n[Enter] Sair\n" + "="*45)
        
        escolha = input("Opção: ").strip()
        if escolha == '': clear_screen(); print("Até logo!\n"); break
        
        if escolha == '1':
            profile = input("\nNome do Perfil [Enter p/ voltar]: ").strip()
            if not profile: continue
            rclone_out = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            remotes = [r.strip(':') for r in rclone_out.stdout.strip().split('\n') if r.strip()]
            for i, r in enumerate(remotes): print(f"  [{i+1}] {r}")
            op_remote = input("\nNúmero da nuvem [Enter p/ voltar]: ").strip()
            if not op_remote or not op_remote.isdigit() or int(op_remote)-1 >= len(remotes): continue
            
            remote = remotes[int(op_remote) - 1]
            local = input(f"\nPasta local (Enter para '~/{remote}'): ").strip() or f"~/{remote}"
                
            safe_name = "".join([c for c in profile.lower().replace(" ", "_") if c.isalnum() or c=='_'])
            config.setdefault("ACCOUNTS", []).append({
                "PROFILE_NAME": profile, "REMOTE_NAME": remote, "LOCAL_DIR": local,
                "IGNORE_PATTERNS": ["venv", ".venv", "__pycache__", ".git", "Personal Vault", "Cofre Pessoal", "*.tmp", ".DS_Store"],
                "DB_FILE": f"sync_metadata_{safe_name}.db", "FILTER_FILE": f"excludes_{safe_name}.txt"
            })
            save_config(config, f"Adicionada conta '{profile}'"); manage_service("reload", LOG_FILE); print("\n✅ Salvo!"); pause()

        elif escolha == '2':
            clear_screen(); print("--- Contas ---")
            for i, acc in enumerate(config.get("ACCOUNTS", [])): print(f"[{i+1}] {acc['PROFILE_NAME']} ({acc['LOCAL_DIR']})")
            pause()
                
        elif escolha == '3':
            contas = config.get("ACCOUNTS", [])
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            op = input("\nNúmero para apagar [Enter para voltar]: ").strip()
            if op.isdigit() and 1 <= int(op) <= len(contas):
                apagada = contas.pop(int(op)-1)
                save_config(config, f"Removida conta '{apagada['PROFILE_NAME']}'"); manage_service("reload", LOG_FILE); print(f"\n🗑️ Removida: {apagada['PROFILE_NAME']}"); pause()
                
        elif escolha == '4':
            while True:
                clear_screen(); print("--- Configurações Globais ---")
                print(f"1. Intervalo ({config.get('SYNC_INTERVAL', 300)}s)")
                print(f"2. Banda ({config.get('BW_LIMIT', '0')})")
                print(f"3. Max Size ({config.get('MAX_SIZE', '0')})")
                print(f"4. Pasta Relatórios (Atual: {config.get('REPORT_DIR', 'Padrão ~/.config/sync_engine')})")
                
                op_cfg = input("\nOpção [Enter p/ voltar]: ").strip()
                if not op_cfg: break
                elif op_cfg == '1': config["SYNC_INTERVAL"] = int(input("Segundos: ") or 300)
                elif op_cfg == '2': config["BW_LIMIT"] = input("Limite (ex: 10M, 0): ").strip()
                elif op_cfg == '3': config["MAX_SIZE"] = input("Max (ex: 1G, 0): ").strip()
                elif op_cfg == '4': config["REPORT_DIR"] = input("Caminho: ").strip()
                save_config(config, "Configurações globais alteradas"); manage_service("reload", LOG_FILE)

        elif escolha == '5':
            contas = config.get("ACCOUNTS", [])
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            op_acc = input("\nConta [Enter p/ voltar]: ").strip()
            if op_acc.isdigit() and 1 <= int(op_acc) <= len(contas):
                conta = contas[int(op_acc) - 1]
                padroes = conta.get("IGNORE_PATTERNS", [])
                while True:
                    clear_screen(); print(f"--- Filtros: {conta['PROFILE_NAME']} ---")
                    for j, p in enumerate(padroes): print(f"  [{j+1}] {p}")
                    print("\n[A] Adicionar  [R] Remover  [S] Salvar e Sair  [Enter] Cancelar Alterações")
                    acao = input("Ação: ").strip().lower()
                    if acao == '' or acao == 'c': break
                    elif acao == 's': conta["IGNORE_PATTERNS"] = padroes; save_config(config, f"Filtros alterados em '{conta['PROFILE_NAME']}'"); manage_service("reload", LOG_FILE); break
                    elif acao == 'a': novo = input("Padrão: ").strip(); padroes.append(novo) if novo else None
                    elif acao == 'r': 
                        num = input("Número: ").strip()
                        if num.isdigit() and 1 <= int(num) <= len(padroes): padroes.pop(int(num)-1)

        elif escolha == '6': run_now()
        elif escolha == '7': clear_screen(); run_doctor_os(); pause()
        elif escolha == '8': clear_screen(); manage_service("start", LOG_FILE); pause()
        elif escolha == '9': clear_screen(); manage_service("stop", LOG_FILE); pause()
        elif escolha == '10': clear_screen(); manage_service("status", LOG_FILE); pause()
        elif escolha == '11': run_update()

def print_help():
    print(f"\n=== Sync Engine Multi-Contas (v{VERSION}) ===")
    print("Uso: sync-engine [COMANDO]")
    print("  config         Assistente interativo.")
    print("  now            🚀 Sincroniza AGORA.")
    print("  start/stop     Liga/Desliga o serviço invisível.")
    print("  status/reload  Checa logs ou reinicia o serviço invisível.")
    print("  -v, --version  Exibe a versão.")
    print("  -h, --help     Exibe esta ajuda.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        if comando in ["-h", "--help", "help"]: print_help()
        elif comando in ["-v", "--version", "version"]: print(f"Sync Engine v{VERSION}")
        elif comando == "config": run_config_wizard()
        elif comando == "now": run_now()
        elif comando == "start": manage_service("start", LOG_FILE)
        elif comando == "stop": manage_service("stop", LOG_FILE)
        elif comando == "status": manage_service("status", LOG_FILE)
        elif comando == "reload": manage_service("reload", LOG_FILE)
        else: run_config_wizard() 
        sys.exit(0)
    else:
        is_terminal = False
        try:
            if sys.stdout is not None and sys.stdout.isatty(): is_terminal = True
        except Exception: pass
        if is_terminal: print_help(); sys.exit(1)
        
    try:
        logger.info("Motor Sync Engine Iniciado em Background.")
        while True:
            config = load_config()
            ACCOUNTS = config.get("ACCOUNTS", [])
            if not ACCOUNTS: sys.exit(1)

            for acc in ACCOUNTS:
                profile = acc.get("PROFILE_NAME", "Local")
                local_dir = os.path.expanduser(acc["LOCAL_DIR"])
                os.makedirs(local_dir, exist_ok=True)
                
                db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
                db_conn = init_db(db_path)
                scan_local(db_conn, local_dir, acc.get("IGNORE_PATTERNS", []))
                try:
                    scan_remote(db_conn, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
                except RuntimeError as e:
                    logger.error(f"[{profile}] Sincronização bloqueada: {e}")
                    continue
                    
                generate_filters(db_conn, filter_file, acc.get("IGNORE_PATTERNS", []))
                db_conn.close()
                
                success, transfers, err_msg = run_sync(local_dir, acc["REMOTE_NAME"], filter_file, config.get("BW_LIMIT", "0"), config.get("MAX_SIZE", "0"), get_report_dir(config), profile)
                
                if success and transfers:
                    logger.info(f"[{profile}] Sincronização concluída com alterações.")
                    send_notification("Sync Engine", f"Conta '{profile}' sincronizada.")
                elif not success:
                    logger.error(f"[{profile}] Erro: {err_msg}")
            
            time.sleep(config.get("SYNC_INTERVAL", 300))
    except Exception as e:
        logger.error(f"FALHA CRÍTICA DO MOTOR: {e}")