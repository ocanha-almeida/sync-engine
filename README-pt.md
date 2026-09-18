<div align="right">
  <a href="README.md">🇺🇸 English</a> | <span>🇧🇷 Português</span>
</div>

# 🔄 Sync Engine - Gerenciador Multi-Contas para Rclone (v7.0)

Um motor de sincronização em nuvem bidirecional inteligente, interativo e seguro, construído sobre o poderoso `rclone bisync`. Projetado para Linux e Windows, ele transforma a complexidade do Rclone em uma experiência fluida através de um assistente CLI completo.

Nascido da necessidade de superar as limitações dos clientes de nuvem tradicionais, este projeto tem foco pesado em sincronização automática em segundo plano, proteção nativa contra exclusões acidentais, limites rígidos de banda/tamanho e bloqueio cirúrgico de pastas.

## ✨ Principais Funcionalidades (Atualizado v7.0)

*   **Configuração Granular por Conta:** Regras de exclusão e limites máximos de tamanho de arquivo (`MAX_SIZE`) agora são definidos individualmente para cada nuvem conectada, oferecendo flexibilidade total entre provedores gratuitos e servidores dedicados.
*   **Analisador de Erros e Assistente de Reconexão (`analyze`):** Esqueça logs confusos. O motor traduz falhas do Rclone em diagnósticos legíveis. A versão 7.0 agora detecta automaticamente tokens de segurança expirados (Microsoft OneDrive/Google Drive) e aciona o navegador para renovação imediata com um clique.
*   **Bloqueio Bidirecional Inteligente (`.nosync`):** Crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta (seja no seu computador ou diretamente na nuvem) e o motor irá ignorá-la instantaneamente.
*   **Relatórios Isolados e Padronizados:** Todos os logs de histórico (Automático, Manual, Dry-Run, Higienizador e Tamanho) são gerados com carimbos de data/hora (timestamps) no cabeçalho e isolados por conta na pasta de sua escolha.
*   **Relatório de Tamanho Duplo:** A auditoria de arquivos grandes varre simultaneamente o seu disco local e a nuvem remota, exibindo resultados formatados de forma legível para humanos (MB e GB).
*   **Higienizador de Nomes Nativo (`clean`):** Varre suas pastas locais em busca de caracteres especiais que causam erros de upload, mostra uma prévia segura das alterações e gera um relatório detalhado preservando os filtros ativos.
*   **Auto-Healing e Quebra de Cadeado (Lock Files):** O script detecta falhas críticas de API e arquivos de trava presos, quebrando os cadeados automaticamente e executando varreduras profundas de cura (`--resync`).
*   **Auto-Desinstalação Segura:** Esqueça scripts externos. O próprio motor agora possui uma rotina de auto-destruição limpa (Opção 16) protegida por um desafio de texto (CAPTCHA), garantindo que nada seja removido por acidente.
*   **Serviço de Segundo Plano (Systemd / Task Scheduler):** Roda silenciosamente a nível de usuário, permitindo inicialização automática sem exigir privilégios administrativos para tarefas diárias.

---

## ⚙️ Pré-requisitos e Instalação

O projeto é multiplataforma, rodando nativamente como um serviço de background tanto no **Linux** quanto no ecossistema **Windows 10/11**.

### Dependências
As ferramentas base exigidas pelo motor são:
*   `python3` (O motor de execução)
*   `rclone` (O motor de transferência)
*   `sqlite3` (Para indexação rápida de metadados)

**🐧 No Linux:**
Todos os pacotes e dependências são baixados e configurados automaticamente pelo script `install-linux.sh`.

