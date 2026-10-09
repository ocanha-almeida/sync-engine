# 🧹 Guia do Higienizador de Nomes (Cleaner & Collision Checker)

Os provedores de nuvem (como Google Drive, OneDrive, Dropbox) possuem regras muito estritas sobre como um arquivo pode ser nomeado. Se o Sync Engine tentar enviar um arquivo com caracteres não suportados pela nuvem, o envio falhará e a sincronização daquela pasta será interrompida.

O **Higienizador de Nomes** é uma ferramenta de manutenção preventiva e corretiva que varre suas pastas locais em busca de arquivos problemáticos, corrige-os com segurança e gera um relatório detalhado.

---

## 1. O que o Higienizador Resolve?

O Higienizador foca em duas frentes principais de erro que costumam travar sincronizações:

1. **Caracteres Especiais e Inválidos:** 
   O Windows e o Linux muitas vezes permitem a criação ou extração de arquivos que contêm caracteres proibidos em servidores de nuvem. O Higienizador rastreia e limpa símbolos como: `?`, `*`, `:`, `<`, `>`, `"`, `|`, `\`, `/`, além de caracteres Unicode problemáticos (ex: estrelas `★`, aspas inclinadas, barras exóticas).
   
2. **Colisão de Maiúsculas e Minúsculas (Case-Sensitivity):**
   No Linux e no macOS, é possível ter dois arquivos na mesma pasta chamados `Relatorio.pdf` e `relatorio.pdf`. No entanto, nuvens e sistemas Windows não diferenciam maiúsculas de minúsculas, o que causa a sobrescrita acidental ou o travamento ("Colisão de Nome"). O Higienizador identifica essas duplicatas estruturais antes que elas causem corrupção na nuvem.

*Nota:* O Higienizador é inteligente e **respeita os seus filtros**. Se uma pasta estiver bloqueada com o marcador `.nosync` ou estiver listada nos seus filtros de exclusão, ela não será analisada nem modificada.

---

## 2. Como Utilizar a Ferramenta

Você pode acessar o Higienizador de duas maneiras:
*   **Pelo Terminal:** Digite `sync-engine clean` e pressione Enter.
*   **Pelo Menu Interativo:** Digite `sync-engine config` e escolha a opção **Cleaner and Collision Checker** na seção de Manutenção.

Ao abrir a ferramenta, você verá uma lista com todas as suas contas configuradas e uma opção extra:

*   **[Contas Cadastradas]:** O sistema puxa automaticamente o caminho da sua pasta local e também os filtros daquela conta.
*   **Enter a manual path (Inserir caminho manual):** Permite que você digite qualquer caminho do seu computador (ex: `C:\Downloads` ou `~/Documentos`) para limpar uma pasta que sequer faz parte da sincronização do Sync Engine.

Ao finalizar a execução, um relatório completo detalhando quais arquivos foram renomeados será salvo na sua pasta de relatórios padrão (com o nome `_ultimo_relatorio_higienizador.txt`).

---

## 3. Exemplos Práticos de Uso

### Exemplo 1: Limpeza Pós-Extração (Arquivos Antigos ou da Internet)
Você baixou um arquivo `.zip` contendo uma coleção de apostilas antigas ou arquivos de sistema do macOS e o extraiu dentro da sua pasta sincronizada do Google Drive. Muitos arquivos vieram com nomes como `Aula 01: Introdução.pdf` ou `Backup 2020/2021.txt`.
**O Risco:** A sincronização vai travar ao encontrar os dois pontos (`:`) e a barra (`/`).
**A Solução:**
1. Abra o terminal e rode `sync-engine clean`.
2. Selecione a sua conta do Google Drive.
3. O Higienizador varrerá a pasta, removerá ou substituirá os caracteres proibidos de forma inteligente e emitirá um aviso de que a pasta está segura.
4. A sincronização continuará naturalmente.

### Exemplo 2: O Alerta Vermelho de Colisão (O Motor Travou)
Você deixou o Sync Engine rodando em segundo plano no Linux. De repente, você recebe uma notificação vermelha ou, ao tentar rodar `sync-engine now`, vê o seguinte aviso:
> *🚨 ALERT: Case-Sensitivity Conflicts or Invalid Characters detected!*
> *Sync for 'Trabalho' paused. Use Option 9 to fix.*
**A Causa:** O motor automático interceptou uma colisão perigosa (como `Foto.JPG` e `foto.jpg` no mesmo diretório) e, para proteger seus dados na nuvem, pausou a sincronização daquela conta.
**A Solução:**
1. Não ignore o erro. Abra o Higienizador (`sync-engine clean`).
2. Selecione a conta "Trabalho".
3. O sistema apontará onde está o conflito de nomenclatura, renomeando o arquivo conflitante para evitar a perda de dados. Com o conflito resolvido, o motor retomará a sincronização sozinho.

### Exemplo 3: Limpeza Avulsa (HD Externo / Pendrive)
Um cliente te entregou um Pendrive cheio de arquivos mal nomeados (com emojis não padronizados, estrelas e barras) e você precisa copiar isso para um servidor Windows, mas o sistema acusa erro de caminho.
**A Solução:**
1. Você não precisa cadastrar o Pendrive no Sync Engine.
2. Rode `sync-engine clean` e selecione **Enter a manual path**.
3. Digite a letra do Pendrive ou o caminho da pasta (ex: `E:\Arquivos_Cliente`).
4. O Higienizador atuará de forma independente, corrigindo todos os nomes corrompidos no pendrive em poucos segundos.