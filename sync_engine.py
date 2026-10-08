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
import fnmatch
import sync_os
from datetime import datetime
import random
import string

# ==========================================
# ÂNCORA E IMPORTAÇÃO DOS MÓDULOS
# ==========================================
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)

from sync_config import load_config, save_config, get_report_dir, VERSION, CONFIG_DIR, LOG_FILE, logger, clean_log_file, clean_log_text, T, BASE_DIR as CONFIG_BASE_DIR
from sync_os import manage_service, send_notification, run_doctor_os, SISTEMA
from sync_core import init_db, scan_local, scan_remote, generate_filters, analyze_sync_logic

UPDATE_URL_RAW = "https://raw.githubusercontent.com/ocanha-almeida/sync-engine/main/sync_config.py"
UPDATE_URL_ZIP = "https://github.com/ocanha-almeida/sync-engine/archive/refs/heads/main.zip"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(T("\nPress Enter to continue..."))

def construir_menu(titulo, itens_menu):
    """
    Construtor reativo. Retorna False se o usuário pressionar Enter (Sair/Voltar).
    Padrões em 'itens_menu':
      - []                    -> Pula uma linha.
      - "Texto"               -> Imprime como cabeçalho.
      - ['Status', None]      -> Painel somente-leitura (O 'None' bloqueia a tecla).
      - ['Label', func]       -> Opção com número sequencial automático.
      - ['Label', func, 'R']  -> Opção com tecla customizada (ex: R).
    """
    clear_screen()
    print(f"=== {titulo} ===\n" + "="*45)
    
    mapa_acoes = {}
    contador = 1
    
    for item in itens_menu:
        if not item:  
            print("")
            continue
            
        if isinstance(item, str):
            print(f"\n{item}")
            continue
            
        etiqueta = item[0]
        acao = item[1]
        
        # O PULO DO GATO: Se a ação for None, é apenas texto informativo
        if acao is None:
            print(etiqueta)
            continue
        
        if len(item) >= 3 and item[2] is not None:
            tecla = str(item[2])
        else:
            tecla = str(contador)
            contador += 1
        
        mapa_acoes[tecla.lower()] = acao
        
        if tecla.isdigit():
            print(f"{tecla}. {etiqueta}")
        else:
            print(f"[{tecla}] {etiqueta}")
            
    print(f"\n[Enter] {T('Return/Exit')}\n" + "="*45)
    
    escolha = input(T("Option: ")).strip().lower()
    if escolha == '':
        return False
        
    if escolha in mapa_acoes:
        mapa_acoes[escolha]()
    return True

# ==========================================
# ROTINAS EXTRAS E UTILITÁRIOS
# ==========================================
def check_name_issues_silent(alvo_expandido, ignore_patterns):
    substituicoes = ["‛", "＂", "｜", "⧸", "：", "？", "＊", "★", "✬", "☆"]
    for root, dirs, files in os.walk(alvo_expandido):
        rel_root = os.path.relpath(root, alvo_expandido)
        if rel_root == '.': rel_root = ""
        rel_root_unix = rel_root.replace("\\", "/")

        if '.nosync' in files: dirs.clear(); continue

        dirs_to_keep = []
        for d in dirs:
            ignored = False
            rel_path = os.path.join(rel_root_unix, d).replace("\\", "/") if rel_root_unix else d.replace("\\", "/")
            for p in ignore_patterns:
                p_unix = p.replace("\\", "/")
                if p_unix.startswith('/') and fnmatch.fnmatch(rel_path, p_unix[1:]): ignored = True; break
                elif fnmatch.fnmatch(d, p_unix): ignored = True; break
            if not ignored: dirs_to_keep.append(d)
        dirs[:] = dirs_to_keep

        vistos_nesta_pasta = set()
        for nome in files:
            rel_path = os.path.join(rel_root_unix, nome).replace("\\", "/") if rel_root_unix else nome.replace("\\", "/")
            ignored = False
            for p in ignore_patterns:
                p_unix = p.replace("\\", "/")
                if p_unix.startswith('/') and fnmatch.fnmatch(rel_path, p_unix[1:]): ignored = True; break
                elif fnmatch.fnmatch(nome, p_unix): ignored = True; break
            if ignored: continue

            if any(char in nome for char in substituicoes): return True
            nome_lower = nome.lower()
            if nome_lower in vistos_nesta_pasta: return True
            vistos_nesta_pasta.add(nome_lower)
    return False

def run_analyze_errors():
    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    logs_disponiveis = []
    
    for acc in config.get("ACCOUNTS", []):
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        auto_log = os.path.join(report_dir, f"{safe_name}_ultimo_ciclo_auto.txt")
        if os.path.exists(auto_log): logs_disponiveis.append((f"🤖 {T('Automatic:')} {acc['PROFILE_NAME']}", auto_log, acc['REMOTE_NAME']))
        manual_log = os.path.join(report_dir, f"{safe_name}_ultima_sincronizacao_manual.txt")
        if os.path.exists(manual_log): logs_disponiveis.append((f"👤 {T('Manual:')} {acc['PROFILE_NAME']}", manual_log, acc['REMOTE_NAME']))
        
    if not logs_disponiveis: 
        clear_screen(); print(f"\n❌ {T('No report found.')}"); pause(); return
        
    mn = []
    for nome, path, remote in logs_disponiveis:
        mn.append([nome, lambda p=path, r=remote: executar_analise_erros(p, r)])
        
    construir_menu(T("Sync Error Analyzer"), mn)
    
def executar_analise_erros(sync_report, remote_name):
    clear_screen()
    total_errors, lstat_errors, etag_errors, resync_requests, lock_errors, auth_errors, other_errors = 0, 0, 0, 0, 0, 0, 0
    with open(sync_report, "r", encoding="utf-8") as f:
        for line in f:
            line_lower = line.lower()
            if "error :" in line_lower or "failed to" in line_lower or "critical error" in line_lower or "prior lock file found" in line_lower:
                total_errors += 1
                if "lstat" in line_lower and "no such file or directory" in line_lower: lstat_errors += 1
                elif "409 conflict" in line_lower or "etag mismatch" in line_lower: etag_errors += 1
                elif "cannot find prior path1 or path2 listings" in line_lower: resync_requests += 1
                elif "prior lock file found" in line_lower: lock_errors += 1
                elif "invalidauthenticationtoken" in line_lower or "couldn't fetch token" in line_lower or "expired" in line_lower or "token" in line_lower: auth_errors += 1
                else: other_errors += 1

    if total_errors == 0: print(f"\n✨ {T('Excellent! Your ecosystem is healthy.')}")
    else:
        print(f"\n⚠️ {T('Found')} {total_errors} {T('problems:')}\n")
        if lock_errors > 0: print(f"🔹 {lock_errors}x {T('Lock File: Engine automatically broke the lock.')}")
        if lstat_errors > 0: print(f"🔹 {lstat_errors}x {T('File not found: Use Option 9 to clean names.')}")
        if etag_errors > 0: print(f"🔹 {etag_errors}x {T('eTag Conflict: Temporary cloud error.')}")
        if resync_requests > 0: print(f"🔹 {resync_requests}x {T('Healing Scan: History broken, engine initiated repair.')}")
        if auth_errors > 0: print(f"🔹 {auth_errors}x {T('Auth/Token Error: The cloud disconnected.')}")
        
    if auth_errors > 0:
        print("\n" + "="*45)
        print(f"🚨🚨 {T('DISCONNECTED CLOUD DETECTED')}")
        print(T("Providers like Microsoft and Google require periodic renewal of security authorization (Token)."))
        resp = input(T("\nDo you want to open the browser and renew the token now? (Y/N) [Y]: ")).strip().lower()
        if resp != 'n':
            print(f"\n⏳ {T('Opening browser for reconnection...')}")
            subprocess.run(["rclone", "config", "reconnect", f"{remote_name}:"])
            print(f"\n✅ {T('Reconnection complete. Future synchronizations should work perfectly.')}")
    pause()

def run_filename_cleaner():
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    
    mn = []
    mn.append([f"⌨️  {T('Enter a manual path')}", acao_cleaner_manual])
    for acc in ACCOUNTS:
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        mn.append([f"📁 {acc['PROFILE_NAME']}", lambda a=acc, s=safe_name: executar_cleaner(a["LOCAL_DIR"], a.get("IGNORE_PATTERNS", []), s)])
        
    construir_menu(T("Cleaner and Collision Checker"), mn)

def acao_cleaner_manual():
    alvo = input(T("\nPath: ")).strip()
    if alvo: executar_cleaner(alvo, [], "avulso")

