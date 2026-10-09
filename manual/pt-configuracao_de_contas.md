# ⚙️ Guia de Configuração de Contas e Sincronização

O Sync Engine permite gerenciar múltiplas contas de nuvem simultaneamente, cada uma com suas próprias regras de sincronização, limites de tamanho e filtros de exclusão. Este guia detalha como cadastrar novos provedores e extrair o máximo de cada configuração individual.

## 1. Como Cadastrar uma Nova Conta

Para iniciar o vínculo de uma nova nuvem, abra o terminal e inicie o assistente principal executando `sync-engine config`.

1. No menu principal, selecione **Add new account** (Adicionar nova conta).
2. **Nome do Perfil:** Escolha um nome amigável e direto para identificar esta configuração (ex: `Trabalho`, `Pessoal`, `Backup_Fotos`).
3. **Seleção da Nuvem:** O sistema listará automaticamente todos os provedores (*remotes*) que você já configurou previamente no Rclone. Digite o número correspondente à nuvem desejada.
4. **Pasta Local:** Informe o caminho absoluto da pasta no seu computador que será sincronizada com esta nuvem.
   * *Dica:* Se você pressionar *Enter* sem digitar nada, o sistema criará automaticamente uma pasta na raiz do seu usuário com o nome da nuvem (ex: `~/gdrive`).

Após salvar, o assistente redirecionará você automaticamente para o painel de controle (dashboard) dessa configuração. A tela exibirá o resumo do seu ecossistema e será semelhante a esta:

```text
=== ⚙️  CONTA: meu_drive ===
=============================================
☁️  Cloud (Remoto)  : meu_gdrive:
📁 Pasta Local    : ~/google_drive
🔄 Sincronização em Segundo Plano : LIGADO
📦 Limite de Tamanho      : 0 (0 = Ilimitado)
🛡️  Filtros Ativos  : 19 regra(s)
🔌 Drive Virtual   : Inativo

1. ✏️  Alterar o caminho da Pasta Local
2. 🔄 Alternar Sincronização em Segundo Plano
3. 📦 Alterar Tamanho Máximo
4. 🛡️  Gerir Filtros

[Enter] Voltar/Sair
=============================================
Opção: 
```

Se o motor em segundo plano estiver ativo, ele já reconhecerá a conta e iniciará o primeiro ciclo de indexação silenciosamente.

---

## 2. Configurações e Detalhes da Conta

Acessando o menu interativo da conta, você pode ajustar regras específicas de operação:

### ✏️ Alterar Pasta Local (Change Local Folder path)
Permite mudar o diretório físico no seu computador que está vinculado à nuvem.
* **Migração Segura:** Ao alterar o caminho, o Sync Engine perguntará se você deseja mover fisicamente (transferir) os arquivos da pasta antiga para a nova. Isso automatiza a reorganização e evita que você tenha que baixar todo o seu conteúdo novamente ou lide com arquivos duplicados.

### 🔄 Sincronização em Segundo Plano (Toggle Background Sync)
Ativa ou desativa a sincronização automática invisível para esta conta específica.
* **ON:** A conta será sincronizada continuamente de acordo com o intervalo global do sistema.
* **OFF [Paused]:** A conta entra em pausa. Ideal para economizar banda de internet ou processamento temporariamente, sem precisar deletar a conta do sistema. Contas em pausa ainda podem ser sincronizadas sob demanda através do comando manual `now`.

### 📦 Limite de Tamanho (Change Max Size)
Define um teto para o tamanho dos arquivos que serão enviados ou baixados, ignorando automaticamente qualquer arquivo que ultrapasse o limite.
* Aceita formatos práticos como `500M` (500 Megabytes) ou `2G` (2 Gigabytes).
* Digite `0` para **Ilimitado** (Unlimited).
* Arquivos ignorados por esta regra não são deletados, apenas pulados durante a sincronização. Você pode verificar quais arquivos foram bloqueados gerando o relatório "Report of Files Over the Limit" no menu de Manutenção.

### 🛡️ Gerenciar Filtros (Manage Filters)
Permite criar regras cirúrgicas para impedir que arquivos, pastas ou extensões específicas subam para a nuvem ou desçam para o seu PC. 

