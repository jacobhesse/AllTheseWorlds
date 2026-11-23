#!/usr/bin/env python3
"""
One-time importer: converts the WordPress REST export in ../wp-export/ into a
static site in ../public/. Keeps every URL the same as the WordPress site.

After the import, edit the files in public/ directly — this script is only
needed again if you want to re-pull content from WordPress (it overwrites pages).

Usage:  python3 tools/import_wordpress.py [--no-media]
"""
import html
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "wp-export"
OUT = ROOT / "public"
DOMAIN = "alltheseworlds.us"
SITE_NAME = "All These Worlds"
HOME_ID = 7

# WordPress pages we deliberately don't carry over.
SKIP = {
    "shop", "cart", "checkout", "my-account",          # WooCommerce (1 free product)
    "test-page", "navigation-test-page",               # scratch pages
}

# Old/broken URLs -> where they should go. Used for _redirects AND to fix links in content.
REDIRECTS = {
    "/site-map.html": "/site-map/",
    "/digital-transformation/index.html": "/digital-transformation/",
    "/security/index.html": "/compliance/",
    "/security/": "/compliance/",
    "/cybersecurity/": "/compliance/",
    "/project-management/index.html": "/project-management-3/",
    "/project-management-2/": "/project-management-3/",
    "/writing/index.html": "/blog/",
    "/tools/index.html": "/site-map/",
    "/privacy.html": "/privacy/",
    "/terms.html": "/terms/",
    "/virtual-ciso/resources": "/project-management-formulas/",
    "/marketplace/": "/846-2/",
    "/change-readiness/": "/digital-transformation/",
    "/shop/": "/hipaa-kit/",
    "/cart/": "/hipaa-kit/",
    "/checkout/": "/hipaa-kit/",
    "/my-account/": "/",
    "/product/*": "/hipaa-kit/",
    "/hipaa.html": "/hippa/",
    "/iso-27001.html": "/iso-27001/",
    "/iso-27001-2022/": "/iso-270012022/",
    "/risk-scorecard.html": "/compliance/",
    "/virtual-ciso/": "/vciso/",
    "/favicon.ico": "/wp-content/uploads/2025/11/cropped-0_3-25456-no-background.png",
}

HEAD_TAGS = (
    '<link rel="icon" href="/wp-content/uploads/2025/11/cropped-0_3-25456-no-background.png">\n'
    '<script src="/assets/site.js" defer></script>\n'
)
UPLOAD_RE = re.compile(
    r"(?:https?:)?//(?:www\.)?" + re.escape(DOMAIN) + r"(/wp-content/uploads/[^\s\"'()<>?#]+)"
)


def text(s):
    return html.unescape(s or "").strip()


def is_empty(content):
    return not re.sub(r"<[^>]+>|\s|&nbsp;", "", content)


def rewrite(content, uploads):
    """Make links root-relative, collect uploads, fix known-broken links."""
    for m in UPLOAD_RE.finditer(content):
        uploads.add(m.group(1))
    content = re.sub(r"https?://(?:www\.)?" + re.escape(DOMAIN) + r"(?=[/\"'#?]|$)", "", content)
    content = re.sub(r'(href=["\'])(["\'])', r"\1/\2", content)  # href="" (was the bare domain)
    for old, new in REDIRECTS.items():
        if "*" not in old:
            content = re.sub(r'(href=["\'])' + re.escape(old) + r'(["\'#?])', r"\g<1>" + new + r"\2", content)
    return content


def split_document(content):
    """If content is a full HTML document, return (head_inner, body_attrs, body_inner)."""
    if not re.search(r"<(html|head|body)[\s>]", content, re.I):
        return None
    head = re.search(r"<head[^>]*>(.*?)</head>", content, re.S | re.I)
    body = re.search(r"<body([^>]*)>(.*?)(?:</body>|$)", content, re.S | re.I)
    head_inner = head.group(1) if head else ""
    if body:
        body_attrs, body_inner = body.group(1), body.group(2)
    else:
        body_attrs = ""
        body_inner = re.sub(r"<head[^>]*>.*?</head>", "", content, flags=re.S | re.I)
    # strip stray document tags / </html> leftovers
    body_inner = re.sub(r"</?html[^>]*>|<!doctype[^>]*>|</body>", "", body_inner, flags=re.I)
    # anything WordPress put before the doctype (rare) is kept at the top of body
    pre = re.split(r"<!doctype|<html", content, maxsplit=1, flags=re.I)[0]
    if pre.strip() and not is_empty(pre):
        body_inner = pre + body_inner
    return head_inner, body_attrs, body_inner