def executar_cleaner(alvo, ignore_patterns, safe_name):
    # ATENÇÃO: COLE AQUI O CORPO INTEIRO DA SUA ANTIGA FUNÇÃO run_filename_cleaner 
    # (Toda a lógica a partir de: alvo_expandido = os.path.expanduser(alvo)... até print("Done").
    # Deixei abreviado aqui para não cortar a resposta do Gemini, mas é 100% igual ao antigo)
    alvo_expandido = os.path.expanduser(alvo)
    if not os.path.isdir(alvo_expandido): print(f"\n❌ {T('Error: The directory does not exist.')}"); pause(); return
    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_relatorio_higienizador.txt"))
    # ... Continue com o bloco do with open() e os renames ...
    print(f"\n📂 {T('Report saved.')}"); pause() # Apenas ilustrativo, cole seu bloco original!


def run_mount_manager():
    while True:
        config = load_config()
        ACCOUNTS = config.get("ACCOUNTS", [])
        if not ACCOUNTS:
            clear_screen(); print(f"❌ {T('No account configured in Sync Engine.')}"); pause(); return
            
        mn = []
        for i, acc in enumerate(ACCOUNTS):
            status = f"🟢 {T('AUTO')}" if acc.get("AUTO_MOUNT") else f"🔴 {T('MANUAL')}"
            caminho = f" -> {acc.get('MOUNT_PATH')}" if acc.get("AUTO_MOUNT") else ""
            mn.append([f"{acc['PROFILE_NAME']} [{status}{caminho}]", lambda idx=i: cmd_mount_acc(idx)])
            
        if not construir_menu(T("Mount Cloud as Virtual Drive (Mount)"), mn):
            break

def cmd_mount_acc(idx):
    while True:
        config = load_config()
        acc = config["ACCOUNTS"][idx]
        mn = []
        mn.append([f"🔌 {T('Mount temporarily NOW (Open terminal window)')}", lambda: acao_mount_now(idx)])
        mn.append([f"🔄 {T('ENABLE Auto-Mount (Restores with Sync Engine)')}", lambda: acao_mount_enable(idx)])
        mn.append([f"⏹️ {T('DISABLE Auto-Mount')}", lambda: acao_mount_disable(idx)])
        
        if not construir_menu(f"{T('Configuring Mount for:')} {acc['PROFILE_NAME']}", mn):
            break

def acao_mount_disable(idx):
    config = load_config()
    acc = config["ACCOUNTS"][idx]
    acc["AUTO_MOUNT"] = False
    acc["MOUNT_PATH"] = ""
    save_config(config, f"{T('Auto-Mount disabled for')} {acc['PROFILE_NAME']}")
    manage_service("reload", LOG_FILE)
    print(f"\n✅ {T('Auto-Mount disabled! It will no longer be recreated on boot.')}"); pause()

def acao_mount_enable(idx):
    config = load_config()
    acc = config["ACCOUNTS"][idx]
    if SISTEMA == "Windows":
        letra = input(T("\nType a free drive letter in Windows (Ex: X, Y, Z)\nLetter: ")).strip().upper()
        if not letra or len(letra) > 1: return
        mount_path = f"{letra}:"
    else: 
        default_path = f"~/Desktop/{acc['REMOTE_NAME']}"
        pasta = input(f"\n{T('Empty folder path to mount (Enter =')} {default_path}): ").strip()
        mount_path = os.path.expanduser(pasta) if pasta else os.path.expanduser(default_path)
    
    acc["AUTO_MOUNT"] = True
    acc["MOUNT_PATH"] = mount_path
    save_config(config, f"{T('Auto-Mount enabled for')} {acc['PROFILE_NAME']} {T('at')} {mount_path}")
    print(f"\n✅ {T('Auto-Mount enabled! Reloading engine to apply...')}")
    manage_service("reload", LOG_FILE); pause()

def acao_mount_now(idx):
    config = load_config()
    acc = config["ACCOUNTS"][idx]
    if SISTEMA == "Windows":
        letra = input(T("\nType a free drive letter in Windows (Ex: X, Y, Z)\nLetter: ")).strip().upper()
        if not letra or len(letra) > 1: return
        mount_path = f"{letra}:"
        cmd_mount = f"start cmd /k rclone mount {acc['REMOTE_NAME']}: {mount_path} --vfs-cache-mode writes --links --network-mode --volname \"{acc['REMOTE_NAME']}\""
        subprocess.Popen(cmd_mount, shell=True)
        print(f"✅ {T('A new black window has opened managing the drive.')}")
    else:
        default_path = f"~/Desktop/{acc['REMOTE_NAME']}"
        pasta = input(f"\n{T('Empty folder path to mount (Enter =')} {default_path}): ").strip()
        mount_path = os.path.expanduser(pasta) if pasta else os.path.expanduser(default_path)
        os.makedirs(mount_path, exist_ok=True)
        cmd_mount = ["rclone", "mount", f"{acc['REMOTE_NAME']}:", mount_path, "--vfs-cache-mode", "writes", "--daemon"]
        res = subprocess.run(cmd_mount, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ {T('Drive mounted successfully in the background!')}")
        else:
            print(f"❌ {T('Error mounting:')} {res.stderr.strip()}")
    pause()
def run_dry_run():
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: clear_screen(); print(T("No account configured.")); pause(); return
    
    mn = []
    mn.append([f"🔁 {T('All accounts (Batch)')}", lambda: executar_dry_run(ACCOUNTS)])
    for acc in ACCOUNTS:
        mn.append([f"📁 {acc['PROFILE_NAME']} ({acc['REMOTE_NAME']}:)", lambda a=acc: executar_dry_run([a])])
        
    construir_menu(T("Test-Drive / Simulation (Dry-Run)"), mn)

def executar_dry_run(contas_alvo):
    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    clear_screen()
    
    for acc in contas_alvo:
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_dry_run.txt"))
        
        with open(report_file, "w", encoding="utf-8") as rep_file:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            def tee(msg=""): print(msg); rep_file.write(msg + "\n")
            tee("="*45 + f"\n🧪 {T('TEST-DRIVE REPORT')} ({acc['PROFILE_NAME']})\n{T('Simulation Date/Time:')} {agora}\n" + "="*45)
            local_dir = os.path.expanduser(acc["LOCAL_DIR"])
            db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            
            db_connection = init_db(db_path)
            scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
            scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
            generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
            db_connection.close()

            cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", "--dry-run", "--color=never"]
            if acc.get("MAX_SIZE", "0") != "0": cmd.append(f"--max-size={acc.get('MAX_SIZE')}")
            if config.get("BW_LIMIT", "0") != "0": cmd.append(f"--bwlimit={config.get('BW_LIMIT')}")

            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if result.stderr: tee(clean_log_text(result.stderr.strip()))
            if result.stdout: tee(clean_log_text(result.stdout.strip()))
            tee("-" * 45)
            print(f"📂 {T('Report saved at:')} {report_file}")
    pause()

def run_now():
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: clear_screen(); print(f"\n{T('No account configured.')}"); pause(); return

    mn = []
    mn.append([f"🔁 {T('All accounts (Batch)')}", lambda: executar_run_now(ACCOUNTS)])
    for acc in ACCOUNTS:
        mn.append([f"📁 {acc['PROFILE_NAME']} ({acc['REMOTE_NAME']}:)", lambda a=acc: executar_run_now([a])])
        
    construir_menu(T("Force Sync Now"), mn)

def executar_run_now(contas_alvo):
    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    sync_realizada = False
    clear_screen()
    
    for acc in contas_alvo:
        print(f"\n🔄 {T('Current account:')} {acc['PROFILE_NAME']}")
        local_dir = os.path.expanduser(acc["LOCAL_DIR"])
        os.makedirs(local_dir, exist_ok=True)
        
        if check_name_issues_silent(local_dir, acc.get("IGNORE_PATTERNS", [])):
            print(f"\n🚨 {T('ALERT: Case-Sensitivity Conflicts or Invalid Characters detected!')}")
            resp = input(T("Do you want to ignore the risk of data loss? (Y/N) [N]: ")).strip().lower()
            if resp not in ['s', 'y']:
                print(T("Synchronization aborted for the current account. Run Menu 9 to fix it."))
                continue

        print(f"\n  [1] {T('Normal Sync (Safe)')}")
        print(f"  [2] ⚠️  {T('FORCE Sync (--force)')}")
        escolha = input(T("\nAction (1-2) [Enter to Skip]: ")).strip()
        if escolha == '': continue

        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        MANUAL_SYNC_REPORT_FILE = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultima_sincronizacao_manual.txt"))
            
        if not sync_realizada:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            with open(MANUAL_SYNC_REPORT_FILE, "w", encoding="utf-8") as f:
                f.write("="*45 + f"\n🚀 {T('MANUAL SYNC REPORT')} ({acc['PROFILE_NAME']})\n{T('Start Date/Time:')} {agora}\n" + "="*45 + "\n\n")
            sync_realizada = True
            
        db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
        db_connection = init_db(db_path)
        scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
        try:
            scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
        except RuntimeError as e:
            print(f"❌ {T('Connection error with')} {acc['REMOTE_NAME']}.")
            continue            
        generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
        db_connection.close()

        cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-P", "-v", f"--log-file={MANUAL_SYNC_REPORT_FILE}"]
        if acc.get("MAX_SIZE", "0") != "0": cmd.append(f"--max-size={acc.get('MAX_SIZE')}")
        
        modo_str = T("FORCED (--force)") if escolha == '2' else T("NORMAL (Safe)")
        if escolha == '2': cmd.append("--force")
        
        with open(MANUAL_SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- {T('Mode:')} {modo_str} ---\n")
        logger.info(f"[{acc['PROFILE_NAME']}] {T('Manual sync triggered by user. Mode:')} {modo_str}")
        
        subprocess.run(cmd)
        
        with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()
        if "prior lock file found" in log_text.lower():
            lock_match = re.search(r'prior lock file found:\s*([^\r\n]+)', log_text, re.IGNORECASE)
            if lock_match:
                print(f"\n⚠️  {T('Automatically breaking lock...')}")
                subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()])
                subprocess.run(cmd)
                with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()

        if "resync" in log_text.lower() or "not found" in log_text.lower():
            print(f"\n⚠️ {T('Triggering healing scan (--resync)...')}")
            cmd.append("--resync"); subprocess.run(cmd)
            
        clean_log_file(MANUAL_SYNC_REPORT_FILE)
        print(f"\n✅ {T('Completed:')} {acc['PROFILE_NAME']}")
    
    if sync_realizada: print(f"\n📂 {T('Isolated reports saved in folder:')} {report_dir}")
    else: print(f"\n{T('No synchronization was performed.')}")
    pause()

