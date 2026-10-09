# 🌐 Guia de Traduções e Internacionalização (i18n)

O Sync Engine suporta a adição fácil de novos idiomas. Este documento está dividido em duas partes: instruções para usuários que desejam traduzir o sistema para sua língua nativa, e documentação técnica para desenvolvedores que precisam atualizar a base de textos após modificar o código-fonte.

---

## 👤 Parte 1: Para Usuários (Como criar o seu idioma)

Você não precisa de conhecimentos de programação para traduzir o sistema. Basta seguir os passos abaixo para criar, editar e ativar a sua própria tradução.

A pasta padrão de instalação da aplicação no Windows é `C:\Users\<SeuUsuario>\sync-engine\`, e no Linux é `$HOME/.local/share/sync-engine/`.

### 1. Localizar a pasta de idiomas
Vá até a pasta onde o Sync Engine está instalado no seu computador. Dentro dela, procure por uma subpasta chamada `locales/`. É aqui que todos os arquivos de tradução ficam guardados.

### 2. Criar o seu arquivo de idioma
Em vez de criar um arquivo do zero, o jeito mais fácil é usar uma tradução existente como molde:
1. Dentro da pasta `locales/`, faça uma cópia de qualquer arquivo existente (por exemplo, `pt.json` ou `es.json`).
2. Renomeie esse novo arquivo para o código oficial do idioma que você deseja criar (por exemplo, `ru.json` para Russo, `ko.json` para Coreano, `it.json` para Italiano).

### 3. Como traduzir
Abra o seu novo arquivo `.json` em qualquer editor de texto simples (como o Bloco de Notas no Windows, Gedit no Linux ou TextEdit no Mac).

O conteúdo do arquivo é uma lista com a seguinte estrutura:
```json
    "account details": "DETALHES DA CONTA",
    "active filters": "Filtros Ativos",
    "add filter": "Adicionar Filtro",
```

**Regras de Ouro para a Tradução:**
*   **Nunca altere o lado esquerdo:** O texto antes dos dois pontos (`:`) e entre aspas é o código interno que o sistema usa para encontrar a frase. Ele deve permanecer exatamente como está (em minúsculas, geralmente em inglês).
*   **Traduza apenas o lado direito:** Substitua o texto que está após os dois pontos pela sua tradução.
*   **Mantenha a formatação:** Se o texto original tiver símbolos especiais (como `[1]`, `(Y/N)`, `...`), mantenha-os na sua tradução para que os menus continuem alinhados.

*Exemplo após a tradução para o Russo:*
```json
    "account details": "ДЕТАЛИ УЧЕТНОЙ ЗАПИСИ",
    "active filters": "Активные фильтры",
    "add filter": "Добавить фильтр",
```
Salve o arquivo após concluir as traduções.

### 4. Ativar a nova tradução no sistema
O Sync Engine reconhece automaticamente qualquer novo idioma adicionado.
1. Abra o terminal e inicie o assistente: `sync-engine config`.
2. No menu principal, vá em **Global Settings** (Configurações Globais).
3. Escolha a opção **Language** (Idioma).
4. O seu novo idioma aparecerá automaticamente na lista (ex: `RU`).
5. Selecione-o. O sistema pedirá para reiniciar. Feche e abra o Sync Engine novamente, e a interface carregará instantaneamente com a sua nova tradução.

---

## 🛠️ Parte 2: Para Desenvolvedores (Atualização via Scripts)

Quando novos recursos são adicionados ou textos são alterados nos arquivos `.py`, o ecossistema de traduções precisa ser atualizado. Para não fazer isso manualmente, o Sync Engine conta com uma suíte de automação na pasta `utilitarios/`.

Siga este fluxo exato de execução após terminar de programar uma nova funcionalidade:

### Passo 1: Extrair os novos textos (`extrair_textos.py`)
Sempre que você criar um novo `print(T("Novo texto"))`, o dicionário base fica desatualizado.
*   **O que faz:** O script varre todos os arquivos `.py` na raiz do projeto, localiza as funções `T()`, extrai o núcleo limpo da string (removendo pontuações das bordas) e gera um novo arquivo mestre chamado `dicionario_base.json`.
*   **Como usar:** Execute `python3 utilitarios/extrair_textos.py`.

### Passo 2: Sincronizar os idiomas (`sincronizar_idiomas.py`)
Agora que o dicionário base está atualizado, você precisa empurrar as novas chaves para os idiomas existentes (pt, es, etc.).
*   **O que faz:** Ele lê o `dicionario_base.json` e injeta as chaves ausentes em todos os `.json` da pasta `locales/`.
*   **A Mágica:** As traduções que já existiam são preservadas intactas. As **novas chaves** recebem o valor em inglês acompanhado de um marcador visual (ex: `"nova chave": "✏️ New key"`). O script também remove chaves "órfãs" que não existem mais no código-fonte.
*   **Como usar:** Execute `python3 utilitarios/sincronizar_idiomas.py`. Depois, basta abrir os arquivos `.json`, buscar pelo ícone `✏️`, traduzir e salvar.

> **💡 Dica Rápida: Como listar o que falta traduzir**
> Se quiser ver rapidamente no terminal quais frases ganharam o marcador "✏️" sem precisar abrir o arquivo, use os comandos abaixo na raiz do projeto:
> *   **No Linux / macOS:**
>     `grep "✏️" locales/pt.json`
> *   **No Windows (PowerShell):**
>     `Select-String -Pattern "✏️" locales\pt.json`

### Passo 3: Higienização de Código e Emojis (`limpador_i18n.py`)
A função `T()` não lida bem com emojis dentro dela (ex: `T("✅ Salvo")`), pois isso suja as chaves do JSON.
*   **O que faz:** Este script refatora automaticamente o seu código Python. Ele encontra chamadas `T()` com emojis, extrai o emoji para fora e converte a string em uma f-string formatada (transformando em `f"✅ {T('Salvo')}"`). Ele também varre a pasta `locales/` removendo espaços duplicados e emojis acidentais das chaves JSON.
*   **Como usar:** Execute `python3 utilitarios/limpador_i18n.py` e confira o `git diff`.

---

### Ferramenta Extra 1: Injeção de Traduções em Lote (`injetar_traducoes.py`)
Se você usou uma inteligência artificial ou uma ferramenta externa para traduzir as novas chaves pendentes, não precisa copiar e colar uma por uma no arquivo do idioma.
*   **O que faz:** Lê um arquivo JSON contendo novas traduções e as mescla automaticamente no arquivo de idioma oficial de destino. Ele substitui as chaves desatualizadas, adiciona as novas e reorganiza tudo em ordem alfabética automaticamente.
*   **Como usar:** Salve as novas traduções em um arquivo na raiz do projeto (ex: `novas.json`) e execute o comando apontando o destino e o arquivo novo:
    `python3 utilitarios/injetar_traducoes.py locales/pt.json novas.json`

### Ferramenta Extra 2: Auditoria de Cobertura (`auditoria_traducoes.py`)
Se você não tem certeza se esqueceu de envolver algum texto com a função `T()` durante a programação de um recurso grande:
*   **O que faz:** Varre o código em busca de comandos de saída (`print`, `logger`, `send_notification`) que **não** utilizam o invólucro `T()`, ignorando inteligentemente quebras de linha e separadores estéticos (`"="*45`).
*   **Como usar:** Execute `python3 utilitarios/auditoria_traducoes.py`. Ele gerará o relatório `linhas_sem_traducao.txt` apontando exatamente o arquivo e a linha suspeita para você corrigir.