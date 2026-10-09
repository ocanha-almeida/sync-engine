# 🛠️ Auxiliary Tools Guide (i18n Utilities)

The `utilitarios/` directory within Sync Engine houses an automation suite built specifically to streamline source code maintenance and the internationalization (i18n) ecosystem.

These scripts eliminate the need for developers to manually hunt for missing translation keys or refactor user-facing strings line by line.

Below is the documentation covering each tool and its operational role.

## 1. Extraction and Synchronization Workflow

These are the routine maintenance utilities. Whenever you modify `.py` files and introduce new user-facing strings wrapped in the `T()` function, run these scripts to update the localization catalogs.

### 📝 `extrair_textos.py`

* **What it does:** Scans all Python source files (`.py`) across the project root for occurrences of the `T("text")` wrapper function. It extracts string literals, sanitizes edge whitespace and punctuation, and compiles an updated master dictionary named `dicionario_base.json`.

* **When to use:** Immediately after completing a new feature or modifying console output and menu labels.

* **Command:** `python3 utilitarios/extrair_textos.py`

### 🔄 `sincronizar_idiomas.py`

* **What it does:** Reads the freshly generated `dicionario_base.json` catalog and cross-references it against every translation dictionary in the `locales/` directory (e.g., `pt.json`, `en.json`, `es.json`).

* **Key Behavior:** It preserves all existing localized translations, prunes obsolete orphan keys that were deleted from the source code, and **injects new keys** automatically prefixed with an inspection badge (`✏️ `). This allows translators to open any locale file and immediately locate pending strings.

* **When to use:** Immediately after running the extraction script to prepare the `.json` files for translation.

* **Command:** `python3 utilitarios/sincronizar_idiomas.py`

## 2. Injection and Refactoring Tools

### 💉 `injetar_traducoes.py`

* **What it does:** Enables batch merging of pending translation keys (such as those generated via an LLM or external translation service) back into the official locale dictionary. The script scans the target dictionary for the `✏️ ` badge, replaces it with the corresponding translated value from your temporary JSON file, and sorts the entire `.json` file alphabetically for consistency.

* **When to use:** When you have a separate JSON file containing newly translated strings and want to merge them into the target language file without manual copy-pasting.

* **Command:** `python3 utilitarios/injetar_traducoes.py locales/en.json new_translations.json`

### 🧹 `limpador_i18n.py`

* **What it does:** Console terminal drivers and JSON lookup mechanisms can behave unpredictably when emojis are embedded directly inside translation keys. This script acts as an automated AST/code refactoring utility. It parses your `.py` source files, extracts emojis trapped inside `T("✅ Saved")` calls, and transforms them into clean f-strings: `f"✅ {T('Saved')}"`. It also cleans trailing spaces and rogue emojis from JSON keys.

* **When to use:** Prior to staging a Git commit to ensure no emojis or formatting anomalies corrupt the JSON dictionary indices.

* **Command:** `python3 utilitarios/limpador_i18n.py`

## 3. Auditing and Coverage Tools

If you developed an interactive CLI menu and want to verify whether any hardcoded strings escaped localization, these utilities function as automated quality inspectors.

### 🕵️ `auditoria_traducoes.py`

* **What it does:** Inspects `.py` files for standard output calls (such as `print()`, `logger.info()`, `input()`, etc.) containing raw string literals that were not wrapped in the `T()` function. It skips divider rules and decorative characters (e.g., `print("-" * 50)`).

* **Output:** Generates an audit report named `linhas_sem_traducao.txt` detailing the exact file path, line number, and unlocalized string snippet.

* **Command:** `python3 utilitarios/auditoria_traducoes.py`

### 🕵️‍♂️ `auditoria_traducoes_2.py`

* **What it does:** A specialized secondary inspection script equipped with aggressive regular expressions (regex). It catches edge cases that the primary AST auditor might overlook, such as raw strings inside local dictionary assignments, `match/case` branches, `sys.exit()` error messages, or nested interactive terminal prompts.

* **Output:** Complements the primary auditor to help developers achieve 100% i18n coverage across the codebase.

## 🚦 Recommended Development Workflow (Summary)

After modifying user-facing features in the codebase, follow this sequential pipeline before publishing a release:

1. Run `limpador_i18n.py` to extract emojis from localization wrappers into formatted f-strings.

2. Run `auditoria_traducoes.py` to ensure no `print()` or CLI prompt was left unwrapped.

3. Run `extrair_textos.py` to compile the base string catalog (`dicionario_base.json`).

4. Run `sincronizar_idiomas.py` to propagate new keys with the `✏️ ` badge to `locales/`.

5. Translate marked entries (either manually or in batch using `injetar_traducoes.py`).