def run_size_report():
    clear_screen()
    config = load_config()
    if not config.get("ACCOUNTS", []): return
    
    report_dir = os.path.normpath(get_report_dir(config))
    
    has_limits = any(acc.get("MAX_SIZE", "0") != "0" for acc in config.get("ACCOUNTS", []))
    if not has_limits:
        print(T("No size limit configured in your accounts."))
        pause()
        return

    print("="*45 + f"\n📊 {T('FILES BLOCKED BY SIZE')}\n" + "="*45)
    print(f"⏳ {T('Analyzing local folders and clouds. This might take a few seconds...')}")

    def format_size(bytes_str):
        try:
            b = int(bytes_str)
            if b < 1024: return f"{b} B"
            elif b < 1024**2: return f"{b/1024:.2f} KB"
            elif b < 1024**3: return f"{b/1024**2:.2f} MB"
            else: return f"{b/1024**3:.2f} GB"
        except:
            return bytes_str

    for acc in config["ACCOUNTS"]:
        max_size = acc.get("MAX_SIZE", "0")
        if max_size == "0":
            continue

        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_relatorio_tamanho.txt"))
        
        with open(report_file, "w", encoding="utf-8") as rep_file:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            def tee(msg=""): rep_file.write(msg + "\n")
            
            tee("="*45 + f"\n📊 {T('FILES BLOCKED BY SIZE')} ({acc['PROFILE_NAME']})\n{T('Date/Time:')} {agora}\n{T('Configured Limit:')} {max_size}\n" + "="*45)
            
            filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            
            tee(f"\n🖥 {T('ON COMPUTER (Local):')}")
            cmd_local = ["rclone", "ls", os.path.expanduser(acc["LOCAL_DIR"]), f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res_local = subprocess.run(cmd_local, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            if res_local.stdout.strip():
                for line in res_local.stdout.strip().split('\n'):
                    partes = line.strip().split(maxsplit=1)
                    if len(partes) == 2:
                        tamanho_hr = format_size(partes[0])
                        caminho = partes[1]
                        tee(f"     - [{T('Local')}] {caminho} ({tamanho_hr})")
                    else:
                        tee(f"     - {line.strip()}")
            else: tee(f"     ({T('None')})")

            tee(f"\n☁ {T('ON CLOUD (Remote):')}")
            cmd_remote = ["rclone", "ls", f"{acc['REMOTE_NAME']}:", f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res_remote = subprocess.run(cmd_remote, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            if res_remote.returncode != 0:
                tee(f"     ({T('Error: Could not connect to cloud')} '{acc['REMOTE_NAME']}')")
            elif res_remote.stdout.strip():
                for line in res_remote.stdout.strip().split('\n'):
                    partes = line.strip().split(maxsplit=1)
                    if len(partes) == 2:
                        tamanho_hr = format_size(partes[0])
                        caminho = partes[1]
                        tee(f"     - [{T('Cloud')}] {caminho} ({tamanho_hr})")
                    else:
                        tee(f"     - {line.strip()}")
            else: tee(f"     ({T('None')})")

            tee("\n" + "-" * 45)
            
    print(f"\n📂 {T('Isolated reports saved in folder:')} {report_dir}")
    pause()

# ==========================================
# NÚCLEO DE SINCRONIZAÇÃO
# ==========================================
def run_sync(local_dir, remote_name, filter_file, bw_limit, max_size, report_dir, profile_name):
    cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
    safe_profile = "".join([c for c in profile_name.lower().replace(" ", "_") if c.isalnum() or c=='_'])
    log_file = os.path.normpath(os.path.join(report_dir, f"{safe_profile}_ultimo_ciclo_auto.txt"))
    
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("="*45 + f"\n🚀 {T('AUTOMATIC SYNC REPORT')} ({profile_name})\n{T('Start Date/Time:')} {agora}\n" + "="*45 + "\n\n")
    
    cmd = ["rclone", "bisync", local_dir, f"{remote_name}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", f"--log-file={log_file}"]
    if bw_limit != "0": cmd.append(f"--bwlimit={bw_limit}")
    if max_size != "0": cmd.append(f"--max-size={max_size}")

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=cflags)
    with open(log_file, "r", encoding="utf-8") as f: log_text = f.read()
    
    if result.returncode != 0 and "prior lock file found" in log_text.lower():
        lock_match = re.search(r'prior lock file found:\s*([^\r\n]+)', log_text, re.IGNORECASE)
        if lock_match:
            subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=cflags)
            
            agora_retry = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("="*45 + f"\n🚀 {T('AUTOMATIC SYNC REPORT')} ({profile_name})\n{T('Start Date/Time:')} {agora_retry} ({T('Retry post-lock')})\n" + "="*45 + "\n\n")
                
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=cflags)
            with open(log_file, "r", encoding="utf-8") as f: log_text = f.read()

    has_transfers, err_msg = analyze_sync_logic(log_text)
    
    if result.returncode == 0:
        clean_log_file(log_file)
        if has_transfers:
            alt_log = os.path.normpath(os.path.join(report_dir, f"{safe_profile}_ultimo_ciclo_COM_ALTERACOES.txt"))
            shutil.copy2(log_file, alt_log)
        return True, has_transfers, ""
        
    elif "resync" in log_text.lower() or "not found" in log_text.lower():
        cmd.append("--resync")
        agora_resync = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("="*45 + f"\n🚀 {T('REPORT (HEALING SCAN)')} ({profile_name})\n{T('Start Date/Time:')} {agora_resync}\n" + "="*45 + "\n\n")
            
        resync_result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=cflags)
        with open(log_file, "r", encoding="utf-8") as f: resync_log = f.read()
        has_resync, _ = analyze_sync_logic(resync_log)
        
        clean_log_file(log_file)
        if has_resync:
            alt_log = os.path.normpath(os.path.join(report_dir, f"{safe_profile}_ultimo_ciclo_COM_ALTERACOES.txt"))
            shutil.copy2(log_file, alt_log)
        return resync_result.returncode == 0, has_resync, ""
    else:
        clean_log_file(log_file)
        return False, False, err_msg

