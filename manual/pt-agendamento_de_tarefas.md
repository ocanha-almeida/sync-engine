# ⏰ Guia do Agendador de Tarefas (Task Scheduler)

O Sync Engine possui um Agendador de Tarefas nativo inspirado no sistema Cron do Linux, mas com uma interface totalmente interativa. Isso significa que você não precisa lidar com o *Agendador de Tarefas do Windows* ou editar arquivos *crontab* no Linux para automatizar rotinas em horários específicos.

Tudo é gerenciado diretamente dentro do assistente do Sync Engine e executado de forma invisível.

---

## ⚠️ Requisito Fundamental

Para que qualquer tarefa agendada seja executada no horário programado, o **Motor em Segundo Plano (Background Motor)** do Sync Engine precisa obrigatoriamente estar **LIGADO (ON)**.

O agendador não "acorda" o computador nem inicia o aplicativo sozinho. Ele funciona como um relógio interno do motor que, a cada ciclo de verificação, confere se há alguma tarefa pendente para aquele exato minuto.

---

## 1. Tipos de Tarefas Suportadas

Ao criar um agendamento, você pode escolher entre três tipos de execução:

1.  **Normal Sync (Safe):** Inicia uma sincronização bidirecional padrão e segura para a conta selecionada.
2.  **FORCED Sync (--force):** Ignora alertas de segurança e força a sincronização (ideal para sobrescrever arquivos e resolver conflitos pendentes automaticamente).
3.  **Cloud-to-Cloud Migration:** Inicia uma cópia direta entre dois provedores de nuvem (ex: OneDrive para Google Drive) totalmente em segundo plano.

---

## 2. Como Criar uma Nova Tarefa

1. Abra o terminal e inicie o assistente: `sync-engine config`
2. No menu de Sincronização, escolha **Task Scheduler (Cron)**.
3. Clique em **➕ Add new scheduled task**.
4. **Escolha o Tipo:** Digite `1`, `2` ou `3` conforme a sua necessidade (Sincronização normal, forçada ou migração).
5. **Selecione o Alvo:**
    * Se for sincronização (1 ou 2), escolha qual conta será sincronizada.
    * Se for migração (3), informe a pasta de origem e a de destino.
6. **Defina a Data:**
    * Digite uma data específica no formato `DD/MM/AAAA` (ex: 25/12/2026).
    * *Dica:* Se você pressionar *Enter* deixando o campo em branco, a tarefa será configurada como **Diária** (Daily).
7. **Defina a Hora:** Informe o horário exato de execução no formato de 24 horas `HH:MM` (ex: 14:30, 23:00).

Após salvar, a tarefa aparecerá listada no painel principal do agendador.

---

## 3. Gerenciamento e Limpeza

*   **Remover Tarefas:** Para apagar uma tarefa, basta acessar o menu do Agendador e digitar o número correspondente à tarefa listada que possui um "❌ Delete".
*   **Auto-Limpeza:** Tarefas criadas para uma data específica são executadas e, no dia seguinte, o sistema as remove automaticamente da lista para não acumular "lixo". Tarefas marcadas como Diárias (*Daily*) permanecem na lista indefinidamente, apenas atualizando o aviso de "Última execução" (Ult).

---

## 4. Exemplos Práticos de Uso

### Exemplo 1: O "Fechamento de Caixa" (Sincronização Diária)
Você trabalha editando arquivos pesados de vídeo diretamente na pasta local o dia todo. Se a sincronização em segundo plano estiver rodando a cada 5 minutos, o consumo de banda pode deixar a internet do escritório lenta.
**A Solução:**
1. Desative a sincronização contínua (Background Sync) da sua conta de trabalho no menu da Conta (coloque em OFF).
2. Vá no Agendador de Tarefas e crie uma tarefa de **Normal Sync**.
3. Deixe a data em branco (para ser Diária) e defina o horário para as `23:00`.
**Resultado:** O motor passará o dia em silêncio. Às 23h, ele fará o upload de todo o trabalho do dia em uma única carga.

### Exemplo 2: O Backup de Fim de Semana (Migração Programada)
Você usa o Google Drive para trabalho diário, mas gosta de manter um espelho (cópia) de segurança exata de tudo no OneDrive. Migrações completas consomem muita banda e você não quer que isso atrapalhe o seu uso da internet durante a semana.
**A Solução:**
1. Crie uma nova tarefa do tipo **Cloud-to-Cloud Migration**.
2. Defina a origem (ex: `gdrive:/Trabalho`) e o destino (`onedrive:/Backup`).
3. Defina a data para o próximo sábado (ex: `10/10/2026`) e o horário para as `02:00` da manhã.
**Resultado:** Enquanto você dorme no sábado, o Sync Engine fará a transferência dos arquivos diretamente entre os servidores, sem ocupar o seu computador.

### Exemplo 3: Resolução de Conflitos Sistêmica (Sincronização Forçada)
Você tem um sistema de notas que constantemente gera arquivos temporários que acabam gerando alertas e bloqueando a sincronização por alterações simultâneas (*Path1 and Path2 modified*).
**A Solução:**
1. Crie uma tarefa do tipo **FORCED Sync**.
2. Deixe a data como Diária e configure para as `12:00` (horário de almoço).
**Resultado:** Todo dia, ao meio-dia, o Sync Engine fará uma varredura forçada. Qualquer conflito gerado durante a manhã será automaticamente quebrado e o sistema alinhará a nuvem com o seu PC agressivamente.