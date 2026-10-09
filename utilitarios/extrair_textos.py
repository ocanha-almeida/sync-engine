#!/usr/bin/env python3
"""
Gera dicionario_base.json analisando todos os .py da pasta-mãe (raiz do projeto)
de forma não recursiva, ignorando scripts acessórios/utilitários.
"""
import os
import ast
import json

def extrair_nucleo_limpo(text):
    """
    Replica a exata lógica da função T() do sync_config.py para 
    gerar a chave de dicionário limpa (sem emojis ou pontuações).
    """
    if not text:
        return text, text
        
    core_start = 0
    for i, char in enumerate(text):
        if char.isalnum() or char in "[({'\"":
            core_start = i
            break
    else:
        return text, text
        
    core_end = len(text)
    for i in range(len(text)-1, core_start-1, -1):
        char = text[i]
        if char.isalnum() or char in "])}'\"":
            core_end = i + 1
            break
            
    core = text[core_start:core_end]
    
    # Retorna a chave em minúsculo (para o índice do JSON) 
    # e o core original (como valor base para facilitar a tradução)
    return core.lower(), core

def extrair_traducoes():
    strings_dict = {}
    arquivos_lidos = 0
    
    # Obtém o caminho absoluto do diretório-pai (pasta principal do projeto)
    dir_script = os.path.dirname(os.path.abspath(__file__))
    dir_pai = os.path.dirname(dir_script)
    
    print(f"🔍 Iniciando varredura por strings de tradução na pasta: {dir_pai}")
    
    # Vasculha apenas os arquivos .py do diretório-pai (não recursivo)
    for item in os.listdir(dir_pai):
        caminho_item = os.path.join(dir_pai, item)
        
        # Analisa somente arquivos .py reais da raiz
        if os.path.isfile(caminho_item) and item.endswith('.py'):
            try:
                with open(caminho_item, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    
                tree = ast.parse(conteudo)
                arquivos_lidos += 1
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id == 'T':
                            if node.args and isinstance(node.args[0], ast.Constant):
                                raw_text = node.args[0].value
                                if isinstance(raw_text, str):
                                    chave, valor_base = extrair_nucleo_limpo(raw_text)
                                    if chave and chave not in strings_dict:
                                        strings_dict[chave] = valor_base
                                        
            except Exception as e:
                print(f"⚠️ Erro ao ler a estrutura do arquivo {item}: {e}")

    # Ordena alfabeticamente
    dicionario_ordenado = {k: strings_dict[k] for k in sorted(strings_dict.keys())}
    
    # Salva o arquivo de saída diretamente na raiz do projeto
    arquivo_saida = os.path.join(dir_pai, 'dicionario_base.json')
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dicionario_ordenado, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Extração concluída com sucesso!")
    print(f"📂 Arquivos analisados na raiz: {arquivos_lidos}")
    print(f"🔑 Chaves únicas encontradas: {len(dicionario_ordenado)}")
    print(f"📝 Resultado salvo em: '{arquivo_saida}'")

if __name__ == "__main__":
    extrair_traducoes()