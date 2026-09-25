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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)

from sync_config import load_config, save_config, get_report_dir, VERSION, CONFIG_DIR, LOG_FILE, logger, clean_log_file, clean_log_text, T
from sync_os import manage_service, send_notification, run_doctor_os, SISTEMA
from sync_core import init_db, scan_local, scan_remote, generate_filters, analyze_sync_logic

UPDATE_URL_RAW = "https://raw.githubusercontent.com/ocanha-almeida/sync-engine/main/sync_config.py"
UPDATE_URL_ZIP = "https://github.com/ocanha-almeida/sync-engine/archive/refs/heads/main.zip"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(T("\nPress Enter to continue..."))

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

def run_filename_cleaner():
    clear_screen()
    print("="*45 + f"\n{T('🧹 CLEANER AND COLLISION RADAR')}\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])

    print(T("Choose the target directory:"))
    print(T("[0] Enter a manual path"))
    for i, acc in enumerate(ACCOUNTS): print(f"[{i+1}] {T('Account')} '{acc['PROFILE_NAME']}' ({acc['LOCAL_DIR']})")
    
    op = input(T("\nOption [Enter to cancel]: ")).strip().lower()
    if op == '' or op == 'c': return

    ignore_patterns = []
    safe_name = "avulso"
    if op == '0': 
        alvo = input(T("\nPath: ")).strip()
    elif op.isdigit() and 1 <= int(op) <= len(ACCOUNTS):
        alvo = ACCOUNTS[int(op)-1]["LOCAL_DIR"]
        ignore_patterns = ACCOUNTS[int(op)-1].get("IGNORE_PATTERNS", [])
        safe_name = "".join([c for c in ACCOUNTS[int(op)-1]['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
    else: return

    if not alvo: return
    alvo_expandido = os.path.expanduser(alvo)
    if not os.path.isdir(alvo_expandido): print(f"\n❌ {T('Error: The directory does not exist.')}"); pause(); return

    report_dir = os.path.normpath(get_report_dir(config))
    report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_relatorio_higienizador.txt"))

    with open(report_file, "w", encoding="utf-8") as rep_file:
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        def tee(msg=""): print(msg); rep_file.write(msg + "\n")
        
        tee("="*45 + f"\n{T('🧹 CLEANER REPORT')} ({safe_name})\n{T('Scan Date/Time:')} {agora}\n" + "="*45 + "\n")
        tee(T("🔍 Analyzing directory...\n"))
        
        substituicoes = {"‛‛": "", "‛": "'", "＂": "", "｜": "-", "⧸": "-", "：": "-", "？": "", "＊": "", "★": "", "✬": "", "☆": ""}
        arquivos_para_renomear, colisoes_case = [], []
        
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

            vistos_nesta_pasta = {}
            for nome in files:
                rel_path = os.path.join(rel_root_unix, nome).replace("\\", "/") if rel_root_unix else nome.replace("\\", "/")
                ignored = False
                for p in ignore_patterns:
                    p_unix = p.replace("\\", "/")
                    if p_unix.startswith('/') and fnmatch.fnmatch(rel_path, p_unix[1:]): ignored = True; break
                    elif fnmatch.fnmatch(nome, p_unix): ignored = True; break
                if ignored: continue

                nome_lower = nome.lower()
                if nome_lower in vistos_nesta_pasta: colisoes_case.append((root, vistos_nesta_pasta[nome_lower], nome))
                else: vistos_nesta_pasta[nome_lower] = nome

                novo_nome = nome
                for ruim, bom in substituicoes.items(): novo_nome = novo_nome.replace(ruim, bom)
                while "  " in novo_nome: novo_nome = novo_nome.replace("  ", " ")
                novo_nome = novo_nome.replace(" .", ".")

                if novo_nome != nome: arquivos_para_renomear.append((os.path.join(root, nome), os.path.join(root, novo_nome), nome, novo_nome))

        if colisoes_case:
            tee(T("🚨 CRITICAL ALERT: NAME COLLISION DETECTED! 🚨"))
            for pasta, arq1, arq2 in colisoes_case: tee(f" 📁 {T('Folder:')} {pasta}\n    ❌ {arq1}\n    ❌ {arq2}\n")
            tee(T("⚠️  RECOMMENDED ACTION: Rename one of these files manually.\n"))

        if not arquivos_para_renomear: 
            tee(T("✨ Clean names! No invalid characters."))
            print(f"\n📂 {T('Report saved at:')} {report_file}")
            pause(); return

        rep_file.write(f"⚠️ {T('Found')} {len(arquivos_para_renomear)} {T('files with invalid characters.')}\n\n")
        print(f"⚠️ {T('Found')} {len(arquivos_para_renomear)} {T('files with invalid characters.')}\n")
        
        for i, (caminho_antigo, _, nome, novo_nome) in enumerate(arquivos_para_renomear):
            msg = f" 📁 {T('In:')}   {os.path.dirname(caminho_antigo)}\n    {T('From:')} {nome}\n    {T('To:')}   {novo_nome}\n"
            rep_file.write(msg + "\n")
            if i < 10: print(msg)
            
        if len(arquivos_para_renomear) > 10:
            print(f"{T('... and')} {len(arquivos_para_renomear) - 10} {T('more hidden files to save screen space.')}")
        
    print(f"\n📂 {T('Complete report saved at:')} {report_file}")
    confirma = input(f"{T('Confirm changing these')} {len(arquivos_para_renomear)} {T('files? (Y/N) [N]: ')}").strip().lower()
    if confirma not in ['s', 'y']: print(T("\nOperation canceled.")); pause(); return

    renomeados = 0
    for caminho_antigo, caminho_novo, nome, novo_nome in arquivos_para_renomear:
        try: os.rename(caminho_antigo, caminho_novo); renomeados += 1
        except Exception: pass
    print(f"\n🎉 {T('Done!')} {renomeados} {T('files cleaned.')}"); pause()

def run_analyze_errors():
    clear_screen()
    print("="*45 + f"\n{T('🔎 ERROR ANALYZER')}\n" + "="*45)
    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    logs_disponiveis = []
        
    for acc in config.get("ACCOUNTS", []):
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        
        auto_log = os.path.join(report_dir, f"{safe_name}_ultimo_ciclo_auto.txt")
        if os.path.exists(auto_log): logs_disponiveis.append((f"{T('Automatic:')} {acc['PROFILE_NAME']}", auto_log, acc['REMOTE_NAME']))
            
        manual_log = os.path.join(report_dir, f"{safe_name}_ultima_sincronizacao_manual.txt")
        if os.path.exists(manual_log): logs_disponiveis.append((f"{T('Manual:')} {acc['PROFILE_NAME']}", manual_log, acc['REMOTE_NAME']))
            
    if not logs_disponiveis: print(T("\n❌ No report found.")); pause(); return

    print(T("\nChoose which report to analyze:\n"))
    for i, (nome, _, _) in enumerate(logs_disponiveis): print(f"  [{i+1}] {nome}")
    
    op = input(T("\nOption [Enter to cancel]: ")).strip().lower()
    if op == '' or op == 'c' or not (op.isdigit() and 1 <= int(op) <= len(logs_disponiveis)): return
        
    sync_report = logs_disponiveis[int(op)-1][1]
    remote_name = logs_disponiveis[int(op)-1][2]
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

    if total_errors == 0: print(T("\n✨ Excellent! Your ecosystem is healthy."))
    else:
        print(f"\n⚠️ {T('Found')} {total_errors} {T('problems:')}\n")
        if lock_errors > 0: print(f"🔹 {lock_errors}x {T('Lock File: Engine automatically broke the lock.')}")
        if lstat_errors > 0: print(f"🔹 {lstat_errors}x {T('File not found: Use Option 9 to clean names.')}")
        if etag_errors > 0: print(f"🔹 {etag_errors}x {T('eTag Conflict: Temporary cloud error.')}")
        if resync_requests > 0: print(f"🔹 {resync_requests}x {T('Healing Scan: History broken, engine initiated repair.')}")
        if auth_errors > 0: print(f"🔹 {auth_errors}x {T('Auth/Token Error: The cloud disconnected.')}")
        
    if auth_errors > 0:
        print("\n" + "="*45)
        print(T("🚨 DISCONNECTED CLOUD DETECTED 🚨"))
        print(T("Providers like Microsoft and Google require periodic"))
        print(T("renewal of security authorization (Token)."))
        print(f"{T('Target cloud:')} {remote_name}")
        resp = input(T("\nDo you want to open the browser and renew the token now? (Y/N) [Y]: ")).strip().lower()
        if resp != 'n':
            print(T("\n⏳ Opening browser for reconnection..."))
            subprocess.run(["rclone", "config", "reconnect", f"{remote_name}:"])
            print(T("\n✅ Reconnection complete. Future synchronizations should work perfectly."))
            
    pause()

def run_dry_run():
    clear_screen()
    print("="*45 + f"\n{T('🧪 TEST-DRIVE REPORT (DRY-RUN)')}\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: print(T("No account configured.")); pause(); return

    print(T("\nChoose the account for the Test-Drive:"))
    print(T(" [0] All accounts (Batch)"))
    for i, acc in enumerate(ACCOUNTS):
        print(f" [{i+1}] {acc['PROFILE_NAME']} ({acc['REMOTE_NAME']}:)")

    op = input(T("\nOption [Enter to cancel]: ")).strip()
    if op == '' or op.lower() == 'c': return

    contas_alvo = []
    if op == '0':
        contas_alvo = ACCOUNTS
    elif op.isdigit() and 1 <= int(op) <= len(ACCOUNTS):
        contas_alvo = [ACCOUNTS[int(op)-1]]
    else:
        return

    report_dir = os.path.normpath(get_report_dir(config))

    for acc in contas_alvo:
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_dry_run.txt"))
        
        with open(report_file, "w", encoding="utf-8") as rep_file:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            def tee(msg=""): print(msg); rep_file.write(msg + "\n")
            tee("="*45 + f"\n{T('🧪 TEST-DRIVE REPORT')} ({acc['PROFILE_NAME']})\n{T('Simulation Date/Time:')} {agora}\n" + "="*45)
            local_dir = os.path.expanduser(acc["LOCAL_DIR"])
            db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            
            db_connection = init_db(db_path)
            scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
            scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
            generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
            db_connection.close()

            cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", "--dry-run"]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            if result.stderr: tee(clean_log_text(result.stderr.strip()))
            if result.stdout: tee(clean_log_text(result.stdout.strip()))
            tee("-" * 45)
            print(f"📂 {T('Report saved at:')} {report_file}")
            
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

    print("="*45 + f"\n{T('📊 FILES BLOCKED BY SIZE')}\n" + "="*45)
    print(T("⏳ Analyzing local folders and clouds. This might take a few seconds..."))

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
            
            tee("="*45 + f"\n{T('📊 FILES BLOCKED BY SIZE')} ({acc['PROFILE_NAME']})\n{T('Date/Time:')} {agora}\n{T('Configured Limit:')} {max_size}\n" + "="*45)
            
            filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            
            tee(f"\n{T('🖥️  ON COMPUTER (Local):')}")
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

            tee(f"\n{T('☁️  ON CLOUD (Remote):')}")
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
        f.write("="*45 + f"\n{T('🚀 AUTOMATIC SYNC REPORT')} ({profile_name})\n{T('Start Date/Time:')} {agora}\n" + "="*45 + "\n\n")
    
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
                f.write("="*45 + f"\n{T('🚀 AUTOMATIC SYNC REPORT')} ({profile_name})\n{T('Start Date/Time:')} {agora_retry} ({T('Retry post-lock')})\n" + "="*45 + "\n\n")
                
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
            f.write("="*45 + f"\n{T('🚀 REPORT (HEALING SCAN)')} ({profile_name})\n{T('Start Date/Time:')} {agora_resync}\n" + "="*45 + "\n\n")
            
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

def run_now():
    clear_screen()
    print("="*45 + f"\n{T('🚀 IMMEDIATE SYNC AND REPAIR (NOW)')}\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: print(f"\n{T('No account configured.')}"); pause(); return

    report_dir = os.path.normpath(get_report_dir(config))
    sync_realizada = False

    for acc in ACCOUNTS:
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
                f.write("="*45 + f"\n{T('🚀 MANUAL SYNC REPORT')} ({acc['PROFILE_NAME']})\n{T('Start Date/Time:')} {agora}\n" + "="*45 + "\n\n")
            sync_realizada = True
            
        db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
        db_connection = init_db(db_path)
        scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
        try:
            scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
        except RuntimeError as e:
            print(f"❌ {T('Connection error with')} {acc['REMOTE_NAME']}.")
            print(f"   {e}")
            print(f"   {T('Synchronization aborted for safety.')}")
            continue            
        generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
        db_connection.close()

        cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-P", "-v", f"--log-file={MANUAL_SYNC_REPORT_FILE}"]
        max_size = acc.get("MAX_SIZE", "0")
        if max_size != "0": cmd.append(f"--max-size={max_size}")
        
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
                logger.warning(f"[{acc['PROFILE_NAME']}] {T('Breaking lock file on manual sync.')}")
                subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()])
                subprocess.run(cmd)
                with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()

        if "resync" in log_text.lower() or "not found" in log_text.lower():
            print(f"\n⚠️ {T('Triggering healing scan (--resync)...')}")
            logger.warning(f"[{acc['PROFILE_NAME']}] {T('Triggering healing scan (--resync) on manual sync.')}")
            cmd.append("--resync"); subprocess.run(cmd)
            
        clean_log_file(MANUAL_SYNC_REPORT_FILE)
        print(f"\n✅ {T('Completed:')} {acc['PROFILE_NAME']}")
        logger.info(f"[{acc['PROFILE_NAME']}] {T('Manual sync completed successfully.')}")
    
    if sync_realizada:
        print(f"\n📂 {T('Isolated reports saved in folder:')} {report_dir}")
    else:
        print(f"\n{T('No synchronization was performed.')}")
    pause()

def run_update():
    import time
    clear_screen()
    print("="*45 + f"\n{T('🔄 UPDATE CHECKER')}\n" + "="*45)
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
        print(T("❌ Could not identify the version on the server.")); pause(); return

    print(f"{T('Remote version:')} {remote_version}\n")
    if remote_version == VERSION:
        print(T("✅ You are already using the latest version!")); pause(); return
        
    print(T("🎉 A new version is available!"))
    resp = input(T("Do you want to download and install the update now? (Y/N) [N]: ")).strip().lower()
    if resp not in ['s', 'y']: return
        
    print(T("\n📥 Downloading update package..."))
    try:
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "update.zip")
        req = urllib.request.Request(UPDATE_URL_ZIP, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(T("📦 Extracting files..."))
        with zipfile.ZipFile(zip_path, 'r') as zip_ref: zip_ref.extractall(tmp_dir)
        
        extract_dir = os.path.join(tmp_dir, "sync-engine-main")
        if SISTEMA == "Windows":
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "_core_install.ps1"], cwd=extract_dir)
        else:
            subprocess.run(["bash", "install-linux.sh"], cwd=extract_dir)
            
        shutil.rmtree(tmp_dir)
        print(T("\n✅ Update completed successfully!")); pause(); sys.exit(0)
    except Exception as e:
        print(f"\n❌ {T('Error during the update process:')} {e}"); pause()

def run_cloud_migration():
    clear_screen()
    print("="*45 + f"\n{T('☁️ DIRECT CLOUD-TO-CLOUD MIGRATION')}\n" + "="*45)
    print(T("Transfers files between providers using RAM."))
    print(T("Does not consume local hard drive space.\n"))
    
    res = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    remotes = [r.strip(':') for r in res.stdout.strip().split('\n') if r.strip()]
    if len(remotes) < 2:
        print(T("❌ You need at least 2 clouds configured in Rclone to migrate."))
        pause(); return

    print(T("Available Providers:"))
    for i, r in enumerate(remotes): print(f"  [{i+1}] {r}")
    
    op_src = input(T("\nSOURCE Cloud (Number) [Enter to cancel]: ")).strip()
    if not op_src.isdigit() or not (1 <= int(op_src) <= len(remotes)): return
    src_remote = remotes[int(op_src)-1]
    
    src_path = input(T("📁 Subfolder in source (Leave blank for root '/'): ")).strip()
    src_full = f"{src_remote}:{src_path}" if src_path else f"{src_remote}:"

    op_dst = input(T("\nDESTINATION Cloud (Number) [Enter to cancel]: ")).strip()
    if not op_dst.isdigit() or not (1 <= int(op_dst) <= len(remotes)): return
    dst_remote = remotes[int(op_dst)-1]
    
    dst_path = input(T("📁 Subfolder in destination (Leave blank for root '/'): ")).strip()
    dst_full = f"{dst_remote}:{dst_path}" if dst_path else f"{dst_remote}:"
    
    if src_full == dst_full:
        print(T("❌ Source and Destination cannot be the same path.")); pause(); return

    print(f"\n{T('Configured flow:')} {src_full} ➔ {dst_full}")
    
    print(T("\nTransfer Mode:"))
    print(T("  [1] 📦 TOTAL         (Copies ABSOLUTELY EVERYTHING)"))
    print(T("  [2] 🛡️  STANDARD     (Blocks vaults, trash and folders with .nosync marker)"))
    print(T("  [3] ⚙️  CUSTOM       (Standard + Imports config.json filters from source)"))
    
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
        print(T("\n🔍 Scanning cloud for '.nosync' markers (May take a few seconds)..."))
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
        print(T("\n\n⏹️ Transfer interrupted by user."))
    
    if modo in ['2', '3']: os.remove(temp_filter)
    
    clean_log_file(report_file)
    print(f"\n✅ {T('Operation finished. Report saved at:')} {report_file}"); pause()

def run_mount_manager():
    clear_screen()
    config = load_config()
    print("="*45 + f"\n{T('🔌 VIRTUAL DRIVE MANAGER (MOUNT)')}\n" + "="*45)
    print(T("⚠️ ATTENTION - SYSTEM REQUIREMENTS:"))
    print(T("   Linux: Requires the 'fuse' package installed (default on Ubuntu)."))
    print(T("   Windows: Requires the free 'WinFsp' program installed.\n"))
    
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS:
        print(T("❌ No account configured in Sync Engine.")); pause(); return

    for i, acc in enumerate(ACCOUNTS):
        status = T("🟢 AUTO-MOUNT ENABLED") if acc.get("AUTO_MOUNT") else T("🔴 MANUAL")
        caminho = f" -> {acc.get('MOUNT_PATH')}" if acc.get("AUTO_MOUNT") else ""
        print(f"  [{i+1}] {acc['PROFILE_NAME']} ({acc['REMOTE_NAME']}:) [{status}{caminho}]")
    
    op = input(T("\nChoose account to configure (Number) [Enter to cancel]: ")).strip()
    if not op.isdigit() or not (1 <= int(op) <= len(ACCOUNTS)): return
    acc = ACCOUNTS[int(op)-1]
    
    print(f"\n--- {T('Configuring Mount for:')} {acc['PROFILE_NAME']} ---")
    print(T("  [1] 🔌 Mount temporarily NOW (Open terminal window)"))
    print(T("  [2] 🔄 ENABLE Auto-Mount (Restores with Sync Engine)"))
    print(T("  [3] ⏹️ DISABLE Auto-Mount"))
    
    acao = input(T("\nAction (1-3) [Enter to cancel]: ")).strip()
    if acao not in ['1', '2', '3']: return

    if acao == '3':
        acc["AUTO_MOUNT"] = False
        acc["MOUNT_PATH"] = ""
        save_config(config, f"{T('Auto-Mount disabled for')} {acc['PROFILE_NAME']}")
        manage_service("reload", LOG_FILE)
        print(T("\n✅ Auto-Mount disabled! It will no longer be recreated on boot.")); pause(); return
        
    if SISTEMA == "Windows":
        print(T("\nType a free drive letter in Windows (Ex: X, Y, Z)"))
        letra = input(T("Letter: ")).strip().upper()
        if not letra or len(letra) > 1: return
        mount_path = f"{letra}:"
    else: 
        default_path = f"~/Desktop/{acc['REMOTE_NAME']}"
        pasta = input(f"\n{T('Empty folder path to mount (Enter =')} {default_path}): ").strip()
        mount_path = os.path.expanduser(pasta) if pasta else os.path.expanduser(default_path)
        
    if acao == '2':
        acc["AUTO_MOUNT"] = True
        acc["MOUNT_PATH"] = mount_path
        save_config(config, f"{T('Auto-Mount enabled for')} {acc['PROFILE_NAME']} {T('at')} {mount_path}")
        print(T("\n✅ Auto-Mount enabled! Reloading engine to apply..."))
        manage_service("reload", LOG_FILE); pause(); return
        
    if acao == '1':
        if SISTEMA == "Windows":
            cmd_mount = f"start cmd /k rclone mount {acc['REMOTE_NAME']}: {mount_path} --vfs-cache-mode writes --links --network-mode --volname \"{acc['REMOTE_NAME']}\""
            print(f"\n⏳ {T('Mapping')} {acc['REMOTE_NAME']} {T('to')} {mount_path}...")
            subprocess.Popen(cmd_mount, shell=True)
            print(T("✅ A new black window has opened managing the drive."))
            print(T("To eject the cloud, just close that terminal window!"))
        else:
            os.makedirs(mount_path, exist_ok=True)
            cmd_mount = ["rclone", "mount", f"{acc['REMOTE_NAME']}:", mount_path, "--vfs-cache-mode", "writes", "--daemon"]
            print(f"\n⏳ {T('Mounting')} {acc['REMOTE_NAME']} {T('to')} {mount_path}...")
            res = subprocess.run(cmd_mount, capture_output=True, text=True)
            if res.returncode == 0:
                print(T("✅ Drive mounted successfully in the background!"))
                print(f"{T('To unmount later, use the command:')} fusermount -u {mount_path}")
            else:
                print(f"❌ {T('Error mounting:')} {res.stderr.strip()}")
        pause()

def run_doctor(config):
    print("="*45 + f"\n{T('🩺 SYSTEM DIAGNOSTICS')}\n" + "="*45)
    
    print(T("[Base Dependencies]"))
    res = subprocess.run(["rclone", "version"], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"🟢 Rclone: {T('Supported')} ({res.stdout.splitlines()[0]})")
    else:
        print(T("🔴 Rclone: Missing! Install rclone and add it to PATH."))
    
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
    print("="*45 + f"\n{T('🧨 SYNC ENGINE UNINSTALLATION')}\n" + "="*45)
    print(T("This action will stop the services and permanently"))
    print(T("remove the application from your system."))
    
    desafio = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(T("\nTo confirm, type exactly the code below:"))
    print(f"👉 {T('Code:')} {desafio}")
    
    confirma = input(T("\nYour answer [Enter to cancel]: ")).strip()
    if confirma != desafio:
        print(T("\n❌ Incorrect code. Operation canceled."))
        pause()
        return
        
    print("\n" + "-"*45)
    print(T("Do you also want to delete settings, databases"))
    print(T("and saved reports?"))
    apagar_dados = input(T("(Y/N) [N]: ")).strip().lower() in ['s', 'y']
    
    print(T("\n⏳ Stopping invisible service..."))
    manage_service("stop", LOG_FILE)
    
    print(T("⏳ Preparing self-destruct script..."))
    
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
        
    print(T("\n✅ Uninstallation triggered successfully!"))
    print(T("The engine will be removed from the drive in 3 seconds."))
    print(T("Goodbye!\n"))
    sys.exit(0)

def run_config_wizard():
    while True:
        config = load_config()
        clear_screen()
        print(f"=== {T('Sync Engine Wizard')} (v{VERSION}) ===\n" + "="*45)
        print(f"\n--- {T('Account Configuration')} ---")
        print(f"1. ➕ {T('Add new account')}")
        print(f"2. 📋 {T('List current accounts')}")
        print(f"3. ❌ {T('Remove an account')}")
        
        print(f"\n--- {T('Global Settings')} ---")
        print(f"4. ⚙️  {T('Edit Interval, Bandwidth, Folders, and Collisions')}")
        print(f"5. 🛡️  {T('Manage Exclusion Filters and Limits per Account')}")
        
        print(f"\n--- {T('Extra Actions')} ---")
        print(f"6. 🚀 {T('Force Sync Now')}")
        print(f"7. 🧪 {T('Test-Drive / Simulation (Dry-Run)')}")
        print(f"8. 📊 {T('Report of Files Over the Limit')}")
        print(f"9. 🧹 {T('Cleaner and Collision Checker')}")
        print(f"10. 🔎 {T('Sync Error Analyzer')}")
        print(f"11. 🩺 {T('System Diagnostics (Doctor)')}")
        print(f"12. ☁️  {T('Direct Cloud-to-Cloud Migration')}")
        print(f"13. 🔌 {T('Mount Cloud as Virtual Drive (Mount)')}")
        
        print(f"\n--- {T('Background Motor')} ---")
        print(f"14. ▶️ {T('Start Service')}")
        print(f"15. ⏹️ {T('Stop Service')}")
        print(f"16. ℹ️ {T('Check Motor Status')}")
        print(f"17. 🔄 {T('Update Application Version')}")
        print(f"18. 🧨 {T('Uninstall Sync Engine')}")
        
        print(f"\n[Enter] {T('Exit')}\n" + "="*45)
        
        escolha = input(T("Option: ")).strip()
        if escolha == '': clear_screen(); print(T("Goodbye!\n")); break
        
        elif escolha == '1':
            clear_screen()
            print("="*45 + f"\n{T('➕ ADD NEW ACCOUNT')}\n" + "="*45)
            profile = input(T("\nProfile Name [Enter to return]: ")).strip()
            if not profile: continue
            rclone_out = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            remotes = [r.strip(':') for r in rclone_out.stdout.strip().split('\n') if r.strip()]
            for i, r in enumerate(remotes): print(f"  [{i+1}] {r}")
            op_remote = input(T("\nCloud number [Enter to return]: ")).strip()
            if not op_remote or not op_remote.isdigit() or int(op_remote)-1 >= len(remotes): continue
            
            remote = remotes[int(op_remote) - 1]
            local = input(f"\n{T('Local folder (Enter for')} '~/{remote}'): ").strip() or f"~/{remote}"
                
            safe_name = "".join([c for c in profile.lower().replace(" ", "_") if c.isalnum() or c=='_'])
            config.setdefault("ACCOUNTS", []).append({
                "PROFILE_NAME": profile, "REMOTE_NAME": remote, "LOCAL_DIR": local,
                "IGNORE_PATTERNS": ["venv", ".venv", "__pycache__", ".git", "Personal Vault", "Cofre Pessoal", "*.tmp", ".DS_Store", "site-packages", "Thumbs.db", "~$*"],
                "DB_FILE": f"sync_metadata_{safe_name}.db", "FILTER_FILE": f"excludes_{safe_name}.txt"
            })
            save_config(config, f"{T('Added account')} '{profile}'"); manage_service("reload", LOG_FILE); print(T("\n✅ Saved!")); pause()

        elif escolha == '2':
            clear_screen()
            print("="*45 + f"\n{T('📋 LIST CURRENT ACCOUNTS')}\n" + "="*45)
            for i, acc in enumerate(config.get("ACCOUNTS", [])): print(f"[{i+1}] {acc['PROFILE_NAME']} ({acc['LOCAL_DIR']})")
            pause()
                
        elif escolha == '3':
            clear_screen()
            print("="*45 + f"\n{T('❌ REMOVE ACCOUNT')}\n" + "="*45)
            contas = config.get("ACCOUNTS", [])
            if not contas:
                print(T("No account configured.")); pause(); continue
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            op = input(T("\nNumber to delete [Enter to return]: ")).strip()
            if op.isdigit() and 1 <= int(op) <= len(contas):
                apagada = contas.pop(int(op)-1)
                save_config(config, f"{T('Removed account')} '{apagada['PROFILE_NAME']}'"); manage_service("reload", LOG_FILE); print(f"\n🗑️ {T('Removed:')} {apagada['PROFILE_NAME']}"); pause()
                
        elif escolha == '4':
            while True:
                clear_screen()
                print("="*45 + f"\n{T('⚙️  EDIT INTERVAL, LIMITS AND FOLDERS')}\n" + "="*45)
                print(f"  [1] {T('Interval')} ({config.get('SYNC_INTERVAL', 300)}s)")
                print(f"  [2] {T('Bandwidth Limit')} ({config.get('BW_LIMIT', '0')})")
                print(f"  [3] {T('Reports Folder')} ({T('Current:')} {os.path.normpath(get_report_dir(config))})")
                print(f"  [4] {T('Auto Block on Name Collisions')} ({T('Current:')} {config.get('AUTO_CHECK_NAMES', True)})")
                
                sub_op = input(T("\nOption (1-4) [Enter = Return]: ")).strip()
                if sub_op == '': break
                elif sub_op == '1':
                    nv = input(T("New interval in seconds: ")).strip()
                    if nv.isdigit(): config["SYNC_INTERVAL"] = int(nv); save_config(config); manage_service("reload", LOG_FILE)
                elif sub_op == '2':
                    nv = input(T("New limit (ex: 1M, 500k, 0 for unlimited): ")).strip()
                    if nv: config["BW_LIMIT"] = nv; save_config(config)
                elif sub_op == '4':
                    config["AUTO_CHECK_NAMES"] = not config.get("AUTO_CHECK_NAMES", True)
                    save_config(config)
                elif sub_op == '3':
                    while True:
                        current_dir = os.path.normpath(get_report_dir(config))
                        os.makedirs(current_dir, exist_ok=True)
                        if SISTEMA == "Windows":
                            root_config = os.path.normpath(os.path.expanduser("~/.config"))
                            if os.path.exists(root_config):
                                subprocess.run(["attrib", "+h", root_config], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
                        
                        clear_screen()
                        print("="*45 + f"\n{T('📂 REPORTS MANAGER')}\n" + "="*45)
                        print(f"{T('Current:')} {current_dir}\n")
                        print(T(" [1] 📂 Open folder in Explorer/Manager"))
                        print(T(" [2] ✏️  Change save location"))
                        print(T(" [3] 🔄 Restore to hidden default folder"))
                        
                        sub_esc = input(T("\nAction (1-3) [Enter = Return]: ")).strip()
                        if sub_esc == '': break
                        elif sub_esc == '1':
                            if SISTEMA == "Windows": os.startfile(current_dir)
                            else: subprocess.run(["xdg-open", current_dir])
                        elif sub_esc == '2':
                            novo_dir = input(T("Type the new absolute path: ")).strip()
                            if novo_dir:
                                config["REPORT_DIR"] = os.path.normpath(novo_dir)
                                save_config(config)
                                print(f"✅ {T('Folder changed to:')} {config['REPORT_DIR']}")
                                pause()
                        elif sub_esc == '3':
                            config["REPORT_DIR"] = "" 
                            save_config(config)
                            print(T("✅ Reports restored to default directory (~/.config/sync_engine)."))
                            pause()

        elif escolha == '5':
            clear_screen()
            print("="*45 + f"\n{T('🛡️ MANAGE FILTERS AND LIMITS PER ACCOUNT')}\n" + "="*45)
            contas = config.get("ACCOUNTS", [])
            if not contas:
                print(T("No account configured.")); pause(); continue
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            op_acc = input(T("\nAccount [Enter to return]: ")).strip()
            if op_acc.isdigit() and 1 <= int(op_acc) <= len(contas):
                conta = contas[int(op_acc) - 1]
                padroes = conta.get("IGNORE_PATTERNS", [])
                tamanho_max = conta.get("MAX_SIZE", "0")
                while True:
                    clear_screen(); print(f"--- {T('Settings:')} {conta['PROFILE_NAME']} ---")
                    print(f"📦 {T('Size Limit:')} {tamanho_max} (0 = {T('Unlimited')})")
                    print(T("\n🛡️  Current Exclusion Filters:"))
                    for j, p in enumerate(padroes): print(f"  [{j+1}] {p}")
                    
                    print(T("\n[T] Change Max Size       [A] Add Filter        [R] Remove Filter"))
                    print(T("[S] Save and Exit         [Enter] Cancel"))
                    acao = input(T("Action: ")).strip().lower()
                    
                    if acao == '' or acao == 'c': break
                    elif acao == 's': 
                        conta["IGNORE_PATTERNS"] = padroes
                        conta["MAX_SIZE"] = tamanho_max
                        save_config(config, f"{T('Filters/Limits changed in')} '{conta['PROFILE_NAME']}'")
                        manage_service("reload", LOG_FILE); break
                    elif acao == 't':
                        nv = input(T("\nNew max size (ex: 100M, 1G, 0 for unlimited): ")).strip()
                        if nv: tamanho_max = nv
                    elif acao == 'a': 
                        print(T("\n💡 ADVANCED FILTERING TIPS:"))
                        print(T("  (?i)*.tmp           -> Ignore Case (ex: log.TMP and log.tmp)"))
                        print(T("  venv                -> Exact name match in any folder"))
                        print(T("  Prefix*             -> Start of name (ex: Backup* ignores Backup_2026)"))
                        print(T("  *.bak               -> Extension wildcard at any level"))
                        print(T("  /Backups            -> Root anchor (ignores only in main folder)"))
                        print(T("  /.*                 -> Ignore hidden folders/files only in root (Linux)"))
                        novo = input(T("\nType the new pattern: ")).strip()
                        if novo: padroes.append(novo)
                    elif acao == 'r': 
                        num = input(T("Number: ")).strip()
                        if num.isdigit() and 1 <= int(num) <= len(padroes): padroes.pop(int(num)-1)

        elif escolha == '6': run_now()
        elif escolha == '7': run_dry_run()
        elif escolha == '8': run_size_report()
        elif escolha == '9': run_filename_cleaner()
        elif escolha == '10': run_analyze_errors()
        elif escolha == '11': clear_screen(); run_doctor(config)
        elif escolha == '12': run_cloud_migration()
        elif escolha == '13': run_mount_manager()
        elif escolha == '14': clear_screen(); manage_service("start", LOG_FILE); pause()
        elif escolha == '15': clear_screen(); manage_service("stop", LOG_FILE); logger.info(T("Motor stopped manually.")); pause()
        elif escolha == '16': clear_screen(); manage_service("status", LOG_FILE); pause()
        elif escolha == '17': run_update()
        elif escolha == '18': run_uninstall()

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
    print(T("  now            🚀 Sync NOW."))
    print(T("  test           🧪 Start Test-Drive mode (Dry-Run)."))
    print(T("  clean          🧹 File name cleaner."))
    print(T("  analyze        🔎 Error analyzer and solutions."))
    print(T("  doctor         🩺 System health diagnostics."))
    print(T("  update         🔄 Download and install the latest version."))
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
            
            time.sleep(config.get("SYNC_INTERVAL", 300))
    except Exception as e:
        logger.error(f"{T('CRITICAL MOTOR FAILURE:')} {e}")