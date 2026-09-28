# Changelog


## [7.2] - 2026-09-25
### Added
- Suporte nativo à internacionalização (i18n) com dicionários JSON (EN, PT-BR, PT-PT, ES, DE, FR, ZH, IT).
- Mecanismo de *fallback* inteligente para variantes regionais de idiomas.

### Fixed
- Correção no modo Dry-Run (`test`) para respeitar o limite de tamanho e suprimir códigos de escape ANSI em relatórios `.txt`.
- Sincronização rigorosa da chave `MAX_SIZE` em letras maiúsculas na arquitetura multi-contas.

## [7.0] - 2026-07-15
### Added
- Migração direta de Nuvem para Nuvem via RAM.
- Gerenciamento de Disco Virtual (Mount) nativo para Linux e Windows.
