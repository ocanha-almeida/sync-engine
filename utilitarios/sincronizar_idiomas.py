#!/usr/bin/env python3
"""
Sincronizador de Dicionários de Idiomas.

Lê o 'dicionario_base.json' atualizado e injeta as chaves ausentes
em todos os arquivos .json da pasta 'locales/'. 
As traduções já existentes são preservadas intactas. As novas recebem
um marcador "✏️" para facilitar a busca e tradução manual posterior.
"""
import os
import json

DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_PAI = os.path.dirname(DIR_SCRIPT)

def sincronizar_dicionarios():
    caminho_base = os.path.join(DIR_PAI, 'dicionario_base.json')
    pasta_locales = os.path.join(DIR_PAI, 'locales')
    
    if not os.path.exists(caminho_base):
        print(f"❌ Arquivo base não encontrado: {caminho_base}")
        return
        
    if not os.path.exists(pasta_locales):
        print(f"❌ Pasta de idiomas não encontrada: {pasta_locales}")
        return
        
    with open(caminho_base, 'r', encoding='utf-8') as f:
        dicionario_base = json.load(f)
        
    for arquivo in os.listdir(pasta_locales):
        if arquivo.endswith('.json'):
            caminho_json = os.path.join(pasta_locales, arquivo)
            
            with open(caminho_json, 'r', encoding='utf-8') as f:
                idioma_atual = json.load(f)
                
            chaves_adicionadas = 0
            chaves_removidas = 0
            novo_idioma = {}
            
            # Reconstrói o dicionário garantindo a ordem alfabética da base
            for chave, valor_ingles in dicionario_base.items():
                if chave in idioma_atual:
                    # Mantém a tradução que você já fez
                    novo_idioma[chave] = idioma_atual[chave]
                else:
                    # Injeta a chave nova com o marcador
                    novo_idioma[chave] = f"✏️ {valor_ingles}"
                    chaves_adicionadas += 1
                    
            # Verifica se existem chaves órfãs (que foram apagadas do código e do base)
            for chave_antiga in idioma_atual.keys():
                if chave_antiga not in dicionario_base:
                    chaves_removidas += 1
                    
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(novo_idioma, f, indent=4, ensure_ascii=False)
                
            if chaves_adicionadas > 0 or chaves_removidas > 0:
                print(f"✅ {arquivo}: {chaves_adicionadas} novas chaves adicionadas | {chaves_removidas} antigas removidas.")
            else:
                print(f"✔️ {arquivo}: Já estava 100% sincronizado com a base.")

if __name__ == "__main__":
    print("🔄 Iniciando sincronização de idiomas...\n")
    sincronizar_dicionarios()
    print("\nFeito! Procure por '✏️' nos seus arquivos JSON para traduzir os novos textos.")