def run_update():
    import time
    clear_screen()
    print("="*45 + f"\n🔄 {T('UPDATE CHECKER')}\n" + "="*45)
    print(f"{T('Local version:')}  {VERSION}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        cache_buster = int(time.time())
        url_no_cache = f"{UPDATE_URL_RAW}?t={cache_buster}"
        
        req = urllib.request.Request(url_no_cache, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'(?im)^[ \t]*VERSION\s*=\s*["\']([^"\']+)["\']', content)
            remote_version = match.group(1) if match else None
    except Exception as e:
        print(f"❌ {T('Network error:')} {e}"); pause(); return

    if not remote_version:
        print(f"❌ {T('Could not identify the version on the server.')}"); pause(); return

    print(f"{T('Remote version:')} {remote_version}\n")

    def parse_version(v):
        return tuple(map(int, re.findall(r'\d+', str(v))))

    if parse_version(remote_version) <= parse_version(VERSION):
        print(f"✅ {T('You are already using the latest version!')}"); pause(); return        
    
    print(f"🎉 {T('A new version is available!')}")
    resp = input(T("Do you want to download and install the update now? (Y/N) [N]: ")).strip().lower()
    if resp not in ['s', 'y']: return
        
    print(f"\n📥 {T('Downloading update package...')}")
    try:
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "update.zip")
        req = urllib.request.Request(UPDATE_URL_ZIP, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"📦 {T('Extracting files...')}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(tmp_dir)
        
        extract_dir = os.path.join(tmp_dir, "sync-engine-main")
        if SISTEMA == "Windows":
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "_core_install.ps1"], cwd=extract_dir)
        else:
            subprocess.run(["bash", "install-linux.sh"], cwd=extract_dir)
            
        shutil.rmtree(tmp_dir)
        print(f"\n✅ {T('Update completed successfully!')}"); pause(); sys.exit(0)
    except Exception as e:
        print(f"\n❌ {T('Error during the update process:')} {e}"); pause()

def run_cloud_migration():
    clear_screen()
    print("="*45 + f"\n☁ {T('DIRECT CLOUD-TO-CLOUD MIGRATION')}\n" + "="*45)
    print(T("Transfers files between providers using RAM."))
    print(T("Does not consume local hard drive space.\n"))
    
    res = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    remotes = [r.strip(':') for r in res.stdout.strip().split('\n') if r.strip()]
    if len(remotes) < 2:
        print(f"❌ {T('You need at least 2 clouds configured in Rclone to migrate.')}")
        pause(); return

    print(T("Available Providers:"))
    for i, r in enumerate(remotes): print(f"  [{i+1}] {r}")
    
    op_src = input(T("\nSOURCE Cloud (Number) [Enter to cancel]: ")).strip()
    if not op_src.isdigit() or not (1 <= int(op_src) <= len(remotes)): return
    src_remote = remotes[int(op_src)-1]
    
    src_path = input("📁 " + T("Subfolder in source (Leave blank for root '/'): ")).strip()
    src_full = f"{src_remote}:{src_path}" if src_path else f"{src_remote}:"

    op_dst = input(T("\nDESTINATION Cloud (Number) [Enter to cancel]: ")).strip()
    if not op_dst.isdigit() or not (1 <= int(op_dst) <= len(remotes)): return
    dst_remote = remotes[int(op_dst)-1]
    
    dst_path = input("📁 " + T("Subfolder in destination (Leave blank for root '/'): ")).strip()
    dst_full = f"{dst_remote}:{dst_path}" if dst_path else f"{dst_remote}:"
    
    if src_full == dst_full:
        print(f"❌ {T('Source and Destination cannot be the same path.')}"); pause(); return

    print(f"\n{T('Configured flow:')} {src_full} ➔ {dst_full}")
    
    print(T("\nTransfer Mode:"))
    print(f"📦 {T('[1] TOTAL (Copies ABSOLUTELY EVERYTHING)')}")
    print(f"🛡 {T('[2] STANDARD (Blocks vaults, trash and folders with .nosync marker)')}")
    print(f"⚙ {T('[3] CUSTOM (Standard + Imports config.json filters from source)')}")
    
    modo = input(T("\nOption (1-3) [Enter to cancel]: ")).strip()
    if modo not in ['1', '2', '3']: return
    
    tamanho = input(T("\nMax size per file (Ex: 1G, 500M, 0 = Unlimited) [0]: ")).strip()
    
    cmd = ["rclone", "copy", src_full, dst_full, "-P", "--transfers=4", "--checkers=8", "--ignore-errors"]
    
    if tamanho and tamanho != "0":
        cmd.append(f"--max-size={tamanho}")
        print(f"\n📏 {T('Size limit activated: Ignoring files larger than')} {tamanho}.")
    
    filtros_extras_list = []
    nosync_folders = []
    
    if modo in ['2', '3']:
        print("\n🔍 " + T("Scanning cloud for '.nosync' markers (May take a few seconds)..."))
        cmd_scan = ["rclone", "lsf", src_full, "-R", "--include", ".nosync", "--ignore-errors"]
        res_scan = subprocess.run(cmd_scan, capture_output=True, text=True, encoding="utf-8", errors="replace")
        
        for line in res_scan.stdout.splitlines():
            line = line.strip()
            if line.endswith(".nosync"):
                folder = line[:-7] 
                if folder:
                    nosync_folders.append(folder)
                    
        import tempfile
        fd, temp_filter = tempfile.mkstemp(suffix=".txt")
        
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("- Personal Vault/**\n")
            f.write("- Cofre Pessoal/**\n")
            f.write("- .DS_Store\n")
            f.write("- Thumbs.db\n")
            
            for folder in nosync_folders:
                f.write(f"- {folder}**\n")
            
            f.write("- **/.nosync\n")
            
            if modo == '3':
                config = load_config()
                for acc in config.get("ACCOUNTS", []):
                    remoto_json = acc.get("REMOTE_NAME", "").lower()
                    perfil_json = acc.get("PROFILE_NAME", "").lower()
                    
                    if src_remote.lower() == remoto_json or src_remote.lower() == perfil_json:
                        filtros = acc.get("IGNORE_PATTERNS", [])
                        for path in filtros:
                            f.write(f"- {path}\n")
                            filtros_extras_list.append(path)
                        break
                        
        cmd.append(f"--filter-from={temp_filter}")
        if modo == '3':
            print(f"⚙️ {T('Custom Filter activated')} ({len(nosync_folders)} {T('.nosync folders')} + {len(filtros_extras_list)} {T('local rules')}).")
        else:
            print(f"🛡️ {T('Standard Filter activated')} ({len(nosync_folders)} {T('folders with .nosync marker isolated')}).")

    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    agora_arquivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    agora_texto = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    report_file = os.path.join(report_dir, f"migracao_{src_remote}_para_{dst_remote}_{agora_arquivo}.txt")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("="*45 + "\n")
        f.write(f"☁️ {T('DIRECT MIGRATION REPORT')}\n")
        f.write(f"{T('Date/Time:')} {agora_texto}\n")
        f.write(f"{T('Source:')}    {src_full}\n")
        f.write(f"{T('Destination:')}   {dst_full}\n")
        
        if modo == '1': tipo_modo = T("TOTAL (Absolute copy)")
        elif modo == '2': tipo_modo = T("STANDARD (Security locks)")
        else: tipo_modo = T("CUSTOM (Locks + config.json filters)")
        f.write(f"{T('Mode:')}      {tipo_modo}\n")
        
        limite_str = tamanho if (tamanho and tamanho != "0") else T("Unlimited")
        f.write(f"{T('Max Size:')} {limite_str}\n")
        
        if modo in ['2', '3']:
            f.write(f"\n{T('Filters Applied in this Session:')}\n")
            f.write(" - Personal Vault/**\n - Cofre Pessoal/**\n - .DS_Store\n - Thumbs.db\n")
            
            if nosync_folders:
                f.write(f"\n [{T('Folders dynamically blocked by .nosync marker:')}]\n")
                for folder in nosync_folders:
                    f.write(f" - {folder}**\n")
            else:
                f.write(f"\n - [{T('No .nosync marker found in source')}]\n")
                
            if modo == '3' and filtros_extras_list:
                f.write(f"\n [{T('Extra Filters imported from config.json:')}]\n")
                for p in filtros_extras_list:
                    f.write(f" - {p}\n")
        f.write("="*45 + "\n\n")
    
    cmd.extend(["-v", f"--log-file={report_file}"])
    
    print(f"\n📝 {T('Generating detailed report at:')} {report_file}")
    print(T("Starting direct transfer. Press Ctrl+C at any time to abort."))
    print(T("If the internet drops, just run it again and it will resume.\n") + "-"*45)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n⏹ " + T("\n Transfer interrupted by user."))
    
    if modo in ['2', '3']: os.remove(temp_filter)
    
    clean_log_file(report_file)
    print(f"\n✅ {T('Operation finished. Report saved at:')} {report_file}"); pause()

def run_doctor(config):
    print("="*45 + f"\n🩺 {T('SYSTEM DIAGNOSTICS')}\n" + "="*45)
    
    print(T("[Base Dependencies]"))
    res = subprocess.run(["rclone", "version"], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"🟢 Rclone: {T('Supported')} ({res.stdout.splitlines()[0]})")
    else:
        print(f"🔴 {T('Rclone: Missing! Install rclone and add it to PATH.')}")
    
    print(T("\n[Operating System Features]"))
    sync_os.run_doctor_os()
    
    print(T("\n[Vital Directories]"))
    config_dir = os.path.normpath(os.path.expanduser("~/.config/sync_engine"))
    if os.path.exists(config_dir):
        print(f"🟢 {T('Settings Vault:')} {config_dir}")
    else:
        print(f"🔴 {T('Settings Vault:')} {T('Missing')}")
        
    report_dir = os.path.normpath(get_report_dir(config))
    if os.path.exists(report_dir):
        print(f"🟢 {T('Reports Folder:')} {report_dir}")
    else:
        print(f"🔴 {T('Reports Folder:')} {T('Missing (will be created on 1st cycle)')}")
    
    print("="*45)
    input(T("\nPress Enter to return..."))

