# 🌐 Translation and Internationalization (i18n) Guide

Sync Engine natively supports the addition of new languages. This document is divided into two sections: end-user instructions for translating the interface into a native language, and technical documentation for developers who need to update the localization text catalog after modifying Python source code.

## 👤 Part 1: For Users (How to Add a New Language)

You do not need programming knowledge to translate the system. Follow the steps below to create, edit, and activate your custom language dictionary.

The default application installation path on Windows is `C:\Users\<YourUser>\AppData\Local\sync-engine\` (or `C:\Users\<YourUser>\sync-engine\`), and on Linux it is `$HOME/.local/share/sync-engine/`.

### 1. Locate the Locales Directory

Open your local Sync Engine installation directory. Locate the subfolder named `locales/`. This folder stores all JSON language translation dictionaries.

### 2. Create Your Language File

Rather than starting from scratch, duplicate an existing dictionary as a template:

1. Inside `locales/`, make a copy of any existing file (e.g., `pt.json` or `es.json`).

2. Rename the new copy using the official two-letter ISO language code for your target language (e.g., `ru.json` for Russian, `ko.json` for Korean, `it.json` for Italian).

### 3. Translate the Dictionary

Open your newly created `.json` file in any plain text editor (such as Notepad on Windows, or Gedit, Kate, or VS Code on Linux).

The file structure is formatted as key-value pairs:

```json
    "account details": "DETALHES DA CONTA",
    "active filters": "Filtros Ativos",
    "add filter": "Adicionar Filtro",
```

**Golden Rules for Translation:**

* **Never modify the left-hand key:** The text before the colon (`:`) enclosed in quotes is the internal string key Sync Engine uses for lookups. It must remain exactly as written (in lowercase, matching the base English codebase).

* **Translate only the right-hand value:** Replace the text following the colon with your localized string.

* **Preserve interface formatting:** If the original phrase includes brackets or control indicators (such as `[1]`, `(Y/N)`, `...`), preserve them in your translation so terminal menus remain aligned.

*Example translated into Russian:*

```json
    "account details": "ДЕТАЛИ УЧЕТНОЙ ЗАПИСИ",
    "active filters": "Активные фильтры",
    "add filter": "Добавить фильтр",
```

Save the file once you have finished editing.

### 4. Activate the New Language

Sync Engine automatically scans the `locales/` directory and exposes newly added languages:

1. Open your terminal and launch the wizard: `sync-engine config`.

2. From the main menu, go to **Global Settings**.

3. Select **Language**.

4. Your new language code will appear in the list (e.g., `RU`).

5. Select it. The system will prompt you to restart. Relaunch Sync Engine, and the interface will render using your new language translations.

## 🛠️ Part 2: For Developers (Script Automation Suite)

When new features are implemented or user-facing strings are modified in `.py` source files, the localization dictionaries must be synchronized. To eliminate manual tracking, Sync Engine includes an automation suite located in the `utilitarios/` directory.

Follow this execution workflow after completing source code changes:

### Step 1: Extract New Strings (`extrair_textos.py`)

Whenever you introduce a new localized string like `print(T("New message"))`, the base dictionary catalog becomes out of sync.

* **Function:** Scans all `.py` files across the project root, parses calls to `T()`, extracts the core sanitized string (trimming extraneous edge punctuation), and regenerates `dicionario_base.json`.

* **Execution:** Run `python3 utilitarios/extrair_textos.py`.

### Step 2: Synchronize Language Dictionaries (`sincronizar_idiomas.py`)

Once the base catalog is regenerated, new string keys must be populated across existing locale files (`pt.json`, `es.json`, etc.).

* **Function:** Reads `dicionario_base.json` and injects missing keys into every `.json` file in the `locales/` directory.

* **Behavior:** Existing localized translations are preserved untouched. **New keys** receive the base English string prefixed with an inspection badge (e.g., `"new feature": "✏️ New feature"`). It also cleans up orphan keys no longer referenced in the source code.

* **Execution:** Run `python3 utilitarios/sincronizar_idiomas.py`. Open the target `.json` file, search for `✏️`, provide the localized translation, and save.

> **💡 Quick Tip: List Pending Translations from Terminal**
> To quickly list all untranslated strings marked with `✏️` without manually browsing through JSON files, run:
>
> * **Linux / macOS:**
>   `grep "✏️" locales/pt.json`
>
> * **Windows (PowerShell):**
>   `Select-String -Pattern "✏️" locales\pt.json`

### Step 3: Code and Emoji Sanitization (`limpador_i18n.py`)

The `T()` lookup wrapper should not contain UI emojis directly (e.g., `T("✅ Saved")`), as this introduces extraneous glyphs into JSON dictionary keys.

* **Function:** Automatically refactors your Python source code. It detects `T()` calls containing emojis, moves the emoji outside the wrapper, and formats the output into a clean f-string (e.g., transforming it into `f"✅ {T('Saved')}"`). It also parses `locales/` to strip redundant spaces and rogue emojis from JSON keys.

* **Execution:** Run `python3 utilitarios/limpador_i18n.py` and inspect your `git diff`.

### Extra Tool 1: Batch Translation Injection (`injetar_traducoes.py`)

If you used an external tool or LLM to translate pending strings in batch, you do not need to merge them one by one.

* **Function:** Reads a JSON file with translated key-value pairs and merges them directly into the target official locale file. It overwrites marked entries, inserts new keys, and re-sorts the entire dictionary alphabetically.

* **Execution:** Save the newly translated JSON file in your project root (e.g., `new_strings.json`) and run:
  `python3 utilitarios/injetar_traducoes.py locales/pt.json new_strings.json`

### Extra Tool 2: Translation Coverage Audit (`auditoria_traducoes.py`)

To verify whether any hardcoded strings were committed without the `T()` wrapper:

* **Function:** Scans source code for console output calls (`print`, `logger`, `send_notification`) that lack a `T()` wrapper, while ignoring empty line breaks and structural divider strings (`"="*45`).

* **Execution:** Run `python3 utilitarios/auditoria_traducoes.py`. It outputs `linhas_sem_traducao.txt`, identifying the exact file and line number for any untranslated string.