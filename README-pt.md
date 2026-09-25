<div align="right">
  <a href="README.md">🇺🇸 English</a> | <span>🇧🇷 Português</span>
</div>

# 🔄 Sync Engine - Gerenciador Multi-Contas Rclone (v7.2)

Um motor de sincronização de nuvem bidirecional inteligente, interativo e seguro, construído sobre o poderoso `rclone bisync`. Projetado para Linux e Windows, ele transforma a complexidade do Rclone em uma experiência fluida através de um assistente CLI completo.

Nascido da necessidade de superar as limitações dos clientes de nuvem tradicionais, este projeto foca fortemente na sincronização automática em segundo plano, proteção nativa contra exclusões acidentais, limites rígidos de banda/tamanho e bloqueio cirúrgico bidirecional de pastas.

## ✨ Principais Recursos (Atualizado v7.2)

*   **Internacionalização Nativa (i18n):** O motor agora detecta automaticamente o idioma do seu sistema operacional e traduz dinamicamente toda a interface CLI e os relatórios gerados. Atualmente com suporte nativo em **Inglês**, **Português**, **Espanhol**, **Francês**, **Alemão** e **Chinês Simplificado**.
*   **Migração Nuvem-para-Nuvem:** Transfira arquivos diretamente entre provedores distintos (ex: OneDrive para Google Drive) usando a memória RAM do seu sistema, preservando o espaço em disco local e ignorando inteligentemente pastas bloqueadas (`.nosync`).
*   **Mapeamento de Disco Virtual:** Transforme qualquer nuvem em um "pen drive virtual" integrado perfeitamente ao seu SO (Suporte nativo a Systemd no Linux e Unidade de Rede no Windows).
*   **Configuração Granular de Contas:** Regras de exclusão e limites de tamanho máximo de arquivo (`MAX_SIZE`) agora são definidos individualmente para cada nuvem conectada.
*   **Analisador de Erros e Auto-Reconexão (`analyze`):** Esqueça os logs confusos. O motor traduz as falhas do Rclone em diagnósticos legíveis. Detecta automaticamente tokens de segurança expirados e abre seu navegador para renovação instantânea com 1 clique.
*   **Bloqueio Inteligente Bidirecional (`.nosync`):** Crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta (localmente ou diretamente na nuvem) e o motor irá ignorá-la instantaneamente.
*   **Relatórios Isolados e Padronizados:** Todos os logs de histórico são gerados com carimbos de data/hora no cabeçalho e isolados por conta na pasta de sua escolha.
*   **Higienizador Nativo de Nomes de Arquivos (`clean`):** Escaneia suas pastas locais em busca de caracteres especiais que causam erros de upload na nuvem, mostra uma prévia segura e gera um relatório detalhado.
*   **Auto-Cura e Auto-Desbloqueio:** O script detecta falhas críticas de API e arquivos de bloqueio (lock files) travados, quebrando automaticamente os bloqueios e realizando ressincronizações profundas (`--resync`) para se recuperar.
*   **Auto-Desinstalação Segura:** O motor agora possui uma rotina de autodestruição limpa (Opção 18) protegida por um desafio de texto (CAPTCHA).
*   **Serviço em Segundo Plano:** Executa silenciosamente em nível de usuário, permitindo inicialização automática sem exigir privilégios administrativos para tarefas diárias.

---

## ⚙️ Pré-requisitos e Instalação

O projeto é multiplataforma, rodando nativamente como um serviço em segundo plano nos ecossistemas **Linux** e **Windows 10/11**.

### Dependências
As ferramentas centrais exigidas pelo motor são:
*   `python3` (O ambiente de execução principal)
*   `rclone` (O motor de transferência)
*   `sqlite3` (Para indexação rápida de metadados)

**🐧 No Linux:**
Não se preocupe, todas as dependências são baixadas e configuradas automaticamente pelo nosso script `install-linux.sh`. O suporte a disco virtual utiliza o pacote nativo `fuse` do sistema.

