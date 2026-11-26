#!/usr/bin/env python3
"""
One-time: capture the WordPress theme "shell" from the live site so the static
pages look identical:
  public/assets/theme.css     ← theme + global styles + your Additional CSS + nav CSS
  public/assets/fonts/*.woff2 ← Manrope / Fira Code (self-hosted)
  partials/header.html        ← the Stargazer nav bar
  partials/footer.html        ← the WordPress footer
Run before tools/import_wordpress.py.  Usage: python3 tools/import_theme.py [saved-page.html]
"""
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "alltheseworlds.us"
SOURCE_URL = f"https://{DOMAIN}/about/"   # any normal page works

# Head <style> blocks we don't want (plugin leftovers)
DROP_STYLE_IDS = {"wp-emoji-styles-inline-css", "woocommerce-inline-inline-css"}
DROP_STYLE_CONTAINS = ("woocommerce-product-gallery",)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "site-migration/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def relink(s):
    return re.sub(r"https?://(?:www\.)?" + re.escape(DOMAIN) + r"(?=[/\"'#?]|$)", "", s)


def main():
    html = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else fetch(SOURCE_URL).decode()
    head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)

    # ---- CSS
    parts = []
    for m in re.finditer(r"<style([^>]*)>(.*?)</style>", head, re.S):
        attrs, css = m.group(1), m.group(2)
        sid = re.search(r"id=['\"]([^'\"]+)", attrs)
        sid = sid.group(1) if sid else "custom"
        if sid in DROP_STYLE_IDS or any(x in css for x in DROP_STYLE_CONTAINS):
            continue
        parts.append(f"/* ---- {sid} ---- */\n{css.strip()}\n")
    css = "\n".join(parts)

    # ---- fonts: download and point @font-face at local copies
    fonts_dir = ROOT / "public" / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for url in sorted(set(re.findall(r"https?://[^)'\"\s]+\.woff2", css))):
        name = url.rsplit("/", 1)[1]
        (fonts_dir / name).write_bytes(fetch(url))
        css = css.replace(url, f"/assets/fonts/{name}")
    css = relink(css)
    (ROOT / "public" / "assets" / "theme.css").write_text(
        "/* Captured from the WordPress site (Twenty Twenty-Five theme + Additional CSS).\n"
        "   Edit freely. Your own site-wide CSS is in the block marked ---- custom ----. */\n\n" + css)

    # ---- header: everything inside .wp-site-blocks up to the page content
    start = html.index('<div class="wp-site-blocks">') + len('<div class="wp-site-blocks">')
    ec = html.index("entry-content", start)
    header = html[start:html.rfind("<div", 0, ec)]
    header = re.sub(r"<p>\s*<!--\s*Stargazer Navbar\s*-->\s*</p>", "", header)

    # ---- footer: the WordPress footer template part
    fstart = html.index('<footer class="wp-block-template-part">')
    footer = html[fstart:html.index("</footer>", fstart) + len("</footer>")]

    pdir = ROOT / "partials"
    pdir.mkdir(exist_ok=True)
    (pdir / "header.html").write_text(relink(header).strip() + "\n")
    (pdir / "footer.html").write_text(relink(footer).strip() + "\n")
    print(f"theme.css: {len(css)//1024} KB, {len(parts)} blocks; fonts: {len(list(fonts_dir.glob('*.woff2')))}; "
          f"header {len(header)} chars; footer {len(footer)} chars")


if __name__ == "__main__":
    main()
