# 🔎 Guia do Analisador de Erros (Sync Error Analyzer)

O Rclone é uma ferramenta incrivelmente poderosa, mas seus relatórios de erro (logs) costumam ser técnicos demais, exibindo centenas de linhas de código, números de requisição e erros de servidor (`HTTP 403`, `Rate Limit Exceeded`, etc.) que podem confundir o usuário.

O **Analisador de Erros** do Sync Engine atua como um tradutor inteligente. Ele lê os logs de sincronizações passadas (manuais ou automáticas), filtra o "ruído" técnico e entrega um diagnóstico limpo, informando exatamente o que falhou e o que você precisa fazer para consertar.

---

## 1. Como Iniciar o Analisador

Você pode acessar a ferramenta de duas formas:
*   **Pelo Terminal:** Digite `sync-engine analyze` e pressione Enter.
*   **Pelo Menu Interativo:** Digite `sync-engine config` e escolha a opção correspondente ao **Sync Error Analyzer** na seção de Manutenção.

O sistema listará todas as contas que registraram algum erro nas últimas horas. Ao selecionar uma conta, o motor fará a varredura do relatório e apresentará as conclusões.

---

## 2. Tradução de Problemas Comuns

O Analisador consegue identificar e simplificar dezenas de falhas de comunicação com a nuvem. Abaixo estão alguns dos diagnósticos mais comuns que ele gera:

### 🔴 Tokens de Segurança Expirados (O mais crítico)
Provedores como o Microsoft OneDrive ou o Google Drive utilizam "tokens de acesso" por razões de segurança. Às vezes, devido a atualizações de política ou inatividade, esses tokens expiram. Em vez de exibir um erro de autenticação obscuro, o Analisador mostrará:
> *🚨 Token Expirado Detectado! A sua nuvem cortou a comunicação por motivos de segurança.*
Neste cenário, a ferramenta acionará uma ação de correção no terminal, perguntando se você deseja abrir o navegador. Ao confirmar, ele engatilhará a renovação com 1 clique diretamente no site oficial do provedor para restabelecer a conexão.

### 🟡 Arquivos em Uso (File Locked by Another Process)
Se o motor tentou sincronizar uma planilha do Excel ou um arquivo de banco de dados que estava aberto no seu computador no momento exato do upload, o Rclone pode falhar.
**O Diagnóstico:** O Analisador listará os arquivos específicos que não puderam ser enviados e aconselhará você a fechar os programas que estão utilizando aqueles arquivos antes do próximo ciclo de sincronização.

### 🟠 Limite de Banda ou Cota Excedida (Rate Limit / Quota Reached)
Se você tentar enviar terabytes de dados de uma vez só, nuvens como o Google Drive podem impor um limite diário de upload.
**O Diagnóstico:** A ferramenta informará que o servidor impôs um "Rate Limit" (limite de tráfego) temporário ou que o seu armazenamento em nuvem está oficialmente cheio.

---

## 3. Exemplos Práticos de Uso

### Exemplo 1: Descobrindo o Bloqueio Misterioso
Você percebeu pelo ícone de status que a conta "Trabalho" está há dois dias sem sincronizar, mesmo com a internet normal.
1. Você abre o terminal e roda `sync-engine analyze`.
2. A ferramenta lê o último log de erro gerado silenciosamente pelo motor de segundo plano.
3. O Analisador aponta: *"Atenção: A sincronização parou porque o token do OneDrive expirou"*.
4. A ferramenta oferece o link direto. Você clica, faz login no navegador e o Sync Engine destrava a conta instantaneamente.

### Exemplo 2: O Arquivo que Não Sobe
Você trabalhou em um projeto de vídeo o dia todo e, no fim da tarde, percebe que o arquivo principal não apareceu no computador da equipe na nuvem.
1. No menu principal, você entra no **Sync Error Analyzer**.
2. O diagnóstico mostra: *"Falha ao transferir 'Projeto_Final.mp4' - Arquivo estava bloqueado por outro processo"*.
3. Você se lembra que deixou o programa de edição de vídeo aberto e minimizado. Basta fechá-lo e o arquivo subirá na próxima verificação.

### Exemplo 3: Identificando Falhas de Nomenclatura Pós-Erro
Você rodou uma sincronização manual e, em vez da barra de progresso ficar verde no final, ela exibiu uma mensagem de erro vermelha com dezenas de caminhos de arquivo.
1. Em vez de tentar decifrar as linhas no terminal, você imediatamente aciona o Analisador.
2. A ferramenta informa: *"Erro de Caracteres Inválidos: A nuvem rejeitou 5 arquivos porque eles contêm pontos de interrogação no nome."*
3. Com o diagnóstico claro, você sabe exatamente que o próximo passo é rodar o **Higienizador de Nomes (`clean`)** na pasta afetada.