"""Check generated navigation, language/version links, assets and AI endpoints."""

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT = Path(__file__).resolve().parents[1]
LANGUAGES = ("zh", "en")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        key = "value" if tag == "option" else "href" if tag in {"a", "link"} else "src"
        if attrs.get(key):
            self.targets.append(attrs[key])


def selected_versions(requested):
    versions = json.loads((PROJECT / "versions.json").read_text(encoding="utf-8"))["versions"]
    if requested == "all":
        return versions
    selected = [version for version in versions if version["id"] == requested]
    assert selected, f"Unknown version: {requested}"
    return selected


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("--production", action="store_true")
    arg_parser.add_argument("--lang", choices=["all", *LANGUAGES], default="all")
    arg_parser.add_argument("--version", default="all")
    args = arg_parser.parse_args()

    root = PROJECT / ("site-production" if args.production else "site")
    public_urls = json.loads((PROJECT / "site-urls.json").read_text(encoding="utf-8"))
    languages = LANGUAGES if args.lang == "all" else (args.lang,)
    versions = selected_versions(args.version)
    hardcoded_names = {
        "zh": ("悦数图数据库开发版", "悦数开发版", "开发版", "GQL"),
        "en": ("NebulaGraph Database Developer Edition", "Developer Edition", "GQL"),
    }
    for version in versions:
        for lang in languages:
            source = PROJECT / version["source"][lang]
            for page in source.rglob("*.md"):
                content = page.read_text(encoding="utf-8")
                for name in hardcoded_names[lang]:
                    assert name not in content, f"Hard-coded documentation name {name!r} in {page}"

    page_roots = [root / lang / version["id"] for lang in languages for version in versions]
    pages = [page for page_root in page_roots for page in page_root.rglob("*.html")]
    assert pages, "Build the selected site first"

    errors = []
    for page in pages:
        link_parser = Links()
        link_parser.feed(page.read_text(encoding="utf-8"))
        for link in link_parser.targets:
            parts = urlsplit(link)
            if not parts.path:
                continue
            if parts.scheme or parts.netloc:
                matches = [(lang, url) for lang, url in public_urls.items() if link.startswith(url)]
                if not args.production or not matches:
                    continue
                lang, public_root = matches[0]
                target = (root / lang / unquote(urlsplit(link[len(public_root) :]).path)).resolve()
            elif parts.path.startswith("/") and args.production:
                lang = page.relative_to(root).parts[0]
                mount = urlsplit(public_urls[lang]).path
                if not parts.path.startswith(mount):
                    errors.append(f"{page}: link outside documentation mount: {link}")
                    continue
                target = (root / lang / unquote(parts.path[len(mount) :])).resolve()
            else:
                target = (
                    root / unquote(parts.path.lstrip("/"))
                    if parts.path.startswith("/")
                    else page.parent / unquote(parts.path)
                ).resolve()
            if not target.is_relative_to(root.resolve()):
                errors.append(f"{page}: link escapes site: {link}")
            elif not target.is_file() and not (target / "index.html").is_file():
                errors.append(f"{page.relative_to(root)}: missing {link}")
    assert not errors, "\n".join(errors)

    for lang in languages:
        for version in versions:
            folder = root / lang / version["id"]
            raw_home = folder / "markdown" / "index.md"
            assert raw_home.is_file()
            assert not raw_home.read_text(encoding="utf-8").startswith("---")
            for artifact in (*folder.rglob("*.html"), *folder.rglob("*.md"), folder / "llms-full.txt"):
                content = artifact.read_text(encoding="utf-8")
                assert "{{gql." not in content, f"Unresolved gql variable in {artifact}"
                assert "{{nebula." not in content, f"Unresolved nebula variable in {artifact}"
            if args.production:
                expected = public_urls[lang] + version["id"] + "/"
                assert f'href="{expected}"' in (folder / "index.html").read_text(encoding="utf-8")
                assert expected in (folder / "sitemap.xml").read_text(encoding="utf-8")
                for name in ("llms.txt", "llms-full.txt"):
                    content = (folder / name).read_text(encoding="utf-8")
                    assert expected in content and "127.0.0.1" not in content

    label = ", ".join(f"{lang}/{version['id']}" for lang in languages for version in versions)
    print(f"Checked {len(pages)} pages: {label}.")


if __name__ == "__main__":
    main()
