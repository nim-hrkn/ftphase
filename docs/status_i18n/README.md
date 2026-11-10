# status_i18n — the JA / EN / ID switch of the status artifact "ftphase 開発状況" (2026-11-10)

The published artifact (https://claude.ai/artifact/NZEKsthcgzmVw4QppWjifk) is the Japanese page with every text block tagged
`data-i18n="<n>"`, plus two embedded JSON dictionaries (English, Indonesian) and a small script with the language buttons
(top right; the choice is kept in localStorage). `extract.py` tags the blocks of a Japanese page and writes `src_*.json`
(5,000-character chunks), `RULES.md` is the brief given to the translators (one subagent per chunk and language),
`build.py` validates each translation (same key set, same HTML tag multiset, no kana outside attributes) and injects the
dictionaries + switcher. `src_all.json` holds the 1,152 Japanese source blocks of version 52; `en/`, `id/` the translations.

Updating the page: edit the Japanese page (keep the `data-i18n` ids), run `extract.py` on it (new blocks get new ids),
translate only the ids whose Japanese text changed or is new, drop them into `en/`/`id/`, run `build.py`, publish.
SVG labels are shrunk/squeezed by the script when a translation is longer than the Japanese text.
