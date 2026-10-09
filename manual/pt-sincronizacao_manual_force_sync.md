# 🚀 Guia de Sincronização Manual (Force Sync Now)

Embora o Sync Engine brilhe pela sua operação invisível em segundo plano, há momentos em que você precisa assumir o controle imediato. O recurso de **Sincronização Manual** foi desenhado para execuções sob demanda, oferecendo feedback visual (barra de progresso nativa do Rclone) e ferramentas agressivas de resolução de conflitos.

## 1. Como Iniciar a Sincronização Manual

Você pode acionar este recurso de duas formas:
*   **Pelo Terminal (Atalho):** Digite `sync-engine now` e pressione Enter.
*   **Pelo Menu Interativo:** Digite `sync-engine config` e escolha a opção **Force Sync Now** na seção de Sincronização.

Ao iniciar, o sistema perguntará se você deseja sincronizar **Todas as contas (Batch)** sequencialmente ou apenas uma **conta específica**.

---

## 2. Modos de Operação

Após selecionar o alvo, você terá duas opções de execução. O sistema registrará a sua escolha e todo o processo no relatório `_ultima_sincronizacao_manual.txt`.

### [1] Normal Sync (Safe)
É o modo de segurança padrão. Ele compara as diferenças entre o seu computador e a nuvem e transfere apenas o que foi criado, modificado ou deletado.
*   **Uso ideal:** Sincronizações rotineiras onde você apenas quer visualizar o progresso (ex: acompanhando o upload de uma pasta pesada recém-criada).
*   **Segurança:** Se o motor detectar que um mesmo arquivo foi alterado tanto no seu computador quanto na nuvem simultaneamente, ou se houver divergências estruturais perigosas, ele abortará a operação preventivamente para proteger seus dados contra perda.

### [2] ⚠️ FORCE Sync (--force)
O modo Forçado ignora os mecanismos de segurança de alterações simultâneas.
*   **Uso ideal:** Quando a sincronização segura (Normal) falha repetidamente emitindo avisos sobre "alterações em ambos os lados" (*Path1 and Path2 modified*) e você tem certeza de que deseja que o sistema resolva o impasse.
*   **Segurança:** Use com cautela. O sistema forçará a sincronização e priorizará a manutenção do arquivo que possuir a data de modificação mais recente.

---

## 3. Segurança Integrada e Auto-Cura

Durante a sincronização manual, o Sync Engine age como um escudo, realizando três verificações vitais sem que você precise digitar comandos complexos:

*   **Verificação de Colisões (Pre-Sync):** Antes de tentar conectar à nuvem, o motor varre sua pasta local. Se encontrar arquivos com o mesmo nome diferenciados apenas por letras maiúsculas (ex: `Relatorio.pdf` e `relatorio.pdf`) ou caracteres especiais inválidos (`?`, `*`, `"`), ele disparará um **Alerta de Conflito**. Isso evita a corrupção da árvore de arquivos na nuvem.
*   **Quebra de Bloqueio Automática (Auto-Unlock):** Se a sincronização travar devido a um arquivo de bloqueio (*lock file*) deixado por uma interrupção abrupta anterior (como queda de energia ou fechamento forçado), o Sync Engine lerá o log, quebrará o bloqueio sozinho e reiniciará a transferência em seguida.
*   **Varredura de Cura (Healing Scan):** Se o histórico de indexação (*Path1/Path2 listings*) se perder ou corromper, o sistema identificará o erro e acionará automaticamente a flag `--resync`, reconstruindo toda a árvore do zero para salvar a conta.

---

## 4. Exemplos Práticos de Uso

### Exemplo 1: Upload de Emergência com Acompanhamento Visual
Você acabou de colocar 15GB de fotos na sua pasta local e precisa desligar o computador para uma viagem, mas quer ter a certeza matemática de que tudo subiu para o Google Drive antes de fechar a tampa.
1. Abra o terminal e digite `sync-engine now`.
2. Selecione a sua conta.
3. Escolha a opção **[1] Normal Sync (Safe)**.
4. O terminal exibirá a barra de progresso em tempo real, mostrando a velocidade de upload, os arquivos sendo transferidos e o tempo estimado. Assim que finalizar com a mensagem verde de conclusão, você pode desligar a máquina.

### Exemplo 2: Destravando uma Conta "Congelada"
Você percebeu que uma de suas contas parou de sincronizar sozinha. Você rodou a opção "Sync Error Analyzer" e o diagnóstico indicou conflito de *eTag* ou arquivos travados.
1. Execute `sync-engine now` e escolha a conta afetada.
2. Selecione a opção **[2] ⚠️ FORCE Sync (--force)**.
3. O sistema forçará a passagem pelas travas do Rclone, quebrando arquivos de lock residuais, alinhando as pontas e gerando um relatório detalhando o que foi substituído.

### Exemplo 3: Auditando Erros de Nomenclatura no Download
Você extraiu um arquivo `.zip` antigo dentro da sua pasta sincronizada, mas o arquivo continha pastas com nomes cheios de caracteres problemáticos. Ao tentar sincronizar via `sync-engine now`, a tela fica vermelha com um alerta:
> *🚨 ALERT: Case-Sensitivity Conflicts or Invalid Characters detected!*
Neste caso, o motor intercepta o perigo e pausa. A sua ação imediata deve ser abortar a sincronização (pressionar Enter) e, no menu principal, rodar a ferramenta **Cleaner and Collision Checker** (`sync-engine clean`). O higienizador varrerá a pasta afetada e limpará os nomes inválidos automaticamente, permitindo que você retorne à Sincronização Manual com segurança logo em seguida.