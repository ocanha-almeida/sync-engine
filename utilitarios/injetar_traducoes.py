#!/usr/bin/env python3
"""
Utilitário para Injetar Traduções em Lote.

Este script lê um arquivo JSON contendo novas traduções e as injeta
diretamente em um arquivo JSON de idioma existente. 

Uso: python injetar_traducoes.py <arquivo_destino.json> <arquivo_novas.json>
"""

import sys
import os
import json

def injetar():
    # Verifica se os argumentos foram passados corretamente
    if len(sys.argv) != 3:
        print("="*45)
        print("❌ Uso incorreto do comando.")
        print("Formato esperado:")
        print("python injetar_traducoes.py <arquivo_destino.json> <arquivo_novas.json>")
        print("\nExemplo:")
        print("python utilitarios/injetar_traducoes.py locales/pt.json novas_pt.json")
        print("="*45)
        sys.exit(1)

    arquivo_destino = sys.argv[1]
    arquivo_novas = sys.argv[2]

    # Verifica se os arquivos existem
    if not os.path.exists(arquivo_destino):
        print(f"❌ Erro: O arquivo de destino '{arquivo_destino}' não foi encontrado.")
        sys.exit(1)

    if not os.path.exists(arquivo_novas):
        print(f"❌ Erro: O arquivo com as novas traduções '{arquivo_novas}' não foi encontrado.")
        sys.exit(1)

    # Carrega o arquivo de destino (ex: pt.json)
    try:
        with open(arquivo_destino, 'r', encoding='utf-8') as f:
            destino_dict = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler '{arquivo_destino}': {e}")
        sys.exit(1)

    # Carrega o arquivo com as novas traduções
    try:
        with open(arquivo_novas, 'r', encoding='utf-8') as f:
            novas_dict = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler '{arquivo_novas}': {e}")
        sys.exit(1)

    chaves_atualizadas = 0
    chaves_adicionadas = 0

    # Injeta as novas traduções no dicionário de destino
    for chave, valor in novas_dict.items():
        if chave in destino_dict:
            # Só contabiliza se o texto for realmente diferente ou se removeu o marcador "✏️"
            if destino_dict[chave] != valor:
                destino_dict[chave] = valor
                chaves_atualizadas += 1
        else:
            destino_dict[chave] = valor
            chaves_adicionadas += 1

    # Ordena alfabeticamente para manter o padrão do projeto
    destino_ordenado = {k: destino_dict[k] for k in sorted(destino_dict.keys())}

    # Salva o resultado de volta no arquivo de destino
    try:
        with open(arquivo_destino, 'w', encoding='utf-8') as f:
            json.dump(destino_ordenado, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao salvar '{arquivo_destino}': {e}")
        sys.exit(1)

    # Exibe o relatório final
    print("="*45)
    print("✅ Injeção de traduções concluída!")
    print(f"📄 Arquivo atualizado: {arquivo_destino}")
    print(f"🔄 Traduções substituídas: {chaves_atualizadas}")
    print(f"➕ Novas chaves adicionadas: {chaves_adicionadas}")
    print("="*45)

if __name__ == "__main__":
    injetar()