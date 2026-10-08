<div align="right">
  <a href="README.md">🇺🇸 English</a> | <span>🇧🇷 Português</span>
</div>

# 🔄 Sync Engine - Gerenciador Multi-Conta Rclone (v7.2.4)

Um motor de sincronização bidirecional em nuvem inteligente, interativo e seguro, construído sobre o poderoso `rclone bisync`. Projetado para Linux e Windows, ele transforma a complexidade do Rclone em uma experiência fluida através de um assistente CLI abrangente.

Nascido da necessidade de superar as limitações dos clientes de nuvem tradicionais, este projeto foca fortemente em sincronização automática em segundo plano, proteção nativa contra exclusões acidentais, limites rígidos de banda/tamanho e bloqueio bidirecional cirúrgico de pastas.

## ✨ Principais Recursos (Atualizado v7.2.4)

*   **Internacionalização Nativa (i18n):** O motor agora detecta automaticamente o idioma do seu sistema operacional e traduz dinamicamente toda a interface CLI e os relatórios gerados. Atualmente com suporte nativo em **Inglês**, **Português**, **Espanhol**, **Francês**, **Alemão**, **Italiano**, **Japonês** e **Chinês Simplificado**, com um Seletor de Idiomas dinâmico embutido nas Configurações Globais.
*   **Agendador de Tarefas Integrado (Cron):** Agende sincronizações em segundo plano (Normais ou Forçadas) e Migrações Nuvem-para-Nuvem para horários e datas específicas, tudo gerenciado diretamente no assistente interativo, sem precisar depender dos agendadores de tarefas do sistema operacional.
*   **Migração Nuvem-para-Nuvem:** Transfira arquivos diretamente entre provedores distintos (ex: OneDrive para Google Drive) usando a memória RAM do seu sistema, preservando o espaço em disco local e ignorando pastas bloqueadas (`.nosync`) de forma inteligente.
*   **Montagem de Drive Virtual:** Transforme qualquer nuvem em um "pendrive virtual" perfeitamente integrado ao seu SO (suporte nativo via Systemd no Linux e Unidade de Rede no Windows).
*   **Configuração Granular de Contas:** Regras de exclusão e limites máximos de tamanho de arquivo (`MAX_SIZE`) agora são definidos individualmente para cada nuvem conectada.
*   **Analisador de Erros & Auto-Reconexão (`analyze`):** Esqueça os logs confusos. O motor traduz as falhas do Rclone em diagnósticos legíveis. Detecta automaticamente tokens de segurança expirados e abre o seu navegador para renovação instantânea com 1 clique.
*   **Bloqueio Bidirecional Inteligente (`.nosync`):** Crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta (localmente ou diretamente na nuvem) e o motor irá ignorá-la instantaneamente.
*   **Relatórios Isolados e Padronizados:** Todos os históricos de logs são gerados com carimbos de data/hora no cabeçalho e isolados por conta na pasta de sua escolha.
*   **Higienizador Nativo de Nomes (`clean`):** Varre suas pastas locais em busca de caracteres especiais que causam erros de upload na nuvem, mostra uma pré-visualização segura e gera um relatório detalhado.
*   **Auto-Cura & Auto-Desbloqueio:** O script detecta falhas críticas de API e arquivos de bloqueio (lock files) travados, quebrando os bloqueios automaticamente e realizando ressincronizações profundas (`--resync`) para se recuperar.
*   **Auto-Desinstalação Segura:** O motor agora possui uma rotina de autodestruição limpa, protegida por um desafio de texto (CAPTCHA).
*   **Serviço em Segundo Plano:** Roda silenciosamente a nível de usuário, permitindo o início automático sem exigir privilégios administrativos para tarefas diárias.

---

## ⚙️ Pré-requisitos e Instalação

O projeto é multiplataforma e roda nativamente como um serviço em segundo plano nos ecossistemas **Linux** e **Windows 10/11**.

### Dependências
As ferramentas essenciais exigidas pelo motor são:
*   `python3` (O ambiente de execução)
*   `rclone` (O motor central de transferência)
*   `sqlite3` (Para indexação rápida de metadados)

**🐧 No Linux:**
Não se preocupe, todas as dependências são baixadas e configuradas automaticamente pelo nosso script `install-linux.sh`. O suporte ao drive virtual utiliza o pacote nativo `fuse` do sistema.

