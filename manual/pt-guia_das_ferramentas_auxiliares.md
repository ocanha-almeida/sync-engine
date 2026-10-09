# 🛠️ Guia das Ferramentas Auxiliares (Utilitários i18n)

A pasta `utilitarios/` do Sync Engine abriga uma suíte de automação desenvolvida especificamente para facilitar a manutenção do código-fonte e o ecossistema de internacionalização (i18n). 

Estes scripts evitam que os desenvolvedores precisem buscar chaves de tradução manualmente ou refatorar textos linha por linha.

Abaixo está a documentação de cada ferramenta e seu propósito.

---

## 1. O Fluxo de Extração e Sincronização

Estas são as ferramentas de uso rotineiro. Sempre que você modificar os arquivos `.py` adicionando novos textos (usando a função `T()`), você deve rodar estes scripts para atualizar os dicionários de idioma.

### 📝 `extrair_textos.py`
* **O que faz:** Varre todo o código-fonte (`.py`) do projeto buscando por ocorrências da função `T("texto")`. Ele extrai esses textos, limpa espaços e pontuações excessivas nas bordas, e compila um dicionário atualizado chamado `dicionario_base.json`.
* **Quando usar:** Imediatamente após terminar de programar uma nova funcionalidade ou alterar frases nos menus.
* **Comando:** `python3 utilitarios/extrair_textos.py`

### 🔄 `sincronizar_idiomas.py`
* **O que faz:** Pega o `dicionario_base.json` (recém-atualizado) e o compara com todos os arquivos de idioma dentro da pasta `locales/` (como `pt.json`, `en.json`). 
* **A Mágica:** Ele preserva as traduções que já existem, apaga chaves que foram removidas do código e **adiciona as novas chaves**, inserindo automaticamente o marcador `✏️ ` ao lado do texto. Isso permite que você abra o arquivo e saiba exatamente o que falta traduzir.
* **Quando usar:** Logo após rodar a extração, para preparar os arquivos `.json` para tradução.
* **Comando:** `python3 utilitarios/sincronizar_idiomas.py`

---

## 2. Ferramentas de Injeção e Refatoração

### 💉 `injetar_traducoes.py`
* **O que faz:** Permite que você traduza chaves pendentes em lote (usando IA, por exemplo) e mescle o resultado automaticamente no dicionário original. O script procura o marcador `✏️ ` no dicionário oficial, substitui pela tradução fornecida no seu arquivo temporário, e reordena o arquivo `.json` inteiro em ordem alfabética para manter a organização.
* **Quando usar:** Quando você tem um arquivo JSON separado apenas com as frases recém-traduzidas e quer injetá-las no idioma oficial sem fazer copiar e colar manual.
* **Comando:** `python3 utilitarios/injetar_traducoes.py locales/en.json traducoes_novas.json`

### 🧹 `limpador_i18n.py`
* **O que faz:** O Rclone e o terminal não lidam bem com emojis diretamente dentro das chaves de tradução JSON. Este script atua como um refatorador de código automatizado. Ele varre os seus `.py`, encontra emojis presos dentro do comando `T("✅ Salvo")`, joga o emoji para fora e transforma o código numa f-string formatada: `f"✅ {T('Salvo')}"`. Além disso, ele limpa espaços duplos remanescentes.
* **Quando usar:** Antes de fechar um *commit*, para garantir que nenhum emoji ou sujeira de formatação esteja corrompendo os índices do JSON.
* **Comando:** `python3 utilitarios/limpador_i18n.py`

---

## 3. Ferramentas de Auditoria e Cobertura

Se você construiu um menu inteiro e não tem certeza se esqueceu de envelopar algum texto com `T()`, estas ferramentas agem como fiscais de qualidade.

### 🕵️ `auditoria_traducoes.py`
* **O que faz:** Inspeciona os arquivos `.py` em busca de funções de saída visual (como `print()`, `logger.info()`, `input()`, etc.) que contenham *strings* cruas que não foram envolvidas pela função `T()`. Ele ignora sabiamente linhas que contêm apenas pontuação (como `print("-" * 50)`).
* **Resultado:** Gera um relatório chamado `linhas_sem_traducao.txt` contendo o nome do arquivo, o número da linha e o texto exato que escapou da tradução.
* **Comando:** `python3 utilitarios/auditoria_traducoes.py`

### 🕵️‍♂️ `auditoria_traducoes_2.py`
* **O que faz:** Uma versão secundária (ou aprimorada) do script de auditoria. Geralmente programada com expressões regulares (*regex*) mais agressivas para capturar casos de borda que o auditor original ignorou (por exemplo, strings hardcoded dentro de variáveis locais, blocos `match/case`, mensagens de erro do `sys.exit()`, ou menus interativos aninhados). 
* **Resultado:** Complementa a varredura primária, ajudando a garantir cobertura i18n de 100%.

---

## 🚦 O Fluxo de Trabalho Perfeito (Resumo)

Trabalhou no código? Siga esta ordem antes de lançar a versão:
1.  Rode `limpador_i18n.py` para isolar emojis dos textos.
2.  Rode `auditoria_traducoes.py` para garantir que não esqueceu o `T()` em nenhum `print`.
3.  Rode `extrair_textos.py` para criar o banco mestre base.
4.  Rode `sincronizar_idiomas.py` para espalhar os novos textos para a pasta `locales/`.
5.  Traduza os termos marcados com `✏️` (manualmente ou injetando com `injetar_traducoes.py`).