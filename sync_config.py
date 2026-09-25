import os
import sys
import json
import logging
import re
import locale
from logging.handlers import RotatingFileHandler

VERSION = "7.2"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.expanduser("~/.config/sync_engine")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "sync.log")

os.makedirs(CONFIG_DIR, exist_ok=True)

# ==========================================
# i18n (INTERNATIONALIZATION) SETUP
# ==========================================
try:
    # Detecta o idioma do sistema (ex: 'pt_BR', 'es_MX')
    sys_lang = locale.getdefaultlocale()[0]
except Exception:
    sys_lang = "en_US"

locale_file = os.path.join(BASE_DIR, "locales", f"{sys_lang}.json")

# Fallback Inteligente: Se não achar 'es_MX.json', tenta o genérico 'es.json'
if not os.path.exists(locale_file) and sys_lang and "_" in sys_lang:
    base_lang = sys_lang.split("_")[0]
    locale_file = os.path.join(BASE_DIR, "locales", f"{base_lang}.json")

translations = {}
if os.path.exists(locale_file):
    try:
        with open(locale_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except Exception:
        pass

def T(text):
    """Traduz o texto com base no dicionário JSON local carregado."""
    return translations.get(text, text)
# ==========================================
# LOGGING & CONFIGURATION
# ==========================================
logger = logging.getLogger("SyncEngine")
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)
if not logger.handlers:
    logger.addHandler(file_handler)

DEFAULT_CONFIG = {
    "SYNC_INTERVAL": 300,
    "BW_LIMIT": "0",
    "MAX_SIZE": "0",
    "REPORT_DIR": "",
    "AUTO_CHECK_NAMES": True,
    "ACCOUNTS": []
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG, T("Default file created"))
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if "AUTO_CHECK_NAMES" not in cfg: 
                cfg["AUTO_CHECK_NAMES"] = True
            return cfg
    except json.JSONDecodeError:
        logger.error(T("Failed to read config.json. Using defaults."))
        return DEFAULT_CONFIG

def save_config(config_data, action_msg=""):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
    if action_msg:
        logger.info(f"{T('Configuration changed:')} {action_msg}")

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
