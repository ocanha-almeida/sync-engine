# 📦 Guia de Upload para Arquivos Bloqueados (Bypass MAX_SIZE)

Quando você configura um Limite de Tamanho (`MAX_SIZE`) em uma conta do Sync Engine (por exemplo, bloqueando arquivos maiores que 500MB), o motor protege a sua largura de banda e o seu armazenamento na nuvem ignorando sumariamente qualquer arquivo que ultrapasse esse teto.

Mas e quando você **precisa** enviar um arquivo gigante específico que ficou de fora?

Como o Sync Engine foi construído sobre uma arquitetura flexível, você não precisa desativar a sua sincronização para resolver isso. Abaixo estão as quatro formas de realizar o upload de arquivos bloqueados, organizadas da mais elegante à mais técnica.

---

## 1. O Drive Virtual (A Solução Nativa e Elegante)

O recurso de **Drive Virtual (Mount)** do Sync Engine opera de forma totalmente paralela ao motor de sincronização em segundo plano. Ele cria um disco de rede no seu sistema operacional e atua diretamente nos servidores da nuvem, ignorando as restrições de filtro ou tamanho configuradas no seu painel de sincronização.

*   **Como fazer:**
    1. Abra o menu `sync-engine config`.
    2. Vá em **Extra Actions** (Ações Extras) e escolha **Mount Cloud as Virtual Drive**.
    3. Monte a nuvem desejada (ex: Unidade `X:` no Windows ou uma pasta no Linux).
    4. Abra o seu gerenciador de arquivos, pegue o arquivo gigante e arraste-o diretamente para dentro do Drive Virtual recém-criado.
*   **Comportamento do Sistema:** O upload é feito instantaneamente através da unidade. Nos próximos ciclos, o motor de sincronização continuará ignorando o arquivo na sua pasta local de sincronização, mas o arquivo já estará a salvo na nuvem.

## 2. Upload pelo Navegador (A Solução Universal)

A forma mais rápida e à prova de falhas, ideal para quem não quer lidar com menus ou montagens.

*   **Como fazer:**
    1. Abra o seu navegador web.
    2. Acesse o site do seu provedor (Google Drive, OneDrive, Dropbox, etc.) e faça o login.
    3. Arraste o arquivo gigante do seu computador diretamente para a pasta correspondente no navegador.
*   **Comportamento do Sistema:** O arquivo subirá normalmente. Quando o Sync Engine acordar no próximo ciclo e ler a nuvem, ele detectará o arquivo gigante lá, mas **não tentará baixá-lo** nem deletá-lo, pois a regra do `MAX_SIZE` orienta o motor a simplesmente ignorar sua existência.

## 3. Ajuste Temporário do Limite (A Solução via Menu)

Se você tem dezenas de arquivos pesados espalhados por várias subpastas e não quer procurá-los manualmente para arrastar pelo navegador, você pode usar a própria inteligência do motor a seu favor.

*   **Como fazer:**
    1. Abra `sync-engine config`, liste suas contas e edite a conta afetada.
    2. Mude temporariamente a opção **Change Max Size** para `0` (Ilimitado).
    3. Vá ao menu principal e rode uma **Sincronização Manual** (`sync-engine now`) no modo Seguro. O motor fará o upload de todos os arquivos gigantes automaticamente.
    4. Ao terminar, volte nas configurações da conta e redefina o limite original (ex: `500M`).

## 4. Comando Rclone Direto (Para Usuários Avançados)

Como o Sync Engine já deixou todas as suas contas devidamente autenticadas no "motor-base" (Rclone), você pode ignorar a interface do Sync Engine e disparar uma transferência cirúrgica via terminal.

*   **Como fazer:**
    1. Abra um terminal do seu sistema operacional.
    2. Digite o comando de cópia apontando diretamente para o destino na nuvem.
    *Exemplo:* `rclone copy /caminho/local/video_gigante.mp4 NomeDaConta:/Caminho/Destino/`
*   **Comportamento do Sistema:** O arquivo é enviado diretamente sem passar pelos filtros do Sync Engine.

---

## Exemplos Práticos de Uso

### Exemplo 1: A Entrega do Editor de Vídeo (Usando o Mount)
Você limitou sua conta do OneDrive a 1GB para evitar lotar a nuvem com lixo de edição. Hoje, você terminou um projeto e o arquivo final gerou 5GB.
**A Solução:** Em vez de mexer nas configurações do motor, você monta o OneDrive como Unidade `Z:`. Arrasta o vídeo final para dentro do `Z:` e envia o link para o cliente. O limite de 1GB continua protegendo sua conta de outros arquivos indesejados, mas a sua entrega foi feita.

### Exemplo 2: O Compartilhamento Rápido (Usando a Web)
O relatório `_ultimo_relatorio_tamanho.txt` indicou que um arquivo `.zip` de backups não subiu devido ao limite de tamanho.
**A Solução:** Você abre o Google Drive no Chrome, acha a pasta de backups e arrasta o `.zip` lá para dentro. O Sync Engine continuará rodando invisível e ignorando esse `.zip`, garantindo que ele não consuma espaço se você vincular essa nuvem a um notebook secundário com HD pequeno.

### Exemplo 3: O "Dia de Faxina" (Usando o Ajuste Temporário)
Você limitou os envios da empresa a 100MB durante toda a semana útil para não engarrafar a rede do escritório. Chegou sexta-feira à noite e existem vários projetos grandes acumulados que precisam subir.
**A Solução:** Você abre as configurações, muda o Limite de Tamanho para `0` (ilimitado) e vai embora. Como o Agendador de Tarefas (Cron) do Sync Engine já estava configurado para rodar uma Sincronização Forçada de madrugada, o sistema subirá tudo automaticamente à noite. Na segunda-feira de manhã, você retorna o limite para 100MB.