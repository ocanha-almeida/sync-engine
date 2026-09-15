import os
import json
import logging
from logging.handlers import RotatingFileHandler

VERSION = "6.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.expanduser("~/.config/sync_engine")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "sync.log")

os.makedirs(CONFIG_DIR, exist_ok=True)

# Configuração unificada do Logger
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
        save_config(DEFAULT_CONFIG, "Criação do arquivo padrão")
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if "AUTO_CHECK_NAMES" not in cfg: 
                cfg["AUTO_CHECK_NAMES"] = True
            return cfg
    except json.JSONDecodeError:
        logger.error("Falha ao ler config.json. Usando padrões.")
        return DEFAULT_CONFIG

def save_config(config_data, action_msg=""):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
    if action_msg:
        logger.info(f"Configuração Alterada: {action_msg}")

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