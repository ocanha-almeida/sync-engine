# Como Adicionar um Novo Idioma ao Sync Engine

O Sync Engine suporta a adição fácil de novos idiomas. Você não precisa de conhecimentos de programação para traduzir o sistema para a sua língua nativa. Basta seguir os passos abaixo.

## 1. Localizar a pasta de idiomas
Vá até a pasta onde o Sync Engine está instalado ou onde você o executa.
Dentro dela, procure por uma subpasta chamada `locales/`. É aqui que todos os arquivos de tradução ficam guardados.

## 2. Criar o seu arquivo de idioma
Em vez de criar um arquivo do zero, o jeito mais fácil é usar uma tradução existente como molde:
1. Dentro da pasta `locales/`, faça uma cópia de qualquer arquivo existente (por exemplo, `es.json` ou `pt.json`).
2. Renomeie esse novo arquivo para o código do idioma que você deseja criar (por exemplo, `ru.json` para Russo, `ko.json` para Coreano, `nl.json` para Holandês).

## 3. Como traduzir
Abra o seu novo arquivo `.json` em qualquer editor de texto simples (como o Bloco de Notas no Windows ou o TextEdit no Mac).

O conteúdo do arquivo é uma lista com a seguinte estrutura:
```json
    "account details": "DETALHES DA CONTA",
    "active filters": "Filtros Ativos",
    "add filter": "Adicionar Filtro",
```

**Regras de Ouro para a Tradução:**
*   **Nunca altere o lado esquerdo:** O texto antes dos dois pontos (`:`) e entre aspas é o código interno que o sistema usa para encontrar a frase. Ele deve permanecer exatamente como está (em inglês).
*   **Traduza apenas o lado direito:** Substitua o texto que está após os dois pontos pela sua tradução.
*   **Mantenha a pontuação:** Se o texto original tiver símbolos ou formatações especiais (como `[1]`, `(Y/N)`, `...`), tente mantê-los na sua tradução para que a interface continue alinhada.

Exemplo após a tradução para o Russo:
```json
    "account details": "ДЕТАЛИ УЧЕТНОЙ ЗАПИСИ",
    "active filters": "Активные фильтры",
    "add filter": "Добавить фильтр",
```

Salve o arquivo após concluir as traduções.

## 4. Ativar o novo idioma
O Sync Engine reconhece automaticamente qualquer novo idioma adicionado.

1. Abra o Sync Engine.
2. No menu principal, vá em **Global Settings** (Configurações Globais).
3. Escolha a opção **Language** (Idioma).
4. O seu novo idioma aparecerá automaticamente na lista (ex: `RU`).
5. Selecione-o, feche o Sync Engine e abra-o novamente. A interface carregará instantaneamente com a sua nova tradução!