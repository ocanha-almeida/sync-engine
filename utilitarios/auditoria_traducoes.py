#!/usr/bin/env python3
"""
Auditoria Abrangente de Mensagens e Strings do Sistema.

Este script inspeciona os ficheiros Python (.py) na raiz do projeto para catalogar
todas as emissões de texto e verificar a cobertura da função de internacionalização T().
"""
import os

DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_PAI = os.path.dirname(DIR_SCRIPT)

def auditar_codigo():
    alvos = ['print(', 'input(', '.write(', 'tee(', 'logger.', 'send_notification(']
    
    ignorar_exatos = [
        'print()', 'print("")', "print('')", 'tee()', 'tee("")', "tee('')",
        'print("\\n")', "print('\\n')", 'tee("\\n")', "tee('\\n')",
        'print("="*45)', "print('='*45)", 'tee("="*45)', "tee('='*45)",
        'print("\\n" + "="*45)', "print('\\n' + '='*45)",
        'print("-" * 45)', "print('-' * 45)", 'tee("-" * 45)', "tee('-' * 45)"
    ]
    
    arquivo_saida = os.path.join(DIR_PAI, 'linhas_sem_traducao.txt')
    encontrados, arquivos_analisados = 0, 0
    
    with open(arquivo_saida, 'w', encoding='utf-8') as out:
        out.write("RELATÓRIO DE AUDITORIA DE TRADUÇÕES\nFormato: arquivo.py; linha; conteudo_da_linha\n" + "="*60 + "\n\n")
        
        for item in sorted(os.listdir(DIR_PAI)):
            caminho_item = os.path.join(DIR_PAI, item)
            if os.path.isfile(caminho_item) and item.endswith('.py'):
                arquivos_analisados += 1
                try:
                    with open(caminho_item, 'r', encoding='utf-8') as f: linhas = f.readlines()
                    for num, linha in enumerate(linhas, start=1):
                        linha_limpa = linha.strip()
                        if linha_limpa.startswith('#'): continue
                            
                        if any(alvo in linha_limpa for alvo in alvos):
                            if 'T(' not in linha_limpa:
                                linha_sem_esp = linha_limpa.replace(" ", "")
                                se_ignorar = any(ign.replace(" ", "") in linha_sem_esp for ign in ignorar_exatos)
                                
                                if not se_ignorar:
                                    out.write(f"{item}; {num}; {linha_limpa}\n")
                                    encontrados += 1
                except Exception as e: print(f"Erro ao ler {item}: {e}")

    print(f"✅ Varredura concluída! {arquivos_analisados} ficheiros analisados na raiz.")
    print(f"⚠️ Foram encontradas {encontrados} linhas suspeitas sem tradução. Relatório salvo em: '{arquivo_saida}'")
    
    if os.path.exists(os.path.join(DIR_PAI, 'auditoria_todas_mensagens.txt')):
        os.remove(os.path.join(DIR_PAI, 'auditoria_todas_mensagens.txt'))
        print("🗑️ Ficheiro antigo 'auditoria_todas_mensagens.txt' apagado com sucesso.")

if __name__ == "__main__":
    auditar_codigo()