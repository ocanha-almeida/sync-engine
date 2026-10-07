import os
import json
import re
import sys

try:
    import emoji
except ImportError:
    print("❌ A biblioteca 'emoji' não foi encontrada. Execute: pip install emoji")
    sys.exit(1)

def limpar_jsons(pasta_locales="locales"):
    if not os.path.exists(pasta_locales):
        print(f"⚠️ Pasta '{pasta_locales}' não encontrada. Pulando JSONs.")
        return
        
    for arquivo in os.listdir(pasta_locales):
        if arquivo.endswith(".json"):
            caminho = os.path.join(pasta_locales, arquivo)
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            novos_dados = {}
            for k, v in dados.items():
                # Remove os emojis
                k_limpo = emoji.replace_emoji(k, replace='').strip()
                v_limpo = emoji.replace_emoji(v, replace='').strip()
                
                # Remove espaços duplos causados pela remoção do emoji
                k_limpo = re.sub(r'\s+', ' ', k_limpo)
                v_limpo = re.sub(r'\s+', ' ', v_limpo)
                
                if k_limpo:
                    novos_dados[k_limpo] = v_limpo
                    
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(novos_dados, f, indent=4, ensure_ascii=False)
            print(f"✅ JSON higienizado: {arquivo}")

def processar_py(caminho_py):
    if not os.path.exists(caminho_py):
        print(f"⚠️ Arquivo '{caminho_py}' não encontrado.")
        return

    with open(caminho_py, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Regex para capturar T('...') ou T("...") e verificar se está entre chaves { }
    padrao = re.compile(r'(\{)?T\((["\'])(.*?)\2\)(\})?')
    
    def substituto(match):
        abre_chave = match.group(1) == '{'
        aspas = match.group(2)
        texto = match.group(3)
        fecha_chave = match.group(4) == '}'
        
        # Coleta todos os emojis presentes dentro da string
        emojis_encontrados = ''.join(c for c in texto if c in emoji.EMOJI_DATA)
        
        if not emojis_encontrados:
            return match.group(0) # Retorna original se não houver emoji
            
        # Preserva o \n se ele estiver no começo do texto
        prefixo = ""
        if texto.startswith(r'\n'):
            prefixo = r'\n'
            texto = texto[2:]
        elif texto.startswith('\n'):
            prefixo = '\n'
            texto = texto[1:]
            
        texto_limpo = emoji.replace_emoji(texto, replace='').strip()
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo)
        
        if abre_chave and fecha_chave:
            # Ex: {T('✅ Olá')} vira ✅ {T('Olá')}
            return f'{prefixo}{emojis_encontrados} {{T({aspas}{texto_limpo}{aspas})}}'
        else:
            # Ex: T('\n✅ Olá') vira f"\n✅ {T('Olá')}"
            aspas_internas = "'" if aspas == '"' else aspas
            return f'f"{prefixo}{emojis_encontrados} {{T({aspas_internas}{texto_limpo}{aspas_internas})}}"'

    novo_conteudo = padrao.sub(substituto, conteudo)
    
    with open(caminho_py, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    print(f"✅ Código Python atualizado: {os.path.basename(caminho_py)}")

if __name__ == "__main__":
    print("="*45 + "\n🧹 HIGIENIZADOR DE i18n\n" + "="*45)
    
    # 1. Limpa os arquivos de idioma
    limpar_jsons("locales")
    
    # 2. Processa os arquivos Python que você deseja limpar
    arquivos_alvo = ["sync_engine.py", "sync_core.py", "sync_os.py"]
    for arq in arquivos_alvo:
        processar_py(arq)
        
    print("\nProcesso finalizado. Verifique seu git diff para confirmar as mudanças!")