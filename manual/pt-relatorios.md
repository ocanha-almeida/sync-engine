# 📄 Guia de Relatórios, Sync Logs e Auditoria de Arquivos Grandes

O Sync Engine foi desenhado para ser transparente. Toda ação importante gera um registro, seja um log contínuo do motor invisível ou um relatório de texto detalhado solicitado por você. O sistema isola esses arquivos por conta e os padroniza com carimbos de data e hora, permitindo que você audite tudo o que ocorre nos bastidores.

---

## 1. Onde ficam os Relatórios e Logs? (Report Save Location)

Por padrão, todos os relatórios e logs gerados pelo Sync Engine são salvos em uma pasta padrão dentro do diretório do programa. No entanto, você pode redirecionar a gravação desses arquivos para qualquer lugar do seu computador.

**Como alterar o local global:**
1. Abra o menu interativo: `sync-engine config`.
2. Acesse **Global Settings** (Configurações Globais).
3. Selecione **Change Report Save Location**.
4. Digite o caminho absoluto da pasta onde deseja concentrar seus logs (ex: `C:\Meus_Logs_Sync` no Windows, ou `~/Documentos/Relatorios` no Linux).

A partir desse momento, todos os relatórios futuros e os arquivos de Log Contínuo passarão a ser gravados nesse novo diretório.

---

## 2. O Log de Sincronização Contínua (Sync.log)

Enquanto os relatórios de texto (`.txt`) são gerados para ações específicas (como um teste ou limpeza), os arquivos `.log` (ex: `[nome_da_conta]_sync.log`) são os "diários oficiais" do motor em segundo plano.

**Como funciona o Sync Log:**
* **Registro Silencioso:** Sempre que o Background Motor acorda e verifica as pastas, ele anota nesse log se encontrou arquivos novos, se houve alguma transferência ou se a nuvem já estava perfeitamente alinhada.
* **Isolamento por Conta:** Cada conta configurada possui o seu próprio arquivo `sync.log` independente, evitando que as informações se misturem em um único arquivo gigante.
* **Auto-Rotação (Limpeza Inteligente):** Você não precisa se preocupar com o arquivo `.log` consumindo todo o seu HD com o passar dos meses. O motor é programado para realizar a rotação automática do log: assim que o arquivo atinge um determinado tamanho, o Sync Engine o arquiva ou o limpa, garantindo que você tenha sempre o histórico recente sem desperdício de espaço.

---

## 3. Auditoria de Arquivos Grandes (Large File Reports)

Se você configurou um limite de tamanho (`MAX_SIZE`) para uma conta (por exemplo, bloqueando arquivos maiores que 500MB), o Sync Engine pulará esses arquivos. Para saber **quais arquivos ficaram de fora**, utilize a ferramenta de Auditoria:

1. No menu principal, vá para a seção de **Manutenção (Maintenance)**.
2. Escolha **Large File Reports** (Relatório de Arquivos Grandes).
3. Selecione a conta que deseja auditar.
4. O sistema gerará um documento (`_ultimo_relatorio_tamanho.txt`) listando o nome do arquivo, a localização exata e o tamanho dele em MB ou GB.

---

## 4. O Ecossistema de Registros do Sync Engine

Ao consultar sua pasta de relatórios, você encontrará diferentes tipos de documentos, sempre prefixados com o nome da conta. Os principais são:

*   **`[conta]_sync.log`**: O diário contínuo do motor em segundo plano.
*   **`[conta]_ultima_sincronizacao_manual.txt`**: Registra o resultado exato da última vez que você rodou o comando `now` (Sincronização Manual).
*   **`[conta]_ultimo_dry_run.txt`**: O log gerado pelo Modo de Simulação Segura (`test`), mostrando o que seria alterado sem modificar nada.
*   **`[conta]_ultimo_relatorio_higienizador.txt`**: A lista de arquivos que possuíam nomes problemáticos ou conflitantes e que foram corrigidos pela ferramenta `clean`.
*   **`migracao_*.txt`**: Relatórios da transferência direta entre nuvens (Cloud-to-Cloud Migration).

---

## 5. Exemplos Práticos de Uso

### Exemplo 1: Verificando a Atividade Silenciosa
Você configurou a conta "Trabalho" para sincronizar a cada 10 minutos em segundo plano, mas passou a manhã inteira sem criar arquivos novos.
**A Solução:** Para confirmar se o motor está realmente rodando e vigiando a pasta, basta abrir o arquivo `Trabalho_sync.log`. Lá estarão registrados todos os "acordares" do motor com os carimbos de hora, confirmando que ele checou a pasta, não encontrou alterações e voltou a dormir.

### Exemplo 2: Monitoramento Remoto de Logs
Você instalou o Sync Engine no servidor do seu escritório (Linux), mas quer acompanhar os relatórios e logs do seu celular ou de casa.
**A Solução:**
1. No Sync Engine do servidor, vá em **Global Settings**.
2. Altera o **Report Save Location** para apontar para uma pasta do Google Drive que já está sincronizada.
3. Agora, toda vez que o sistema rodar ou gerar o `sync.log`, o arquivo será enviado para a nuvem.

### Exemplo 3: O Que Ficou Para Trás? (Auditoria de MAX_SIZE)
Sua conta limitou arquivos a 2GB e um vídeo não subiu.
**A Solução:** Rode a opção **Large File Reports**. O relatório gerado mostra imediatamente o tamanho e a localização exata do arquivo bloqueado.