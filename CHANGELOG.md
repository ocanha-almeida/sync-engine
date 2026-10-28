# Changelog - Sync Engine

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao Versionamento Semântico.

## [7.2.8] - 2026-10-28

### Modificações e Correções (Instalador Windows)
* **Correção do Auto-Update Invisível:** Removida a instrução `Read-Host` no final do script `_core_install.ps1`. Isso impedia que a atualização em segundo plano fosse concluída, eliminando o travamento do processo na memória.
* **Blindagem contra Arquivos Residuais:** Adicionada uma rotina de verificação que detecta e remove "arquivos folha" corrompidos (gerados por instalações anteriores que falharam), garantindo a criação correta da árvore de diretórios.
* **Refatoração da Instalação de Idiomas:** O script agora extrai e copia o conteúdo da pasta `locales` de forma explícita para o destino, solucionando o erro de cópia de contêineres do PowerShell.
* **Compatibilidade com PowerShell 5.1:** Substituição do parâmetro `-LiteralPath` por `-Path` nas chamadas estruturais (`New-Item`, `Test-Path`), assegurando compatibilidade total com o Windows 10 e 11 nativos.

## [7.2.7] - 2026-10-27

### Adições e Melhorias
* **Novo Motor de Tradução Automática:** O utilitário `auto_tradutor.py` foi totalmente reescrito para utilizar a biblioteca nativa `deep-translator` (Google Translate), abandonando a API do Gemini. Isso resolve definitivamente os erros de cota excedida (HTTP 429) e sobrecarga (HTTP 503).
* **Proteção contra Bloqueios de IP:** Implementado um controle de requisições com intervalo (`time.sleep`) no tradutor automático, prevenindo o erro "Too many requests" da API pública do Google.
* **Backups Inteligentes:** O módulo de backup foi finalizado, permitindo agora a exportação e restauração modular. O usuário pode escolher fazer backup parcial (contas específicas) ou total, incluindo as configurações globais.
* **Distribuição via GitHub Releases:** O sistema de auto-update passou a rastrear oficialmente as Tags do Git e as Releases do repositório, consolidando o GitHub como fonte unificada de atualizações.
* **Nova Documentação:** Adicionados os manuais oficiais do tradutor (`auto_translator_en.md` e `auto_translator_pt.md`) detalhando o novo fluxo de internacionalização sem necessidade de chaves de API.

## [7.2.6] - 2026-10-21

### Adições
- **Painel de Status Enriquecido:** O comando `sync-engine status` agora lista as "Contas de Sincronização em Segundo Plano", exibindo em tempo real quais contas estão sendo vigiadas pelo motor e se estão ativas (🟢) ou pausadas (🔴).
- **Proteção de Loops em Drives Virtuais:** Ao adicionar uma nova conta ou montar um drive virtual (temporário ou permanente), o sistema verifica através da nova função `is_subpath()` se o drive está sendo montado dentro de uma pasta de sincronização e sugere automaticamente a criação de um filtro `.nosync` para evitar uploads infinitos.
- **Backup Parcial:** A funcionalidade de Backup de Configurações agora permite escolher entre um backup total ou parcial (escolhendo contas específicas para exportar).

### Modificações
- **Refatoração do Higienizador de Nomes (`clean`):** A função `executar_cleaner` foi totalmente reconstruída. Agora ela executa as correções físicas nos nomes dos arquivos (tratando caracteres inválidos da nuvem, colisões de maiúsculas/minúsculas e removendo espaços soltos no final de formatações).
- **Desativação de Paginação no Status (Linux):** A flag `--no-pager` foi adicionada ao comando `systemctl status` no `sync_os.py` para evitar que a tela seja travada exigindo que o usuário pressione `q` para sair.
- **Menu Conta Mais Seguro:** A opção de "Remover Conta" foi retirada do menu principal e movida para o final do painel de "Detalhes da Conta", incluindo um aviso vermelho de confirmação (Y/N) para evitar exclusões acidentais.
- **Limpeza do Local de Salvar Backups:** O sistema agora sugere automaticamente a pasta de usuário (`~/` ou `%USERPROFILE%`) como caminho padrão para salvar os arquivos `.json` de backup.

