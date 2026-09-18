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

from sync_config import load_config, save_config, get_report_dir, VERSION, CONFIG_DIR, LOG_FILE, logger, clean_log_file, clean_log_text
from sync_os import manage_service, send_notification, run_doctor_os, SISTEMA
from sync_core import init_db, scan_local, scan_remote, generate_filters, analyze_sync_logic

UPDATE_URL_RAW = "https://raw.githubusercontent.com/ocanha-almeida/sync-engine/main/sync_engine.py"
UPDATE_URL_ZIP = "https://github.com/ocanha-almeida/sync-engine/archive/refs/heads/main.zip"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPressione Enter para continuar...")

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
    print("="*45 + "\n🧹 HIGIENIZADOR E RADAR DE COLISÃO\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])

    print("Escolha o diretório alvo:")
    print("[0] Digitar um caminho manual")
    for i, acc in enumerate(ACCOUNTS): print(f"[{i+1}] Conta '{acc['PROFILE_NAME']}' ({acc['LOCAL_DIR']})")
    
    op = input("\nOpção [Enter p/ cancelar]: ").strip().lower()
    if op == '' or op == 'c': return

    ignore_patterns = []
    safe_name = "avulso"
    if op == '0': 
        alvo = input("\nCaminho: ").strip()
    elif op.isdigit() and 1 <= int(op) <= len(ACCOUNTS):
        alvo = ACCOUNTS[int(op)-1]["LOCAL_DIR"]
        ignore_patterns = ACCOUNTS[int(op)-1].get("IGNORE_PATTERNS", [])
        safe_name = "".join([c for c in ACCOUNTS[int(op)-1]['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
    else: return

    if not alvo: return
    alvo_expandido = os.path.expanduser(alvo)
    if not os.path.isdir(alvo_expandido): print(f"\n❌ Erro: O diretório não existe."); pause(); return

    # Definição do novo relatório
    report_dir = os.path.normpath(get_report_dir(config))
    report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_relatorio_higienizador.txt"))

    with open(report_file, "w", encoding="utf-8") as rep_file:
        agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        def tee(msg=""): print(msg); rep_file.write(msg + "\n")
        
        tee("="*45 + f"\n🧹 RELATÓRIO DO HIGIENIZADOR ({safe_name})\nData/Hora da Varredura: {agora}\n" + "="*45 + "\n")
        tee("🔍 Analisando diretório...\n")
        
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
            tee("🚨 ALERTA CRÍTICO: COLISÃO DE NOMES DETECTADA! 🚨")
            for pasta, arq1, arq2 in colisoes_case: tee(f" 📁 Pasta: {pasta}\n    ❌ {arq1}\n    ❌ {arq2}\n")
            tee("⚠️  AÇÃO RECOMENDADA: Renomeie um destes arquivos manualmente.\n")

        if not arquivos_para_renomear: 
            tee("✨ Nomes limpos! Nenhum caractere inválido.")
            print(f"\n📂 Relatório salvo em: {report_file}")
            pause(); return

        # Grava todos no .txt, mas imprime apenas 10 no terminal
        rep_file.write(f"⚠️ Encontrados {len(arquivos_para_renomear)} arquivos com caracteres inválidos.\n\n")
        print(f"⚠️ Encontrados {len(arquivos_para_renomear)} arquivos com caracteres inválidos.\n")
        
        for i, (caminho_antigo, _, nome, novo_nome) in enumerate(arquivos_para_renomear):
            msg = f" 📁 Em:   {os.path.dirname(caminho_antigo)}\n    De:   {nome}\n    Para: {novo_nome}\n"
            rep_file.write(msg + "\n")
            if i < 10: print(msg)
            
        if len(arquivos_para_renomear) > 10:
            print(f"... e mais {len(arquivos_para_renomear) - 10} arquivos ocultos para economizar tela.")
        
    print(f"\n📂 Relatório completo salvo em: {report_file}")
    confirma = input(f"Confirma a alteração destes {len(arquivos_para_renomear)} arquivos? (S/N) [N]: ").strip().lower()
    if confirma != 's': print("\nOperação cancelada."); pause(); return

    renomeados = 0
    for caminho_antigo, caminho_novo, nome, novo_nome in arquivos_para_renomear:
        try: os.rename(caminho_antigo, caminho_novo); renomeados += 1
        except Exception: pass
    print(f"\n🎉 Concluído! {renomeados} arquivos higienizados."); pause()

def run_analyze_errors():
    clear_screen()
    print("="*45 + "\n🔎 ANALISADOR DE ERROS\n" + "="*45)
    config = load_config()
    report_dir = os.path.normpath(get_report_dir(config))
    logs_disponiveis = []
        
    for acc in config.get("ACCOUNTS", []):
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        
        auto_log = os.path.join(report_dir, f"{safe_name}_ultimo_ciclo_auto.txt")
        # NOVIDADE: Agora passamos o REMOTE_NAME (acc['REMOTE_NAME']) na lista
        if os.path.exists(auto_log): logs_disponiveis.append((f"Automático: {acc['PROFILE_NAME']}", auto_log, acc['REMOTE_NAME']))
            
        manual_log = os.path.join(report_dir, f"{safe_name}_ultima_sincronizacao_manual.txt")
        if os.path.exists(manual_log): logs_disponiveis.append((f"Manual: {acc['PROFILE_NAME']}", manual_log, acc['REMOTE_NAME']))
            
    if not logs_disponiveis: print("\n❌ Nenhum relatório encontrado."); pause(); return

    print("\nEscolha qual relatório analisar:\n")
    for i, (nome, _, _) in enumerate(logs_disponiveis): print(f"  [{i+1}] {nome}")
    
    op = input("\nOpção [Enter p/ cancelar]: ").strip().lower()
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
                # NOVIDADE: Radar de falha de autenticação
                elif "invalidauthenticationtoken" in line_lower or "couldn't fetch token" in line_lower or "expired" in line_lower or "token" in line_lower: auth_errors += 1
                else: other_errors += 1

    if total_errors == 0: print("\n✨ Excelente! Seu ecossistema está saudável.")
    else:
        print(f"\n⚠️ Encontrados {total_errors} problemas:\n")
        if lock_errors > 0: print(f"🔹 {lock_errors}x 'Lock File': Motor quebrou o cadeado automaticamente.")
        if lstat_errors > 0: print(f"🔹 {lstat_errors}x 'Arquivo não encontrado': Use a Opção 9 para higienizar nomes.")
        if etag_errors > 0: print(f"🔹 {etag_errors}x 'Conflito de eTag': Erro passageiro de nuvem.")
        if resync_requests > 0: print(f"🔹 {resync_requests}x 'Varredura de Cura': Histórico quebrou, motor iniciou o reparo.")
        if auth_errors > 0: print(f"🔹 {auth_errors}x 'Erro de Autenticação/Token': A nuvem desconectou.")
        
    # Assistente Automático de Reconexão
    if auth_errors > 0:
        print("\n" + "="*45)
        print("🚨 NUVEM DESCONECTADA DETECTADA 🚨")
        print("Provedores como Microsoft e Google exigem a renovação")
        print("periódica da autorização de segurança (Token).")
        print(f"Nuvem alvo: {remote_name}")
        resp = input("\nDeseja abrir o navegador e renovar o token agora? (S/N) [S]: ").strip().lower()
        if resp != 'n':
            print("\n⏳ Abrindo navegador para reconexão...")
            subprocess.run(["rclone", "config", "reconnect", f"{remote_name}:"])
            print("\n✅ Reconexão concluída. As próximas sincronizações devem funcionar perfeitamente.")
            
    pause()

def run_dry_run():
    clear_screen()
    print("="*45 + "\n🧪 RELATÓRIO DE TEST-DRIVE (DRY-RUN)\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: print("Nenhuma conta configurada."); pause(); return

    print("\nEscolha a conta para o Test-Drive:")
    print(" [0] Todas as contas (Em lote)")
    for i, acc in enumerate(ACCOUNTS):
        print(f" [{i+1}] {acc['PROFILE_NAME']} ({acc['REMOTE_NAME']}:)")

    op = input("\nOpção [Enter p/ cancelar]: ").strip()
    if op == '' or op.lower() == 'c': return

    contas_alvo = []
    if op == '0':
        contas_alvo = ACCOUNTS
    elif op.isdigit() and 1 <= int(op) <= len(ACCOUNTS):
        contas_alvo = [ACCOUNTS[int(op)-1]]
    else:
        return

    # Correção definitiva das barras de texto no Windows
    report_dir = os.path.normpath(get_report_dir(config))

    for acc in contas_alvo:
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        report_file = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultimo_dry_run.txt"))
        
        with open(report_file, "w", encoding="utf-8") as rep_file:
            agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
            def tee(msg=""): print(msg); rep_file.write(msg + "\n")
            tee("="*45 + f"\n🧪 RELATÓRIO DE TEST-DRIVE ({acc['PROFILE_NAME']})\nData/Hora da Simulação: {agora}\n" + "="*45)
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
            print(f"📂 Relatório salvo em: {report_file}")
            
    pause()

def run_size_report():
    clear_screen()
    config = load_config()
    if not config.get("ACCOUNTS", []): return
    
    report_dir = os.path.normpath(get_report_dir(config))
    
    has_limits = any(acc.get("MAX_SIZE", "0") != "0" for acc in config.get("ACCOUNTS", []))
    if not has_limits:
        print("Nenhum limite de tamanho configurado nas suas contas.")
        pause()
        return

    print("="*45 + "\n📊 ARQUIVOS BLOQUEADOS POR TAMANHO\n" + "="*45)
    print("⏳ Analisando pastas locais e nuvens. Isso pode levar alguns segundos...")

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
            agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
            def tee(msg=""): rep_file.write(msg + "\n")
            
            tee("="*45 + f"\n📊 ARQUIVOS BLOQUEADOS POR TAMANHO ({acc['PROFILE_NAME']})\nData/Hora: {agora}\nLimite Configurado: {max_size}\n" + "="*45)
            
            filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            
            # --- VARREDURA LOCAL ---
            tee("\n🖥️  NO COMPUTADOR (Local):")
            cmd_local = ["rclone", "ls", os.path.expanduser(acc["LOCAL_DIR"]), f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res_local = subprocess.run(cmd_local, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            if res_local.stdout.strip():
                for line in res_local.stdout.strip().split('\n'):
                    partes = line.strip().split(maxsplit=1)
                    if len(partes) == 2:
                        tamanho_hr = format_size(partes[0])
                        caminho = partes[1]
                        tee(f"     - [Local] {caminho} ({tamanho_hr})")
                    else:
                        tee(f"     - {line.strip()}")
            else: tee("     (Nenhum)")

            # --- VARREDURA NA NUVEM ---
            tee("\n☁️  NA NUVEM (Remoto):")
            cmd_remote = ["rclone", "ls", f"{acc['REMOTE_NAME']}:", f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res_remote = subprocess.run(cmd_remote, capture_output=True, text=True, encoding="utf-8", errors="replace")
            
            if res_remote.returncode != 0:
                tee(f"     (Erro: Não foi possível conectar à nuvem '{acc['REMOTE_NAME']}')")
            elif res_remote.stdout.strip():
                for line in res_remote.stdout.strip().split('\n'):
                    partes = line.strip().split(maxsplit=1)
                    if len(partes) == 2:
                        tamanho_hr = format_size(partes[0])
                        caminho = partes[1]
                        tee(f"     - [Nuvem] {caminho} ({tamanho_hr})")
                    else:
                        tee(f"     - {line.strip()}")
            else: tee("     (Nenhum)")

            tee("\n" + "-" * 45)
            
    print(f"\n📂 Relatórios isolados salvos na pasta: {report_dir}")
    pause()

# ==========================================
# NÚCLEO DE SINCRONIZAÇÃO
# ==========================================
def run_sync(local_dir, remote_name, filter_file, bw_limit, max_size, report_dir, profile_name):
    cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
    safe_profile = "".join([c for c in profile_name.lower().replace(" ", "_") if c.isalnum() or c=='_'])
    log_file = os.path.normpath(os.path.join(report_dir, f"{safe_profile}_ultimo_ciclo_auto.txt"))
    
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("="*45 + f"\n🚀 RELATÓRIO DE SINCRONIZAÇÃO AUTOMÁTICA ({profile_name})\nData/Hora de Início: {agora}\n" + "="*45 + "\n\n")
    
    cmd = ["rclone", "bisync", local_dir, f"{remote_name}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", f"--log-file={log_file}"]
    if bw_limit != "0": cmd.append(f"--bwlimit={bw_limit}")
    if max_size != "0": cmd.append(f"--max-size={max_size}")

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=cflags)
    with open(log_file, "r", encoding="utf-8") as f: log_text = f.read()
    
    if result.returncode != 0 and "prior lock file found" in log_text.lower():
        lock_match = re.search(r'prior lock file found:\s*([^\r\n]+)', log_text, re.IGNORECASE)
        if lock_match:
            subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=cflags)
            
            agora_retry = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("="*45 + f"\n🚀 RELATÓRIO DE SINCRONIZAÇÃO AUTOMÁTICA ({profile_name})\nData/Hora de Início: {agora_retry} (Repetição pós-cadeado)\n" + "="*45 + "\n\n")
                
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
        agora_resync = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("="*45 + f"\n🚀 RELATÓRIO (VARREDURA DE CURA) ({profile_name})\nData/Hora de Início: {agora_resync}\n" + "="*45 + "\n\n")
            
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
    print("="*45 + "\n🚀 SINCRONIZAÇÃO IMEDIATA E REPARO (NOW)\n" + "="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: print("\nNenhuma conta configurada."); pause(); return

    report_dir = os.path.normpath(get_report_dir(config))
    sync_realizada = False

    for acc in ACCOUNTS:
        print(f"\n🔄 Conta atual: {acc['PROFILE_NAME']}")
        local_dir = os.path.expanduser(acc["LOCAL_DIR"])
        os.makedirs(local_dir, exist_ok=True)
        
        if check_name_issues_silent(local_dir, acc.get("IGNORE_PATTERNS", [])):
            print("\n🚨 ALERTA: Conflitos de Case-Sensitivity ou Caracteres Inválidos detectados!")
            resp = input("Deseja ignorar o risco de perda de dados? (S/N) [N]: ").strip().lower()
            if resp != 's':
                print("Sincronização abortada para a conta atual. Execute o Menu 9 para corrigir.")
                continue

        print("\n  [1] Sincronização Normal (Segura)")
        print("  [2] ⚠️  FORÇAR Sincronização (--force)")
        
        escolha = input("\nAção (1-2) [Enter = Pular]: ").strip()
        if escolha == '': continue

        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        MANUAL_SYNC_REPORT_FILE = os.path.normpath(os.path.join(report_dir, f"{safe_name}_ultima_sincronizacao_manual.txt"))
            
        # O cabeçalho só é criado/sobrescrito se a conta não for pulada
        if not sync_realizada:
            agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
            with open(MANUAL_SYNC_REPORT_FILE, "w", encoding="utf-8") as f:
                f.write("="*45 + f"\n🚀 RELATÓRIO DE SINCRONIZAÇÃO MANUAL ({acc['PROFILE_NAME']})\nData/Hora de Início: {agora}\n" + "="*45 + "\n\n")
            sync_realizada = True
            
        db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
        db_connection = init_db(db_path)
        scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
        try:
            scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
        except RuntimeError as e:
            print(f"❌ Erro de conexão com {acc['REMOTE_NAME']}.")
            print(f"   {e}")
            print("   Sincronização abortada por segurança.")
            continue            
        generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
        db_connection.close()

        cmd = ["rclone", "bisync", local_dir, f"{acc['REMOTE_NAME']}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-P", "-v", f"--log-file={MANUAL_SYNC_REPORT_FILE}"]
        max_size = acc.get("MAX_SIZE", "0")
        if max_size != "0": cmd.append(f"--max-size={max_size}")
        
        modo_str = "FORÇADA (--force)" if escolha == '2' else "NORMAL (Segura)"
        if escolha == '2': cmd.append("--force")
        
        with open(MANUAL_SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- Modo: {modo_str} ---\n")
        logger.info(f"[{acc['PROFILE_NAME']}] Sincronização manual disparada pelo usuário. Modo: {modo_str}")
        
        subprocess.run(cmd)
        
        with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()
        if "prior lock file found" in log_text.lower():
            lock_match = re.search(r'prior lock file found:\s*([^\r\n]+)', log_text, re.IGNORECASE)
            if lock_match:
                print(f"\n⚠️  Quebrando cadeado automaticamente...")
                logger.warning(f"[{acc['PROFILE_NAME']}] Quebrando cadeado (lock file) na sincronização manual.")
                subprocess.run(["rclone", "deletefile", lock_match.group(1).strip()])
                subprocess.run(cmd)
                with open(MANUAL_SYNC_REPORT_FILE, "r", encoding="utf-8") as f_log: log_text = f_log.read()

        if "resync" in log_text.lower() or "not found" in log_text.lower():
            print(f"\n⚠️ Acionando varredura de cura (--resync)...")
            logger.warning(f"[{acc['PROFILE_NAME']}] Acionando varredura de cura (--resync) na sincronização manual.")
            cmd.append("--resync"); subprocess.run(cmd)
            
        clean_log_file(MANUAL_SYNC_REPORT_FILE)
        print(f"\n✅ Concluído: {acc['PROFILE_NAME']}")
        logger.info(f"[{acc['PROFILE_NAME']}] Sincronização manual concluída com sucesso.")
    
    # A MENSAGEM FINAL FICA AQUI INTACTA:
    if sync_realizada:
        print(f"\n📂 Relatórios isolados salvos na pasta: {report_dir}")
    else:
        print("\nNenhuma sincronização foi executada.")
    pause()

def run_update():
    import time
    clear_screen()
    print("="*45 + "\n🔄 VERIFICADOR DE ATUALIZAÇÕES\n" + "="*45)
    print(f"Versão local:  {VERSION}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        # Drible do Cache do GitHub: Adiciona um timestamp na URL para forçar o download da versão mais recente
        cache_buster = int(time.time())
        url_no_cache = f"{UPDATE_URL_RAW}?t={cache_buster}"
        
        req = urllib.request.Request(url_no_cache, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            content = response.read().decode('utf-8')
            
            # Regex blindado: aceita espaços antes/depois, aspas simples/duplas e ignora case
            match = re.search(r'(?im)^[ \t]*VERSION\s*=\s*["\']([^"\']+)["\']', content)
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
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "_core_install.ps1"], cwd=extract_dir)
        else:
            subprocess.run(["bash", "install-linux.sh"], cwd=extract_dir)
            
        shutil.rmtree(tmp_dir)
        print("\n✅ Atualização concluída com sucesso!"); pause()
    except Exception as e:
        print(f"\n❌ Erro durante o processo de atualização: {e}"); pause()

def run_doctor(config):
    print("="*45 + "\n🩺 DIAGNÓSTICO DO SISTEMA\n" + "="*45)
    
    print("[Dependências Base]")
    res = subprocess.run(["rclone", "version"], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"🟢 Rclone: Suportado ({res.stdout.splitlines()[0]})")
    else:
        print("🔴 Rclone: Ausente! Instale o rclone e adicione ao PATH.")
    
    print("\n[Recursos do Sistema Operacional]")
    sync_os.run_doctor_os()
    
    print("\n[Diretórios Vitais]")
    config_dir = os.path.normpath(os.path.expanduser("~/.config/sync_engine"))
    if os.path.exists(config_dir):
        print(f"🟢 Cofre de Configurações: {config_dir}")
    else:
        print(f"🔴 Cofre de Configurações: Ausente")
        
    # NOVIDADE: Checagem da pasta de relatórios
    report_dir = os.path.normpath(get_report_dir(config))
    if os.path.exists(report_dir):
        print(f"🟢 Pasta de Relatórios: {report_dir}")
    else:
        print(f"🔴 Pasta de Relatórios: Ausente (será criada no 1º ciclo)")
    
    print("="*45)
    input("\nPressione Enter para voltar...")

def run_uninstall():
    clear_screen()
    print("="*45 + "\n🧨 DESINSTALAÇÃO DO MOTOR SYNC ENGINE\n" + "="*45)
    print("Esta ação irá desligar os serviços e remover o aplicativo")
    print("definitivamente do seu sistema.")
    
    # Geração do CAPTCHA
    desafio = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(f"\nPara confirmar, digite exatamente o código abaixo:")
    print(f"👉 Código: {desafio}")
    
    confirma = input("\nSua resposta [Enter p/ cancelar]: ").strip()
    if confirma != desafio:
        print("\n❌ Código incorreto. Operação cancelada.")
        pause()
        return
        
    print("\n" + "-"*45)
    print("Deseja apagar também as configurações, bancos de dados")
    print("e relatórios salvos?")
    apagar_dados = input("(S/N) [N]: ").strip().lower() == 's'
    
    print("\n⏳ Parando serviço invisível...")
    manage_service("stop", LOG_FILE)
    
    print("⏳ Preparando script de auto-destruição...")
    
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
        sh_content += '\nrm -- "$0"'
        
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o777)
        
        subprocess.Popen(["nohup", "bash", sh_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
        
    print("\n✅ Desinstalação acionada com sucesso!")
    print("O motor será removido da unidade em 3 segundos.")
    print("Adeus!\n")
    sys.exit(0)

def run_config_wizard():
    while True:
        config = load_config()
        clear_screen()
        print(f"=== Assistente Sync Engine (v{VERSION}) ===\n" + "="*45)
        print("\n--- Configuração de Contas ---")
        print("1. ➕ Adicionar nova conta")
        print("2. 📋 Listar contas atuais")
        print("3. ❌ Remover uma conta")
        
        print("\n--- Configurações Globais ---")
        print("4. ⚙️  Editar Intervalo, Banda, Pastas, e Colisões")
        print("5. 🛡️  Gerenciar Filtros de Exclusão e Limites por Conta")
        
        print("\n--- Ações Extras ---")
        print("6. 🚀 Forçar Sincronização Agora")
        print("7. 🧪 Test-Drive / Simulação (Dry-Run)")
        print("8. 📊 Relatório de Arquivos Maiores que o Limite")
        print("9. 🧹 Higienizador e Verificador de Colisão")
        print("10. 🔎 Analisador de Erros de Sincronização")
        print("11. 🩺 Diagnóstico do Sistema (Doctor)")
        
        print("\n--- Motor de Segundo Plano ---")
        print("12. ▶️ Ligar Serviço")
        print("13. ⏹️ Desligar Serviço")
        print("14. ℹ️ Checar Status do Motor")
        print("15. 🔄 Atualizar Versão do Aplicativo")
        print("16. 🧨 Desinstalar o Sync Engine")
        
        print("\n[Enter] Sair\n" + "="*45)
        
        escolha = input("Opção: ").strip()
        if escolha == '': clear_screen(); print("Até logo!\n"); break
        
        elif escolha == '1':
            clear_screen()
            print("="*45 + "\n➕ ADICIONAR NOVA CONTA\n" + "="*45)
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
                "IGNORE_PATTERNS": ["venv", ".venv", "__pycache__", ".git", "Personal Vault", "Cofre Pessoal", "*.tmp", ".DS_Store", "site-packages", "Thumbs.db", "~$*"],
                "DB_FILE": f"sync_metadata_{safe_name}.db", "FILTER_FILE": f"excludes_{safe_name}.txt"
            })
            save_config(config, f"Adicionada conta '{profile}'"); manage_service("reload", LOG_FILE); print("\n✅ Salvo!"); pause()

        elif escolha == '2':
            clear_screen()
            print("="*45 + "\n📋 LISTAR CONTAS ATUAIS\n" + "="*45)
            for i, acc in enumerate(config.get("ACCOUNTS", [])): print(f"[{i+1}] {acc['PROFILE_NAME']} ({acc['LOCAL_DIR']})")
            pause()
                
        elif escolha == '3':
            clear_screen()
            print("="*45 + "\n❌ REMOVER CONTA\n" + "="*45)
            contas = config.get("ACCOUNTS", [])
            if not contas:
                print("Nenhuma conta configurada."); pause(); continue
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            op = input("\nNúmero para apagar [Enter p/ voltar]: ").strip()
            if op.isdigit() and 1 <= int(op) <= len(contas):
                apagada = contas.pop(int(op)-1)
                save_config(config, f"Removida conta '{apagada['PROFILE_NAME']}'"); manage_service("reload", LOG_FILE); print(f"\n🗑️ Removida: {apagada['PROFILE_NAME']}"); pause()
                
        elif escolha == '4':
            while True:
                clear_screen()
                print("="*45 + "\n⚙️  EDITAR INTERVALO, LIMITES E PASTAS\n" + "="*45)
                print(f"  [1] Intervalo ({config.get('SYNC_INTERVAL', 300)}s)")
                print(f"  [2] Limite de Banda ({config.get('BW_LIMIT', '0')})")
                print(f"  [3] Pasta Relatórios (Atual: {os.path.normpath(get_report_dir(config))})")
                print(f"  [4] Bloqueio Auto em Colisões de Nomes (Atual: {config.get('AUTO_CHECK_NAMES', True)})")
                
                sub_op = input("\nOpção (1-4) [Enter = Voltar]: ").strip()
                if sub_op == '': break
                elif sub_op == '1':
                    nv = input("Novo intervalo em segundos: ").strip()
                    if nv.isdigit(): config["SYNC_INTERVAL"] = int(nv); save_config(config); manage_service("reload", LOG_FILE)
                elif sub_op == '2':
                    nv = input("Novo limite (ex: 1M, 500k, 0 p/ ilimitado): ").strip()
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
                        print("="*45 + "\n📂 GERENCIADOR DE RELATÓRIOS\n" + "="*45)
                        print(f"Atual: {current_dir}\n")
                        print(" [1] 📂 Abrir pasta no Explorador/Gerenciador")
                        print(" [2] ✏️  Alterar o local de salvamento")
                        print(" [3] 🔄 Restaurar para a pasta padrão oculta")
                        
                        sub_esc = input("\nAção (1-3) [Enter = Voltar]: ").strip()
                        if sub_esc == '': break
                        elif sub_esc == '1':
                            if SISTEMA == "Windows": os.startfile(current_dir)
                            else: subprocess.run(["xdg-open", current_dir])
                        elif sub_esc == '2':
                            novo_dir = input(f"Digite o novo caminho absoluto: ").strip()
                            if novo_dir:
                                config["REPORT_DIR"] = os.path.normpath(novo_dir)
                                save_config(config)
                                print(f"✅ Pasta alterada para: {config['REPORT_DIR']}")
                                pause()
                        elif sub_esc == '3':
                            config["REPORT_DIR"] = "" 
                            save_config(config)
                            print("✅ Relatórios restaurados para o diretório padrão (~/.config/sync_engine).")
                            pause()

        elif escolha == '5':
            clear_screen()
            print("="*45 + "\n🛡️ GERENCIAR FILTROS E LIMITES POR CONTA\n" + "="*45)
            contas = config.get("ACCOUNTS", [])
            if not contas:
                print("Nenhuma conta configurada."); pause(); continue
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            op_acc = input("\nConta [Enter p/ voltar]: ").strip()
            if op_acc.isdigit() and 1 <= int(op_acc) <= len(contas):
                conta = contas[int(op_acc) - 1]
                padroes = conta.get("IGNORE_PATTERNS", [])
                tamanho_max = conta.get("MAX_SIZE", "0")
                while True:
                    clear_screen(); print(f"--- Configurações: {conta['PROFILE_NAME']} ---")
                    print(f"📦 Limite de Tamanho: {tamanho_max} (0 = Ilimitado)")
                    print("\n🛡️ Filtros de Exclusão Atuais:")
                    for j, p in enumerate(padroes): print(f"  [{j+1}] {p}")
                    
                    print("\n[T] Alterar Tamanho Máx.  [A] Adicionar Filtro  [R] Remover Filtro")
                    print("[S] Salvar e Sair         [Enter] Cancelar")
                    acao = input("Ação: ").strip().lower()
                    
                    if acao == '' or acao == 'c': break
                    elif acao == 's': 
                        conta["IGNORE_PATTERNS"] = padroes
                        conta["MAX_SIZE"] = tamanho_max
                        save_config(config, f"Filtros/Limites alterados em '{conta['PROFILE_NAME']}'")
                        manage_service("reload", LOG_FILE); break
                    elif acao == 't':
                        nv = input("\nNovo tamanho máx. (ex: 100M, 1G, 0 p/ ilimitado): ").strip()
                        if nv: tamanho_max = nv
                    elif acao == 'a': 
                        print("\n💡 DICAS AVANÇADAS DE FILTRAGEM:")
                        print("  (?i)*.tmp           -> Ignora Maiúsculas/Minúsculas (ex: log.TMP e log.tmp)")
                        print("  venv                -> Correspondência exata do nome em qualquer pasta")
                        print("  Prefixo*            -> Início do nome (ex: Backup* ignora Backup_2026)")
                        print("  *.bak               -> Curinga de extensão em qualquer nível")
                        print("  /Backups            -> Âncora de raiz (ignora só na pasta principal)")
                        print("  /.*                 -> Ignora pastas/arquivos ocultos apenas na raiz (Linux)")
                        novo = input("\nDigite o novo padrão: ").strip()
                        if novo: padroes.append(novo)
                    elif acao == 'r': 
                        num = input("Número: ").strip()
                        if num.isdigit() and 1 <= int(num) <= len(padroes): padroes.pop(int(num)-1)

        elif escolha == '6': run_now()
        elif escolha == '7': run_dry_run()
        elif escolha == '8': run_size_report()
        elif escolha == '9': run_filename_cleaner()
        elif escolha == '10': run_analyze_errors()
        elif escolha == '11': clear_screen(); run_doctor(config)
        elif escolha == '12': clear_screen(); manage_service("start", LOG_FILE); pause()
        elif escolha == '13': clear_screen(); manage_service("stop", LOG_FILE); logger.info("Motor parado manualmente pelo usuário."); pause()
        elif escolha == '14': clear_screen(); manage_service("status", LOG_FILE); pause()
        elif escolha == '15': run_update()
        elif escolha == '16': run_uninstall()

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
        comando = sys.argv[1].strip().lower()
        if comando in ["-h", "--help", "help"]: 
            print_help()
            sys.exit(0)
        elif comando in ["-v", "--version", "version"]: 
            print(f"Sync Engine v{VERSION}")
            sys.exit(0)
        elif comando == "config": run_config_wizard()
        elif comando == "now": run_now()
        elif comando == "start": manage_service("start", LOG_FILE)
        elif comando == "stop": manage_service("stop", LOG_FILE); logger.info("Motor parado via linha de comando.")
        elif comando == "status": manage_service("status", LOG_FILE)
        elif comando == "reload": manage_service("reload", LOG_FILE)
        else: 
            print(f"\n⚠️ Comando não reconhecido: '{comando}'")
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
        logger.info("Motor Sync Engine Iniciado em Background.")
        while True:
            config = load_config()
            ACCOUNTS = config.get("ACCOUNTS", [])
            if not ACCOUNTS: sys.exit(1)

            for acc in ACCOUNTS:
                profile = acc.get("PROFILE_NAME", "Local")
                local_dir = os.path.expanduser(acc["LOCAL_DIR"])
                os.makedirs(local_dir, exist_ok=True)
                
                if config.get("AUTO_CHECK_NAMES", True):
                    if check_name_issues_silent(local_dir, acc.get("IGNORE_PATTERNS", [])):
                        logger.error(f"[{profile}] Sincronização bloqueada: Colisão de nomes ou caracteres detectados.")
                        send_notification("Conflito de Nomes", f"Sincronização de '{profile}' pausada. Use a Opção 9 para corrigir.", "critical")
                        continue
                
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
                
                success, transfers, err_msg = run_sync(local_dir, acc["REMOTE_NAME"], filter_file, config.get("BW_LIMIT", "0"), acc.get("MAX_SIZE", "0"), get_report_dir(config), profile)
                
                if success and transfers:
                    logger.info(f"[{profile}] Sincronização concluída com alterações.")
                    send_notification("Sync Engine", f"Conta '{profile}' sincronizada.")
                elif not success:
                    logger.error(f"[{profile}] Erro: {err_msg}")
                else:
                    logger.info(f"[{profile}] Checagem concluída. Nenhuma alteração detectada.")
            
            time.sleep(config.get("SYNC_INTERVAL", 300))
    except Exception as e:
        logger.error(f"FALHA CRÍTICA DO MOTOR: {e}")