def page_html(title, content, description=""):
    doc = split_document(content)
    if doc:
        head_inner, body_attrs, body_inner = doc
        if not re.search(r"<title", head_inner, re.I):
            head_inner = f"<title>{html.escape(title)} – {SITE_NAME}</title>\n" + head_inner
        if not re.search(r'name=["\']viewport', head_inner, re.I):
            head_inner = '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + head_inner
        if not re.search(r"<meta[^>]+charset", head_inner, re.I):
            head_inner = '<meta charset="utf-8">\n' + head_inner
        return (f"<!doctype html>\n<html lang=\"en\">\n<head>\n{head_inner.strip()}\n{HEAD_TAGS}</head>\n"
                # Single wrapper div mirrors WordPress's .wp-site-blocks, so page CSS that
                # styles <body> (flex/grid layouts) behaves exactly as it did on WordPress.
                f"<body{body_attrs}>\n<div class=\"wp-site-blocks\">\n<atw-header></atw-header>\n{body_inner.strip()}\n"
                f"<atw-footer></atw-footer>\n</div>\n</body>\n</html>\n")

    # Fragment: custom-styled fragments get a wide container and no auto title.
    styled = "<style" in content.lower()
    h1 = "" if styled or re.search(r"<h1[\s>]", content, re.I) else f"<h1>{html.escape(title)}</h1>\n"
    desc = f'<meta name="description" content="{html.escape(description)}">\n' if description else ""
    return (f"<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{html.escape(title)} – {SITE_NAME}</title>\n{desc}"
            f"<link rel=\"stylesheet\" href=\"/assets/base.css\">\n{HEAD_TAGS}</head>\n<body>\n"
            f"<atw-header></atw-header>\n<main class=\"atw-content{' wide' if styled else ''}\">\n{h1}{content.strip()}\n</main>\n"
            f"<atw-footer></atw-footer>\n</body>\n</html>\n")


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def excerpt(s, n=200):
    t = text(re.sub(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", " ", s, flags=re.S))
    t = re.sub(r"\s+", " ", t)
    return t[:n].rsplit(" ", 1)[0] + "…" if len(t) > n else t


def main():
    pages = json.loads((EXPORT / "pages.json").read_text())
    posts = json.loads((EXPORT / "posts.json").read_text())
    media = json.loads((EXPORT / "media.json").read_text())
    uploads = set()
    for m in media:
        mm = UPLOAD_RE.search(m.get("source_url", ""))
        if mm:
            uploads.add(mm.group(1))

    written, skipped = [], []

    for p in pages:
        slug, title = p["slug"], text(p["title"]["rendered"]) or p["slug"]
        content = p["content"]["rendered"]
        if slug in SKIP or (is_empty(content) and p["id"] != HOME_ID and slug != "blog"):
            skipped.append(slug)
            continue
        if slug == "blog":
            continue  # generated below
        content = rewrite(content, uploads)
        path = OUT / "index.html" if p["id"] == HOME_ID else OUT / slug / "index.html"
        write(path, page_html(title, content))
        written.append(("/" if p["id"] == HOME_ID else f"/{slug}/", title, p["modified"]))

    # Blog posts + index
    posts.sort(key=lambda x: x["date"], reverse=True)
    items = []
    for p in posts:
        slug, title = p["slug"], text(p["title"]["rendered"])
        date = datetime.fromisoformat(p["date"]).strftime("%B %-d, %Y")
        body = rewrite(p["content"]["rendered"], uploads)
        content = f'<article><h1>{html.escape(title)}</h1>\n<p class="meta">{date}</p>\n{body}</article>'
        write(OUT / slug / "index.html", page_html(title, content, excerpt(body, 155)))
        written.append((f"/{slug}/", title, p["modified"]))
        items.append(f'<li><h2><a href="/{slug}/">{html.escape(title)}</a></h2>'
                     f'<p class="meta">{date}</p><p>{html.escape(excerpt(body))}</p></li>')
    write(OUT / "blog" / "index.html",
          page_html("All These Blogs", f'<h1>All These Blogs</h1>\n<ul class="post-list">\n' + "\n".join(items) + "\n</ul>"))
    written.append(("/blog/", "All These Blogs", posts[0]["modified"] if posts else ""))

    # Contact page (linked from About and several articles, never existed on WordPress)
    contact = OUT / "contact" / "index.html"
    if not contact.exists():  # don't clobber your edits on re-import
        write(contact, page_html("Contact",
              "<h1>Contact</h1>\n<p>The best way to reach me is on "
              '<a href="https://www.linkedin.com/in/jacob-hesse/">LinkedIn</a>.</p>\n'
              "<!-- Add an email link or a Formspree form here if you want one. -->"))
    written.append(("/contact/", "Contact", datetime.now().isoformat()))

    # Site map page (replaces the old broken /site-map.html link)
    links = "\n".join(f'<li><a href="{u}">{html.escape(t)}</a></li>'
                      for u, t, _ in sorted(written, key=lambda w: w[1].lower()))
    write(OUT / "site-map" / "index.html", page_html("Site Map", f"<h1>Site Map</h1>\n<ul>\n{links}\n</ul>"))

    # 404
    write(OUT / "404.html", page_html("Page not found",
          '<h1>Page not found</h1>\n<p>That page doesn’t exist or has moved. '
          'Try the <a href="/">home page</a> or the <a href="/site-map/">site map</a>.</p>'))

    # sitemap.xml / robots.txt / _redirects
    urls = "\n".join(f"  <url><loc>https://{DOMAIN}{u}</loc><lastmod>{m[:10]}</lastmod></url>" for u, _, m in written)
    write(OUT / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
          f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n")
    write(OUT / "_redirects", "# Old WordPress / broken URLs (Cloudflare Pages & Netlify format)\n"
          + "\n".join(f"{a} {b} 301" for a, b in REDIRECTS.items()) + "\n")

    # Media
    if "--no-media" not in sys.argv:
        failed = []
        for u in sorted(uploads):
            dest = OUT / u.lstrip("/")
            if dest.exists():
                continue
            try:
                req = urllib.request.Request(f"https://{DOMAIN}{u}", headers={"User-Agent": "site-migration/1.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(r.read())
            except Exception as e:  # noqa: BLE001
                failed.append(f"{u} ({e})")
        print(f"media: {len(uploads)} referenced, {len(failed)} failed")
        for f in failed:
            print("  FAILED", f)

    print(f"pages written: {len(written)} (+ site-map, 404)")
    print(f"skipped: {', '.join(sorted(skipped))}")


if __name__ == "__main__":
    main()
