#!/usr/bin/env python3
"""
Utilitário de Higienização e Refatoração de Internacionalização (i18n).

Este script executa duas tarefas essenciais de manutenção na raiz do projeto:
1. Higienização de Dicionários JSON (pasta 'locales'):
   - Remove todos os emojis das chaves e valores dos ficheiros de tradução.
   - Normaliza os espaços em branco, garantindo chaves limpas para o motor.

2. Refatoração de Código Python (ficheiros .py na raiz):
   - Localiza ocorrências da função T() que contenham emojis embutidos.
   - Extrai automaticamente os emojis para fora da chamada T(), convertendo
     as strings em f-strings formatadas (ex: T('✅ Texto') -> f'✅ {T("Texto")}').
   - Preserva quebras de linha iniciais (\\n) e ajusta as aspas.

Nota: Opera a partir da subpasta 'utilitarios', apontando dinamicamente para
a pasta-mãe (raiz) de forma não recursiva.
"""

import os
import json
import re
import sys

try:
    import emoji
except ImportError:
    print("❌ A biblioteca 'emoji' não foi encontrada. Execute: pip install emoji")
    sys.exit(1)

# Caminho absoluto da pasta-mãe (raiz do projeto)
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_PAI = os.path.dirname(DIR_SCRIPT)

def limpar_jsons(nome_pasta="locales"):
    pasta_locales = os.path.join(DIR_PAI, nome_pasta)
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
                k_limpo = emoji.replace_emoji(k, replace='').strip()
                v_limpo = emoji.replace_emoji(v, replace='').strip()
                
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

    padrao = re.compile(r'(\{)?T\((["\'])(.*?)\2\)(\})?')
    
    def substituto(match):
        abre_chave = match.group(1) == '{'
        aspas = match.group(2)
        texto = match.group(3)
        fecha_chave = match.group(4) == '}'
        
        emojis_encontrados = ''.join(c for c in texto if c in emoji.EMOJI_DATA)
        
        if not emojis_encontrados:
            return match.group(0)
            
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
            return f'{prefixo}{emojis_encontrados} {{T({aspas}{texto_limpo}{aspas})}}'
        else:
            aspas_internas = "'" if aspas == '"' else aspas
            return f'f"{prefixo}{emojis_encontrados} {{T({aspas_internas}{texto_limpo}{aspas_internas})}}"'

    novo_conteudo = padrao.sub(substituto, conteudo)
    
    with open(caminho_py, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    print(f"✅ Código Python atualizado: {os.path.basename(caminho_py)}")

if __name__ == "__main__":
    print("="*45 + "\n🧹 HIGIENIZADOR DE i18n\n" + "="*45)
    print(f"📂 Diretório alvo (raiz do projeto): {DIR_PAI}\n")
    
    # 1. Limpa os arquivos de idioma na pasta locales da raiz
    limpar_jsons("locales")
    
    # 2. Processa apenas os arquivos Python principais na raiz (não recursivo)
    for item in os.listdir(DIR_PAI):
        caminho_item = os.path.join(DIR_PAI, item)
        if os.path.isfile(caminho_item) and item.endswith('.py'):
            processar_py(caminho_item)
        
    print("\nProcesso finalizado. Verifique seu git diff para confirmar as mudanças!")