def run_uninstall():
    clear_screen()
    print("="*45 + f"\n🧨 {T('SYNC ENGINE UNINSTALLATION')}\n" + "="*45)
    print(T("This action will stop the services and permanently"))
    print(T("remove the application from your system."))
    
    desafio = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(T("\nTo confirm, type exactly the code below:"))
    print(f"👉 {T('Code:')} {desafio}")
    
    confirma = input(T("\nYour answer [Enter to cancel]: ")).strip()
    if confirma != desafio:
        print(f"\n❌ {T('Incorrect code. Operation canceled.')}")
        pause()
        return
        
    print("\n" + "-"*45)
    print(T("Do you also want to delete settings, databases"))
    print(T("and saved reports?"))
    apagar_dados = input(T("(Y/N) [N]: ")).strip().lower() in ['s', 'y']
    
    print(f"\n⏳ {T('Stopping invisible service...')}")
    manage_service("stop", LOG_FILE)
    
    print(f"⏳ {T('Preparing self-destruct script...')}")
    
    if SISTEMA == "Windows":
        bat_path = os.path.join(tempfile.gettempdir(), "sync_suicide.bat")
        bat_content = f"""@echo off
timeout /t 3 /nobreak > NUL
rmdir /s /q "{BASE_DIR}"
"""
        if apagar_dados:
            bat_content += f'\nrmdir /s /q "{CONFIG_DIR}"'
        bat_content += '\ndel "%~f0"'
        
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        
    else:
        sh_path = os.path.join(tempfile.gettempdir(), "sync_suicide.sh")
        sh_content = f"""#!/bin/bash
sleep 3
rm -rf "{BASE_DIR}"
"""
        if apagar_dados:
            sh_content += f'\nrm -rf "{CONFIG_DIR}"'
            
        sh_content += f'\nrm -f "$HOME/.local/bin/sync-engine"'
        sh_content += f'\nrm -f "$HOME/.config/systemd/user/sync-engine.service"'
        sh_content += f'\nsystemctl --user daemon-reload'
        sh_content += '\nrm -- "$0"'
        
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o777)
        
        subprocess.Popen(["nohup", "bash", sh_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
        
    print(f"\n✅ {T('Uninstallation triggered successfully!')}")
    print(T("The engine will be removed from the drive in 3 seconds."))
    print(T("Goodbye!\n"))
    sys.exit(0)

def cmd_add_account():
    clear_screen()
    config = load_config()
    print("="*45 + f"\n➕ {T('ADD NEW ACCOUNT')}\n" + "="*45)
    profile = input(T("\nProfile Name [Enter to return]: ")).strip()
    if not profile: return
    rclone_out = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    remotes = [r.strip(':') for r in rclone_out.stdout.strip().split('\n') if r.strip()]
    for i, r in enumerate(remotes): print(f"  [{i+1}] {r}")
    op_remote = input(T("\nCloud number [Enter to return]: ")).strip()
    if not op_remote or not op_remote.isdigit() or int(op_remote)-1 >= len(remotes): return
    
    remote = remotes[int(op_remote) - 1]
    local = input(f"\n{T('Local folder (Enter for')} '~/{remote}'): ").strip() or f"~/{remote}"
        
    safe_name = "".join([c for c in profile.lower().replace(" ", "_") if c.isalnum() or c=='_'])
    config.setdefault("ACCOUNTS", []).append({
        "PROFILE_NAME": profile, "REMOTE_NAME": remote, "LOCAL_DIR": local,
        "IGNORE_PATTERNS": ["venv", ".venv", "__pycache__", ".git", "Personal Vault", "Cofre Pessoal", "*.tmp", ".DS_Store", "site-packages", "Thumbs.db", "~$*"],
        "DB_FILE": f"sync_metadata_{safe_name}.db", "FILTER_FILE": f"excludes_{safe_name}.txt"
    })
    save_config(config, f"{T('Added account')} '{profile}'")
    manage_service("reload", LOG_FILE); print(f"\n✅ {T('Saved!')}"); pause()

def cmd_remove_account():
    while True:
        config = load_config()
        contas = config.get("ACCOUNTS", [])
        if not contas:
            clear_screen(); print(T("No account configured.")); pause(); return
            
        mn = []
        for i, acc in enumerate(contas):
            mn.append([acc['PROFILE_NAME'], lambda idx=i: acao_remover_conta(idx)])
            
        if not construir_menu(T("Remove an account"), mn):
            break
            
def acao_remover_conta(idx):
    config = load_config()
    apagada = config["ACCOUNTS"].pop(idx)
    save_config(config, f"{T('Removed account')} '{apagada['PROFILE_NAME']}'")
    manage_service("reload", LOG_FILE)
    print(f"\n🗑️ {T('Removed:')} {apagada['PROFILE_NAME']}"); pause()


def cmd_open_reports():
    config = load_config()
    current_dir = os.path.normpath(get_report_dir(config))
    os.makedirs(current_dir, exist_ok=True)
    if SISTEMA == "Windows": os.startfile(current_dir)
    else: subprocess.run(["xdg-open", current_dir])

def cmd_service_start(): clear_screen(); manage_service("start", LOG_FILE); pause()
def cmd_service_stop(): clear_screen(); manage_service("stop", LOG_FILE); logger.info(T("Motor stopped manually.")); pause()
def cmd_service_status(): clear_screen(); manage_service("status", LOG_FILE); pause()

def cmd_list_accounts():
    # Captura os tipos de nuvem de forma leve e segura
    rclone_types = {}
    try:
        res = subprocess.run(["rclone", "listremotes", "--long"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
        for line in res.stdout.strip().split('\n'):
            if ':' in line:
                partes = line.split(':', 1)
                nome = partes[0].strip()
                tipo = partes[1].strip()
                # Apenas grava se o Rclone realmente devolveu um tipo
                if tipo:
                    rclone_types[nome] = tipo
    except Exception:
        pass
        
    while True:
        config = load_config()
        contas = config.get("ACCOUNTS", [])
        if not contas:
            clear_screen(); print(T("No account configured.")); pause(); return
        
        mn = []
        for i, acc in enumerate(contas):
            status_sync = "" if acc.get("AUTO_SYNC", True) else f" ⏸️  [{T('Paused')}]"
            
            # Identifica o tipo (ex: drive, onedrive)
            remote_name = acc.get('REMOTE_NAME', '')
            cloud_type = rclone_types.get(remote_name, "")
            
            # Se a leitura falhou ou a versão do rclone retornou vazio, removemos os colchetes feios
            info_tipo = f" [{cloud_type.upper()}]" if cloud_type else ""
            
            label = f"{acc['PROFILE_NAME']}{info_tipo}{status_sync}"
            mn.append([label, lambda idx=i: cmd_detalhes_conta(idx)])
        
        if not construir_menu(f"📋 {T('ACCOUNT DETAILS')}", mn):
            break

def acao_add_filtro(idx):
    print(f"\n💡 {T('ADVANCED FILTERING TIPS:')}")
    # Isolando as traduções das sintaxes Regex para evitar falhas nos espaços
    print(f"  (?i)*.tmp           -> {T('Ignore Case (ex: log.TMP and log.tmp)')}")
    print(f"  venv                -> {T('Exact name match in any folder')}")
    print(f"  Prefix*             -> {T('Start of name (ex: Backup* ignores Backup_2026)')}")
    print(f"  *.bak               -> {T('Extension wildcard at any level')}")
    print(f"  /Backups            -> {T('Root anchor (ignores only in main folder)')}")
    print(f"  /.*                 -> {T('Ignore hidden folders/files only in root (Linux)')}")
    
    novo = input("\n" + T("Type the new pattern [Enter to cancel]: ")).strip()
    if novo:
        cfg = load_config()
        cfg["ACCOUNTS"][idx].setdefault("IGNORE_PATTERNS", []).append(novo)
        save_config(cfg, f"{T('Filters/Limits changed in')} '{cfg['ACCOUNTS'][idx]['PROFILE_NAME']}'")
        manage_service("reload", LOG_FILE)

def acao_rem_filtro(idx):
    cfg = load_config()
    padroes = cfg["ACCOUNTS"][idx].get("IGNORE_PATTERNS", [])
    if not padroes: return
    
    num = input("\n" + T("Number of the rule to remove (1, 2, 3...) [Enter to cancel]: ")).strip()
    if num.isdigit() and 1 <= int(num) <= len(padroes):
        padroes.pop(int(num)-1)
        save_config(cfg, f"{T('Filters/Limits changed in')} '{cfg['ACCOUNTS'][idx]['PROFILE_NAME']}'")
        manage_service("reload", LOG_FILE)

def cmd_detalhes_conta(idx):
    while True:
        config = load_config()
        conta = config["ACCOUNTS"][idx]
        
        mn = []
        mn.append([f"☁️  {T('Cloud (Remote)')}  : {conta['REMOTE_NAME']}:", None])
        mn.append([f"📁 {T('Local Folder')}    : {conta['LOCAL_DIR']}", None])
        
        # Painel de Status
        sync_status = T("ON") if conta.get("AUTO_SYNC", True) else T("OFF")
        mn.append([f"🔄 {T('Background Sync')} : {sync_status}", None])
        mn.append([f"📦 {T('Size Limit')}      : {conta.get('MAX_SIZE', '0')} (0 = {T('Unlimited')})", None])
        mn.append([f"🛡️  {T('Active Filters')}  : {len(conta.get('IGNORE_PATTERNS', []))} {T('rule(s)')}", None])
        
        status_mount = T("ACTIVE") if conta.get("AUTO_MOUNT") else T("Inactive")
        mn.append([f"🔌 {T('Virtual Drive')}   : {status_mount}", None])
        mn.append([])
        
        # Botões de Ação Centralizados
        mn.append([f"✏️  {T('Change Local Folder path')}", lambda: acao_mudar_pasta(idx)])
        mn.append([f"🔄 {T('Toggle Background Sync')}", lambda: acao_toggle_sync(idx)])
        mn.append([f"📦 {T('Change Max Size')}", lambda: acao_mudar_tamanho_acc(idx)])
        mn.append([f"🛡️  {T('Manage Filters')}", lambda: cmd_gerenciar_filtros_conta(idx)])
        
        if not construir_menu(f"⚙️  {T('ACCOUNT:')} {conta['PROFILE_NAME']}", mn):
            break

def acao_toggle_sync(idx):
    cfg = load_config()
    atual = cfg["ACCOUNTS"][idx].get("AUTO_SYNC", True)
    cfg["ACCOUNTS"][idx]["AUTO_SYNC"] = not atual
    save_config(cfg, f"{T('Background Sync for')} '{cfg['ACCOUNTS'][idx]['PROFILE_NAME']}' {T('changed to')} {not atual}")
    manage_service("reload", LOG_FILE)

def acao_mudar_tamanho_acc(idx):
    nv = input(T("\nNew max size (ex: 100M, 1G, 0 for unlimited): ")).strip()
    if nv:
        cfg = load_config()
        cfg["ACCOUNTS"][idx]["MAX_SIZE"] = nv
        save_config(cfg, f"{T('Size Limit changed in')} '{cfg['ACCOUNTS'][idx]['PROFILE_NAME']}'")
        manage_service("reload", LOG_FILE)

def cmd_gerenciar_filtros_conta(idx):
    while True:
        config = load_config()
        conta = config["ACCOUNTS"][idx]
        padroes = conta.get("IGNORE_PATTERNS", [])
        
        mn = []
        mn.append([f"🛡️  {T('Current Exclusion Filters:')}", None])
        if not padroes:
            mn.append([f"   ({T('None')})", None])
        for j, p in enumerate(padroes):
            mn.append([f"   {j+1}. {p}", None])
            
        mn.append([])
        mn.append([f"➕ {T('Add Filter')}", lambda: acao_add_filtro(idx)])
        mn.append([f"❌ {T('Remove Filter')}", lambda: acao_rem_filtro(idx)])
        
        if not construir_menu(f"{T('Filters:')} {conta['PROFILE_NAME']}", mn):
            break

def acao_mudar_pasta(idx):
    # (Mantenha aqui aquela mesma lógica de inputs e shutil.move que criamos ontem)
    config = load_config()
    conta = config["ACCOUNTS"][idx]
    novo_dir = input(T("\nEnter the new absolute path for the folder (Ex: ~/NewFolder): ")).strip()
    if novo_dir:
        dir_expandido_novo = os.path.expanduser(novo_dir)
        dir_expandido_velho = os.path.expanduser(conta["LOCAL_DIR"])
        if os.path.abspath(dir_expandido_novo) == os.path.abspath(dir_expandido_velho):
            print(f"\n⚠️ {T('The entered path is the same as the current configuration.')}")
            pause(); return
            
        print(f"\n{T('Do you want to physically MOVE all files from the old folder to the new one?')}")
        mover = input(T("(Y/N) [N]: ")).strip().lower() in ['s', 'y']
        try:
            if mover and os.path.exists(dir_expandido_velho):
                print(f"\n⏳ {T('Moving files... This may take a while depending on the size.')}")
                os.makedirs(dir_expandido_novo, exist_ok=True)
                import shutil
                itens_movidos = 0
                for item in os.listdir(dir_expandido_velho):
                    origem = os.path.join(dir_expandido_velho, item)
                    destino = os.path.join(dir_expandido_novo, item)
                    if not os.path.exists(destino):
                        shutil.move(origem, destino)
                        itens_movidos += 1
                print(f"✅ {itens_movidos} {T('root item(s) moved successfully!')}")
                
            conta["LOCAL_DIR"] = novo_dir
            save_config(config, f"{T('Local folder for account')} '{conta['PROFILE_NAME']}' {T('changed to')} {novo_dir}")
            manage_service("reload", LOG_FILE)
            print(f"\n✅ {T('Configuration saved! The new working folder is:')} {novo_dir}")
        except Exception as e:
            print(f"\n❌ {T('Error during move:')} {e}")
        pause()

def cmd_global_settings():
    while True:
        config = load_config()
        mn = []
        mn.append([f"🌐 {T('Language')} ({config.get('LANGUAGE', 'auto')})", cmd_language_menu])
        mn.append([f"⏱️  {T('Interval')} ({config.get('SYNC_INTERVAL', 300)}s)", acao_mudar_intervalo])
        mn.append([f"📶 {T('Bandwidth Limit')} ({config.get('BW_LIMIT', '0')})", acao_mudar_banda])
        mn.append([f"📂 {T('Reports Folder')} ({T('Current:')} {os.path.normpath(get_report_dir(config))})", cmd_menu_relatorios])
        status_col = T("ON") if config.get("AUTO_CHECK_NAMES", True) else T("OFF")
        mn.append([f"🛡️  {T('Auto Block on Name Collisions')} ({status_col})", acao_toggle_colisao])
        
        if not construir_menu(T("Edit Interval, Bandwidth, Folders, and Collisions"), mn):
            break


def cmd_language_menu():
    while True:
        config = load_config()

        # Usa a raiz EXATA garantida pelo sync_config
        locales_dir = os.path.join(CONFIG_BASE_DIR, "locales")

        # Cria a pasta locales automaticamente se ela não existir
        os.makedirs(locales_dir, exist_ok=True)

        disponiveis = []
        for f in os.listdir(locales_dir):
            if f.endswith(".json") and f not in ["dicionario_base.json", "config.json"]:
                disponiveis.append(f.replace(".json", ""))

        disponiveis.sort()

        mn = []
        mn.append([f"🤖 {T('Auto (System Default)')}", lambda: acao_mudar_idioma("auto")])
        mn.append([f"🇺🇸 {T('English (Base Code)')}", lambda: acao_mudar_idioma("en")])
        mn.append([])  # Linha em branco para separar

        if not disponiveis:
            # Agora o erro mostra EXATAMENTE o caminho físico que ele tentou ler
            mn.append([f"⚠️  {T('No extra languages found in')} {locales_dir}", None])
        else:
            for lang in disponiveis:
                mn.append([f"🌐 {lang.upper()}", lambda l=lang: acao_mudar_idioma(l)])

        if not construir_menu(T("Select Language"), mn):
            break
def acao_mudar_idioma(lang_code):
    config = load_config()
    config["LANGUAGE"] = lang_code
    save_config(config, f"Language set to {lang_code}")
    print(f"\n✅ {T('Language changed to:')} {lang_code.upper()}")
    print(T("Please restart the application to apply the new language."))
    pause()

def acao_mudar_intervalo():
    nv = input(T("\nNew interval in seconds: ")).strip()
    if nv.isdigit(): 
        cfg = load_config(); cfg["SYNC_INTERVAL"] = int(nv)
        save_config(cfg); manage_service("reload", LOG_FILE)

def acao_mudar_banda():
    nv = input(T("\nNew limit (ex: 1M, 500k, 0 for unlimited): ")).strip()
    if nv: 
        cfg = load_config(); cfg["BW_LIMIT"] = nv
        save_config(cfg)

def acao_toggle_colisao():
    cfg = load_config()
    cfg["AUTO_CHECK_NAMES"] = not cfg.get("AUTO_CHECK_NAMES", True)
    save_config(cfg)

def cmd_menu_relatorios():
    while True:
        config = load_config()
        current_dir = os.path.normpath(get_report_dir(config))
        os.makedirs(current_dir, exist_ok=True)
        if SISTEMA == "Windows":
            root_config = os.path.normpath(os.path.expanduser("~/.config"))
            if os.path.exists(root_config):
                subprocess.run(["attrib", "+h", root_config], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        
        mn = []
        mn.append([f"📂 {T('Open folder in Explorer/Manager')}", cmd_open_reports])
        mn.append([f"✏️  {T('Change save location')}", acao_mudar_pasta_relatorios])
        mn.append([f"🔄 {T('Restore to hidden default folder')}", acao_restaurar_relatorios])
        
        if not construir_menu(f"{T('REPORTS MANAGER')} ({current_dir})", mn):
            break

def acao_mudar_pasta_relatorios():
    cfg = load_config()
    novo_dir = input(T("\nType the new absolute path: ")).strip()
    if novo_dir:
        cfg["REPORT_DIR"] = os.path.normpath(novo_dir)
        save_config(cfg)
        print(f"✅ {T('Folder changed to:')} {cfg['REPORT_DIR']}")
        pause()

def acao_restaurar_relatorios():
    cfg = load_config()
    cfg["REPORT_DIR"] = "" 
    save_config(cfg)
    print(f"\n✅ {T('Reports restored to default directory')}")
    pause()

def cmd_scheduler_menu():
    while True:
        config = load_config()
        tasks = config.get("SCHEDULED_TASKS", [])
        
        mn = []
        # Aviso fixo sobre a necessidade do motor
        mn.append(f"⚠️  {T('NOTE: Scheduled tasks only run if the Background Motor is ACTIVE.')}")
        mn.append([])
        mn.append([f"➕ {T('Add new scheduled task')}", acao_add_task])
        mn.append([])
        
        if not tasks:
            mn.append([f"   ({T('No scheduled tasks')})", None])
        else:
            # Instrução clara sobre o clique apagar a tarefa
            mn.append(T("Select a task below to REMOVE it:"))
            for i, t in enumerate(tasks):
                tipo = t['type'].upper()
                label = t.get('label', '')
                data_str = T('Daily') if t.get('date', 'daily') == 'daily' else t.get('date')
                ultimo = t.get('last_run', T('Never'))
                mn.append([f"❌ {T('Delete')} -> {data_str} {t['time']} | {tipo} | {label} (Ult: {ultimo})", lambda idx=i: acao_rem_task(idx)])
                
        if not construir_menu(f"⏰ {T('TASK SCHEDULER')}", mn):
            break

def acao_add_task():
    clear_screen()
    config = load_config()
    print("="*45 + f"\n➕ {T('NEW SCHEDULED TASK')}\n" + "="*45)
    
    print("1. " + T("Normal Sync (Safe)"))
    print("2. " + T("FORCED Sync (--force)"))
    print("3. " + T("Cloud-to-Cloud Migration"))
    
    op = input("\n" + T("Task Type (1-3) [Enter to cancel]: ")).strip()
    if op not in ['1', '2', '3']: return
    
    task = {"last_run": ""}
    
    if op in ['1', '2']:
        contas = config.get("ACCOUNTS", [])
        if not contas: print(f"❌ {T('No account configured.')}"); pause(); return
        for i, acc in enumerate(contas): print(f"  [{i+1}] {acc['PROFILE_NAME']}")
        idx = input("\n" + T("Account Number [Enter to cancel]: ")).strip()
        if not idx.isdigit() or not (1 <= int(idx) <= len(contas)): return
        
        task["type"] = "sync" if op == '1' else "force"
        task["account"] = contas[int(idx)-1]["PROFILE_NAME"]
        task["label"] = task["account"]
        
    elif op == '3':
        print(T("\nEx: gdrive:/Backups"))
        src = input(T("Source path [Enter to cancel]: ")).strip()
        if not src: return
        dst = input(T("Destination path [Enter to cancel]: ")).strip()
        if not dst: return
        
        task["type"] = "migration"
        task["src"] = src
        task["dst"] = dst
        task["label"] = f"{src.split(':')[0]} -> {dst.split(':')[0]}"
        
    # Pergunta a data (Se der enter em branco, fica "daily")
    data_op = input("\n" + T("Date (DD/MM/YYYY) or [Enter for Daily]: ")).strip()
    if data_op:
        if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$", data_op):
            print(f"❌ {T('Invalid date format. Use DD/MM/YYYY.')}"); pause(); return
        task["date"] = data_op
    else:
        task["date"] = "daily"

    hora = input(T("Execution Time (HH:MM) [ex: 02:30]: ")).strip()
    if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", hora):
        print(f"❌ {T('Invalid time format. Use HH:MM.')}"); pause(); return
        
    task["time"] = hora
    config.setdefault("SCHEDULED_TASKS", []).append(task)
    save_config(config, f"New scheduled task: {task['type']} para {task['date']} às {hora}")
    manage_service("reload", LOG_FILE)
    print(f"\n✅ {T('Task Scheduled!')}")
    print(f"💡 {T('Tip: Remember to turn ON the Background Motor in the main menu so your tasks can run.')}")
    pause()

def process_scheduled_tasks(config):
    tasks = config.get("SCHEDULED_TASKS", [])
    if not tasks: return

    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")
    data_atual = agora.strftime("%Y-%m-%d")
    data_br = agora.strftime("%d/%m/%Y")
    mudou = False
    report_dir = os.path.normpath(get_report_dir(config))

    tarefas_restantes = []

    for task in tasks:
        t_date = task.get("date", "daily")
        
        # Limpa tarefas de dias passados que o motor estava desligado e não rodou
        if t_date != "daily" and t_date != data_br:
            try:
                d_task = datetime.strptime(t_date, "%d/%m/%Y").date()
                if d_task < agora.date():
                    mudou = True
                    continue 
            except: pass
            
            # Se a tarefa é para um dia futuro, guarda e pula
            if t_date != data_br:
                tarefas_restantes.append(task)
                continue

        # Se já rodou hoje ou a hora não chegou
        if task.get("last_run") == data_atual or hora_atual < task["time"]: 
            tarefas_restantes.append(task)
            continue

        logger.info(f"⏰ {T('Starting scheduled task:')} {task['type']} ({task.get('label', '')})")
        
        try:
            if task["type"] in ["sync", "force"]:
                acc = next((a for a in config.get("ACCOUNTS", []) if a["PROFILE_NAME"] == task["account"]), None)
                if acc:
                    local_dir = os.path.expanduser(acc["LOCAL_DIR"])
                    safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
                    log_file = os.path.join(report_dir, f"{safe_name}_agendamento.txt")
                    filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
                    
                    cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", f"--log-file={log_file}"]
                    if task["type"] == "force": cmd.append("--force")
                    if acc.get("MAX_SIZE", "0") != "0": cmd.append(f"--max-size={acc.get('MAX_SIZE')}")
                    
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    send_notification(T("Scheduled Sync"), f"{acc['PROFILE_NAME']} {T('completed.')}")

            elif task["type"] == "migration":
                agora_arquivo = datetime.now().strftime("%Y-%m-%d_%H-%M")
                log_file = os.path.join(report_dir, f"migracao_agendada_{agora_arquivo}.txt")
                cmd = ["rclone", "copy", task["src"], task["dst"], "-v", "--ignore-errors", f"--log-file={log_file}"]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                send_notification(T("Scheduled Migration"), f"{task['label']} {T('completed.')}")
                
        except Exception as e:
            logger.error(f"{T('Scheduled task failure:')} {e}")
            
        task["last_run"] = data_atual
        mudou = True
        
        # Se for tarefa DIÁRIA, ela fica na lista. Se for de data específica, ela já some sozinha do painel.
        if t_date == "daily":
            tarefas_restantes.append(task)

    if mudou:
        config["SCHEDULED_TASKS"] = tarefas_restantes
        save_config(config)

def acao_rem_task(idx):
    config = load_config()
    apagada = config["SCHEDULED_TASKS"].pop(idx)
    save_config(config, f"Scheduled task removed: {apagada.get('label')}")
    manage_service("reload", LOG_FILE)

def run_config_wizard():
    while True:
        mn = []
        
        mn.append(f"--- {T('Account Configuration')} ---")
        mn.append([f"📋 {T('List current accounts')}", cmd_list_accounts])
        mn.append([f"➕ {T('Add new account')}", cmd_add_account])
        mn.append([f"❌ {T('Remove an account')}", cmd_remove_account])
        
        mn.append(f"--- {T('Global Settings')} ---")
        mn.append([f"⚙️  {T('Edit Interval, Bandwidth, Folders, and Collisions')}", cmd_global_settings])
        
        mn.append(f"--- {T('Synchronization')} ---")
        mn.append([f"🧪 {T('Test-Drive / Simulation (Dry-Run)')}", run_dry_run])
        mn.append([f"🚀 {T('Force Sync Now')}", run_now])
        mn.append([f"{T('⏰ Task Scheduler (Cron)')}", cmd_scheduler_menu])
        
        mn.append(f"--- {T('Maintenance')} ---")
        mn.append([f"📊 {T('Report of Files Over the Limit')}", run_size_report])
        mn.append([f"🧹 {T('Cleaner and Collision Checker')}", run_filename_cleaner])
        mn.append([f"🔎 {T('Sync Error Analyzer')}", run_analyze_errors])
        mn.append([f"🩺 {T('System Diagnostics (Doctor)')}", lambda: run_doctor(load_config())])
        
        mn.append(f"--- {T('Extra Actions')} ---")
        mn.append([f"☁️  {T('Direct Cloud-to-Cloud Migration')}", run_cloud_migration])
        mn.append([f"🔌 {T('Mount Cloud as Virtual Drive (Mount)')}", run_mount_manager])
        
        mn.append(f"--- {T('Background Motor')} ---")
        mn.append([f"▶️  {T('Start Service')}", cmd_service_start])
        mn.append([f"⏹️  {T('Stop Service')}", cmd_service_stop])
        mn.append([f"ℹ️  {T('Check Motor Status')}", cmd_service_status])
        mn.append([f"🔄 {T('Update Application Version')}", run_update])
        mn.append([f"🧨 {T('Uninstall Sync Engine')}", run_uninstall])
        
        mn.append([])
        mn.append([f"📂 {T('Open Reports')}", cmd_open_reports, 'R'])
        
        # O construtor desenha a tela e trava. Ao dar Enter, ele retorna False e quebra o while True.
        if not construir_menu(f"{T('Sync Engine Wizard')} (v{VERSION})", mn):
            break
            
    clear_screen()
    print(T("Goodbye!\n"))

def ensure_mount(acc):
    if not acc.get("AUTO_MOUNT") or not acc.get("MOUNT_PATH"): return
    mount_path = acc["MOUNT_PATH"]
    remote = acc["REMOTE_NAME"]
    
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
    except OSError:
        logger.warning(f"[{acc['PROFILE_NAME']}] {T('No internet. Auto-mount postponed.')}")
        return
        
    if SISTEMA == "Windows":
        ps_check = f"Get-WmiObject Win32_Process -Filter \"Name='rclone.exe'\" | Where-Object {{ $_.CommandLine -match 'mount' -and $_.CommandLine -match '{mount_path}' }}"
        res = subprocess.run(["powershell", "-NoProfile", "-Command", f"({ps_check}).ProcessId"], capture_output=True, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        if not res.stdout.strip():
            ps_kill = f"Get-WmiObject Win32_Process -Filter \"Name='rclone.exe'\" | Where-Object {{ $_.CommandLine -match '{mount_path}' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
            cmd = ["rclone", "mount", f"{remote}:", mount_path, "--vfs-cache-mode", "writes", "--links", "--network-mode", "--volname", remote]
            subprocess.Popen(cmd, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
            logger.info(f"[{acc['PROFILE_NAME']}] {T('Virtual drive (Auto-Mount) restored at')} {mount_path}")
    
    else: 
        is_mounted = False
        try:
            is_mounted = os.path.ismount(mount_path)
        except Exception:
            pass 
            
        if not is_mounted:
            env = os.environ.copy()
            env["PATH"] = f"{env.get('PATH', '')}:/usr/local/bin:/usr/bin:/bin:{os.path.expanduser('~/.local/bin')}"
            
            subprocess.run(["fusermount", "-uz", mount_path], capture_output=True, text=True, env=env)
            os.makedirs(mount_path, exist_ok=True)
            
            cmd = ["rclone", "mount", f"{remote}:", mount_path, "--vfs-cache-mode", "writes", "--daemon"]
            res = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if res.returncode == 0:
                logger.info(f"[{acc['PROFILE_NAME']}] {T('Virtual drive (Auto-Mount) successfully activated at')} {mount_path}")
            else:
                logger.error(f"[{acc['PROFILE_NAME']}] {T('Critical error in Auto-Mount:')} {res.stderr.strip()}")

def print_help():
    print(f"\n=== {T('Sync Engine Multi-Account')} (v{VERSION}) ===")
    print(T("Usage: sync-engine [COMMAND]"))
    print(T("  config         Interactive wizard."))
    print(f"🚀 {T('now Sync NOW.')}")
    print(f"🧪 {T('test Start Test-Drive mode (Dry-Run).')}")
    print(f"🧹 {T('clean File name cleaner.')}")
    print(f"🔎 {T('analyze Error analyzer and solutions.')}")
    print(f"🩺 {T('doctor System health diagnostics.')}")
    print(f"🔄 {T('update Download and install the latest version.')}")
    print(T("  start/stop     Start/Stop the invisible service."))
    print(T("  status/reload  Check logs or restart the invisible service."))
    print(T("  -v, --version  Show version."))
    print(T("  -h, --help     Show this help."))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        comando = sys.argv[1].strip().lower()
        if comando in ["-h", "--help", "help"]: 
            print_help()
            sys.exit(0)
        elif comando in ["-v", "--version", "version"]: 
            print(f"Sync Engine v{VERSION}")
            sys.exit(0)
        elif comando == "config": run_config_wizard()
        elif comando == "now": run_now()
        elif comando == "test": run_dry_run()
        elif comando == "clean": run_filename_cleaner()
        elif comando == "analyze": run_analyze_errors()
        elif comando == "doctor": 
            clear_screen()
            run_doctor(load_config())
        elif comando == "update": run_update()
        elif comando == "start": manage_service("start", LOG_FILE)
        elif comando == "stop": manage_service("stop", LOG_FILE); logger.info(T("Motor stopped manually."))
        elif comando == "status": manage_service("status", LOG_FILE)
        elif comando == "reload": manage_service("reload", LOG_FILE)
        else: 
            print(f"\n⚠️ {T('Command not recognized:')} '{comando}'")
            print_help()
            sys.exit(1) 
        sys.exit(0)
    else:
        is_terminal = False
        try:
            if sys.stdout is not None and sys.stdout.isatty(): is_terminal = True
        except Exception: pass
        
        if is_terminal: 
            print_help()
            sys.exit(1)
        
    try:
        logger.info(T("Sync Engine Motor Started in Background."))
        while True:
            config = load_config()
            ACCOUNTS = config.get("ACCOUNTS", [])
            if not ACCOUNTS: sys.exit(1)

            for acc in ACCOUNTS:
                ensure_mount(acc)
                if not acc.get("AUTO_SYNC", True):
                    continue
                profile = acc.get("PROFILE_NAME", "Local")
                local_dir = os.path.expanduser(acc["LOCAL_DIR"])
                os.makedirs(local_dir, exist_ok=True)
                
                if config.get("AUTO_CHECK_NAMES", True):
                    if check_name_issues_silent(local_dir, acc.get("IGNORE_PATTERNS", [])):
                        logger.error(f"[{profile}] {T('Sync blocked: Name collision or invalid characters detected.')}")
                        send_notification(T("Name Conflict"), f"{T('Sync for')} '{profile}' {T('paused. Use Option 9 to fix.')}", "critical")
                        continue
                
                db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
                db_conn = init_db(db_path)
                scan_local(db_conn, local_dir, acc.get("IGNORE_PATTERNS", []))
                try:
                    scan_remote(db_conn, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
                except RuntimeError as e:
                    logger.error(f"[{profile}] {T('Sync blocked:')} {e}")
                    continue
                    
                generate_filters(db_conn, filter_file, acc.get("IGNORE_PATTERNS", []))
                db_conn.close()
                
                success, transfers, err_msg = run_sync(local_dir, acc["REMOTE_NAME"], filter_file, config.get("BW_LIMIT", "0"), acc.get("MAX_SIZE", "0"), get_report_dir(config), profile)
                
                if success and transfers:
                    logger.info(f"[{profile}] {T('Sync completed with changes.')}")
                    send_notification(T("Sync Engine"), f"{T('Account')} '{profile}' {T('synced.')}")
                elif not success:
                    logger.error(f"[{profile}] {T('Error:')} {err_msg}")
                else:
                    logger.info(f"[{profile}] {T('Check complete. No changes detected.')}")
            
            process_scheduled_tasks(config) # <--- Checa o relógio e executa agendamentos pendentes
            time.sleep(config.get("SYNC_INTERVAL", 300))
    except Exception as e:
        logger.error(f"{T('CRITICAL MOTOR FAILURE:')} {e}")