**🪟 No Windows:**
Você deve baixar e instalar estas ferramentas manualmente antes de rodar o instalador. Certifique-se de marcar a opção **"Add to PATH"** durante a instalação:
*   **Python 3:** [Baixar Instalador Windows](https://www.python.org/downloads/windows/)
*   **Rclone:** [Baixar Rclone](https://rclone.org/downloads/) *(Extraia o `.exe` e coloque em uma pasta no seu PATH, ex: `C:\Windows`)*
*   **SQLite3:** [Baixar SQLite Tools](https://www.sqlite.org/download.html) *(Extraia o `.exe` e coloque no seu PATH)*

### Instalação Passo-a-Passo

1. **Clone este repositório para o seu computador:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Execute o instalador correto para o seu Sistema Operacional:**
   * 🐧 **No Linux:** Dê um duplo-clique no arquivo `install-linux.sh` e escolha "Executar no Terminal", ou rode `bash ./install-linux.sh` no terminal.
   * 🪟 **No Windows:** Apenas dê um duplo-clique no arquivo `install-windows.cmd` localizado dentro da pasta clonada.

3. **Configure suas contas de nuvem:**
   Abra um terminal qualquer e execute (como usuário padrão, NÃO use sudo/admin):
   ```bash
   rclone config
   ```
   *(Siga as instruções do Rclone para vincular seus provedores).*

---

## 💻 Referência de Comandos (CLI)

O Sync Engine pode ser operado pelo assistente interativo ou por atalhos diretos no terminal. Uso básico: `sync-engine [COMANDO]`

| Comando | Descrição |
| :--- | :--- |
| `config` | Abre o Assistente Interativo (Menu Principal). |
| `now` | 🚀 Força uma Sincronização Imediata (Exibe barras de progresso). |
| `test` | 🧪 Inicia o modo Dry-Run interativo por conta (Simulação segura). |
| `clean` | 🧹 Inicia o higienizador de nomes (Gera relatório e respeita filtros). |
| `analyze` | 🔎 Analisa os relatórios automáticos/manuais recentes e oferece soluções. |
| `doctor` | 🩺 Checa a saúde do sistema (Dependências e permissões). |
| `update` | 🔄 Baixa e instala a versão mais recente do GitHub. |
| `start` / `stop` / `reload`| LIGA, DESLIGA ou RECARREGA o serviço invisível de background. |
| `status` | Exibe o status atual do serviço e captura os logs recentes na memória. |

*(Dica: Enviar um comando inválido agora exibe automaticamente o menu de Ajuda e encerra a operação com segurança).*

---

## 🛠️ Guia do Assistente Interativo (`sync-engine config`)

O menu interativo foi expandido para suportar o gerenciamento granular da versão 7.0:

1. **Configuração de Contas (Opções 1 a 3):** Adicione, liste ou remova vínculos de pastas locais com suas nuvens. Remover uma conta aciona uma coleta de lixo inteligente.
2. **Configurações Globais (Opção 4):** Altere intervalos de sincronização, limites globais de banda (`BW_LIMIT`), defina o diretório absoluto para salvar relatórios, e controle o bloqueio automático contra colisões de case-sensitivity.
3. **Filtros e Limites por Conta (Opção 5):** Escolha uma conta específica para atribuir limites de tamanho customizados e manipular a lista de exclusões (arquivos/pastas ignorados).
4. **Ações Extras e Relatórios (Opções 6 a 11):** Atalhos rápidos para sincronização (`now`), simulação (`test`), relatório de arquivos grandes locais/remotos, higienizador, analisador de erros e doutor do sistema.
5. **Controle do Motor (Opções 12 a 16):** Interface amigável para ligar, desligar, checar status, atualizar ou acionar a **Auto-Desinstalação** do sistema completo.

---

## 🎯 Guia de Filtros e Exclusões

Para evitar a sincronização de pastas ou arquivos indesejados, utilize as seguintes sintaxes ao adicionar um filtro na **Opção 5**:

*   **Ignorar Case (Sensibilidade a Maiúsculas):** `(?i)*.tmp` *(Ignora tanto `log.tmp` quanto `LOG.TMP` em qualquer sistema operacional).*
*   **Correspondência Exata:** `venv` ou `.git`
*   **Início do Nome de Arquivo:** `Prefixo*` *(Ex: `Backup*` bloqueia qualquer arquivo/pasta que comece com essa palavra).*
*   **Curinga de Texto (`*`):** `*.bak`
*   **Âncora de Raiz (`/`):** `/Backups` *(Bloqueia a pasta "Backups", mas *apenas* se ela estiver exatamente na raiz do seu diretório de sincronização).*
*   **Arquivos Ocultos na Raiz (Linux):** `/.*` *(Bloqueia pastas/arquivos ocultos como `.bashrc` ou `.config`, mas *apenas* se estiverem localizados no nível raiz).*
*   **Bloqueador Universal:** Apenas crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta que deseje bloquear permanentemente.

---

## 💡 Servidor Contínuo Automático (Linger / Logon)

Para transformar o seu PC em um verdadeiro "servidor":
*   **No Linux:** O script de instalação habilita automaticamente o recurso Linger (`loginctl enable-linger`). Isso permite que o motor de sincronização inicie imediatamente após o boot do sistema, mesmo que a máquina pare na tela de bloqueio de usuário.
*   **No Windows:** Uma tarefa invisível é criada no Agendador de Tarefas vinculada ao gatilho de *Logon* do usuário, garantindo inicialização limpa e silenciosa assim que a área de trabalho for carregada.

---

## ⚠️ Limitações Conhecidas

1. **Não é Tempo Real (Inotify):** O script não monitora cliques no disco ativamente. Ele opera em janelas cíclicas de varredura (padrão: a cada 5 minutos).
2. **Ignora Symlinks:** Para prevenir loops infinitos, o motor não copia e nem segue atalhos de sistema.
3. **Tempo de Resync Inicial:** Na primeiríssima execução de uma conta, o motor rodará uma varredura profunda (`--resync`), o que pode demorar alguns minutos. Nas próximas vezes será quase instantâneo.
4. **Cofres Pessoais:** O motor bloqueia acesso ao *Personal Vault* do OneDrive por padrão para evitar falhas de permissão de leitura de API.

---

## 🗑️ Desinstalação

O método via script instalador externo (`.cmd` e `.sh`) foi descontinuado na versão 7.0 para evitar problemas de incompatibilidade de versão (*version mismatch*).

Para remover completamente o Sync Engine (limpando o executável raiz, atalhos do sistema e desligando os serviços de background invisíveis):
1. Abra o terminal e digite `sync-engine config`
2. Selecione a **Opção 16 (Desinstalar o Sync Engine)**
3. O sistema solicitará um código aleatório em texto (CAPTCHA) para confirmar a exclusão.
4. Você poderá escolher se deseja manter ou apagar definitivamente seu histórico de configurações e relatórios antigos da pasta `.config`.
5. O programa se autodestruirá com segurança em 3 segundos.