No momento em que você cria a conta, o Sync Engine **adiciona automaticamente uma lista de filtros de proteção padrão** para evitar falhas, travamentos ou desperdício absurdo de banda. Esses filtros iniciais cobrem:
* **Arquivos de Sistema e Ocultos:** `desktop.ini`, `Thumbs.db`, `.DS_Store`, `$RECYCLE.BIN`. (Evitam conflitos de ícones e lixeiras de HD externo). * **Desenvolvimento e Versionamento:** `venv`, `.venv`, `__pycache__`, `.git`, `site-packages`, `node_modules`. (Pastas de código que contêm milhares de arquivos minúsculos que costumam travar a API da nuvem). * **Travas e Arquivos Temporários:** `*.tmp`, `~$*`, `.~lock.*`. (Evitam que o motor tente sincronizar um documento Word/LibreOffice no exato momento em que ele está aberto e sendo editado).
* **Downloads Incompletos:** `*.crdownload`, `*.part`. (Impedem o upload de um arquivo que ainda está sendo baixado pelo navegador).
* **Cofres e Lixeiras de Nuvem:** `Personal Vault`, `Cofre Pessoal`, `*.trashinfo`, `.Trash`.

> **💡 IMPORTANTE: Você está no controle.**
> Estas exclusões padrão não são definitivas. Se você, por exemplo, é um programador e **deseja** que o Sync Engine faça backup da sua pasta `node_modules` ou dos seus repositórios `.git`, basta entrar na opção **Gerir Filtros** no painel da conta, digitar o número da regra correspondente e **apagá-la**.

**Sintaxe suportada para criar novas regras:**
* `(?i)*.tmp`: Ignora arquivos pela extensão sem diferenciar maiúsculas e minúsculas (*Case Insensitive*).
* `venv`: Ignora pastas ou arquivos específicos pelo nome exato, não importa onde estejam dentro da estrutura.
* `Backup*`: Ignora qualquer item que comece com este prefixo (ex: `Backup_2026`).
* `*.bak`: Curinga de extensão padrão aplicável a qualquer nível de pasta.
* `/Arquivos_Antigos`: O uso da barra (`/`) garante que a pasta só será ignorada se estiver exatamente na raiz do seu diretório de sincronização, protegendo subpastas que tenham o mesmo nome em outros lugares.
* `.*`: Ignora arquivos iniciados com ponto (padrão de arquivo oculto no Linux) em qualquer local dentro da estrutura.
* `/.*`: Ignora arquivos iniciados com ponto (padrão de arquivo oculto no Linux) somente na pasta inicial da estrutura. Arquivos iniciados com ponto em subpastas serão sincronizados.

---

## 3. O Marcador Dinâmico de Bloqueio (`.nosync`)
Se você precisar bloquear uma pasta rapidamente e não quiser abrir o terminal para configurar regras de filtro, use a abordagem dinâmica:

Crie um arquivo vazio chamado `.nosync` dentro de qualquer pasta (seja no seu explorador de arquivos local ou diretamente pelo navegador na nuvem). O Sync Engine rastreará esse marcador no ciclo seguinte e **isolará a pasta inteira**, bloqueando a sincronização do seu conteúdo imediatamente e com segurança.

---

## 4. Drive Virtual Integrado (Mount)
O Sync Engine permite que você ative um Drive Virtual para qualquer conta cadastrada. Este recurso atua de forma paralela e não afeta as regras de sincronização bidirecional.

* **Como ativar:** No menu principal, acesse **Mount Cloud as Virtual Drive**.
* **No Windows:** O sistema solicitará uma letra de unidade livre (ex: `X`, `Y`). A nuvem será montada e aparecerá como um disco de rede no "Meu Computador".
* **No Linux:** A nuvem será montada diretamente em um diretório no sistema de arquivos local (por padrão, na sua Área de Trabalho, mas o caminho é customizável).
* **Auto-Mount:** Ao habilitar o recurso definitivo, o Drive Virtual será restaurado silenciosa e automaticamente em segundo plano toda vez que o Sync Engine for iniciado junto com o sistema.