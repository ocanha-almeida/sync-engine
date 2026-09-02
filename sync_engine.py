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
from logging.handlers import RotatingFileHandler

# ==========================================
# DIRETÓRIOS E LOGS XDG
# ==========================================
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
    "ACCOUNTS": []
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Erro: config.json corrompido. Usando padrões de fábrica.")
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

# ==========================================
# UTILITÁRIOS DE TELA E DIAGNÓSTICO
# ==========================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPressione Enter para continuar...")

def run_doctor():
    clear_screen()
    print("=== 🩺 Médico do Sistema (Doctor) ===")
    print("Verificando a saúde do ambiente para o Sync Engine...\n")

    if shutil.which("rclone"): print("🟢 Rclone: Instalado e pronto.")
    else: print("🔴 Rclone: NÃO ENCONTRADO! Instale antes de continuar.")

    if shutil.which("systemctl"): print("🟢 Systemd: Disponível (Auto-start suportado).")
    else: print("🔴 Systemd: NÃO ENCONTRADO! (O motor de fundo não funcionará).")

    if shutil.which("notify-send"): print("🟢 Notificações (libnotify): Instalado.")
    else: print("🟡 Notificações: Ausente (Instale 'libnotify-bin' se quiser alertas).")

    try:
        sqlite3.connect(":memory:").close()
        print("🟢 SQLite3: Motor de banco de dados nativo funcionando.")
    except Exception:
        print("🔴 SQLite3: Falha no módulo interno do Python!")

    if os.access(CONFIG_DIR, os.W_OK): print("🟢 Permissões: Acesso total à pasta de configurações.")
    else: print("🔴 Permissões: Sem acesso de escrita na pasta ~/.config!")

    print("\n✅ Diagnóstico concluído.")
    pause()

# ==========================================
# GERENCIADOR DE SERVIÇOS E AÇÕES IMEDIATAS
# ==========================================
def manage_service(action):
    SERVICE = "sync-engine.service"
    try:
        if action == "start":
            print("\n⚙️ Ligando e ativando o Motor em segundo plano...")
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
            subprocess.run(["systemctl", "--user", "enable", "--now", SERVICE], check=False)
            print("✅ Sucesso! O motor agora está rodando de forma invisível.")
        elif action == "stop":
            print("\n🛑 Desligando e desinstalando o Motor deste usuário...")
            subprocess.run(["systemctl", "--user", "disable", "--now", SERVICE], check=False)
            print("✅ Sucesso! O motor foi parado.")
        elif action == "status":
            print(f"\n📊 Status do Serviço ({SERVICE}):\n")
            subprocess.run(["systemctl", "--user", "status", SERVICE, "--no-pager"])
            print(f"\n📝 Últimos registros de Log ({LOG_FILE}):")
            subprocess.run(["tail", "-n", "10", LOG_FILE])
        elif action == "reload":
            check = subprocess.run(["systemctl", "--user", "is-active", SERVICE], capture_output=True, text=True)
            if check.stdout.strip() == "active":
                print("🔄 Serviço detectado. Reiniciando automaticamente...")
                subprocess.run(["systemctl", "--user", "restart", SERVICE], check=False)
    except Exception as e:
        print(f"Erro ao interagir com o sistema: {e}")

