#!/usr/bin/env python3
import os
import json
import subprocess
import time
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("❌ Instale a biblioteca: pip install deep-translator")
    exit(1)

DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_PAI = os.path.dirname(DIR_SCRIPT)
LOCALES_DIR = os.path.join(DIR_PAI, "locales")

MAPA_IDIOMAS = {
    "de": "de", 
    "es": "es", 
    "fr": "fr",
    "it": "it", 
    "jp": "ja",    
    "pt": "pt", 
    "zh": "zh-CN"  
}

NOME_IDIOMAS = {
    "de": "Alemão", "es": "Espanhol", "fr": "Francês",
    "it": "Italiano", "jp": "Japonês", "pt": "Português", "zh": "Chinês Simplificado"
}

def executar_pipeline():
    print("🔄 1. Extraindo e sincronizando o código-fonte...")
    subprocess.run(["python3", os.path.join(DIR_SCRIPT, "extrair_textos.py")])
    subprocess.run(["python3", os.path.join(DIR_SCRIPT, "sincronizar_idiomas.py")])

    print("\n🌐 2. Traduzindo pendências diretamente via Google Translate...")
    for arquivo in os.listdir(LOCALES_DIR):
        if not arquivo.endswith(".json"): continue
        
        codigo_lang = arquivo.replace(".json", "")
        if codigo_lang not in MAPA_IDIOMAS: continue
        
        caminho = os.path.join(LOCALES_DIR, arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
            
        pendentes = {k: v for k, v in dados.items() if str(v).startswith("✏️ ")}
        
        if not pendentes:
            print(f"✔️ {arquivo}: Já estava 100% traduzido.")
            continue
            
        print(f"⏳ Traduzindo {len(pendentes)} novas strings para {NOME_IDIOMAS[codigo_lang]} ({arquivo})...")
        
        tradutor = GoogleTranslator(source='en', target=MAPA_IDIOMAS[codigo_lang])
        
        for chave in pendentes.keys():
            try:
                texto_traduzido = tradutor.translate(chave)
                dados[chave] = texto_traduzido
                # Pausa leve para não sobrecarregar o serviço web
                time.sleep(2)
            except Exception as e:
                print(f"❌ Erro ao traduzir '{chave}': {e}")
        
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            
        print(f"✅ {arquivo}: Atualizado e salvo com sucesso.")

if __name__ == "__main__":
    executar_pipeline()