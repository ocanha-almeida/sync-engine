import os
import json
import sqlite3
import subprocess
import fnmatch
import re
import sync_config

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
                    if entry.name == '.nosync':
                        records.append(('local', rel_path, parent_rel.replace("\\", "/"), False, 0, '', True))
                        continue
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
    
    # BLINDAGEM: Se o Rclone falhar, ele não continua a sincronização
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    if result.returncode != 0:
        error_msg = result.stderr.strip() if result.stderr else "Erro de comunicação com a nuvem."
        sync_config.logger.error(f"Falha na varredura remota de {remote_name}: {error_msg}")
        raise Exception(f"Leitura da nuvem abortada. Proteção .nosync ativada. Detalhes: {error_msg}")

    if result.stdout.strip():
        try:
            parsed_json = json.loads(result.stdout)
            for item in parsed_json:
                path = item.get("Path", "")
                parts = path.split("/")
                parent_dir = "/".join(parts[:-1]) if len(parts) > 1 else ""
                records.append(('remote', path, parent_dir, item.get("IsDir", False), item.get("Size", 0), item.get("ModTime", ""), (parts[-1] == '.nosync')))
            conn.executemany("INSERT INTO metadata (source, path, parent_dir, is_dir, size, mod_time, has_nosync) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()
        except json.JSONDecodeError as e:
            sync_config.logger.error(f"Corrupção de dados da nuvem {remote_name}: {e}")
            raise Exception("Falha ao decodificar a lista de arquivos remotos.")

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

def analyze_sync_logic(log_text):
    mudancas = ["Copied (", "Deleted:", "Moved (", "Updated:"]
    has_changes = any(m in log_text for m in mudancas)
    if "resync is required" in log_text.lower() or "resyncing" in log_text.lower():
        has_changes = True
    errors = [line for line in log_text.split('\n') if "ERROR" in line]
    err_msg = errors[0].split("ERROR :")[-1].strip() if errors else "Verifique o log detalhado."
    return has_changes, err_msg

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
        return False, False, errors[0].split("ERROR :")[-1].strip() if errors else "Erro fatal do Rclone."
```