#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    print("BeautifulSoup4 not found. Please install with: pip install beautifulsoup4")
    raise

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "_mirror"
CONTENT = ROOT / "content"
STATIC = ROOT / "static"


def extract_main_html(html_path: Path) -> tuple[str, str, str]:
    """Return (title, description, inner_html_of_main) from a mirrored HTML file."""
    data = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(data, "html.parser")

    # Title and description
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else html_path.stem
    # Strip site name suffix if present
    title = re.sub(r"\s*-\s*Championnat.*$", "", title).strip()

    desc = ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        desc = desc_tag["content"].strip()

    # Main content
    main = soup.find("main", id="content") or soup.find("main")
    if main:
        main_html = "".join(str(x) for x in main.contents)
    else:
        # Fallbacks: Elementor wrappers commonly used on WP pages
        page_content = soup.find("div", class_="page-content")
        if page_content:
            main_html = page_content.decode()
        else:
            elem = soup.find("div", attrs={"data-elementor-type": re.compile(r"wp-(page|post)")})
            main_html = elem.decode() if elem else ""

    # Clean up some lazyload placeholders: prefer noscript images if present
    # Replace <img ... data-lazy-src=...> with that URL
    def fix_lazyload_images(s: str) -> str:
        # remove placeholder data URI src attributes
        s = re.sub(r'\s+src=\"data:image[^\"]*\"', '', s)
        # normalize lazyload attributes
        s = re.sub(r'data-lazy-srcset=\"[^\"]*\"', '', s)
        s = re.sub(r'data-lazy-sizes=\"[^\"]*\"', '', s)
        s = re.sub(r'data-lazy-src=\"([^\"]+)\"', r'src="\1"', s)
        # Convert data-background on DIVs to simple IMG
        def repl_div_to_img(m: re.Match) -> str:
            attrs = m.group(1)
            url = m.group(2)
            alt_match = re.search(r'aria-label=\"([^\"]*)\"', attrs)
            alt = alt_match.group(1) if alt_match else ''
            return f'<img src="{url}" alt="{alt}" />'

        s = re.sub(r'<div([^>]*?)\sdata-background=\"([^\"]+)\"[^>]*>(?:.*?)</div>', repl_div_to_img, s, flags=re.DOTALL)
        # Remove noscript placeholders
        s = re.sub(r"<noscript>(.*?)</noscript>", "", s, flags=re.DOTALL)
        return s

    main_html = fix_lazyload_images(main_html)

    # Rewrite absolute site URLs to root-relative
    main_html = re.sub(r"https?://championnatavionpapier\.fr", "", main_html)

    # Normalize wp-content paths
    main_html = main_html.replace("../wp-content/", "/wp-content/")
    main_html = main_html.replace("wp-content/", "/wp-content/")
    # Ensure no protocol-relative leftovers like //wp-content/
    main_html = re.sub(r'([\s\"\'=])//wp-content/', r'\1/wp-content/', main_html)

    return title, desc, main_html


def write_leaf_bundle(slug: str, title: str, desc: str, html: str):
    bundle_dir = CONTENT / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)
    out = bundle_dir / "index.html"
    safe_title = title.replace('"', '\\"')
    fm = [
        "---",
        f"title: \"{safe_title}\"",
    ]
    if desc:
        fm.append(f"description: \"{desc.replace('"', '\\"')}\"")
    fm.append("draft: false")
    fm.append("---\n")
    out.write_text("\n".join(fm) + html, encoding="utf-8")
    print(f"Wrote {out}")


def write_home(title: str, desc: str, html: str):
    out = CONTENT / "_index.html"
    safe_title = title.replace('"', '\\"')
    fm = [
        "---",
        f"title: \"{safe_title}\"",
    ]
    if desc:
        fm.append(f"description: \"{desc.replace('"', '\\"')}\"")
    fm.append("draft: false")
    fm.append("---\n")
    out.write_text("\n".join(fm) + html, encoding="utf-8")
    print(f"Wrote {out}")


def copy_uploads():
    src = MIRROR / "wp-content"
    dst = STATIC / "wp-content"
    if dst.exists():
        return
    if src.exists():
        print(f"Copying {src} -> {dst}")
        shutil.copytree(src, dst)


def main():
    CONTENT.mkdir(exist_ok=True)
    STATIC.mkdir(exist_ok=True)
    copy_uploads()

    # Home page
    home_html = MIRROR / "index.html"
    if home_html.exists():
        t, d, h = extract_main_html(home_html)
        write_home("Accueil", d, h)

    # Known content directories to import (have index.html)
    skip = {"wp-content", "wp-includes", "wp-json", "cdn-cgi", "comments", "feed"}
    for path in sorted(MIRROR.iterdir()):
        if not path.is_dir():
            continue
        if path.name in skip:
            continue
        html_file = path / "index.html"
        if not html_file.exists():
            continue
        t, d, h = extract_main_html(html_file)
        slug = path.name
        write_leaf_bundle(slug, t, d, h)


if __name__ == "__main__":
    main()
