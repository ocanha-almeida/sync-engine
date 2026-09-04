<div align="right">
  <a href="README.md">🇺🇸 English</a> | <span>🇧🇷 Português</span>
</div>

# 🔄 Sync Engine - Multi-Account Rclone Manager

Um motor inteligente, interativo e seguro para sincronização bidirecional em nuvem, construído sobre o poderoso `rclone bisync`. Projetado exclusivamente para Linux, ele transforma a complexidade do Rclone em uma experiência fluida através de um assistente de terminal (CLI) completo.

Nascido da necessidade de superar as limitações de clientes tradicionais para o Linux, este projeto traz foco total em sincronização automática de fundo, proteção nativa contra exclusões acidentais, controle rígido de banda/tamanho e bloqueio cirúrgico de pastas de forma bidirecional.

## ✨ Principais Recursos

*   **Bloqueio Inteligente Bidirecional (`.nosync`):** Crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta (seja no seu computador **ou direto na nuvem**) para que o motor a ignore instantaneamente. A leitura remota garante que diretórios indesejados na nuvem nunca sejam baixados acidentalmente, sem a necessidade de editar arquivos de configuração globais.
*   **Assistente CLI Interativo:** Um menu de 13 opções para gerenciar contas, filtros, serviços e gerar relatórios.
*   **Higienizador Nativo (`clean`):** Varre suas pastas locais em busca de caracteres especiais que causam erros de upload na nuvem. Exibe uma pré-visualização, respeita rigorosamente suas regras de filtro e `.nosync`, exige confirmação do usuário e gera um relatório detalhado de alterações.
*   **Analisador de Erros (`analyze`):** Esqueça logs confusos. O motor lê os relatórios de falha do Rclone e traduz problemas comuns (como *eTag Mismatch* ou *Lock Files* emperrados) em diagnósticos e soluções fáceis de aplicar.
*   **Auto-Atualizador (`update`):** Verifica, baixa e instala novas versões do script diretamente do repositório no GitHub com um único comando.
*   **Suporte Multi-Contas:** Conecte simultaneamente Google Drive, OneDrive, Dropbox, S3, ou qualquer outro provedor suportado pelo Rclone.
*   **Filtros Avançados:** Defina exclusões globais utilizando curingas, limite de tamanho de arquivo (`MAX_SIZE`) e limite de uso de banda (`BW_LIMIT`).
*   **Serviço em Segundo Plano (Systemd):** Roda de forma invisível no seu usuário (sem necessidade de root para a sincronização diária).
*   **Relatórios Exportáveis:** Gere relatórios seguros de simulação (Dry-Run), histórico de sincronizações manuais e listagens de arquivos bloqueados por tamanho, salvos em texto puro na pasta de sua escolha.
*   **Notificações no Desktop:** Avisos nativos do Linux (via `notify-send`) sobre sucesso ou erros na sincronização.
*   **Auto-Cura (Auto-Resync):** O script detecta falhas críticas da API (como quebras no histórico do Rclone) e realiza a varredura de cura automaticamente.
*   **Serviço em Segundo Plano (Systemd):** Roda invisível no seu nível de usuário, com suporte a inicialização automática desde o boot.

---

## ⚙️ Pré-requisitos e Instalação

O projeto foi construído para ecossistemas Linux (testado em distribuições baseadas em Debian/Ubuntu/Mint).

### Dependências
As ferramentas abaixo serão instaladas automaticamente pelo script de instalação:
*   `rclone` (O motor central de transferência)
*   `sqlite3` (Para indexação rápida de metadados e lógica `.nosync`)
*   `libnotify-bin` (Para notificações na área de trabalho)
*   *Nota: Requer `python3` nativo do sistema.*

### Instalação Passo a Passo

1. **Clone este repositório:**
   ```bash
   git clone [https://github.com/ocanha-almeida/sync-engine.git](https://github.com/ocanha-almeida/sync-engine.git)
   cd sync-engine
   ```

2. **Execute o instalador automático (requer sudo):**
   ```bash
   sudo ./install.sh
   ```

3. **Configure as suas contas de nuvem (Via usuário comum, NÃO use sudo):**
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
| `start` / `stop`| LIGA ou DESLIGA o serviço invisível `systemd` em segundo plano. |
| `status` | Exibe o status atual do serviço e os últimos logs gerados. |
| `status` | Exibe o status atual do serviço `systemd` e os últimos logs gerados. |
| `help` (ou `-h`) | Exibe a mensagem de ajuda e a lista de comandos no terminal. |

---

## 🛠️ Guia do Assistente Interativo (`sync-engine config`)

O menu interativo divide-se em 4 blocos principais:

