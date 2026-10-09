# 🔗 Configuração do Rclone com Google Drive (Client ID Próprio)

O uso de um Client ID personalizado é altamente recomendado para integrações com o Google Drive, pois evita o erro de "Rate Limit Exceeded" e interrupções de token que ocorrem ao dividir a cota padrão do Rclone com a comunidade global de usuários.

## Etapa 1: Criar o Projeto no Google Cloud
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/) logado na conta Google que será sincronizada.
2. No canto superior esquerdo (ao lado do logo do Google Cloud), clique no menu suspenso de projetos e selecione **Novo projeto** (New Project).
3. Dê um nome ao projeto (ex: `SyncEngine-Rclone`) e clique em **Criar**.
4. Aguarde a notificação de conclusão e certifique-se de selecionar o projeto recém-criado no menu superior.

## Etapa 2: Habilitar a API do Google Drive
1. No menu lateral esquerdo, vá em **APIs e Serviços** > **Biblioteca** (Library).
2. Na barra de pesquisa, digite `Google Drive API`.
3. Clique no resultado correspondente e depois no botão azul **Ativar** (Enable).

## Etapa 3: Configurar a Tela de Consentimento (Nova Interface)
Contas `@gmail.com` comuns não podem usar aplicativos "Internos" (restritos ao Google Workspace empresarial). Precisamos criar um app "Externo" e preencher dados básicos para liberar a publicação.

1. No menu lateral, acesse **APIs e Serviços** > **Tela de consentimento OAuth** (OAuth consent screen).
2. Em "Tipo de usuário" (User Type), selecione **Externo** (External) e clique em **Criar**.
3. Na seção **Informações do App** / **Branding**:
   - **Nome do app:** `SyncEngine` (ou outro de sua preferência).
   - **E-mail para suporte do usuário:** Selecione seu e-mail no menu suspenso.
   - **Página inicial do aplicativo:** `https://rclone.org`
   - **Link da Política de Privacidade:** `https://rclone.org`
   - **Domínios autorizados:** Clique em "Adicionar domínio" e digite `rclone.org`
   - **Dados de contato do desenvolvedor:** Insira seu e-mail novamente.
4. Clique em **Salvar e Continuar** nas telas seguintes (Escopos e Usuários de Teste) sem alterar nada.

## Etapa 4: Publicar o Aplicativo (Crucial)
*Nota: Pular esta etapa fará com que o Google revogue o acesso do Rclone a cada 7 dias.*
1. No menu lateral esquerdo, clique na aba **Público-alvo** (Audience).
2. O status do seu aplicativo estará como "Testando". Clique no botão **Publicar aplicativo** (ou *Mudar para Produção*).
3. O Google exibirá um alerta dizendo que o app precisa de verificação. **Ignore o aviso e confirme.** Como o aplicativo é apenas para seu uso pessoal através do Rclone, a verificação oficial não é necessária.

## Etapa 5: Gerar as Credenciais (Client ID e Secret)
1. No menu lateral, acesse **Credenciais** (Credentials).
2. Clique em **+ CRIAR CREDENCIAIS** no topo da página e selecione **ID do cliente OAuth** (OAuth client ID).
3. No campo "Tipo de aplicativo", selecione **App para computador** (Desktop app).
4. Dê um nome de identificação (ex: `Rclone Desktop`) e clique em **Criar**.
5. Uma janela aparecerá contendo seu **ID de Cliente** (`Client ID`) e sua **Chave Secreta do Cliente** (`Client Secret`). Mantenha esta janela aberta para copiar os códigos.

## Etapa 6: Vincular as chaves ao Rclone
Abra o seu terminal (como usuário padrão, sem `sudo`) e inicie a configuração base do Rclone:

```bash
rclone config
```

Responda ao assistente interativo com a seguinte sequência:
1. **`n`** (New remote)
2. **Name:** `gdrive_secundario` (ou o nome da sua escolha)
3. **Storage:** Digite `drive` (Google Drive)
4. **client_id:** Cole o seu *Client ID* gerado na Etapa 5.
5. **client_secret:** Cole a sua *Chave Secreta* gerada na Etapa 5.
6. **scope:** `1` (Full access all files)
7. **service_account_file:** Deixe em branco (pressione Enter)
8. **Edit advanced config?** `n` (No)
9. **Use auto config?** `y` (Yes)

O Rclone abrirá o navegador automaticamente para você fazer login na sua conta Google. 
> **Aviso de Segurança do Google:** O Google exibirá uma tela vermelha informando "O Google não verificou este app". Isso é normal (já que não enviamos para auditoria na Etapa 4). Clique em **Avançado** e, em seguida, em **Acessar SyncEngine (não seguro)** para permitir a conexão.

10. **Configure this as a Shared Drive (Team Drive)?** `n` (No)
11. Confirme o resumo com **`y`** (Yes this is OK) e depois digite **`q`** para sair do configurador.