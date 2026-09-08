<div align="right">
  <a href="README.md">🇺🇸 English</a> | <span>🇧🇷 Português</span>
</div>

# 🔄 Sync Engine - Multi-Account Rclone Manager

Um motor inteligente, interativo e seguro para sincronização bidirecional em nuvem, construído sobre o poderoso `rclone bisync`. Projetado exclusivamente para Linux e Windows, ele transforma a complexidade do Rclone em uma experiência fluida através de um assistente de terminal (CLI) completo.

Nascido da necessidade de superar as limitações de clientes tradicionais, este projeto traz foco total em sincronização automática de fundo, proteção nativa contra exclusões acidentais, controle rígido de banda/tamanho e bloqueio cirúrgico de pastas de forma bidirecional.

## ✨ Principais Recursos

*   **Bloqueio Inteligente Bidirecional (`.nosync`):** Crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta (seja no seu computador **ou direto na nuvem**) para que o motor a ignore instantaneamente. A leitura remota garante que diretórios indesejados na nuvem nunca sejam baixados acidentalmente, sem a necessidade de editar arquivos de configuração globais.
*   **Assistente CLI Interativo:** Um menu completo para gerenciar contas, filtros, serviços e gerar relatórios.
*   **Higienizador Nativo (`clean`):** Varre suas pastas locais em busca de caracteres especiais que causam erros de upload na nuvem. Exibe uma pré-visualização, respeita rigorosamente suas regras de filtro e `.nosync`, exige confirmação do usuário e gera um relatório detalhado de alterações.
*   **Analisador de Erros (`analyze`):** Esqueça logs confusos. O motor lê os relatórios de falha do Rclone e traduz problemas comuns (como *eTag Mismatch* ou *Lock Files* emperrados) em diagnósticos e soluções fáceis de aplicar.
*   **Auto-Atualizador (`update`):** Verifica, baixa e instala novas versões do script diretamente do repositório no GitHub com um único comando.
*   **Suporte Multi-Contas:** Conecte simultaneamente Google Drive, OneDrive, Dropbox, S3, ou qualquer outro provedor suportado pelo Rclone.
*   **Filtros Avançados:** Defina exclusões globais utilizando curingas, limite de tamanho de arquivo (`MAX_SIZE`) e limite de uso de banda (`BW_LIMIT`).
*   **Serviço em Segundo Plano (Systemd / Task Scheduler):** Roda invisível no seu nível de usuário, com suporte a inicialização automática desde o boot (sem necessidade de privilégios de administrador para a sincronização diária).
*   **Relatórios Exportáveis:** Gere relatórios seguros de simulação (Dry-Run), histórico de sincronizações manuais e listagens de arquivos bloqueados por tamanho, salvos em texto puro na pasta de sua escolha.
*   **Notificações no Desktop:** Avisos nativos sobre sucesso ou erros na sincronização (suportado no Linux via `notify-send` e no Windows via balões de notificação do PowerShell).
*   **Auto-Cura e Auto-Unlocker:** O script detecta falhas críticas da API e travas residuais (lock files), realizando a quebra do cadeado e a varredura de cura automaticamente.

---

## ⚙️ Pré-requisitos e Instalação

O projeto é multiplataforma, rodando nativamente como serviço de fundo tanto em ecossistemas **Linux** quanto **Windows 10/11**.

### Dependências
As ferramentas base exigidas pelo motor são:
*   `python3` (A linguagem base do sistema)
*   `rclone` (O motor central de transferência)
*   `sqlite3` (Para indexação rápida de metadados)

**🐧 No Linux:**
Não se preocupe, todas as dependências são baixadas e configuradas automaticamente pelo nosso script `install.sh`.

