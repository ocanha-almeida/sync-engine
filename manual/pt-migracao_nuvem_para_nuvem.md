# ☁️ Guia de Migração Nuvem-para-Nuvem (Cloud-to-Cloud Migration)

O recurso de **Migração Nuvem-para-Nuvem** permite que você copie ou transfira arquivos diretamente entre dois provedores diferentes (por exemplo, do Google Drive para o OneDrive, ou do Dropbox para o Mega).

A grande vantagem deste sistema é que **ele não consome espaço no seu disco rígido local**. O Sync Engine utiliza a memória RAM do seu computador como uma ponte de transferência temporária, fazendo o download e o upload simultaneamente.

---

## ⚠️ Pré-requisitos

Para utilizar este recurso, você precisa ter **pelo menos 2 (duas) nuvens configuradas no Rclone**. 
*Nota:* Não é obrigatório que essas nuvens estejam cadastradas nas contas de sincronização ativa do Sync Engine (você pode transferir arquivos de um pendrive na rede ou de um provedor que você só usa esporadicamente).

---

## 1. Como Iniciar a Migração

1. Abra o terminal e inicie o assistente: `sync-engine config`.
2. No menu de **Ações Extras (Extra Actions)**, escolha **Direct Cloud-to-Cloud Migration**.
3. **Origem (Source):** O sistema listará todas as nuvens disponíveis. Digite o número da nuvem de onde os arquivos sairão.
   * *Subpasta:* Em seguida, você pode informar uma subpasta específica (ex: `Projetos_2026`). Se quiser copiar a nuvem inteira, basta apertar *Enter* (deixar em branco).
4. **Destino (Destination):** Digite o número da nuvem que receberá os arquivos.
   * *Subpasta:* Informe a pasta de destino (ex: `Backup_Projetos`). Se deixar em branco, os arquivos irão para a raiz da nuvem destino.

*Dica: Você não pode escolher a mesma nuvem e a mesma pasta como origem e destino.*

---

## 2. Modos de Transferência (Filtros)

Após selecionar a origem e o destino, o sistema perguntará qual o nível de filtro você deseja aplicar à transferência:

*   **[1] TOTAL (Absolute copy):**
    O motor copiará **absolutamente tudo**. Não importa se há pastas ocultas, lixeiras ou arquivos temporários. Se está na origem, irá para o destino.
*   **[2] STANDARD (Security locks):**
    O motor aplicará um filtro de segurança padrão. Ele fará uma varredura (scan) rápida na origem e **bloqueará automaticamente** pastas que contenham o marcador `.nosync`, arquivos inúteis de sistema (`.DS_Store`, `Thumbs.db`) e diretórios nomeados como "Personal Vault" ou "Cofre Pessoal".
*   **[3] CUSTOM (Locks + config.json filters):**
    Aplica todas as regras de segurança do modo *Standard* e, adicionalmente, **importa os filtros personalizados** que você configurou no painel da conta (caso a nuvem de origem seja uma das contas ativas de sincronização do Sync Engine).

Por fim, o sistema perguntará se você deseja aplicar um **Limite de Tamanho (Max Size)**. Se digitar `1G`, por exemplo, qualquer arquivo maior que 1 Gigabyte será ignorado na cópia. Digite `0` para ilimitado.

---

## 3. Acompanhamento e Relatórios

Assim que a transferência começar, você verá estatísticas detalhadas no terminal (progresso, velocidade e arquivos restantes).
*   Se a sua internet cair ou você precisar desligar o computador no meio do processo, basta apertar `Ctrl+C` para abortar.
*   **O sistema é inteligente:** Quando você iniciar a mesma transferência novamente no dia seguinte, ele não fará o download do que já foi transferido; ele pulará os arquivos idênticos e continuará de onde parou.
*   Ao terminar, um relatório detalhado será salvo na sua pasta de relatórios (ex: `migracao_gdrive_para_onedrive_2026-10-09.txt`).

---

## 4. Exemplos Práticos de Uso

### Exemplo 1: Espelhamento de Segurança (Backup Total)
Você usa o Google Drive para o seu trabalho diário, mas não quer correr o risco de perder tudo se a sua conta for bloqueada. Você assina um plano barato do OneDrive apenas como cofre de segurança.
**A Solução:**
1. Inicie a Migração Nuvem-para-Nuvem.
2. Escolha o Google Drive como Origem (raiz) e OneDrive como Destino (raiz).
3. Selecione o modo **[2] STANDARD** para ignorar pastas marcadas com `.nosync` que você não quer salvar no cofre.
4. Deixe o limite de tamanho em `0`. O sistema clonará a estrutura do Drive para o OneDrive sem usar o seu HD.

### Exemplo 2: Transferência de Subpasta Específica
Seu cliente enviou um link do Dropbox com dezenas de vídeos brutos pesados. Você conectou esse Dropbox temporariamente no Rclone, mas quer mover esses vídeos para a pasta "Projetos_Vídeo" do seu Google Drive.
**A Solução:**
1. Na Origem, selecione o Dropbox temporário e defina a subpasta como `Entregas_Cliente`.
2. No Destino, selecione o Google Drive e defina a subpasta como `Projetos_Vídeo/Cliente_X`.
3. Escolha o modo **[1] TOTAL**.
4. O Sync Engine fará o transporte diretamente para a subpasta correta, mantendo a organização do seu Drive intacta.

### Exemplo 3: Automação Noturna via Agendador de Tarefas
Você não quer ficar olhando para a tela preta do terminal durante horas enquanto 500GB são copiados.
**A Solução:**
1. Em vez de rodar a migração imediata, vá em **Task Scheduler (Cron)** no menu principal.
2. Crie uma nova tarefa e escolha o Tipo `3 (Cloud-to-Cloud Migration)`.
3. Configure a origem, destino e agende para a próxima madrugada (ex: `02:00`).
4. O motor em segundo plano (Background Motor) assumirá o controle no horário marcado e fará toda a cópia silenciosamente sem a necessidade de manter janelas abertas.