**🪟 No Windows:**
Você deve baixar e instalar manualmente essas ferramentas antes de executar o instalador. Certifique-se de selecionar **"Add to PATH"** durante a instalação:
1.  **Python 3:** [Baixar Instalador do Windows](https://www.python.org/downloads/windows/)
2.  **Rclone:** [Baixar Rclone](https://rclone.org/downloads/) *(Extraia o `.exe` e coloque em uma pasta no seu PATH, ex: `C:\Windows`)*
3.  **SQLite3:** [Baixar Ferramentas SQLite](https://www.sqlite.org/download.html) *(Extraia o `.exe` e coloque no seu PATH)*
4.  **WinFsp:** [Baixar WinFsp](https://winfsp.dev/) *(Obrigatório **APENAS** se você planeja usar o recurso de Mapear Disco Virtual - Opção 13 do Menu).*

### Instalação Passo-a-Passo

1. **Clone este repositório para o seu computador:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Execute o instalador correto para o seu SO:**
   * 🐧 **No Linux:** Dê um clique duplo no arquivo `install-linux.sh` e escolha "Executar no Terminal", ou rode `bash ./install-linux.sh` via CLI.
   * 🪟 **No Windows:** Simplesmente dê um clique duplo no arquivo `install-windows.cmd` localizado na pasta clonada.

3. **Configure suas contas de nuvem:**
   Tanto no Windows quanto no Linux, abra um terminal e rode (como usuário padrão, NÃO use sudo/admin):
   ```bash
   rclone config
   ```
   *(Siga as instruções do Rclone para configurar seus remotos de nuvem).*

---

## 💻 Referência de Comandos CLI

O Sync Engine pode ser operado via assistente interativo ou atalhos diretos no terminal. Uso básico: `sync-engine [COMANDO]`

| Comando | Descrição |
| :--- | :--- |
| `config` | Abre o Assistente Interativo (Menu principal). |
| `now` | 🚀 Força uma Sincronização imediata (exibe barra de progresso). |
| `test` | 🧪 Inicia o modo interativo de Test-Drive por conta (Simulação segura). |
| `clean` | 🧹 Inicia o higienizador de nomes de arquivos (Gera relatório e respeita filtros). |
| `analyze` | 🔎 Analisa relatórios manuais/automáticos recentes e fornece soluções práticas. |
| `doctor` | 🩺 Roda uma verificação de saúde do sistema (dependências e permissões). |
| `update` | 🔄 Baixa e instala a versão mais recente do GitHub. |
| `start` / `stop` / `reload` | LIGA, DESLIGA ou REINICIA o serviço invisível em segundo plano. |
| `status` | Exibe o status atual do serviço e logs recentes da memória. |

---

## 🛠️ Guia do Assistente Interativo (`sync-engine config`)

O menu interativo foi expandido para suportar gerenciamento granular:

1. **Configuração de Contas (Opções 1 a 3):** Adicione, liste ou remova vínculos de pastas locais com suas nuvens. Remover uma conta aciona a coleta de lixo inteligente.
2. **Configurações Globais (Opção 4):** Altere intervalos de sincronização, limites globais de banda (`BW_LIMIT`), defina o caminho absoluto da pasta para relatórios salvos e alterne o bloqueio de case-sensitivity.
3. **Filtros e Limites de Conta (Opção 5):** Escolha uma conta específica para atribuir limites de tamanho máximo personalizados e gerenciar sua lista de exclusão.
4. **Ações Extras e Relatórios (Opções 6 a 13):** Atalhos para execução imediata (`now`), simulação (`test`), relatórios de arquivos grandes, higienizador, analisador de erros, diagnóstico do sistema, **Migração Nuvem-para-Nuvem** e **Mapeamento de Disco Virtual**.
5. **Controle do Motor (Opções 14 a 18):** Interface amigável para iniciar, parar, checar status, atualizar ou acionar a **Auto-Desinstalação** em todo o sistema.

---

## 🎯 Guia de Filtros e Exclusões

Para impedir a sincronização de pastas ou arquivos indesejados, use as seguintes sintaxes ao adicionar um filtro via **Opção 5**:

*   **Ignorar Maiúsculas/Minusculas:** `(?i)*.tmp` *(Ignora tanto `log.tmp` quanto `LOG.TMP` em qualquer SO).*
*   **Correspondência Exata:** `venv` ou `.git`
*   **Início do Nome do Arquivo:** `Prefixo*` *(ex: `Backup*` bloqueia qualquer arquivo/pasta começando com essa palavra).*
*   **Curinga de Texto (`*`):** `*.bak`
*   **Âncora de Raiz (`/`):** `/Backups` *(Bloqueia a pasta "Backups", mas *apenas* se ela estiver exatamente na raiz do seu diretório de sincronização).*
*   **Arquivos Ocultos na Raiz (Linux):** `/.*` *(Bloqueia arquivos/pastas ocultos como `.bashrc` ou `.config`, mas *apenas* se estiverem no nível da raiz).*
*   **Bloqueador Universal:** Basta criar um arquivo vazio chamado `.nosync` dentro de qualquer pasta que você deseja bloquear permanentemente.

---

## 💡 Servidor Contínuo Automático (Linger / Logon)

Para transformar seu PC em um verdadeiro "servidor":
*   **No Linux:** O script de instalação habilita automaticamente o recurso Linger (`loginctl enable-linger`). Isso permite que o motor de sincronização inicie imediatamente após o boot do sistema, mesmo se a máquina ficar na tela de bloqueio.
*   **No Windows:** Uma tarefa invisível é criada no Agendador de Tarefas vinculada ao gatilho de *Logon* do usuário, garantindo um início limpo e silencioso assim que a área de trabalho carregar.

---

## 🗑️ Desinstalação

Para remover completamente o Sync Engine do seu sistema (limpando o executável raiz, atalhos do sistema e desligando serviços em segundo plano):
1. Abra seu terminal e digite `sync-engine config`
2. Selecione a **Opção 18 (Desinstalar o Sync Engine)**
3. O sistema fará um desafio de texto aleatório (CAPTCHA) para confirmar a exclusão.
4. Você será questionado se deseja manter ou excluir permanentemente seu histórico de configuração e relatórios antigos.
5. O software se autodestruirá com segurança em 3 segundos.