**🪟 No Windows:**
Você deve baixar e instalar estas ferramentas manualmente antes de executar o instalador. Certifique-se de marcar a opção **"Add to PATH"** (Adicionar ao PATH) durante a instalação:
1.  **Python 3:** [Baixar Instalador do Windows](https://www.python.org/downloads/windows/)
2.  **Rclone:** [Baixar Rclone](https://rclone.org/downloads/) *(Extraia o `.exe` e coloque-o em uma pasta no seu PATH, ex: `C:\Windows`)*
3.  **SQLite3:** [Baixar Ferramentas SQLite](https://www.sqlite.org/download.html) *(Extraia o `.exe` e coloque-o no seu PATH)*
4.  **WinFsp:** [Baixar WinFsp](https://winfsp.dev/) *(Exigido **APENAS** se você planeja usar o recurso de Montagem de Drive Virtual).*

### Instalação Passo a Passo

1. **Clone este repositório para o seu computador:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Execute o instalador correto para o seu SO:**
   * 🐧 **No Linux:** Clique duas vezes no arquivo `install-linux.sh` e escolha "Executar no Terminal", ou rode `bash ./install-linux.sh` via CLI.
   * 🪟 **No Windows:** Basta clicar duas vezes no arquivo `install-windows.cmd` localizado na pasta clonada.

3. **Configure suas contas de nuvem:**
   Tanto no Windows quanto no Linux, abra um terminal e execute (como usuário padrão, NÃO use sudo/admin):
   ```bash
   rclone config
   ```
   *(Siga as instruções do Rclone para configurar os seus remotos de nuvem).*

---

## 💻 Referência de Comandos CLI

O Sync Engine pode ser operado via assistente interativo ou atalhos diretos no terminal. Uso básico: `sync-engine [COMANDO]`

| Comando | Descrição |
| :--- | :--- |
| `config` | Abre o Assistente Interativo (Menu principal). |
| `now` | 🚀 Força uma Sincronização imediata (exibe barra de progresso). |
| `test` | 🧪 Inicia o modo interativo de Test-Drive por conta (Simulação segura). |
| `clean` | 🧹 Inicia o higienizador de nomes de arquivo (Gera relatório e respeita filtros). |
| `analyze` | 🔎 Analisa relatórios recentes (manuais/automáticos) e fornece soluções acionáveis. |
| `doctor` | 🩺 Executa um diagnóstico de saúde do sistema (dependências e permissões). |
| `update` | 🔄 Baixa e instala a última versão do GitHub. |
| `start` / `stop` / `reload` | LIGA, DESLIGA ou RECARREGA o serviço invisível em segundo plano. |
| `status` | Exibe o status atual do serviço e os logs recentes da memória. |

---

## 🛠️ Guia do Assistente Interativo (`sync-engine config`)

O menu interativo foi totalmente categorizado para suportar um gerenciamento granular:

1. **Configuração de Conta:** Adicione, liste, edite ou remova vínculos de pastas locais com suas nuvens. Cada conta possui um painel próprio para gerenciar limites máximos de tamanho, padrões de exclusão e drives montados ativos.
2. **Configurações Globais:** Altere o idioma do sistema, intervalos globais de sincronização, limites de banda (`BW_LIMIT`), defina o caminho absoluto da pasta para relatórios salvos e alterne o bloqueio por diferenciação de maiúsculas/minúsculas.
3. **Sincronização:** Atalhos para execução imediata (`now`), simulação (`test`) e o **Agendador de Tarefas (Cron)** para automatizar rotinas em datas e horários específicos.
4. **Manutenção:** Acesse os Relatórios de Arquivos Grandes, o Higienizador de Nomes, o Analisador de Erros de Sincronização e o Diagnóstico do Sistema (Doctor).
5. **Ações Extras:** Configure **Migrações Nuvem-para-Nuvem** e **Montagens de Drive Virtual**.
6. **Motor em Segundo Plano:** Interface amigável para iniciar, parar, verificar o status, atualizar o aplicativo ou acionar a **Auto-Desinstalação** do sistema.

---

## 🎯 Guia de Filtros e Exclusões

Para evitar a sincronização de pastas ou arquivos indesejados, utilize as seguintes sintaxes ao adicionar um filtro a uma conta:

*   **Ignorar Maiúsculas/Minúsculas (Case Insensitive):** `(?i)*.tmp` *(Ignora tanto `log.tmp` quanto `LOG.TMP` em qualquer SO).*
*   **Correspondência Exata:** `venv` ou `.git`
*   **Início do Nome de Arquivo:** `Prefixo*` *(ex: `Backup*` bloqueia qualquer arquivo/pasta que comece com essa palavra).*
*   **Curinga de Texto (`*`):** `*.bak`
*   **Âncora de Raiz (`/`):** `/Backups` *(Bloqueia a pasta "Backups", mas *apenas* se ela estiver exatamente na raiz do seu diretório de sincronização).*
*   **Arquivos Ocultos na Raiz (Linux):** `/.*` *(Bloqueia arquivos/pastas ocultos como `.bashrc` ou `.config`, mas *apenas* se estiverem no nível raiz).*
*   **Bloqueador Universal:** Basta criar um arquivo vazio chamado `.nosync` dentro de qualquer pasta que você deseja bloquear permanentemente.

---

## 💡 Servidor Contínuo Automático (Linger / Logon)

Para transformar o seu PC em um verdadeiro "servidor":
*   **No Linux:** O script de instalação habilita automaticamente o recurso Linger (`loginctl enable-linger`). Isso permite que o motor de sincronização inicie imediatamente após o boot do sistema, mesmo se a máquina ficar parada na tela de bloqueio.
*   **No Windows:** Uma tarefa invisível é criada no Agendador de Tarefas vinculada ao gatilho de *Logon* do usuário, garantindo um início limpo e silencioso assim que a área de trabalho carregar.

---

## 🗑️ Desinstalação

Para remover completamente o Sync Engine do seu sistema (limpando o executável raiz, atalhos do sistema e desligando os serviços em segundo plano):
1. Abra o seu terminal e digite `sync-engine config`
2. Selecione **Desinstalar Sync Engine** na seção do Motor em Segundo Plano.
3. O sistema solicitará um desafio de texto aleatório (CAPTCHA) para confirmar a exclusão.
4. Você será questionado se deseja manter ou excluir permanentemente o seu histórico de configurações e relatórios antigos.
5. O software irá se autodestruir com segurança.