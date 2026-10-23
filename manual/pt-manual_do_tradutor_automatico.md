# 🌐 Manual do Tradutor Automático (`auto_tradutor.py`)

O **Tradutor Automático** é um utilitário inteligente criado para automatizar completamente o fluxo de internacionalização (i18n) do Sync Engine. 

Em vez de traduzir manualmente novas strings para todos os 7 idiomas suportados, este script extrai automaticamente novos textos do código-fonte, identifica traduções pendentes e utiliza a **API do Google Translate** para traduzi-las e injetá-las nos respectivos arquivos `.json`.

## ✨ Principais Recursos
* **Zero Autenticação:** Utiliza a biblioteca `deep-translator`, que interage diretamente com a API pública do Google Translate. Não exige chaves de API (`API Keys`) ou contas no Google Cloud.
* **Sincronização Inteligente:** Executa automaticamente o `extrair_textos.py` e o `sincronizar_idiomas.py` antes de traduzir, garantindo que o dicionário base esteja sempre atualizado.
* **Tradução Cirúrgica:** Ele traduz apenas as strings marcadas com o emoji `✏️ ` (traduções pendentes), preservando suas correções manuais existentes e evitando chamadas redundantes à API.

---

## ⚙️ Pré-requisitos

Como o utilitário usa bibliotecas externas, é altamente recomendável executá-lo dentro do Ambiente Virtual Python (`.venv`) para respeitar a norma PEP 668 no Linux.

1. **Ative o Ambiente Virtual:**
   ```bash
   # No Linux:
   source .venv/bin/activate
   
   # No Windows:
   .venv\Scripts\activate
   ```

2. **Instale a biblioteca necessária:**
   ```bash
   pip install deep-translator
   ```

---

## 🚀 Como Usar

Sempre que você adicionar novas strings `T("Seu texto aqui")` no código Python do Sync Engine, basta rodar o utilitário a partir da pasta raiz:

```bash
python3 utilitarios/auto_tradutor.py
```

### O Fluxo de Trabalho:
1. **Extração:** O script fará a varredura no código e atualizará o `dicionario_base.json`.
2. **Sincronização:** Ele comparará o dicionário base com todos os arquivos da pasta `locales/`, adicionando as strings ausentes com o prefixo `✏️ `.
3. **Tradução:** Ele iterará por cada idioma (Alemão, Espanhol, Francês, Italiano, Japonês, Português e Chinês Simplificado), traduzirá as strings pendentes, removerá o marcador de lápis e salvará os arquivos automaticamente.

---

## ⚠️ Solução de Problemas: "Too Many Requests" (Muitas Requisições)

O Google Translate impõe limites diários e por segundo em requisições anônimas. Se você traduzir uma quantidade massiva de strings de uma só vez, seu IP pode ser bloqueado temporariamente, resultando no seguinte erro:

> `Server Error: You made too many requests to the server.`

**Como consertar:**
1. **Aguarde:** O bloqueio geralmente é temporário. Espere alguns minutos ou mude seu IP (ex: roteando a internet do celular) e tente novamente.
2. **Aumente a Pausa (Delay):** Abra o arquivo `utilitarios/auto_tradutor.py` e localize o comando `time.sleep()` dentro do laço de tradução. Aumente o valor para desacelerar as requisições e simular o comportamento humano:
   ```python
   # Mude de:
   time.sleep(0.5)
   
   # Para:
   time.sleep(2) # Pausa de 2 segundos entre cada frase traduzida
   ```