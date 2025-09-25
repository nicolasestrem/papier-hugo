# Championnat Avion Papier – Hugo Site

This repo contains a Hugo static site converted from https://championnatavionpapier.fr/ (WordPress).

## Prereqs
- Hugo Extended installed (v0.150+)
- Python 3.12 with venv (optional, for re-import)

## Structure
- `content/` – Imported pages (HTML with front matter)
- `static/wp-content/` – Images and assets from WordPress uploads
- `themes/PaperMod/` – Theme
- `_mirror/` – Raw wget mirror (ignored)

## Run locally
```bash
hugo server -D
```

## Re-import content (optional)
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install beautifulsoup4
python scripts/import_from_mirror.py
```

## Build
```bash
hugo --minify
```

Update `hugo.toml` `baseURL` when deploying.

