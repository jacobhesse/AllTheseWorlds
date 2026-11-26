#!/usr/bin/env python3
"""
Copy partials/header.html and partials/footer.html into every page in public/.

Edit the menu or footer in partials/, then run:
    python3 tools/apply_partials.py
Only the text between <!-- site-header --> / <!-- /site-header --> (and the footer
equivalents) is replaced; the rest of each page is untouched.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parts = {name: (ROOT / "partials" / f"{name}.html").read_text().strip()
             for name in ("header", "footer")}
    changed = 0
    for page in sorted((ROOT / "public").rglob("*.html")):
        s = original = page.read_text(encoding="utf-8")
        for name, markup in parts.items():
            s = re.sub(rf"(<!-- site-{name} -->\n).*?(\n<!-- /site-{name} -->)",
                       lambda m: m.group(1) + markup + m.group(2), s, flags=re.S)
        if s != original:
            page.write_text(s, encoding="utf-8")
            changed += 1
    print(f"updated {changed} page(s)")


if __name__ == "__main__":
    main()
