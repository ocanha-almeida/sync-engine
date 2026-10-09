# ⚙️ Guia do Motor em Segundo Plano e Diagnóstico

O coração do Sync Engine é o seu **Motor em Segundo Plano (Background Motor)**. Diferente de muitos sistemas de backup corporativos, ele foi projetado com uma arquitetura focada na segurança, privacidade e baixo consumo de recursos, rodando inteiramente de forma invisível no seu computador.

---

## 1. Arquitetura: O "Espaço de Usuário" (User Space)

O diferencial de segurança mais importante do Sync Engine é que o motor opera estritamente no **Espaço de Usuário (User Space)**.

*   **Zero Privilégios Administrativos:** O Sync Engine nunca pedirá sua senha de Administrador no Windows, nem exigirá acesso `root` (`sudo`) no Linux para sincronizar os seus arquivos.
*   **Isolamento de Dados:** Como roda atrelado ao seu usuário específico do sistema operacional, ele só tem acesso às pastas que você mesmo tem acesso. Ele não consegue ler arquivos de outros usuários da mesma máquina.
*   **Inicialização Segura:** 
    *   No **Linux**, ele se integra nativamente como um serviço de usuário (`systemctl --user`), iniciando automaticamente apenas quando você faz login na sua conta.
    *   No **Windows**, ele cria um registro de inicialização silenciosa (`pythonw.exe`) atrelado exclusivamente à sua sessão.

---

## 2. Gerenciamento do Motor

Você tem controle total sobre o ciclo de vida do motor acessando a seção **Background Motor** no menu principal (`sync-engine config`). As opções disponíveis são:

*   **▶️ Start Service (Ligar):** Instala (se for a primeira vez) e inicia o serviço invisível. Ele passará a iniciar automaticamente junto com o seu computador.
*   **⏸️ Stop / Kill Service (Desligar):** Interrompe a execução imediatamente e remove a inicialização automática. Ideal se você for rotear a internet do seu celular e não quiser consumo de banda de fundo.
*   **📊 View Service Status (Status):** Mostra um painel em tempo real informando se o motor está **Ativo (Running)** ou **Parado (Stopped)**, além de exibir a data e hora da última vez que ele concluiu um ciclo de varredura (último "acordar").

---

## 3. O Diagnóstico do Sistema (System Doctor)

Se o Sync Engine apresentar qualquer lentidão, falha de inicialização ou se a sincronização não estiver ocorrendo, a sua primeira parada deve ser a ferramenta de diagnóstico.

*   **Como acessar:** No menu principal, vá em **Manutenção** > **System Diagnostic (Doctor)**.

O Doctor fará uma varredura de "Raio-X" na sua instalação e exibirá um painel de semáforo (Verde, Amarelo, Vermelho) avaliando os seguintes pilares:
1.  **Dependências do Sistema:** Verifica se o Python e o núcleo do Rclone estão devidamente instalados e acessíveis no *PATH* do seu sistema.
2.  **Integridade do Banco de Dados:** Testa a leitura e gravação no arquivo SQLite (onde o Sync Engine guarda o índice rápido de arquivos).
3.  **Conexões Remotas:** Tenta disparar um "ping" silencioso para todas as suas contas cadastradas para garantir que nenhuma está com o token de segurança revogado pela nuvem.
4.  **Caminhos Locais:** Confirma se as pastas locais (ex: `~/gdrive`) vinculadas às nuvens ainda existem fisicamente no seu HD.

---

## 4. Atualização e Desinstalação

A arquitetura de espaço de usuário também torna a manutenção do sistema muito mais limpa:

*   **Auto-Atualização (Update System):** Pelo menu do motor, você pode solicitar uma atualização. O Sync Engine fará o download da versão mais recente direto do GitHub oficial e atualizará seus próprios arquivos, sem tocar nas suas configurações ou contas (`config.json`), garantindo uma transição contínua.
*   **Desinstalação Limpa (Uninstall/Clean-up):** Com apenas um clique, esta opção desfaz a inicialização automática, mata os processos em andamento e entrega instruções exatas sobre quais duas pastas locais você deve apagar (a pasta do programa e a pasta global do rclone) para remover o Sync Engine permanentemente do seu computador, sem deixar "lixo" no registro do Windows ou nos serviços globais do Linux.