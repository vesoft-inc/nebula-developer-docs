"""Build the bilingual, versioned static documentation. No private dependencies."""
import argparse
import functools
import html
import http.server
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

import yaml

ROOT = Path(__file__).resolve().parents[1]
NAV_EN = [
    {"Getting started": [{"Overview": "index.md"}, {"Meet Developer Edition": "introduction.md"}]},
    {"Capabilities and versions": [{"Product boundaries": "limitations.md"}, {"Documentation versions": "versions.md"}]},
    {"Community": [{"Contribute to the docs": "contributing.md"}, {"Use docs with AI": "ai.md"}]},
]

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")

def redirect(path, target):
    safe = html.escape(target, quote=True)
    write(path, f'<!doctype html><html lang="en"><meta charset="utf-8">'
          f'<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url={safe}">'
          f'<title>Developer Edition documentation</title><a href="{safe}">Open documentation</a></html>')

def build(base_url=None, production=False):
    manifest = json.loads((ROOT / "versions.json").read_text())
    versions = manifest["versions"]
    ids = [v["id"] for v in versions]
    if len(ids) != len(set(ids)) or manifest["default"] not in ids:
        raise ValueError("Version IDs must be unique and default must exist.")
    for ident in ids:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", ident) or ident in {"latest", "zh", "en"}:
            raise ValueError("Invalid or reserved version ID: " + ident)
    if base_url and not re.match(r"^https?://", base_url):
        raise ValueError("--base-url must be an HTTP(S) URL.")
    base_url = (base_url or "http://127.0.0.1:8000/").rstrip("/") + "/"
    public_urls = json.loads((ROOT / "site-urls.json").read_text())
    roots = public_urls if production else {lang: urljoin(base_url, lang + "/") for lang in ("zh", "en")}
    output = ROOT / ("site-production" if production else "site")
    staging = ROOT / ".build"
    sitemaps = []
    for version in versions:
        ident = version["id"]
        for lang in ("zh", "en"):
            source = (ROOT / version["source"][lang]).resolve()
            if not source.is_relative_to(ROOT) or not source.is_dir():
                raise ValueError("Source must be an existing directory inside this repository.")
            stage = staging / lang / ident / "docs"
            # Only generated directories are removed, never source content.
            if stage.exists():
                shutil.rmtree(stage)
            shutil.copytree(source, stage)
            prefix = f"{lang}/{ident}/"
            site_url = urljoin(roots[lang], ident + "/")
            entries, full = [], []
            for page in sorted(source.rglob("*.md")):
                rel = page.relative_to(source)
                raw = page.read_text(encoding="utf-8")
                clean = re.sub(r"\A---\n.*?\n---\n", "", raw, count=1, flags=re.S)
                title = next((line[2:] for line in clean.splitlines() if line.startswith("# ")), rel.stem)
                route = rel.with_suffix("").as_posix() + "/"
                if rel.name == "index.md":
                    route = "" if rel.parent == Path(".") else rel.parent.as_posix() + "/"
                url = urljoin(site_url, route)
                write(stage / "markdown" / rel, clean)
                entries.append(f"- [{title}]({url}): [Markdown]({urljoin(site_url, 'markdown/' + rel.as_posix())})")
                full.append(f"# {title}\n\nVersion: {ident}; Language: {lang}\nSource: {url}\n\n{clean}")
            heading = f"# NebulaGraph Developer Edition — {ident} ({lang})\n\n"
            note = "Documentation preview. Deployment instructions are not included.\n\n" if ident == "preview" else ""
            write(stage / "llms.txt", heading + note + "\n".join(entries) + "\n")
            write(stage / "llms-full.txt", heading + note + "\n\n---\n\n".join(full))
            config_path = ROOT / f"mkdocs-{lang}.yml"
            if not config_path.exists():
                config_path = ROOT / "mkdocs.yml"
            config = yaml.safe_load(config_path.read_text())
            config["docs_dir"] = str(stage)
            config["site_dir"] = str(output / prefix)
            config["site_url"] = site_url
            config["theme"]["custom_dir"] = str(ROOT / "theme")
            config["theme"]["language"] = lang
            config["site_name"] = "悦数开发版文档" if lang == "zh" else "NebulaGraph Developer Edition"
            config["site_description"] = f"NebulaGraph Developer Edition documentation. Version: {ident}. Language: {lang}."
            if lang == "en":
                config["nav"] = NAV_EN
            config["exclude_docs"] = "markdown/"
            config["edit_uri"] = f"edit/{version['ref']}/{version['source'][lang]}/"
            # Relative links work on localhost, domains and hosted subdirectories.
            other = "en" if lang == "zh" else "zh"
            config["extra"] = {
                "preview": not production,
                "language_url": f"../../{other}/{ident}/",
                "language_absolute": urljoin(roots[other], ident + "/") if production else None,
                "official_url": "https://yueshu.com.cn/" if lang == "zh" else "https://nebula-graph.io/",
                "switches": [{"title": v["title"][lang], "url": f"../{v['id']}/", "current": v["id"] == ident} for v in versions],
            }
            # The template prefixes relative links using base_url for deep pages.
            cfg = staging / lang / ident / "mkdocs.yml"
            write(cfg, yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
            subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-f", str(cfg)], check=True, cwd=ROOT)
            # Serve raw Markdown as a separate, non-rendered representation.
            shutil.copytree(stage / "markdown", output / prefix / "markdown", dirs_exist_ok=True)
            sitemaps.append(urljoin(site_url, "sitemap.xml"))
    default = manifest["default"]
    if not production:
        redirect(output / "index.html", f"zh/{default}/")
    for lang in ("zh", "en"):
        redirect(output / lang / "index.html", f"{default}/")
        redirect(output / lang / "latest" / "index.html", f"../{default}/")
    write(output / "versions.json", json.dumps({"default": default, "versions": [{"id":v["id"],"title":v["title"]} for v in versions]}, ensure_ascii=False, indent=2))
    write(output / "llms.txt", "# NebulaGraph Developer Edition documentation\n\n" + "\n".join(
        f"- [{lang} {v['id']}]({urljoin(base_url, lang + '/' + v['id'] + '/llms.txt')})"
        for v in versions for lang in ("zh", "en")) + "\n")
    write(output / "robots.txt", "User-agent: *\n" + ("Allow: /\n" if production else "Disallow: /\n") +
          "".join(f"Sitemap: {url}\n" for url in sitemaps))
    if production:
        # Each language directory is a separate deployment artifact, mounted at /docs-dev/.
        for lang in ("zh", "en"):
            write(output / lang / "versions.json", (output / "versions.json").read_text())
            write(output / lang / "llms.txt", "# NebulaGraph Developer Edition documentation\n\n" + "\n".join(
                f"- [{lang} {v['id']}]({urljoin(roots[lang], v['id'] + '/llms.txt')})" for v in versions) + "\n")
        # Packaging root is not a website root; robots must be managed at each official domain root.
        for name in ("versions.json", "llms.txt", "robots.txt"):
            (output / name).unlink()
    print(f"Built {len(versions)} version(s), 2 languages: {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "serve"], nargs="?", default="build")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--base-url", help="Public site root, including any subdirectory.")
    parser.add_argument("--production", action="store_true", help="Build separate language sites using site-urls.json; allow indexing.")
    args = parser.parse_args()
    if args.production and (args.base_url or args.command == "serve"):
        parser.error("Use build --production with site-urls.json; use serve without --production for local preview.")
    build(args.base_url or f"http://127.0.0.1:{args.port}/", args.production)
    if args.command == "serve":
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "site"))
        with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            print(f"Preview: http://127.0.0.1:{args.port}/", flush=True)
            server.serve_forever()
