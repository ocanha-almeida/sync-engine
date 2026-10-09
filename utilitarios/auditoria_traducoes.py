#!/usr/bin/env python3
"""
Auditoria de Cobertura de Internacionalização (i18n).

Este script inspeciona os arquivos Python (.py) na raiz do projeto em busca
de mensagens e textos enviados para telas, logs e relatórios que possam estar
sem o tratamento da função de tradução T().

Funcionalidades:
- Analisa instruções de saída comuns: print(), input(), .write(), tee(),
  chamadas de logger e send_notification().
- Identifica ocorrências que não utilizam o invólucro T().
- Ignora linhas puramente estéticas ou de formatação vazia.
- Opera a partir da pasta 'utilitarios' e direciona a varredura exclusivamente
  para a pasta-mãe (raiz do projeto) de forma não recursiva.
- Gera um relatório detalhado formatado (arquivo.py; linha; conteudo).
"""
import os

# Caminho absoluto da pasta-mãe (raiz do projeto)
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_PAI = os.path.dirname(DIR_SCRIPT)

def auditar_codigo():
    # Fragmentos que indicam saída de texto
    alvos = ['print(', 'input(', '.write(', 'tee(', 'logger.', 'send_notification(']
    
    # Falsos positivos comuns (linhas que imprimem apenas formatação ou espaços e não precisam de tradução)
    ignorar_exatos = [
        'print()', 'print("")', "print('')", 
        'print("\\n")', "print('\\n')",
        'print("="*45)', "print('='*45)",
        'print("\\n" + "="*45)', "print('\\n' + '='*45)",
        'print("-" * 45)', "print('-' * 45)"
    ]
    
    arquivo_saida = os.path.join(DIR_PAI, 'linhas_sem_traducao.txt')
    encontrados = 0
    arquivos_analisados = 0
    
    with open(arquivo_saida, 'w', encoding='utf-8') as out:
        out.write("RELATÓRIO DE AUDITORIA DE TRADUÇÕES\n")
        out.write("Formato: arquivo.py; linha; conteudo_da_linha\n")
        out.write("="*60 + "\n\n")
        
        # Percorre apenas os arquivos na pasta-mãe (não recursivo)
        for item in sorted(os.listdir(DIR_PAI)):
            caminho_item = os.path.join(DIR_PAI, item)
            
            if os.path.isfile(caminho_item) and item.endswith('.py'):
                arquivos_analisados += 1
                try:
                    with open(caminho_item, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()
                        
                    for num, linha in enumerate(linhas, start=1):
                        linha_limpa = linha.strip()
                        
                        # Pula comentários
                        if linha_limpa.startswith('#'):
                            continue
                            
                        # Verifica se a linha contém algum dos métodos de saída
                        if any(alvo in linha_limpa for alvo in alvos):
                            # Se não possui a função T(, é suspeita
                            if 'T(' not in linha_limpa:
                                # Filtra os falsos positivos (quebras de linha, linhas decorativas)
                                linha_sem_espacos = linha_limpa.replace(" ", "")
                                se_ignorar = any(ign.replace(" ", "") == linha_sem_espacos for ign in ignorar_exatos)
                                
                                if not se_ignorar:
                                    out.write(f"{item}; {num}; {linha_limpa}\n")
                                    encontrados += 1
                except Exception as e:
                    print(f"Erro ao ler {item}: {e}")

    print("✅ Varredura concluída!")
    print(f"📂 Arquivos analisados na raiz: {arquivos_analisados}")
    print(f"⚠️  Foram encontradas {encontrados} linhas suspeitas.")
    print(f"📄 Relatório salvo em: '{arquivo_saida}'")

if __name__ == "__main__":
    auditar_codigo()