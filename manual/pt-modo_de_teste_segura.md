# 🧪 Guia do Modo de Simulação Segura (Dry-Run)

Ao configurar novas contas ou criar filtros complexos de exclusão, é natural ter receio de iniciar uma sincronização e acabar deletando arquivos importantes por engano. 

Para resolver isso, o Sync Engine conta com o **Modo de Simulação Segura (Dry-Run)**. Esta ferramenta executa uma "falsa sincronização": ela rastreia o seu computador, lê a nuvem, calcula exatamente o que seria baixado, enviado ou deletado, mas **não modifica absolutamente nenhum dado real**.

---

## 1. Como Iniciar a Simulação

Você pode acessar a Simulação Segura de duas maneiras:
*   **Pelo Terminal:** Digite `sync-engine test` e pressione Enter.
*   **Pelo Menu Interativo:** Digite `sync-engine config` e escolha a opção **Test / Dry-Run (Safe Simulation)** na seção de Sincronização.

O sistema pedirá que você escolha uma das suas contas ativas. Ao selecionar, o motor iniciará a varredura bidirecional. Dependendo da quantidade de arquivos na sua nuvem, isso pode levar de alguns segundos a alguns minutos.

---

## 2. Lendo o Relatório de Simulação

Diferente de uma sincronização normal, a simulação não exibe uma barra de progresso gráfica. Em vez disso, ao terminar, ela gera um relatório detalhado chamado `[nome_da_conta]_ultimo_dry_run.txt` e o salva na sua pasta padrão de relatórios.

O arquivo de texto exibirá marcações claras e nativas do Rclone para cada ação simulada:
*   `+` (Sinal de Mais): Arquivos que **seriam enviados** (Upload) ou **baixados** (Download).
*   `-` (Sinal de Menos): Arquivos que **seriam deletados** (da nuvem ou do PC, dependendo de onde foram removidos primeiro para garantir o espelhamento).
*   `*` (Asterisco): Arquivos que **seriam atualizados** ou substituídos (por terem sofrido modificações recentes).

*Nota:* Se você configurou um limite de tamanho (`MAX_SIZE`) na conta, o relatório apontará claramente quais arquivos foram pulados na simulação por excederem o limite.

---

## 3. Exemplos Práticos de Uso

### Exemplo 1: Testando um Novo Filtro de Segurança
Você editou as configurações da conta "Trabalho" e adicionou o filtro `*.mp4` para impedir que arquivos de vídeo pesados subam para o Google Drive. Antes de deixar o motor automático rodar, você quer ter certeza de que escreveu a regra corretamente.
**A Solução:**
1. Rode `sync-engine test` e selecione a conta "Trabalho".
2. Ao final da simulação, abra o relatório gerado.
3. Pressione `Ctrl+F` no documento e pesquise por `.mp4`. Se a regra foi aplicada com sucesso, nenhum vídeo aparecerá listado com o sinal de `+` (pronto para envio), confirmando que a extensão foi totalmente ignorada.

### Exemplo 2: Auditoria Antes de um Grande Download
Você instalou o Sync Engine em um computador novo, vinculou uma pasta local vazia à sua nuvem gigante de 500GB, mas quer saber exatamente o que o sistema pretende baixar para o seu disco rígido.
**A Solução:**
1. Inicie a simulação pelo menu interativo.
2. Leia o relatório gerado. Ele listará toda a árvore de diretórios programada para download.
3. Se você encontrar uma pasta antiga (ex: "Backups_2020") que não quer manter no computador novo, basta ir no menu de filtros, adicionar a regra para ignorá-la (`/Backups_2020`), e rodar a simulação novamente para auditar a mudança.

### Exemplo 3: Aferindo o Bloqueador de Pastas `.nosync`
Você criou um arquivo de texto vazio chamado `.nosync` dentro da pasta local "Finanças" para bloqueá-la e impedi-la de subir para a nuvem.
**A Solução:**
Para validar o bloqueio cirúrgico sem correr riscos, rode a simulação. O log confirmará que a pasta foi ignorada, atestando que os dados confidenciais estão isolados e que você pode iniciar a sincronização manual (`now`) ou ligar o serviço de segundo plano com segurança.