def run_now():
    clear_screen()
    print("="*45)
    print("🚀 SINCRONIZAÇÃO IMEDIATA E REPARO (NOW)")
    print("="*45)
    
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    if not ACCOUNTS:
        print("\nNenhuma conta configurada para sincronizar.")
        return

    bw_limit = config.get("BW_LIMIT", "0")
    max_size = config.get("MAX_SIZE", "0")
    
    report_dir = get_report_dir(config)
    MANUAL_SYNC_REPORT_FILE = os.path.join(report_dir, "ultima_sincronizacao_manual.txt")

    with open(MANUAL_SYNC_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("="*45 + "\n")
        f.write("🚀 RELATÓRIO DE SINCRONIZAÇÃO MANUAL\n")
        f.write(f"Data gerada: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*45 + "\n\n")

    for acc in ACCOUNTS:
        print(f"\n🔄 Conta atual: {acc['PROFILE_NAME']}")
        print("  [1] Sincronização Normal (Segura)")
        print("  [2] ⚠️  FORÇAR Sincronização (--force) -> Libera exclusão em massa (>50%)")
        print("  [3] Pular esta conta")
        
        escolha = input("\nEscolha a ação para esta conta (1-3): ").strip()
        if escolha == '3': 
            with open(MANUAL_SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
                f.write(f"⏭️ Conta '{acc['PROFILE_NAME']}' pulada pelo usuário.\n\n")
            continue
            
        with open(MANUAL_SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
            modo = 'FORÇADA' if escolha == '2' else 'NORMAL'
            f.write(f"🔄 Iniciando conta: {acc['PROFILE_NAME']} (Modo: {modo})\n")
            
        local_dir = os.path.expanduser(acc["LOCAL_DIR"])
        remote_name = acc["REMOTE_NAME"]
        filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
        db_path = os.path.join(CONFIG_DIR, acc["DB_FILE"])
        
        os.makedirs(local_dir, exist_ok=True)
        db_connection = init_db(db_path)
        scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
        scan_remote(db_connection, remote_name, acc.get("IGNORE_PATTERNS", []))
        generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
        db_connection.close()

        cmd = [
            "rclone", "bisync", local_dir, f"{remote_name}:",
            f"--filter-from={filter_file}", "--transfers=16", "--checkers=16",
            "--create-empty-src-dirs", "--fix-case", "-P",
            f"--log-file={MANUAL_SYNC_REPORT_FILE}", "--log-level=INFO"
        ]
        if bw_limit != "0": cmd.append(f"--bwlimit={bw_limit}")
        if max_size != "0": cmd.append(f"--max-size={max_size}")
        
        if escolha == '2':
            cmd.append("--force")
            print("\n⚠️ Modo FORCE ativado. Arquivos serão deletados sem trava de segurança.")
        
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print(f"\n⚠️ Rclone solicitou uma varredura de cura (--resync). Iniciando...")
            with open(MANUAL_SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
                f.write("⚠️ Varredura de cura (--resync) acionada automaticamente...\n")
                
            if "--resync" not in cmd: cmd.append("--resync")
            subprocess.run(cmd)

        print(f"\n✅ Concluído: {acc['PROFILE_NAME']}")
        
        with open(MANUAL_SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n✅ Concluído: {acc['PROFILE_NAME']}\n")
            f.write("-" * 45 + "\n\n")
    
    print("\n🎉 Todas as tarefas imediatas foram concluídas!")
    print(f"📂 Um relatório completo foi salvo em: {MANUAL_SYNC_REPORT_FILE}")

def run_dry_run():
    clear_screen()
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    
    report_dir = get_report_dir(config)
    DRY_RUN_REPORT_FILE = os.path.join(report_dir, "ultimo_dry_run.txt")
    
    with open(DRY_RUN_REPORT_FILE, "w", encoding="utf-8") as rep_file:
        def tee(msg=""):
            print(msg)
            rep_file.write(msg + "\n")

        tee("="*45)
        tee("🧪 RELATÓRIO DE TEST-DRIVE (DRY-RUN)")
        tee(f"Data gerada: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        tee("Simulando as regras. Nenhum arquivo foi alterado.")
        tee("="*45)

        if not ACCOUNTS:
            tee("\nNenhuma conta configurada para testar.")
            return

        bw_limit = config.get("BW_LIMIT", "0")
        max_size = config.get("MAX_SIZE", "0")

        for acc in ACCOUNTS:
            tee(f"\n🚀 Testando: {acc['PROFILE_NAME']}")
            local_dir = os.path.expanduser(acc["LOCAL_DIR"])
            remote_name = acc["REMOTE_NAME"]
            filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            db_path = os.path.join(CONFIG_DIR, acc["DB_FILE"])
            
            os.makedirs(local_dir, exist_ok=True)
            db_connection = init_db(db_path)
            scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
            scan_remote(db_connection, remote_name, acc.get("IGNORE_PATTERNS", []))
            generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
            db_connection.close()

            cmd = [
                "rclone", "bisync", local_dir, f"{remote_name}:",
                f"--filter-from={filter_file}", "--transfers=16", "--checkers=16",
                "--create-empty-src-dirs", "--fix-case", "-v", "--dry-run"
            ]
            if bw_limit != "0": cmd.append(f"--bwlimit={bw_limit}")
            if max_size != "0": cmd.append(f"--max-size={max_size}")
            
            tee("\nLogs do Rclone:\n")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stderr: tee(result.stderr.strip())
            if result.stdout: tee(result.stdout.strip())
            
            tee(f"\n✅ Fim da simulação para {acc['PROFILE_NAME']}")
            tee("-" * 45)
            
    print(f"\n📂 Uma cópia deste relatório foi salva em: {DRY_RUN_REPORT_FILE}")

def run_size_report():
    clear_screen()
    config = load_config()
    ACCOUNTS = config.get("ACCOUNTS", [])
    
    report_dir = get_report_dir(config)
    SIZE_REPORT_FILE = os.path.join(report_dir, "ultimo_relatorio_tamanho.txt")
    
    with open(SIZE_REPORT_FILE, "w", encoding="utf-8") as rep_file:
        def tee(msg=""):
            print(msg)
            rep_file.write(msg + "\n")

        tee("="*45)
        tee("📊 RELATÓRIO DE ARQUIVOS BLOQUEADOS POR TAMANHO")
        tee(f"Data gerada: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        tee("="*45)

        if not ACCOUNTS:
            tee("\nNenhuma conta configurada.")
            return

        max_size = config.get("MAX_SIZE", "0")
        if max_size == "0":
            tee("\nNenhum limite de tamanho configurado no momento (MAX_SIZE = 0).")
            tee("Todos os arquivos estão liberados para sincronização.")
            return

        tee(f"\nAnalisando arquivos maiores que {max_size}... (Ignorando bloqueios ativos)\n")

        def format_size_line(line):
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0].isdigit():
                size = float(parts[0])
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size < 1024.0:
                        size_str = f"{size:.2f}".replace('.', ',')
                        return f"[{size_str} {unit}] {parts[1]}"
                    size /= 1024.0
            return line.strip()

        for acc in ACCOUNTS:
            tee(f"🔄 Conta: {acc['PROFILE_NAME']}")
            local_dir = os.path.expanduser(acc["LOCAL_DIR"])
            remote_name = acc["REMOTE_NAME"]
            filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
            db_path = os.path.join(CONFIG_DIR, acc["DB_FILE"])

            os.makedirs(local_dir, exist_ok=True)
            db_connection = init_db(db_path)
            scan_local(db_connection, local_dir, acc.get("IGNORE_PATTERNS", []))
            scan_remote(db_connection, remote_name, acc.get("IGNORE_PATTERNS", []))
            generate_filters(db_connection, filter_file, acc.get("IGNORE_PATTERNS", []))
            db_connection.close()

            # Busca Local
            tee("  💻 No Computador Local:")
            cmd_local = ["rclone", "ls", local_dir, f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res_local = subprocess.run(cmd_local, capture_output=True, text=True)
            if res_local.stdout.strip():
                for line in res_local.stdout.strip().split('\n'):
                    tee(f"     - {format_size_line(line)}")
            else:
                tee("     (Nenhum arquivo local excede o limite estipulado)")

            # Busca Nuvem
            tee("\n  ☁️  Na Nuvem:")
            cmd_remote = ["rclone", "ls", f"{remote_name}:", f"--min-size={max_size}", f"--filter-from={filter_file}", "-q"]
            res_remote = subprocess.run(cmd_remote, capture_output=True, text=True)
            if res_remote.stdout.strip():
                for line in res_remote.stdout.strip().split('\n'):
                    tee(f"     - {format_size_line(line)}")
            else:
                tee("     (Nenhum arquivo na nuvem excede o limite estipulado)")
            tee("-" * 45)

        tee("\n✅ Relatório concluído!")
    print(f"\n📂 Uma cópia deste relatório foi salva em: {SIZE_REPORT_FILE}")

# ==========================================
# MÓDULO WIZARD (INTERFACE INTERATIVA)
# ==========================================
def run_config_wizard():
    config = load_config()
    
    while True:
        clear_screen()
        print("=== Assistente do Sync Engine ===")
        print("\n" + "="*45)
        print("--- Configuração de Contas ---")
        print("1. Adicionar nova conta (Nuvem via Rclone)")
        print(f"2. Listar contas atuais ({len(config.get('ACCOUNTS', []))} configurada(s))")
        print("3. Remover uma conta")
        print("4. Configurações Globais (Intervalo, Banda, Tamanho, Relatórios)")
        print("5. Gerenciar Filtros Globais (Ignorar arquivos/pastas)")
        print("\n--- Ações Extras ---")
        print("6. 🚀 Forçar Sincronização Agora (Ao vivo / Reparo)")
        print("7. 🧪 Test-Drive / Dry-Run (Simular Sincronização)")
        print("8. 📊 Relatório de Arquivos Bloqueados por Tamanho")
        print("9. 🩺 Médico (Diagnóstico do Sistema)")
        print("\n--- Controle do Motor em Fundo ---")
        print("10. ▶️  Ligar Motor (Start)")
        print("11. ⏹️  Desligar Motor (Stop)")
        print("12. ℹ️  Ver Status do Motor (Status)")
        print("\n13. Sair")
        print("="*45)
        
        escolha = input("Escolha uma opção (1-13): ").strip()
        
        if escolha == '1':
            clear_screen()
            print("--- Adicionando Nova Conta ---")
            profile = input("Nome do Perfil (ex: GDrive Pessoal, OneDrive Empresa): ").strip()
            if not profile: 
                pause(); continue
                
            remote = None
            while True:
                clear_screen()
                print(f"--- Vinculando Nuvem ao Perfil '{profile}' ---")
                rclone_out = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
                remotes = [r.strip(':') for r in rclone_out.stdout.strip().split('\n') if r.strip()]

                print("\nConexões Rclone disponíveis:")
                if not remotes: print("  [ Nenhuma conexão encontrada ]")
                else:
                    for i, r in enumerate(remotes): print(f"  [{i+1}] {r}")
                
                print("\n  [N] Criar nova conexão no Rclone")
                print("  [C] Cancelar")
                op_remote = input("\nEscolha o número da nuvem, 'N' para nova ou 'C' para cancelar: ").strip().lower()

                if op_remote == 'c': break
                elif op_remote == 'n':
                    clear_screen(); subprocess.run(["rclone", "config"]); continue
                elif op_remote.isdigit() and 0 <= int(op_remote) - 1 < len(remotes):
                    remote = remotes[int(op_remote) - 1]; break
                else: 
                    print("❌ Opção inválida."); time.sleep(1.5)

            if not remote: continue

            conflitos_remote = [acc for acc in config.get("ACCOUNTS", []) if acc["REMOTE_NAME"] == remote]
            if conflitos_remote:
                print(f"\n⚠️  AVISO: A nuvem '{remote}' já está vinculada.")
                confirma = input("Deseja usar essa mesma nuvem novamente? (S/N): ").strip().lower()
                if confirma != 's': pause(); continue

            default_local = f"~/{remote}"
            local = input(f"\nCaminho da pasta local (Enter para usar '{default_local}'): ").strip()
            if not local:
                local = default_local
                print(f"📂 Diretório definido: {local}")

            local_expanded = os.path.expanduser(local)
            conflitos_local = [acc for acc in config.get("ACCOUNTS", []) if os.path.expanduser(acc["LOCAL_DIR"]) == local_expanded]
            if conflitos_local:
                print(f"\n⚠️  AVISO: A pasta '{local}' já está sendo usada.")
                confirma_local = input("Deseja compartilhar esta pasta (Criar Ponte)? (S/N): ").strip().lower()
                if confirma_local != 's': pause(); continue
                
            safe_name = "".join([c for c in profile.lower().replace(" ", "_") if c.isalnum() or c=='_'])
            nova_conta = {
                "PROFILE_NAME": profile,
                "REMOTE_NAME": remote,
                "LOCAL_DIR": local,
                "IGNORE_PATTERNS": ["venv", ".venv", "__pycache__", ".git", "site-packages", "Personal Vault", "Cofre Pessoal", "*.tmp", "Thumbs.db", ".DS_Store"],
                "DB_FILE": f"sync_metadata_{safe_name}.db",
                "FILTER_FILE": f"excludes_{safe_name}.txt"
            }
            config.setdefault("ACCOUNTS", []).append(nova_conta)
            save_config(config)
            print(f"\n✅ Conta '{profile}' adicionada com sucesso!")
            manage_service("reload")
            pause()

        elif escolha == '2':
            clear_screen()
            print("--- Contas Configuradas ---")
            contas = config.get("ACCOUNTS", [])
            if not contas: print("\nNenhuma conta configurada ainda.")
            for i, acc in enumerate(contas):
                print(f"\n[{i+1}] {acc['PROFILE_NAME']}\n    Nuvem: {acc['REMOTE_NAME']}\n    Pasta: {acc['LOCAL_DIR']}")
            pause()
                
        elif escolha == '3':
            while True:
                clear_screen()
                contas = config.get("ACCOUNTS", [])
                if not contas: break
                
                print("--- Remover Conta ---")
                for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
                print("[C] Voltar")
                
                op = input("\nDigite o número para apagar ou 'C' para voltar: ").strip().lower()
                if op == 'c': break
                if op.isdigit() and 1 <= int(op) <= len(contas):
                    apagada = contas.pop(int(op)-1)
                    
                    db_path = os.path.join(CONFIG_DIR, apagada.get("DB_FILE", ""))
                    filter_path = os.path.join(CONFIG_DIR, apagada.get("FILTER_FILE", ""))
                    
                    if db_path and os.path.exists(db_path):
                        try: os.remove(db_path)
                        except OSError: pass
                        
                    if filter_path and os.path.exists(filter_path):
                        try: os.remove(filter_path)
                        except OSError: pass
                    
                    save_config(config); manage_service("reload")
                    print(f"\n🗑️ Conta '{apagada['PROFILE_NAME']}' e arquivos residuais removidos com sucesso!")
                    pause()
                else: 
                    print("❌ Opção inválida."); time.sleep(1.5)
                
        elif escolha == '4':
            while True:
                clear_screen()
                print("--- Configurações Globais ---")
                print(f"1. Intervalo de Sincronização (Atual: {config.get('SYNC_INTERVAL', 300)}s)")
                print(f"2. Limite de Banda (Atual: {config.get('BW_LIMIT', '0')} [0 = Sem limite])")
                print(f"3. Tamanho Máximo de Arquivo (Atual: {config.get('MAX_SIZE', '0')} [0 = Sem limite])")
                
                atual_rep = config.get('REPORT_DIR', '')
                print(f"4. Pasta de Relatórios (Atual: {atual_rep if atual_rep else 'Padrão (~/.config/sync_engine)'})")
                print("C. Voltar")
                
                op_cfg = input("\nEscolha uma opção: ").strip().lower()
                if op_cfg == 'c': break
                elif op_cfg == '1':
                    novo = input("\nNovo tempo em segundos (ex: 300): ")
                    if novo.isdigit() and int(novo) >= 30:
                        config["SYNC_INTERVAL"] = int(novo); save_config(config); manage_service("reload")
                        print("✅ Intervalo alterado."); pause()
                    else: print("❌ Inválido. Mínimo 30s."); time.sleep(1.5)
                elif op_cfg == '2':
                    novo = input("\nLimite de banda (ex: 10M, 500K, 0 = ilimitado): ").strip()
                    if novo:
                        config["BW_LIMIT"] = novo; save_config(config); manage_service("reload")
                        print("✅ Limite de banda alterado."); pause()
                elif op_cfg == '3':
                    novo = input("\nTamanho máximo de arquivo (ex: 500M, 1G, 0 = ilimitado): ").strip()
                    if novo:
                        config["MAX_SIZE"] = novo; save_config(config); manage_service("reload")
                        print("✅ Tamanho máximo alterado."); pause()
                elif op_cfg == '4':
                    print("\nDefina a pasta para salvar os relatórios em texto gerados pelo assistente.")
                    print("Exemplos: ~/Documentos | /tmp | /var/log")
                    print("Para voltar ao padrão oculto (~/.config/sync_engine), aperte Enter deixando vazio.")
                    novo = input("\nNovo caminho: ").strip()
                    config["REPORT_DIR"] = novo
                    save_config(config)
                    print("✅ Caminho dos relatórios atualizado!"); pause()
                else: print("❌ Opção inválida."); time.sleep(1.5)

        elif escolha == '5':
            contas = config.get("ACCOUNTS", [])
            if not contas: 
                clear_screen(); print("\nNenhuma conta configurada."); pause(); continue
            
            clear_screen()
            print("--- Gerenciar Filtros Globais ---")
            for i, acc in enumerate(contas): print(f"[{i+1}] {acc['PROFILE_NAME']}")
            print("[C] Voltar")
            
            op_acc = input("\nEscolha a conta: ").strip().lower()
            if op_acc == 'c': continue
            if op_acc.isdigit() and 1 <= int(op_acc) <= len(contas):
                conta = contas[int(op_acc) - 1]
                padroes = conta.get("IGNORE_PATTERNS", conta.get("SKIP_DIRS", []))
                
                while True:
                    clear_screen()
                    print(f"--- Filtros de '{conta['PROFILE_NAME']}' ---")
                    if not padroes: print("  [ Nenhum filtro configurado ]")
                    for j, p in enumerate(padroes): print(f"  [{j+1}] {p}")
                    
                    print("\n[A] Adicionar  [R] Remover  [H] Ajuda  [C] Salvar e Sair")
                    acao = input("Escolha uma ação: ").strip().lower()
                    
                    if acao == 'c':
                        conta["IGNORE_PATTERNS"] = padroes; save_config(config); manage_service("reload")
                        print("\n✅ Filtros salvos!"); pause(); break
                    elif acao == 'a':
                        novo = input("\nDigite o padrão: ").strip()
                        if novo and novo not in padroes: padroes.append(novo); print(f"✅ '{novo}' adicionado!"); time.sleep(1)
                    elif acao == 'r':
                        num = input("\nNúmero para remover: ").strip()
                        if num.isdigit() and 1 <= int(num) <= len(padroes): padroes.pop(int(num)-1); time.sleep(1)
                    elif acao == 'h':
                        clear_screen()
                        print("="*45)
                        print("--- Guia de Filtros e Exclusões ---")
                        print("\n▶ 1. ARQUIVO .nosync")
                        print("  Crie um arquivo '.nosync' dentro de qualquer pasta para ignorá-la.")
                        print("\n▶ 2. CURINGAS (* e ?)")
                        print("  * : Qualquer texto (ex: *.tmp)")
                        print("  ? : 1 caractere (ex: cam_?.dav)")
                        print("\n▶ 3. ANCORAGEM NA RAIZ (/)")
                        print("  Use '/' no começo para aplicar apenas na pasta principal.")
                        print("="*45)
                        pause()
                    else: print("❌ Opção inválida."); time.sleep(1)
            else: print("❌ Conta inválida."); time.sleep(1.5)

        elif escolha == '6': run_now(); pause()
        elif escolha == '7': run_dry_run(); pause()
        elif escolha == '8': run_size_report(); pause()
        elif escolha == '9': run_doctor()
        elif escolha == '10': clear_screen(); manage_service("start"); pause()
        elif escolha == '11': clear_screen(); manage_service("stop"); pause()
        elif escolha == '12': clear_screen(); manage_service("status"); pause()
        elif escolha == '13': clear_screen(); print("Saindo... Até logo!\n"); break
        else: print("❌ Opção inválida."); time.sleep(1)

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
    cursor.execute("CREATE INDEX idx_source ON metadata(source)")
    conn.commit()
    return conn

def scan_local(conn, local_dir, ignore_patterns):
    records = []
    def matches_pattern(name, rel_path):
        for p in ignore_patterns:
            if p.startswith('/'):
                if fnmatch.fnmatch(rel_path, p[1:]): return True
            else:
                if fnmatch.fnmatch(name, p): return True
        return False
        
    def fast_scan(current_path, parent_rel=""):
        try:
            with os.scandir(current_path) as it:
                entries = list(it)
                has_nosync = any(e.name == '.nosync' for e in entries)
                
                for entry in entries:
                    rel_path = os.path.join(parent_rel, entry.name) if parent_rel else entry.name
                    
                    if entry.name == '.nosync':
                        records.append(('local', rel_path, parent_rel, False, 0, '', True))
                        continue 
                        
                    if has_nosync:
                        continue 
                        
                    if matches_pattern(entry.name, rel_path): 
                        continue 
                        
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            records.append(('local', rel_path, parent_rel, True, 0, '', False))
                            fast_scan(entry.path, rel_path)
                        else:
                            stat = entry.stat(follow_symlinks=False)
                            records.append(('local', rel_path, parent_rel, False, stat.st_size, str(stat.st_mtime), False))
                    except OSError:
                        pass
        except OSError: 
            pass
            
    fast_scan(local_dir)
    conn.executemany("INSERT INTO metadata (source, path, parent_dir, is_dir, size, mod_time, has_nosync) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
    conn.commit()

def scan_remote(conn, remote_name, ignore_patterns):
    records = []
    cmd = ["rclone", "lsjson", f"{remote_name}:", "--fast-list", "--recursive"]
    
    for p in ignore_patterns:
        cmd.extend(["--exclude", f"{p}/**", "--exclude", f"{p}/", "--exclude", p])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout.strip():
            for item in json.loads(result.stdout):
                path = item.get("Path", "")
                parent_dir = os.path.dirname(path)
                
                is_nosync = (os.path.basename(path) == '.nosync')
                
                records.append(('remote', path, parent_dir, item.get("IsDir", False), item.get("Size", 0), item.get("ModTime", ""), is_nosync))
                
            conn.executemany("INSERT INTO metadata (source, path, parent_dir, is_dir, size, mod_time, has_nosync) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()
    except Exception: 
        pass

def generate_filters(conn, filter_file, ignore_patterns):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT parent_dir FROM metadata WHERE has_nosync = 1 UNION SELECT DISTINCT parent_dir FROM metadata WHERE path LIKE '%/.nosync' OR path = '.nosync'")
    filters = []
    
    for p in ignore_patterns:
        filters.append(f"- {p}")
        filters.append(f"- {p}/**")
        filters.append(f"- {p}/")
        
    for (folder,) in cursor.fetchall():
        clean_folder = folder.strip("/")
        if clean_folder: 
            filters.append(f"- /{clean_folder}/")
            filters.append(f"- /{clean_folder}/**")
            
    with open(filter_file, "w", encoding="utf-8") as f:
        for line in filters: f.write(line + "\n")
        
def run_sync(local_dir, remote_name, filter_file, bw_limit="0", max_size="0"):
    start_time = time.time()
    cmd = [
        "rclone", "bisync", local_dir, f"{remote_name}:",
        f"--filter-from={filter_file}", "--transfers=16", "--checkers=16",
        "--create-empty-src-dirs", "--fix-case", "-v"
    ]
    if bw_limit != "0": cmd.append(f"--bwlimit={bw_limit}")
    if max_size != "0": cmd.append(f"--max-size={max_size}")

    def analyze_output(stderr_text):
        has_changes = "Copied (" in stderr_text or "Deleted:" in stderr_text or "Moved (" in stderr_text or "Updated:" in stderr_text
        errors = [line for line in stderr_text.split('\n') if "ERROR" in line]
        err_msg = errors[0].split("ERROR :")[-1].strip() if errors else "Verifique o log no terminal."
        return has_changes, err_msg

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        has_transfers, _ = analyze_output(result.stderr)
        return True, time.time() - start_time, has_transfers, ""
    else:
        if "resync" in result.stderr.lower() or "not found" in result.stderr.lower():
            cmd.append("--resync")
            resync_result = subprocess.run(cmd, capture_output=True, text=True)
            if resync_result.returncode == 0:
                has_transfers, _ = analyze_output(resync_result.stderr)
                return True, time.time() - start_time, has_transfers, ""
            else:
                _, err_msg = analyze_output(resync_result.stderr)
                return False, 0, False, err_msg
        else:
            _, err_msg = analyze_output(result.stderr)
            return False, 0, False, err_msg

def send_notification(title, message, urgency="normal"):
    try:
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"
        subprocess.run(["notify-send", title, message, "--urgency", urgency, "--app-name", "Sync Engine", "--icon", "folder-remote"], env=env, check=False)
    except Exception: pass

# ==========================================
# MÓDULO DE AJUDA (HELP)
# ==========================================
def print_help():
    ajuda = """
=== Sync Engine Multi-Contas 3.0 (Rclone) ===

Uso: sync-engine [COMANDO]

Comandos Principais:
  config         Assistente interativo (Contas, Filtros e Limites).
  now            🚀 Sincroniza AGORA (força o envio/download imediato).
  test           🧪 Simula sincronização (Dry-Run) sem alterar nada.
  doctor         🩺 Diagnóstico de sistema (verifica rclone, systemd, etc).

Gerenciamento do Motor de Fundo:
  start          LIGA o serviço em segundo plano (inicia com o sistema).
  stop           DESLIGA e remove o serviço em segundo plano.
  status         Exibe o status e o histórico de logs do motor.

Utilitários:
  help, -h       Exibe esta ajuda.
"""
    print(ajuda.strip())

# ==========================================
# EXECUÇÃO PRINCIPAL (ROTEADOR DE COMANDOS)
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        if comando in ["help", "-h", "--help"]: print_help()
        elif comando == "config": run_config_wizard()
        elif comando == "now": run_now()
        elif comando == "test": run_dry_run()
        elif comando == "doctor": run_doctor()
        elif comando == "start": manage_service("start")
        elif comando == "stop": manage_service("stop")
        elif comando == "status": manage_service("status")
        else:
            clear_screen()
            print(f"❌ Erro: Comando desconhecido '{sys.argv[1]}'\n")
            print_help()
        sys.exit(0)
    else:
        if sys.stdout.isatty():
            clear_screen()
            print("❌ Erro: Nenhum comando informado.\n")
            print_help()
            sys.exit(1)
        
    try:
        logger.info("Motor Sync Engine Iniciado em Background.")
        while True:
            config = load_config()
            SYNC_INTERVAL = config.get("SYNC_INTERVAL", 300)
            BW_LIMIT = config.get("BW_LIMIT", "0")
            MAX_SIZE = config.get("MAX_SIZE", "0")
            ACCOUNTS = config.get("ACCOUNTS", [])
            
            if not ACCOUNTS:
                sys.exit(1)

            for acc in ACCOUNTS:
                profile_name = acc.get("PROFILE_NAME", "Desconhecido")
                local_dir = os.path.expanduser(acc["LOCAL_DIR"])
                
                os.makedirs(local_dir, exist_ok=True)
                
                remote_name = acc["REMOTE_NAME"]
                ignore_patterns = acc.get("IGNORE_PATTERNS", acc.get("SKIP_DIRS", []))
                
                db_path = os.path.join(CONFIG_DIR, acc["DB_FILE"])
                filter_file = os.path.join(CONFIG_DIR, acc["FILTER_FILE"])
                
                logger.debug(f"[{profile_name}] Gerando filtros e lendo metadados...")
                db_connection = init_db(db_path)
                scan_local(db_connection, local_dir, ignore_patterns)
                scan_remote(db_connection, remote_name, ignore_patterns)
                generate_filters(db_connection, filter_file, ignore_patterns)
                db_connection.close()
                
                success, tempo, has_transfers, err_msg = run_sync(local_dir, remote_name, filter_file, BW_LIMIT, MAX_SIZE)
                
                if success and has_transfers:
                    logger.info(f"[{profile_name}] Transferência concluída em {tempo:.1f}s.")
                    send_notification(f"Sync: {profile_name}", f"Atualizado com sucesso ({tempo:.1f}s).")
                elif success and not has_transfers:
                    logger.info(f"[{profile_name}] Checagem concluída. Nenhuma alteração detectada.")
                elif not success:
                    clean_error = err_msg.replace('"', '').replace("'", "")[:120]
                    logger.error(f"[{profile_name}] Falha na sincronização: {clean_error}")
                    send_notification(f"Erro: {profile_name}", f"Falha: {clean_error}", "critical")
                    
            time.sleep(SYNC_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Sincronização interrompida pelo usuário.")
        send_notification("Sync Engine", "Sincronização desligada.")