**🪟 No Windows:**
Você precisa baixar e instalar estas ferramentas manualmente antes de rodar o instalador. Certifique-se de marcar a opção **"Add to PATH"** (Adicionar à variável de ambiente) durante as instalações:
1.  **Python 3:** [Baixar Instalador do Windows](https://www.python.org/downloads/windows/)
2.  **Rclone:** [Baixar Rclone](https://rclone.org/downloads/) *(Extraia o `.exe` e coloque-o em uma pasta no seu PATH, ex: `C:\Windows`)*
3.  **SQLite3:** [Baixar SQLite Tools](https://www.sqlite.org/download.html) *(Extraia o `.exe` e coloque-o em uma pasta no seu PATH)*

### Instalação Passo a Passo

1. **Clone este repositório no seu computador:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Execute o instalador de acordo com o seu sistema:**
   * 🐧 **No Linux:** Abra o terminal e execute:
     ```bash
     sudo ./install.sh
     ```
   * 🪟 **No Windows:** Localize a pasta clonada, clique com o botão direito sobre o arquivo `install.ps1` e selecione **"Executar com o PowerShell"**. *(Uma tela azul pedirá permissão de Administrador; basta confirmar).*

3. **Configure as suas contas de nuvem:**
   Tanto no Windows quanto no Linux, abra um terminal e digite (com o seu usuário comum, NÃO use sudo/admin):
   ```bash
   rclone config
   ```
   *(Siga as instruções do Rclone para criar suas conexões na nuvem).*

---

## 💻 Referência de Comandos (CLI)

O Sync Engine pode ser operado via interface interativa ou através de atalhos diretos no terminal.

Uso básico: `sync-engine [COMANDO]`

| Comando | Descrição |
| :--- | :--- |
| `config` | Abre o Assistente Interativo (Menu principal). |
| `now` | 🚀 Sincroniza AGORA. Exibe barra de progresso e força o envio/download imediato. |
| `test` | 🧪 Inicia o modo de simulação (Dry-Run). Não altera nenhum arquivo. |
| `clean` | 🧹 Inicia o higienizador de nomes de arquivos (Gera relatório e respeita filtros). |
| `analyze` | 🔎 Analisa o log da última sincronização manual para dar diagnósticos de erros. |
| `doctor` | 🩺 Executa um diagnóstico de sistema verificando dependências e permissões. |
| `update` | 🔄 Baixa e instala a última versão disponível no GitHub. |
| `start` / `stop`| LIGA ou DESLIGA o serviço invisível em segundo plano. |
| `status` | Exibe o status atual do serviço e os últimos logs gerados. |
| `version` (`-v`)| Exibe a versão atual do motor. |

---

## 🛠️ Guia do Assistente Interativo (`sync-engine config`)

O menu interativo divide-se em 4 blocos principais:

1. **Configuração de Contas (Opções 1 a 3):** Adicione, liste ou remova vínculos de pastas locais com suas nuvens. Ao remover uma conta, o script faz a limpeza inteligente de lixo (bancos de dados e filtros residuais).
2. **Configurações Globais (Opções 4 e 5):** Altere o intervalo de sincronização (ex: `300s`), limite de banda (ex: `10M`), corte de arquivos gigantes (ex: `2G`) e defina a pasta de destino dos relatórios (ex: `/tmp` ou `~/Relatorios`).
3. **Ações Extras (Opções 6 a 11):** Atalhos para execução imediata (`now`), simulação (`test`), diagnóstico (`doctor`), analisador de erros (`analyze`) e o **Relatório de Tamanho**, que lista arquivos barrados pela regra de limite de tamanho de forma legível.
4. **Controle do Motor (Opções 12 a 15):** Interface amigável para ligar, desligar, ver o status do motor ou rodar o instalador de atualizações.

---

## 🎯 Guia de Filtros e Exclusões

Para evitar a sincronização de pastas ou arquivos indesejados, você pode usar dois métodos:

### Método 1: A Flag `.nosync` (Recomendado)
Basta criar um arquivo vazio com o nome exato `.nosync` dentro de qualquer diretório, seja no seu computador ou na interface web da sua nuvem. 
No próximo ciclo do motor, essa pasta e todo o seu conteúdo serão ignorados instantaneamente e bloqueados no Rclone de forma segura.

### Método 2: Filtros Globais (Menu 5 - Gerenciar Filtros)
Aplica regras gerais para todas as pastas da sua conta. Suporta as seguintes sintaxes avançadas:
*   **Nome exato:** `venv` ou `.git` (Bloqueia qualquer pasta/arquivo com esse nome, em qualquer nível).
*   **Curinga de Texto (`*`):** `*.tmp` (Bloqueia todos os arquivos que terminem com `.tmp`).
*   **Curinga de Caractere (`?`):** `cam_?.dav` (Bloqueia `cam_1.dav`, `cam_A.dav`, etc).
*   **Ancoragem na Raiz (`/`):** `/Backups` (Bloqueia a pasta "Backups", mas *apenas* se ela estiver na raiz da sua nuvem/pasta principal).

---

## 💡 Servidor Contínuo Automático (Linger / Logon)

Para transformar seu PC num verdadeiro "servidor":
*   **No Linux:** O script de instalação ativa automaticamente o recurso Linger (`loginctl enable-linger`). Isso permite que o motor inicie imediatamente após o *boot* do sistema, mesmo que a máquina fique parada na tela de bloqueio de senha. *(Nota: O Linger não é desativado na desinstalação, pois é uma permissão valiosa para o usuário).*
*   **No Windows:** A tarefa é criada no Agendador de Tarefas vinculada ao gatilho de *Logon* do usuário, garantindo que rode invisível assim que a área de trabalho for carregada.

---

## 💡 Dicas de Uso e Fluxos de Trabalho

*   **Pastas de Relatórios Efêmeras:** No menu de Configurações Globais, você pode mudar a pasta de relatórios gerados para `/tmp` (no Linux). O sistema operacional apagará seus relatórios antigos magicamente a cada reinício da máquina.
*   **Múltiplas Nuvens:** Crie uma conta no menu apontando para o Google Drive (`~/GDrive`) e outra para o OneDrive (`~/OneDrive`). O motor cuidará de ambas paralelamente com regras e bancos de dados independentes.

---

## ⚠️ Limitações Conhecidas

1. **Não é em Tempo Real (Inotify):** O script não monitora ativamente cada alteração (clique) no disco. Ele opera em janelas de varredura cíclicas (padrão: a cada 5 minutos). 
2. **Ignora Links Simbólicos (Symlinks):** Para evitar loops infinitos acidentais, o motor não copia nem segue atalhos do sistema.
3. **Tempo de Resync Inicial:** Na primeira sincronização de uma conta (ou se o histórico quebrar), o motor precisará rodar uma varredura profunda (`--resync`). Isso é feito de forma automática.
4. **Cofres Pessoais (Vaults):** Algumas nuvens exigem chaves de decriptação nativas (ex: *Personal Vault* do OneDrive). O Sync Engine as bloqueia por padrão via filtros para impedir falhas de permissão de leitura.

---

## 🗑️ Desinstalação

Para remover completamente o Sync Engine do seu sistema (limpando o executável raiz, atalhos e os serviços de fundo):

*   **No Linux:** `sudo ./install.sh uninstall`
*   **No Windows:** Clique com o botão direito no `install.ps1` e escolha "Executar com o PowerShell", digitando `uninstall` quando o script oferecer suporte ou rodando via terminal: `.\install.ps1 uninstall`

*(As suas regras `config.json` e metadados `.db` serão mantidos em `~/.config/sync_engine/` por segurança).*