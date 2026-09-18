import os
import subprocess
import sqlite3
import json
import fnmatch
import time
import re
from sync_config import logger, clean_log_file

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
    cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
    records = []
    cmd = ["rclone", "lsjson", f"{remote_name}:", "--fast-list", "--recursive"]
    
    for p in ignore_patterns:
        p_clean = p.replace("\\", "/")
        cmd.extend(["--exclude", f"{p_clean}/**", "--exclude", p_clean])
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=cflags)
    
    if result.returncode != 0:
        erro_real = result.stderr.strip()
        logger.error(f"Falha ao ler a nuvem ({remote_name}): {erro_real}")
        raise RuntimeError(f"Detalhes do Rclone:\n{erro_real}")

    if result.stdout.strip():
        for item in json.loads(result.stdout):
            path = item.get("Path", "")
            parts = path.split("/")
            parent_dir = "/".join(parts[:-1]) if len(parts) > 1 else ""
            records.append(('remote', path, parent_dir, item.get("IsDir", False), item.get("Size", 0), item.get("ModTime", ""), (parts[-1] == '.nosync')))
        conn.executemany("INSERT INTO metadata (source, path, parent_dir, is_dir, size, mod_time, has_nosync) VALUES (?, ?, ?, ?, ?, ?, ?)", records)
        conn.commit()

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

def analyze_sync_logic(log_text):
    # Otimizado para não gerar notificação falsa no Linux. Só alerta se realmente houver transferência.
    mudancas = ["Copied (", "Deleted:", "Moved (", "Updated:"]
    has_changes = any(m in log_text for m in mudancas)
    if "resync is required" in log_text.lower() or "resyncing" in log_text.lower():
        has_changes = True
    errors = [line for line in log_text.split('\n') if "ERROR" in line]
    err_msg = errors[0].split("ERROR :")[-1].strip() if errors else "Verifique o log."
    return has_changes, err_msg
