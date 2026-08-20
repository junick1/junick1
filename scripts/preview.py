#!/usr/bin/env python3
"""
WRITTEN BY CLAUDE

Renders README.md / README-ko.md exactly the way GitHub will, into preview.html.

Uses GitHub's own /markdown API (so <details>, tables, alerts and emoji all
behave as they do on the profile page), then rewrites the raw.githubusercontent
asset URLs to the local assets/ folder so you see un-pushed changes.

Usage:
    python3 scripts/preview.py              # English
    python3 scripts/preview.py README-ko.md # Korean
    python3 scripts/preview.py --dark       # dark theme

Requires the GitHub CLI (`gh auth status`) for the render call.
"""

import json
import os
import subprocess
import sys

RAW = "https://raw.githubusercontent.com/junick1/junick1/main/assets/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS = ("https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/"
       "github-markdown-{scheme}.css")  # pinned per theme, not OS preference


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dark = "--dark" in sys.argv
    src = args[0] if args else "README.md"

    with open(os.path.join(ROOT, src), encoding="utf-8") as f:
        text = f.read()

    payload = json.dumps({"text": text, "mode": "gfm", "context": "junick1/junick1"})
    body = subprocess.run(
        ["gh", "api", "/markdown", "--input", "-"],
        input=payload, capture_output=True, text=True, check=True,
    ).stdout

    # point the un-pushed assets at the working copy
    body = body.replace(RAW, "assets/")
    if dark:
        # <picture> can't be resolved by prefers-color-scheme in a forced preview,
        # so swap the light <img> fallbacks for their dark twins directly.
        for name in ("hero", "hero-ko", "highlights", "highlights-ko",
                     "profiles", "profiles-ko"):
            body = body.replace(f"assets/{name}-light.svg", f"assets/{name}-dark.svg")

    scheme = "dark" if dark else "light"
    page = f"""<!doctype html>
<meta charset="utf-8">
<meta name="color-scheme" content="{scheme}">
<title>{src} preview</title>
<link rel="stylesheet" href="{CSS.format(scheme=scheme)}">
<style>
  :root {{ color-scheme: {scheme}; }}
  body {{ margin:0; background:{'#0d1117' if dark else '#f6f8fa'}; }}
  .wrap {{ max-width:1012px; margin:0 auto; padding:24px; }}
  .markdown-body {{
      padding:32px; border-radius:6px;
      background:{'#0d1117' if dark else '#ffffff'};
      border:1px solid {'#3d444d' if dark else '#d1d9e0'};
  }}
</style>
<div class="wrap"><article class="markdown-body" data-theme="{scheme}">
{body}
</article></div>
"""
    out = os.path.join(ROOT, "preview.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out}  ({len(page)} bytes, {scheme} theme, from {src})")
    print("open it with:  open preview.html")


if __name__ == "__main__":
    main()
