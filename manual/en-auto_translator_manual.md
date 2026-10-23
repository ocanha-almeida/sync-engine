# 🌐 Auto Translator Manual (`auto_tradutor.py`)

The **Auto Translator** is an intelligent utility designed to fully automate the internationalization (i18n) workflow of the Sync Engine. 

Instead of manually translating new strings across all 7 supported languages, this script automatically extracts new texts from the source code, identifies missing translations, and uses the **Google Translate API** to translate and inject them into the respective `.json` files.

## ✨ Key Features
* **Zero Authentication:** Uses the `deep-translator` library, which interacts directly with the public Google Translate API. No API keys or Google Cloud accounts are required.
* **Smart Sync:** Automatically runs `extrair_textos.py` and `sincronizar_idiomas.py` before translating, ensuring the base dictionary is always up-to-date.
* **Targeted Translation:** It only translates strings marked with the `✏️ ` emoji (pending translations), preserving your existing manual corrections and avoiding redundant API calls.

---

## ⚙️ Prerequisites

Since the utility uses external libraries, it is highly recommended to run it inside the Python Virtual Environment (`.venv`) to comply with PEP 668 on Linux.

1. **Activate the Virtual Environment:**
   ```bash
   # On Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

2. **Install the required library:**
   ```bash
   pip install deep-translator
   ```

---

## 🚀 How to Use

Whenever you add new `T("Your text here")` strings to the Sync Engine Python code, simply run the utility from the root folder:

```bash
python3 utilitarios/auto_tradutor.py
```

### The Workflow:
1. **Extraction:** The script will scan the codebase and update `dicionario_base.json`.
2. **Synchronization:** It will compare the base dictionary with all language files in the `locales/` folder, adding missing strings with a `✏️ ` prefix.
3. **Translation:** It will iterate through each language (German, Spanish, French, Italian, Japanese, Portuguese, and Simplified Chinese), translate the pending strings, remove the pencil marker, and save the files automatically.

---

## ⚠️ Troubleshooting: "Too Many Requests" (HTTP 429 / 503)

Google Translate imposes daily and per-second limits on anonymous API requests. If you translate a massive amount of strings at once, your IP might get temporarily blocked, resulting in the following error:

> `Server Error: You made too many requests to the server.`

**How to fix it:**
1. **Wait:** The block is usually temporary. Wait a few minutes or change your IP (e.g., connect to a mobile hotspot) and try again.
2. **Increase the Delay:** Open `utilitarios/auto_tradutor.py` and locate the `time.sleep()` command inside the translation loop. Increase the value to slow down the requests and mimic human behavior:
   ```python
   # Change from:
   time.sleep(0.5)
   
   # To:
   time.sleep(2) # Pauses for 2 seconds between each translated phrase
   ```