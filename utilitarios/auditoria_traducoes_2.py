#!/usr/bin/env python3
"""
Auditoria Abrangente de Mensagens e Strings do Sistema.

Este script inspeciona os ficheiros Python (.py) na raiz do projeto para catalogar
todas as emissões de texto (ecrã, ficheiros de relatório, alertas e registos de log),
bem como todas as invocações da função de internacionalização T().

Funcionalidades:
- Rastreia saídas de texto e diálogos: print(), input(), .write(), tee(), logger,
  send_notification() e chamadas diretas a T().
- Permite validar a padronização das mensagens base em inglês e localizar
  eventuais textos remanescentes noutros idiomas.
- Descarta linhas puramente cosméticas (separadores visuais e quebras de linha isoladas).
- Executa a partir do subdiretório 'utilitarios', apontando a pesquisa exclusivamente
  para a pasta-mãe (raiz do projeto) de modo não recursivo.
- Exporta o inventário estruturado (ficheiro.py; linha; conteudo) na raiz do projeto.
"""
import os

# Caminho absoluto da pasta-mãe (raiz do projeto)
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_PAI = os.path.dirname(DIR_SCRIPT)

def auditar_todas_mensagens():
    alvos = ['print(', 'input(', '.write(', 'tee(', 'logger.', 'send_notification(', 'T(']
    
    # Linhas de formatação estética sem texto relevante
    ignorar_exatos = [
        'print()', 'print("")', "print('')", 
        'print("\\n")', "print('\\n')",
        'print("="*45)', "print('='*45)",
        'print("\\n" + "="*45)', "print('\\n' + '='*45)",
        'print("-" * 45)', "print('-' * 45)"
    ]
    
    arquivo_saida = os.path.join(DIR_PAI, 'auditoria_todas_mensagens.txt')
    total_encontradas = 0
    arquivos_analisados = 0
    
    with open(arquivo_saida, 'w', encoding='utf-8') as out:
        out.write("AUDITORIA GERAL DE MENSAGENS E STRINGS\n")
        out.write("Formato: arquivo.py; linha; conteudo_da_linha\n")
        out.write("="*65 + "\n\n")
        
        # Percorre apenas os ficheiros na pasta-mãe (não recursivo)
        for item in sorted(os.listdir(DIR_PAI)):
            caminho_item = os.path.join(DIR_PAI, item)
            
            if os.path.isfile(caminho_item) and item.endswith('.py'):
                arquivos_analisados += 1
                try:
                    with open(caminho_item, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()
                        
                    for num, linha in enumerate(linhas, start=1):
                        linha_limpa = linha.strip()
                        
                        # Ignora comentários
                        if linha_limpa.startswith('#'):
                            continue
                            
                        # Verifica se contém algum dos métodos de saída ou a função T(
                        if any(alvo in linha_limpa for alvo in alvos):
                            linha_sem_espacos = linha_limpa.replace(" ", "")
                            se_ignorar = any(ign.replace(" ", "") == linha_sem_espacos for ign in ignorar_exatos)
                            
                            if not se_ignorar:
                                out.write(f"{item}; {num}; {linha_limpa}\n")
                                total_encontradas += 1
                except Exception as e:
                    print(f"Erro ao processar {item}: {e}")

    print("✅ Varredura completa concluída!")
    print(f"📂 Ficheiros analisados na raiz: {arquivos_analisados}")
    print(f"📄 Linhas registadas: {total_encontradas}")
    print(f"📂 Ficheiro gerado: '{arquivo_saida}'")

if __name__ == "__main__":
    auditar_todas_mensagens()