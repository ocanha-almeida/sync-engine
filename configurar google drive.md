# 🔗 Configuração do Rclone com Google Drive (Client ID Próprio)

O uso de um Client ID personalizado é altamente recomendado para integrações com o Google Drive, pois evita o erro de "Rate Limit Exceeded" e interrupções de token que ocorrem ao dividir a cota padrão do Rclone com outros usuários.

## Etapa 1: Criar o Projeto no Google Cloud
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/) logado na conta Google que será sincronizada (ou em uma conta principal de administração).
2. No canto superior esquerdo (ao lado do logo do Google Cloud), clique no menu suspenso de projetos e selecione **Novo projeto** (New Project).
3. Dê um nome ao projeto (ex: `SyncEngine-Rclone`) e clique em **Criar**.
4. Aguarde a notificação de conclusão (ícone de sino) e selecione o projeto recém-criado.

## Etapa 2: Habilitar a API do Google Drive
1. No menu lateral esquerdo, vá em **APIs e Serviços** > **Biblioteca** (Library).
2. Na barra de pesquisa, digite `Google Drive API`.
3. Clique no resultado correspondente e depois no botão azul **Ativar** (Enable).

## Etapa 3: Configurar a Tela de Consentimento OAuth
1. No menu lateral, acesse **APIs e Serviços** > **Tela de consentimento OAuth** (OAuth consent screen).
2. Em "User Type", selecione **Externo** (External) e clique em **Criar**.
3. Preencha os campos obrigatórios:
   - **Nome do app:** `SyncEngine` (ou outro de sua preferência).
   - **E-mail para suporte do usuário:** Selecione seu e-mail no menu suspenso.
   - **Dados de contato do desenvolvedor:** Insira seu e-mail novamente.
4. Clique em **Salvar e Continuar** nas próximas telas (Escopos e Usuários de Teste) sem alterar nada.
5. **Atenção:** De volta ao painel da Tela de Consentimento, clique no botão **Publicar aplicativo** (Publish App) e confirme. *(Pular esta etapa fará com que o Rclone perca o acesso a cada 7 dias).*

## Etapa 4: Gerar as Credenciais (Client ID e Secret)
1. No menu lateral, acesse **APIs e Serviços** > **Credenciais** (Credentials).
2. Clique em **+ CRIAR CREDENCIAIS** (Create Credentials) no topo da página e selecione **ID do cliente OAuth** (OAuth client ID).
3. No campo "Tipo de aplicativo", selecione **App para computador** (Desktop app).
4. Dê um nome de identificação (ex: `Rclone Desktop`) e clique em **Criar**.
5. Uma janela aparecerá contendo seu **ID de Cliente** (`Client ID`) e sua **Chave Secreta do Cliente** (`Client Secret`). Mantenha esta janela aberta ou copie esses dois códigos temporariamente.

## Etapa 5: Vincular ao Rclone
Abra o seu terminal (como usuário padrão, sem `sudo`) e inicie a configuração base do Rclone:

```bash
rclone config
```

Responda ao assistente interativo com a seguinte sequência:
1. **`n`** (New remote)
2. **Name:** `gdrive_secundario` (ou o nome da sua escolha)
3. **Storage:** Digite `drive` (Google Drive)
4. **client_id:** Cole o seu *Client ID* gerado na Etapa 4.
5. **client_secret:** Cole a sua *Client Secret* gerada na Etapa 4.
6. **scope:** `1` (Full access all files)
7. **service_account_file:** Deixe em branco (pressione Enter)
8. **Edit advanced config?** `n` (No)
9. **Use auto config?** `y` (Yes)

O Rclone abrirá o navegador automaticamente. Faça o login na conta do Google Drive correspondente. Como o app foi criado por você, o Google pode exibir uma tela de "App não verificado". Basta clicar em **Avançado** > **Acessar SyncEngine (não seguro)** e conceder as permissões.

10. **Configure this as a Shared Drive (Team Drive)?** `n` (No) - *A menos que o alvo seja um drive de equipe do Google Workspace.*
11. Confirme o resumo com **`y`** (Yes this is OK) e depois digite **`q`** para sair do configurador.