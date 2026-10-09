# Changelog - Sync Engine

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao Versionamento Semântico.

## \[7.2.4\] - 2026-10-09

### Added

* **i18n Utilities:** Adicionado script `injetar_traducoes.py` para mesclar traduções geradas em lote nativamente nos arquivos `.json` de idioma.

* **Uninstaller:** Incluído aviso amigável durante a desinstalação orientando o usuário sobre a possível limpeza manual da dependência externa (`rclone`).

* **Scheduler:** Agendamento de execução integrado ao sync-engine, listando dinamicamente os *remotes* disponíveis no Rclone durante a criação de uma Migração Nuvem-para-Nuvem.

* **Security:** Inserção de novos filtros de exclusão padrão na criação de contas (`*.trashinfo`, `.Trash`, `desktop.ini`, `.~lock.*`, `*.crdownload`, `*.part`, `node_modules`, `$RECYCLE.BIN`).

* **Documentation:** Criação de vasta documentação em Markdown: `Guia de Configuração de Contas`, `Guia de Relatórios e Logs`, `Guia do Modo Dry-Run`, `Guia de Upload de Arquivos Bloqueados`, `Guia do Motor em Segundo Plano` e `Guia de Traduções e Internacionalização`.

* **UI:** Inclusão do Seletor de Idiomas no menu Global Settings.

### Fixed

* **CLI Interface:** Corrigido o alinhamento de espaçamento no menu de ajuda do terminal (`sync-engine -h`).

* **Scheduler Engine:** O motor em segundo plano agora herda e aplica corretamente as regras de Filtro Avançado e os Limites de Tamanho (`MAX_SIZE`) nas tarefas de madrugada.

* **i18n Engine:** Função de tradução melhorada para ignorar emojis, pontuação final e capitalização, evitando duplicações nas chaves dos dicionários `.json` na pasta `locales/`.

* Atualização do arquivo `.gitignore` para o repositório.

* Limpeza estrutural nos menus de configuração e de filtros, removendo blocos de código obsoletos.

## \[7.2.3.1\] - 2026-10-07

### Fixed

* Fechamento prematuro ao selecionar a conta para sincronização Nuvem a Nuvem.

* Resolução do erro fatal de sintaxe (TypeError) na migração Nuvem a Nuvem.

* Validação do algoritmo matemático de atualização online.

## \[7.2.3\] - 2026-10-07

### Added

* Exibe o provedor (tipo de nuvem) da conexão diretamente na listagem de contas.

* Permite selecionar independentemente quais conexões sincronizam automaticamente em background quando o serviço está ligado.

### Fixed

* Comportamento das opções de configuração na listagem de conta.

* Traduções que estavam faltantes na listagem de contas.

* Correção na opção de cancelar a alteração de filtros (retorno seguro).

## \[7.2.2\] - 2026-10-06

### Added

* Padronizado o renderizador de menus interativos (construtor dinâmico).

* Ferramenta (Cleaner) para detectar e higienizar conflitos de nomes (*Case-Sensitivity*) entre SOs.

* Refatorada a ação de mudança de pasta local utilizando `shutil` para movimentação física.

### Fixed

* Emojis não são mais enviados como chaves para os motores de tradução.

## \[7.2.1\] - 2026-10-05

### Added

* Menu "📋 Listar contas atuais" permite inspecionar configurações e alterar pastas.

* Atalho direto no menu principal para abrir a pasta de relatórios.

* Divisão arquitetural em módulos: `sync_engine.py`, `sync_core.py`, `sync_config.py` e `sync_os.py`.

### Fixed

* Falha na lógica de comparação das versões local e do GitHub durante a rotina de atualização online.

* Padronização de design e retornos do menu nas seções de Sincronização Imediata e Reparo.

## \[7.2.0\] - 2026-09-25

### Added

* Suporte nativo à internacionalização (i18n) com dicionários JSON (EN, PT-BR, PT-PT, ES, DE, FR, ZH, IT, JP).

* Mecanismo de *fallback* inteligente para identificar a variante regional do idioma do sistema operacional.

### Fixed

* Correção no modo Dry-Run (`test`) para respeitar o limite de tamanho configurado e suprimir códigos de escape ANSI que sujavam os relatórios.

## \[7.0.0\] - 2026-09-15

### Added

* **A Grande Refatoração:** Lançamento da primeira versão estável e unificada baseada na nova arquitetura em Python (substituindo o antigo núcleo em Bash/PowerShell).

* **Multi-Account:** Banco de dados persistente `config.json` para suportar múltiplas nuvens simultâneas.

* **SQLite Indexing:** Substituição da listagem em texto por banco de dados rápido (`sync_metadata.db`).

* Migração direta de Nuvem para Nuvem operando em RAM.

* Disco Virtual (Mount) suportado nativamente.

* Módulo nativo de auto-update integrado ao repositório do GitHub.

## \[Fundação Python\] - 2026-09-08

### Added

* **O Marco Inicial:** Início do desenvolvimento colaborativo e transição definitiva do `sync-engine` para a linguagem Python.

* Decisão arquitetural de isolar a aplicação em User Space (`systemctl --user`).

## \[6.0.0\]

*O auge da era Bash/PowerShell.*

### Added

* Unificação final dos scripts de shell para Linux e Windows.

* Criação dos instaladores automáticos nativos (`install-linux.sh` e `_core_install.ps1`).

* Integração profunda com o Systemd para operação contínua e silenciosa em segundo plano no Linux, sem necessidade de sessão gráfica ativa.

## \[5.0.0\]

### Added

* Suporte inicial a múltiplas nuvens utilizando perfis de configuração separados.

* Implementação inicial de limites rígidos de banda (`BW_LIMIT`) nos scripts de upload para proteger redes locais lentas durante horário comercial.

## \[4.0.0\]

### Added

* Nascimento da lógica de exclusão nativa (arquivos `excludes.txt`).

* Criação do conceito de isolamento via marcador `.nosync` para bloquear pastas localmente sem necessidade de editar as configurações do sistema.

* Inclusão do modo de teste (Dry-Run).

## \[3.0.0\]

### Added

* Implementação de Agendador (Scheduler) rudimentar via `cron` para disparar rotinas noturnas na ausência do usuário.

## \[2.0.0\]

### Added

* O Sync Engine ganha forma como um "Wrapper" automatizado e seguro sobre os comandos nativos do Rclone, simplificando os processos bidirecionais (Bisync).

* Implementação de logs simples e tratamento de falhas em conexões instáveis.