### Correções
- Corrigido o erro `NameError: name 'CONFIG_FILE' is not defined` que impedia a geração de backups pelo menu do usuário.
- O campo global de `MAX_SIZE` obsoleto foi removido do `DEFAULT_CONFIG` inicial para não gerar chaves inúteis no arquivo de novos usuários.
- **Atualização da Suíte de Internacionalização (i18n):** O contador do script `injetar_traducoes.py` foi revisado para ignorar strings equivalentes e a nova string do "Drive Virtual" contendo quebras de linha (`\n`) foi devidamente adicionada ao banco de dados dos 7 idiomas nativos.

## [7.2.5] - 2026-10-16

### 🚀 Adicionado
* **Inteligência de Montagem (Drive Virtual):** Implementada a função `is_subpath`. O sistema agora detecta se um Drive Virtual está sendo montado dentro de uma pasta de sincronização e oferece a criação automática de regras de exclusão (filtros `.nosync`) para evitar loops infinitos e uploads redundantes.
* **Proteção na Exclusão de Filtros:** Adicionado um alerta de segurança. Se o usuário tentar apagar uma regra de exclusão que protege um Drive Virtual ativo da conta, o motor emitirá um aviso vermelho contra loops de sincronização, exigindo confirmação explícita.
* **Backup Parcial e Seletivo:** Nova interface de exportação. Agora é possível escolher entre um backup total ou parcial (escolhendo cirurgicamente apenas as contas que deseja migrar).
* **Monitoramento Reativo de Status:** A opção "Check Motor Status" agora cruza dados dos processos do sistema operacional e exibe atividade visual (⚡ Sincronização em andamento ou 💤 Ocioso) indicando se há uma cópia de dados ativa no momento.
* **Logging Universal:** Adicionada rastreabilidade total. Toda mudança de configuração de conta (montagem/desmontagem de drives, alteração de limites ou mudança de filtros) passa a ser guardada como um evento no arquivo principal `sync.log`.

### 🔄 Modificado
* **Contas em Modo Seguro:** Novas contas cadastradas passam a iniciar com o motor de segundo plano desligado por padrão (`AUTO_SYNC = False`), emitindo um aviso no terminal para o usuário parametrizar limites e regras de exclusão de antemão.
* **Layout do Painel da Conta:** Menu de detalhes reordenado. Agora o layout acusa claramente qual o caminho físico do Drive Virtual, sinalizando se ele é Temporário ou Permanente, e provê uma opção rápida (atalho direto) para gerenciá-lo da própria tela da conta.
* **Caminho Padrão de Backup:** A geração de backups JSON foi refatorada e agora aponta, de maneira nativa, para a raiz das pastas do usuário (`~/` no Linux ou `%USERPROFILE%` no Windows) em vez do diretório oculto da aplicação.

### 🐛 Corrigido
* **Reconstrução do Higienizador (Cleaner):** A função `executar_cleaner` teve seu escopo interno completamente restaurado. A aplicação varre pastas locais validamente, limpa caracteres proibidos, quebra colisões do tipo *Case-Sensitivity* para proteger a nuvem e gera o arquivo físico de relatório ao terminar.
* **Tratamento de Espaços Pós-Traço:** Adicionado loop de repetição `while` na ferramenta de Cleaner, garantindo que espaços perdidos acidentalmente após o sublinhado (ex: `relatorio_ .pdf`) sejam iterativamente deletados.
* **Queda do App no Backup (NameError):** Corrigido um *crash* que encerrava a aplicação ao tentar realizar a exportação total do backup por ausência da variável global `CONFIG_FILE`.
* **Remoção de Código Morto:** Deletada a chave residual `"MAX_SIZE": "0"` do escopo primário do script gerador `sync_config.py`, concentrando a regra exclusivamente dentro do módulo local das contas.

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