1. **Configuração de Contas (Opções 1 a 3):** Adicione, liste ou remova vínculos de pastas locais com suas nuvens. Ao remover uma conta, o script faz a limpeza inteligente de lixo (bancos de dados e filtros residuais).
2. **Configurações Globais (Opções 4 e 5):** Altere o intervalo de sincronização (ex: `300s`), limite de banda (ex: `10M`), corte de arquivos gigantes (ex: `2G`) e defina a pasta de destino dos relatórios (ex: `/tmp` ou `~/Relatorios`).
3. **Ações Extras (Opções 6 a 9):** Atalhos para execução imediata (`now`), simulação (`test`), diagnóstico (`doctor`) e o **Relatório de Tamanho**, que lista arquivos barrados pela regra de limite de tamanho de forma legível (ex: `[3,07 GB] /videos/aula.mp4`).
4. **Controle do Motor (Opções 10 a 12):** Interface amigável para ligar, desligar e ver o status do motor (mesmo efeito dos comandos diretos `start`, `stop`, `status`).

---

## 🎯 Guia de Filtros e Exclusões

Para evitar a sincronização de pastas ou arquivos indesejados, você pode usar dois métodos:

### Método 1: A Flag `.nosync` (Recomendado)
Basta criar um arquivo vazio com o nome exato `.nosync` dentro de qualquer diretório, seja no seu computador ou na interface web da sua nuvem. 
No próximo ciclo do motor, essa pasta e todo o seu conteúdo serão ignorados instantaneamente e bloqueados no Rclone de forma segura.
*Exemplo no terminal Linux:* `touch ~/MeusProjetos/Testes/.nosync`

### Método 2: Filtros Globais (Menu 5 - Gerenciar Filtros)
Aplica regras gerais para todas as pastas da sua conta. Suporta as seguintes sintaxes avançadas:
*   **Nome exato:** `venv` ou `.git` (Bloqueia qualquer pasta/arquivo com esse nome, em qualquer nível).
*   **Curinga de Texto (`*`):** `*.tmp` (Bloqueia todos os arquivos que terminem com `.tmp`).
*   **Curinga de Caractere (`?`):** `cam_?.dav` (Bloqueia `cam_1.dav`, `cam_A.dav`, etc).
*   **Ancoragem na Raiz (`/`):** `/Backups` (Bloqueia a pasta "Backups", mas *apenas* se ela estiver na raiz da sua nuvem/pasta principal. Uma pasta chamada `Fotos/Backups` será sincronizada normalmente).

---

## 💡 Servidor Contínuo Automático (Linger)

Por padrão de segurança do Linux, serviços atrelados ao usuário só iniciam quando você digita sua senha na tela de login. 

Para transformar seu PC num verdadeiro "servidor", **o script de instalação ativa automaticamente o recurso Linger** (`loginctl enable-linger`). Isso permite que o motor de sincronização inicie imediatamente após o *boot* do sistema, mesmo que a máquina fique parada na tela de bloqueio.

*Nota: Ao desinstalar o Sync Engine, o Linger não é desativado do seu usuário. Optamos por mantê-lo ativo, pois é uma permissão valiosa caso você deseje rodar outros aplicativos e serviços em segundo plano no futuro.*

---

## 💡 Dicas de Uso e Fluxos de Trabalho

*   **Pastas de Relatórios Efêmeras:** Na **Opção 4** do assistente, você pode mudar a pasta de relatórios gerados (Dry-Run e Tamanho) para `/tmp`. O Linux apagará seus relatórios antigos magicamente a cada reinício da máquina.
*   **Múltiplas Nuvens:** Crie uma conta no menu apontando para o Google Drive (`~/GDrive`) e outra para o OneDrive (`~/OneDrive`). O motor cuidará de ambas paralelamente com regras e bancos de dados SQLite independentes.

---

## ⚠️ Limitações Conhecidas

1. **Não é em Tempo Real (Inotify):** O script não monitora ativamente cada alteração (clique) no disco. Ele opera em janelas de varredura cíclicas (padrão: a cada 5 minutos). 
2. **Ignora Links Simbólicos (Symlinks):** Para evitar loops infinitos acidentais, o motor não copia nem segue atalhos do sistema (isso previne panes estruturais entre o Linux e a Nuvem).
3. **Tempo de Resync Inicial:** Na primeira sincronização de uma conta (ou se o processo for finalizado à força com erro fatal), o motor precisará rodar uma varredura profunda (`--resync`). Isso é feito de forma automática, mas consome mais tempo do que a sincronização incremental diária.
4. **Cofres Pessoais (Vaults):** Algumas nuvens exigem chaves de decriptação nativas (ex: *Personal Vault* do OneDrive). O Sync Engine bloqueia o "Cofre Pessoal" e o "Personal Vault" por padrão via filtros para impedir falhas de permissão de leitura na API.

---

## 🗑️ Desinstalação

Para remover completamente o Sync Engine do seu sistema (limpando o executável raiz, atalhos e os serviços do `systemd`), use a rotina nativa do instalador:

```bash
sudo ./install.sh uninstall
```
*(As suas regras `config.json` e metadados `.db` serão mantidos em `~/.config/sync_engine/` por segurança. Você pode apagar a pasta toda manualmente caso não deseje reinstalar a ferramenta no futuro).*
