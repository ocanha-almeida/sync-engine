# 🌍 Guia de Configurações Globais (Global Settings)

Enquanto os painéis de Conta configuram regras isoladas para cada nuvem, o menu de **Configurações Globais** dita o comportamento do "cérebro" do Sync Engine. As regras definidas aqui afetam todo o sistema, o consumo de internet e o desempenho da sua máquina.

Para acessar estas opções, inicie o assistente (`sync-engine config`) e selecione **Global Settings**.

---

## 1. Idioma do Sistema (Language Selector)

O Sync Engine possui suporte nativo a múltiplos idiomas. 
*   **A Opção "Auto (System Default)":** É a configuração de fábrica recomendada. O motor lê a língua do seu sistema operacional e carrega o dicionário correspondente (ex: se o seu Windows estiver em Português, o Sync Engine carregará o arquivo `pt.json`). Se o idioma do seu PC não for suportado, ele adotará o Inglês (código base) automaticamente.
*   **Seleção Manual:** Você pode forçar qualquer idioma disponível na lista, independentemente do idioma do seu sistema operacional. A mudança é imediata na próxima vez que iniciar o aplicativo.

## 2. Limite Global de Banda (Bandwidth Limit - BW_LIMIT)

Se você trabalha com arquivos grandes (como vídeos ou bancos de dados), o Sync Engine pode consumir toda a sua largura de banda durante o upload, deixando a internet lenta para outras tarefas.
*   **Como configurar:** Você pode definir um limite global de velocidade que o Rclone deverá respeitar. Formatos aceitos incluem `500K` (500 Kilobytes por segundo) ou `2M` (2 Megabytes por segundo).
*   **Insight de Uso:** Defina `0` (Zero) para ilimitado durante a noite ou fins de semana para acelerar migrações. Durante o horário de expediente, limite a `1M` ou `2M` para garantir que a sincronização invisível não afete as suas chamadas de vídeo ou navegação.

## 3. Intervalo Global de Sincronização (Sync Interval)

Esta configuração define a frequência com que o Motor em Segundo Plano "acorda" para verificar se houve alterações nos seus arquivos.
*   **Como configurar:** O valor é definido em minutos (ex: `5`, `15`, `60`).
*   **Insight de Desempenho:** 
    *   Um intervalo de `5` minutos garante espelhamento quase em tempo real, mas consome mais CPU e gera mais chamadas (API requests) aos servidores da nuvem.
    *   Para servidores ou contas gratuitas de nuvem com limites rígidos de API, recomenda-se um intervalo de `15` a `30` minutos para evitar bloqueios temporários por excesso de tráfego (Rate Limiting).

## 4. Bloqueio de Case-Sensitivity (Maiúsculas/Minúsculas)

Ativa ou desativa a proteção global contra arquivos com nomes estruturalmente idênticos (ex: `relatorio.pdf` e `Relatorio.pdf`).
*   **Insight de Uso:** Mantenha esta opção **Ligada (ON)** se as suas nuvens são acessadas por usuários de Linux/macOS misturados com Windows. Desativar esta verificação acelera ligeiramente o tempo de varredura pré-sincronização, mas remove a sua principal proteção contra a corrupção de diretórios na nuvem.

---

## 🚨 MODO PÂNICO: Como restaurar o idioma manualmente

**O Cenário:** Você estava explorando as configurações e acidentalmente alterou o idioma para Japonês (`jp`) ou Chinês (`zh`). Como não consegue ler os menus, tornou-se impossível navegar de volta até a opção "Global Settings > Language" para reverter o erro através do assistente.

O Sync Engine salva todas as suas preferências de forma persistente em um arquivo de texto simples. Você pode forçar a restauração operando o "Modo Pânico":

### Passo a Passo da Restauração:
1.  **Feche completamente o Sync Engine** e feche as janelas do terminal.
2.  Vá até a pasta principal onde o Sync Engine está instalado. A localização padrão geralmente é:
    *   **No Linux:** `~/sync-engine/` (na pasta raiz do seu usuário).
    *   **No Windows:** `C:\Users\SeuUsuario\sync-engine\`.
3.  Procure o arquivo chamado **`config.json`**.
4.  **🛑 PASSO CRUCIAL:** Antes de abrir, faça uma **cópia de segurança** desse arquivo (ex: copie e cole renomeando para `config_backup.json`). Isso garante que você não perca suas contas se algo der errado.
5.  Abra o arquivo `config.json` original com um editor de texto simples (Bloco de Notas no Windows ou editor de texto padrão no Linux/Mac).
6.  Procure a linha que dita o idioma (estará no topo do arquivo) e você verá algo como:
    ```json
    "language": "zh",
    ```
7.  Altere apenas as letras do código do idioma para `auto`. A linha deve ficar exatamente assim:
    ```json
    "language": "auto",
    ```
8.  Salve o arquivo (`Ctrl+S`) e feche o editor. Ao reabrir o terminal e executar o Sync Engine, ele voltará a falar a língua nativa do seu sistema.

### ⚠️ AVISO DE PERIGO (Edição Estrutural)
O arquivo `config.json` é o banco de dados central do aplicativo.
*   **NUNCA remova as aspas duplas (`""`)** que envolvem as palavras.
*   **NUNCA remova a vírgula (`,`)** no final da linha (se existir).
*   Se a estrutura JSON for quebrada (por exemplo, apagar uma vírgula acidentalmente), **o Sync Engine irá falhar (Crash) no próximo arranque** ou, como medida de segurança extrema, irá apagar o arquivo corrompido e gerar um novo em branco, o que resultará na **perda imediata do registro de todas as suas contas e filtros**. Edite apenas o texto interior das aspas e feche rapidamente o arquivo.