#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import subprocess
import time
import fnmatch
import logging
import shutil
import urllib.request
import tempfile
import zipfile
import re
import platform
import ssl
from logging.handlers import RotatingFileHandler

# ==========================================
# ÂNCORA DE DIRETÓRIO
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)

SISTEMA = platform.system()
if SISTEMA == "Linux":
    import os_linux as sys_tools
elif SISTEMA == "Windows":
    import os_windows as sys_tools
else:
    print(f"❌ Erro crítico: O sistema '{SISTEMA}' não é suportado.")
    sys.exit(1)

VERSION = "5.6"
UPDATE_URL_RAW = "https://raw.githubusercontent.com/ocanha-almeida/sync-engine/main/sync_engine.py"
UPDATE_URL_ZIP = "https://github.com/ocanha-almeida/sync-engine/archive/refs/heads/main.zip"

CONFIG_DIR = os.path.expanduser("~/.config/sync_engine")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "sync.log")
os.makedirs(CONFIG_DIR, exist_ok=True)

logger = logging.getLogger("SyncEngine")
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)
if not logger.handlers:
    logger.addHandler(file_handler)

DEFAULT_CONFIG = {
    "_INSTRUCOES_GERAIS": "Edite este arquivo com cuidado.",
    "SYNC_INTERVAL": 300,
    "BW_LIMIT": "0",
    "MAX_SIZE": "0",
    "REPORT_DIR": "",
    "AUTO_CHECK_NAMES": True,
    "ACCOUNTS": []
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if "AUTO_CHECK_NAMES" not in cfg: cfg["AUTO_CHECK_NAMES"] = True
            return cfg
    except json.JSONDecodeError:
        return DEFAULT_CONFIG

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def get_report_dir(config):
    custom_dir = config.get("REPORT_DIR", "").strip()
    if custom_dir:
        expanded = os.path.expanduser(custom_dir)
        try:
            os.makedirs(expanded, exist_ok=True)
            return expanded
        except OSError:
            return CONFIG_DIR
    return CONFIG_DIR

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPressione Enter para continuar...")

def clean_log_text(text):
    cleaned = []
    skip = False
    for line in text.split('\n'):
        if "Bisyncing with Comparison Settings" in line or "Lockfile info" in line:
            skip = True; continue
        if skip and line.strip() == "}":
            skip = False; continue
        if skip: continue
        if "Setting --ignore-listing-checksum" in line: continue
        if "Valid lock file found" in line: continue
        cleaned.append(line)
    return "\n".join(cleaned)

def clean_log_file(file_path):
    try:
        if not os.path.exists(file_path): return
        with open(file_path, "r", encoding="utf-8") as f: text = f.read()
        text = re.sub(r'Bisyncing with Comparison Settings:\s*\{.*?\}', '', text, flags=re.DOTALL)
        text = re.sub(r'Lockfile info:\s*\{.*?\}', '', text, flags=re.DOTALL)
        cleaned = []
        for line in text.split('\n'):
            if "Setting --ignore-listing-checksum" in line: continue
            if "Valid lock file found" in line: continue
            if line.strip() == "" and not cleaned: continue
            cleaned.append(line)
        final_text = re.sub(r'\n{3,}', '\n\n', "\n".join(cleaned))
        with open(file_path, "w", encoding="utf-8") as f: f.write(final_text)
    except Exception: pass

def run_doctor():
    clear_screen()
    print("=== 🩺 Médico do Sistema (Doctor) ===")
    print("Verificando a saúde do ambiente para o Sync Engine...\n")
    if shutil.which("rclone"): print("🟢 Rclone: Instalado e pronto.")
    else: print("🔴 Rclone: NÃO ENCONTRADO! Instale antes de continuar.")
    try:
        sqlite3.connect(":memory:").close()
        print("🟢 SQLite3: Motor de banco de dados nativo funcionando.")
    except Exception: print("🔴 SQLite3: Falha no módulo interno do Python!")
    sys_tools.run_doctor_os(CONFIG_DIR)
    print("\n✅ Diagnóstico concluído.")
    pause()

def run_update():
    clear_screen()
    print("="*45)
    print("🔄 VERIFICADOR DE ATUALIZAÇÕES")
    print("="*45)
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
        sys_tools.run_update_installer(os.path.join(tmp_dir, "sync-engine-main"))
        shutil.rmtree(tmp_dir)
        pause()
    except Exception as e:
        print(f"\n❌ Erro durante o processo de atualização: {e}"); pause()

# --- RADAR DE COLISÃO SILENCIOSO ---
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
    print("="*45)
    print("🧹 HIGIENIZADOR E RADAR DE COLISÃO")
    print("="*45)
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])

    print("Escolha o diretório alvo para a análise:")
    print("[0] Digitar um caminho manual personalizado")
    for i, acc in enumerate(ACCOUNTS): print(f"[{i+1}] Conta '{acc['PROFILE_NAME']}' ({acc['LOCAL_DIR']})")
    
    op = input("\nOpção (Enter para cancelar): ").strip().lower()
    if op == '' or op == 'c': return

    ignore_patterns = []
    if op == '0': alvo = input("\nDigite o caminho da pasta: ").strip()
    elif op.isdigit() and 1 <= int(op) <= len(ACCOUNTS):
        conta = ACCOUNTS[int(op)-1]
        alvo, ignore_patterns = conta["LOCAL_DIR"], conta.get("IGNORE_PATTERNS", [])
    else: return

    if not alvo: return
    alvo_expandido = os.path.expanduser(alvo)
    if not os.path.isdir(alvo_expandido):
        print(f"\n❌ Erro: O diretório '{alvo_expandido}' não existe."); pause(); return

    print("\n🔍 Analisando diretório... Aguarde.\n")
    substituicoes = {"‛‛": "", "‛": "'", "＂": "", "｜": "-", "⧸": "-", "：": "-", "？": "", "＊": "", "★": "", "✬": "", "☆": ""}
    arquivos_para_renomear = []
    colisoes_case = []
    
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
            if nome_lower in vistos_nesta_pasta:
                colisoes_case.append((root, vistos_nesta_pasta[nome_lower], nome))
            else:
                vistos_nesta_pasta[nome_lower] = nome

            novo_nome = nome
            for ruim, bom in substituicoes.items(): novo_nome = novo_nome.replace(ruim, bom)
            while "  " in novo_nome: novo_nome = novo_nome.replace("  ", " ")
            novo_nome = novo_nome.replace(" .", ".")

            if novo_nome != nome:
                arquivos_para_renomear.append((os.path.join(root, nome), os.path.join(root, novo_nome), nome, novo_nome))

    if colisoes_case:
        print("🚨 ALERTA CRÍTICO: COLISÃO DE NOMES DETECTADA! 🚨")
        print("Sistemas Windows e Nuvens podem corromper estes arquivos devido a nomes idênticos diferindo apenas por letras maiúsculas/minúsculas:\n")
        for pasta, arq1, arq2 in colisoes_case:
            print(f" 📁 Pasta: {pasta}\n    ❌ {arq1}\n    ❌ {arq2}\n")
        print("⚠️  AÇÃO RECOMENDADA: Renomeie um destes arquivos manualmente antes de sincronizar.\n")

    if not arquivos_para_renomear:
        print("✨ Nomes de arquivos limpos! Nenhum caractere inválido encontrado.")
        pause(); return

    print(f"⚠️ Encontrados {len(arquivos_para_renomear)} arquivos com caracteres inválidos.\n")
    print("--- PRÉ-VISUALIZAÇÃO ---")
    for caminho_antigo, _, nome, novo_nome in arquivos_para_renomear[:10]:
        print(f" 📁 Em:   {os.path.dirname(caminho_antigo)}\n    De:   {nome}\n    Para: {novo_nome}\n")
    
    confirma = input(f"Confirma a alteração destes {len(arquivos_para_renomear)} arquivos? (S/N) [N]: ").strip().lower()
    if confirma != 's': print("\nOperação cancelada."); pause(); return

    renomeados = 0
    for caminho_antigo, caminho_novo, nome, novo_nome in arquivos_para_renomear:
        try: os.rename(caminho_antigo, caminho_novo); renomeados += 1
        except Exception: pass
    print(f"\n🎉 Concluído! {renomeados} arquivos foram higienizados."); pause()

