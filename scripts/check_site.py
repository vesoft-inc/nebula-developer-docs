"""Check generated navigation, language/version links, assets and AI endpoints."""
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

PROJECT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--production", action="store_true")
args = parser.parse_args()
ROOT = PROJECT / ("site-production" if args.production else "site")
public_urls = json.loads((PROJECT / "site-urls.json").read_text())

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        key = "value" if tag == "option" else "href" if tag in {"a", "link"} else "src"
        if attrs.get(key):
            self.targets.append(attrs[key])

errors = []
pages = list(ROOT.rglob("*.html"))
assert pages, "Build the site first"
for page in pages:
    parser = Links()
    parser.feed(page.read_text())
    for link in parser.targets:
        parts = urlsplit(link)
        if not parts.path:
            continue
        if parts.scheme or parts.netloc:
            matches = [(lang, root) for lang, root in public_urls.items() if link.startswith(root)]
            if not args.production or not matches:
                continue
            lang, root = matches[0]
            target = (ROOT / lang / unquote(urlsplit(link[len(root):]).path)).resolve()
        elif parts.path.startswith("/") and args.production:
            lang = page.relative_to(ROOT).parts[0]
            mount = urlsplit(public_urls[lang]).path
            if not parts.path.startswith(mount):
                errors.append(f"{page}: link outside documentation mount: {link}")
                continue
            target = (ROOT / lang / unquote(parts.path[len(mount):])).resolve()
        else:
            target = (ROOT / unquote(parts.path.lstrip("/")) if parts.path.startswith("/")
                      else page.parent / unquote(parts.path)).resolve()
        if not target.is_relative_to(ROOT.resolve()):
            errors.append(f"{page}: link escapes site: {link}")
        elif not target.is_file() and not (target / "index.html").is_file():
            errors.append(f"{page.relative_to(ROOT)}: missing {link}")
assert not errors, "\n".join(errors)
for lang in ("zh", "en"):
    versions = json.loads((PROJECT / "versions.json").read_text())["versions"]
    for version in versions:
        folder = ROOT / lang / version["id"]
        assert (folder / "markdown" / "index.md").is_file()
        assert not (folder / "markdown" / "index.md").read_text().startswith("---")
        if args.production:
            expected = public_urls[lang] + version["id"] + "/"
            assert f'href="{expected}"' in (folder / "index.html").read_text()
            assert expected in (folder / "sitemap.xml").read_text()
            for name in ("llms.txt", "llms-full.txt"):
                content = (folder / name).read_text()
                assert expected in content and "127.0.0.1" not in content
print(f"Checked links in {len(pages)} pages, including language/version navigation and raw Markdown.")