def run_analyze_errors():
    clear_screen()
    print("="*45 + "\n🔎 ANALISADOR DE ERROS DE SINCRONIZAÇÃO\n" + "="*45)
    config = load_config()
    report_dir = get_report_dir(config)
    logs_disponiveis = []
    manual_log = os.path.join(report_dir, "ultima_sincronizacao_manual.txt")
    if os.path.exists(manual_log): logs_disponiveis.append(("Sincronização Manual", manual_log))
        
    for acc in config.get("ACCOUNTS", []):
        safe_name = "".join([c for c in acc['PROFILE_NAME'].lower().replace(" ", "_") if c.isalnum() or c=='_'])
        auto_log = os.path.join(report_dir, f"ultimo_ciclo_auto_{safe_name}.txt")
        if os.path.exists(auto_log): logs_disponiveis.append((f"Ciclo Automático: {acc['PROFILE_NAME']}", auto_log))
            
    if not logs_disponiveis: print("\n❌ Nenhum relatório encontrado."); pause(); return

    print("\nEscolha qual relatório analisar:\n")
    for i, (nome, _) in enumerate(logs_disponiveis): print(f"  [{i+1}] {nome}")
    
    op = input("\nOpção (Enter para cancelar): ").strip().lower()
    if op == '' or op == 'c': return
    if not (op.isdigit() and 1 <= int(op) <= len(logs_disponiveis)): return
        
    sync_report = logs_disponiveis[int(op)-1][1]
    
    total_errors, lstat_errors, etag_errors, resync_requests, lock_errors, other_errors = 0, 0, 0, 0, 0, 0

    with open(sync_report, "r", encoding="utf-8") as f:
        for line in f:
            line_lower = line.lower()
            if "error :" in line_lower or "failed to" in line_lower or "critical error" in line_lower or "prior lock file found" in line_lower:
                total_errors += 1
                if "lstat" in line_lower and "no such file or directory" in line_lower: lstat_errors += 1
                elif "409 conflict" in line_lower or "etag mismatch" in line_lower: etag_errors += 1
                elif "cannot find prior path1 or path2 listings" in line_lower: resync_requests += 1
                elif "prior lock file found" in line_lower: lock_errors += 1
                else: other_errors += 1

    if total_errors == 0: print("\n✨ Excelente! Seu ecossistema está saudável.")
    else:
        print(f"\n⚠️ Encontrados {total_errors} indícios de problemas:\n")
        if lock_errors > 0: print(f"🔹 {lock_errors}x 'Cadeado Trancado' (Lock File): O motor já deve ter quebrado o cadeado automaticamente.")
        if lstat_errors > 0: print(f"🔹 {lstat_errors}x 'Arquivo não encontrado' (lstat): Use a Opção 9 para higienizar nomes de arquivos.")
        if etag_errors > 0: print(f"🔹 {etag_errors}x 'Conflito de eTag': Erro passageiro de ansiedade da nuvem. Será curado sozinho.")
        if resync_requests > 0: print(f"🔹 {resync_requests}x 'Varredura de Cura': O histórico quebrou, o motor já iniciou o reparo.")
    pause()

def analyze_sync_logic(log_text):
    # Removido "Applying changes" para evitar falsos positivos no Linux
    mudancas = ["Copied (", "Deleted:", "Moved (", "Updated:"]
    has_changes = any(m in log_text for m in mudancas)
    if "resync is required" in log_text.lower() or "resyncing" in log_text.lower():
        has_changes = True
    errors = [line for line in log_text.split('\n') if "ERROR" in line]
    err_msg = errors[0].split("ERROR :")[-1].strip() if errors else "Verifique o log detalhado."
    return has_changes, err_msg

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
        
        # O Radar Automático atua aqui no comando manual também!
        if check_name_issues_silent(local_dir, acc.get("IGNORE_PATTERNS", [])):
            print("\n🚨 ALERTA: Foram detectados conflitos de Case-Sensitivity ou Caracteres Inválidos nesta pasta!")
            resp = input("Deseja continuar ignorando os riscos de perda de dados? (S/N) [N]: ").strip().lower()
            if resp != 's':
                print("Sincronização abortada para a conta atual. Execute o Menu 9 para corrigir.")
                continue

        print("\n  [1] Sincronização Normal (Segura)")
        print("  [2] ⚠️  FORÇAR Sincronização (--force)")
        print("  [3] Pular esta conta")
        
        escolha = input("\nAção (1-3) [Enter = Pular]: ").strip()
        if escolha == '' or escolha == '3': continue
            
        db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
        
        db_connection = init_db(db_path)
        scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
        scan_remote(db_connection, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
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

def run_dry_run():
    clear_screen()
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS: return
    
    report_dir = get_report_dir(config)
    DRY_RUN_REPORT_FILE = os.path.join(report_dir, "ultimo_dry_run.txt")
    
    with open(DRY_RUN_REPORT_FILE, "w", encoding="utf-8") as rep_file:
        def tee(msg=""): print(msg); rep_file.write(msg + "\n")
        tee("="*45 + "\n🧪 RELATÓRIO DE TEST-DRIVE (DRY-RUN)\n" + "="*45)

        for acc in ACCOUNTS:
            tee(f"\n🚀 Testando: {acc['PROFILE_NAME']}")
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
    print(f"\n📂 Salvo em: {DRY_RUN_REPORT_FILE}"); pause()

def run_size_report():
    clear_screen()
    config = load_config()
    if not config.get("ACCOUNTS", []): return
    max_size = config.get("MAX_SIZE", "0")
    if max_size == "0": print("Nenhum limite de tamanho configurado."); pause(); return

    SIZE_REPORT_FILE = os.path.join(get_report_dir(config), "ultimo_relatorio_tamanho.txt")
    with open(SIZE_REPORT_FILE, "w", encoding="utf-8") as rep_file:
        def tee(msg=""): print(msg); rep_file.write(msg + "\n")
        tee("="*45 + "\n📊 ARQUIVOS BLOQUEADOS POR TAMANHO\n" + "="*45)

        for acc in config["ACCOUNTS"]:
            tee(f"\n🔄 Conta: {acc['PROFILE_NAME']}")
            filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            cmd_local = ["rclone", "ls", os.path.expanduser(acc["LOCAL_DIR"]), f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res = subprocess.run(cmd_local, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res.stdout.strip():
                for line in res.stdout.strip().split('\n'): tee(f"     - {line.strip()}")
            else: tee("     (Nenhum)")
            tee("-" * 45)
    pause()

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
        print("7. 🧪 Test-Drive / Simulação (Dry-Run)")
        print("8. 📊 Relatório de Arquivos Maiores que o Limite")
        print("9. 🧹 Higienizador e Verificador de Colisão")
        print("10. 🔎 Analisador de Erros de Sincronização")
        print("11. 🩺 Diagnóstico do Sistema (Doctor)")
        
        print("\n--- Motor de Segundo Plano ---")
        print("12. ▶️ Ligar Serviço Invisível")
        print("13. ⏹️ Desligar Serviço Invisível")
        print("14. ℹ️ Checar Status e Logs do Motor")
        print("15. 🔄 Atualizar Versão do Aplicativo")
        
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
            save_config(config); sys_tools.manage_service("reload", LOG_FILE); print("\n✅ Salvo!"); pause()

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
                save_config(config); sys_tools.manage_service("reload", LOG_FILE); print(f"\n🗑️ Removida: {apagada['PROFILE_NAME']}"); pause()
                
        elif escolha == '4':
            while True:
                clear_screen(); print("--- Configurações Globais ---")
                print(f"1. Intervalo ({config.get('SYNC_INTERVAL', 300)}s)")
                print(f"2. Banda ({config.get('BW_LIMIT', '0')})")
                print(f"3. Max Size ({config.get('MAX_SIZE', '0')})")
                print(f"4. Pasta Relatórios")
                print(f"5. Bloqueio Auto em Colisões de Nomes (Atual: {config.get('AUTO_CHECK_NAMES', True)})")
                
                op_cfg = input("\nOpção [Enter p/ voltar]: ").strip()
                if not op_cfg: break
                elif op_cfg == '1': config["SYNC_INTERVAL"] = int(input("Segundos: ") or 300)
                elif op_cfg == '2': config["BW_LIMIT"] = input("Limite (ex: 10M, 0): ").strip()
                elif op_cfg == '3': config["MAX_SIZE"] = input("Max (ex: 1G, 0): ").strip()
                elif op_cfg == '4': config["REPORT_DIR"] = input("Caminho: ").strip()
                elif op_cfg == '5': config["AUTO_CHECK_NAMES"] = not config.get('AUTO_CHECK_NAMES', True)
                save_config(config); sys_tools.manage_service("reload", LOG_FILE)

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
                    elif acao == 's': conta["IGNORE_PATTERNS"] = padroes; save_config(config); sys_tools.manage_service("reload", LOG_FILE); break
                    elif acao == 'a': novo = input("Padrão: ").strip(); padroes.append(novo) if novo else None
                    elif acao == 'r': 
                        num = input("Número: ").strip()
                        if num.isdigit() and 1 <= int(num) <= len(padroes): padroes.pop(int(num)-1)

        elif escolha == '6': run_now()
        elif escolha == '7': run_dry_run()
        elif escolha == '8': run_size_report()
        elif escolha == '9': run_filename_cleaner()
        elif escolha == '10': run_analyze_errors()
        elif escolha == '11': run_doctor()
        elif escolha == '12': clear_screen(); sys_tools.manage_service("start", LOG_FILE); pause()
        elif escolha == '13': clear_screen(); sys_tools.manage_service("stop", LOG_FILE); pause()
        elif escolha == '14': clear_screen(); sys_tools.manage_service("status", LOG_FILE); pause()
        elif escolha == '15': run_update()

# ==========================================
# PROCESSAMENTO DE BACKGROUND E METADADOS
# ==========================================
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS metadata")
    cursor.execute("CREATE TABLE metadata (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, path TEXT NOT NULL, parent_dir TEXT NOT NULL, is_dir BOOLEAN NOT NULL, size INTEGER, mod_time TEXT, has_nosync BOOLEAN DEFAULT 0)")
    cursor.execute("CREATE INDEX idx_path ON metadata(path)")
    cursor.execute("CREATE INDEX idx_parent ON metadata(parent_dir)")
    conn.commit()
    return conn

def scan_local(conn, local_dir, ignore_patterns):
    records = []
    def fast_scan(current_path, parent_rel=""):
        try:
            with os.scandir(current_path) as it:
                entries = list(it)
                has_nosync = any(e.name == '.nosync' for e in entries)
                for entry in entries:
                    rel_path = (os.path.join(parent_rel, entry.name) if parent_rel else entry.name).replace("\\", "/")
                    if entry.name == '.nosync': records.append(('local', rel_path, parent_rel.replace("\\", "/"), False, 0, '', True)); continue
                    if has_nosync: continue
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            records.append(('local', rel_path, parent_rel.replace("\\", "/"), True, 0, '', False))
                            fast_scan(entry.path, rel_path)
                        else:
                            stat = entry.stat(follow_symlinks=False)
                            records.append(('local', rel_path, parent_rel.replace("\\", "/"), False, stat.st_size, str(stat.st_mtime), False))
                    except OSError: pass
        except OSError: pass
    fast_scan(local_dir)
    conn.executemany("INSERT INTO metadata (source, path, parent_dir, is_dir, size, mod_time, has_nosync) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
    conn.commit()

def scan_remote(conn, remote_name, ignore_patterns):
    records = []
    cmd = ["rclone", "lsjson", f"{remote_name}:", "--fast-list", "--recursive"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.stdout.strip():
            for item in json.loads(result.stdout):
                path = item.get("Path", "")
                parts = path.split("/")
                parent_dir = "/".join(parts[:-1]) if len(parts) > 1 else ""
                records.append(('remote', path, parent_dir, item.get("IsDir", False), item.get("Size", 0), item.get("ModTime", ""), (parts[-1] == '.nosync')))
            conn.executemany("INSERT INTO metadata (source, path, parent_dir, is_dir, size, mod_time, has_nosync) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()
    except Exception: pass

def generate_filters(conn, filter_file, ignore_patterns):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT parent_dir FROM metadata WHERE has_nosync = 1 UNION SELECT DISTINCT parent_dir FROM metadata WHERE path LIKE '%/.nosync' OR path = '.nosync'")
    filters = []
    for p in ignore_patterns:
        p_clean = p.replace("\\", "/")
        filters.extend([f"- {p_clean}", f"- {p_clean}/**", f"- {p_clean}/"])
    for (folder,) in cursor.fetchall():
        clean_folder = folder.replace("\\", "/").strip("/")
        if clean_folder: filters.extend([f"- /{clean_folder}/", f"- /{clean_folder}/**"])
    with open(filter_file, "w", encoding="utf-8") as f:
        for line in filters: f.write(line + "\n")
        
def run_sync(local_dir, remote_name, filter_file, bw_limit, max_size, report_dir, profile_name):
    safe_profile = "".join([c for c in profile_name.lower().replace(" ", "_") if c.isalnum() or c=='_'])
    log_file = os.path.join(report_dir, f"ultimo_ciclo_auto_{safe_profile}.txt")
    
    cmd = ["rclone", "bisync", local_dir, f"{remote_name}:", f"--filter-from={filter_file}", "--create-empty-src-dirs", "--fix-case", "-v", f"--log-file={log_file}"]
    
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
        errors = [line for line in log_text.split('\n') if "ERROR" in line]
        return False, False, errors[0].split("ERROR :")[-1].strip() if errors else "Erro fatal."

def print_help():
    print(f"\n=== Sync Engine Multi-Contas (v{VERSION}) ===")
    print("Uso: sync-engine [COMANDO]")
    print("  config         Assistente interativo (Contas, Filtros, Limites).")
    print("  now            🚀 Sincroniza AGORA (força o envio/download).")
    print("  start/stop     Liga/Desliga o serviço invisível.")
    print("  status/reload  Checa logs ou reinicia o serviço invisível.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        if comando == "config": run_config_wizard()
        elif comando == "now": run_now()
        elif comando == "start": sys_tools.manage_service("start", LOG_FILE)
        elif comando == "stop": sys_tools.manage_service("stop", LOG_FILE)
        elif comando == "status": sys_tools.manage_service("status", LOG_FILE)
        elif comando == "reload": sys_tools.manage_service("reload", LOG_FILE)
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
                
                # Radar Automático Antes de Sincronizar (Gatilho Silencioso)
                if config.get("AUTO_CHECK_NAMES", True):
                    if check_name_issues_silent(local_dir, acc.get("IGNORE_PATTERNS", [])):
                        logger.error(f"[{profile}] Sincronização bloqueada: Colisão de nomes ou caracteres detectados.")
                        sys_tools.send_notification("Conflito de Nomes", f"A sincronização de '{profile}' foi pausada. Use a Opção 9 para corrigir.", "critical")
                        continue # Pula a sincronização para salvar a nuvem de danos
                
                db_path, filter_file = os.path.join(CONFIG_DIR, acc["DB_FILE"]), os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
                db_conn = init_db(db_path)
                scan_local(db_conn, local_dir, acc.get("IGNORE_PATTERNS", []))
                scan_remote(db_conn, acc["REMOTE_NAME"], acc.get("IGNORE_PATTERNS", []))
                generate_filters(db_conn, filter_file, acc.get("IGNORE_PATTERNS", []))
                db_conn.close()
                
                success, transfers, err_msg = run_sync(local_dir, acc["REMOTE_NAME"], filter_file, config.get("BW_LIMIT", "0"), config.get("MAX_SIZE", "0"), get_report_dir(config), profile)
                
                if success and transfers:
                    logger.info(f"[{profile}] Sincronização concluída com alterações.")
                    sys_tools.send_notification("Sync Engine", f"Conta '{profile}' sincronizada.")
                elif not success:
                    logger.error(f"[{profile}] Erro: {err_msg}")
            
            time.sleep(config.get("SYNC_INTERVAL", 300))
    except Exception as e:
        logger.error(f"FALHA CRÍTICA DO MOTOR: {e}")