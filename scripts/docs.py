"""Build and preview the bilingual, versioned public documentation site."""

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
from threading import Lock, Timer
from urllib.parse import urljoin

import yaml


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("zh", "en")
VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_]\w*(?:\.\w+)*)\s*\}\}")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def redirect(path, target, product_name, lang="en"):
    safe = html.escape(target, quote=True)
    title = f"{product_name}文档" if lang == "zh" else f"{product_name} documentation"
    link_text = "打开文档" if lang == "zh" else "Open documentation"
    write(
        path,
        f'<!doctype html><html lang="{lang}"><meta charset="utf-8">'
        f'<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url={safe}">'
        f'<title>{html.escape(title)}</title><a href="{safe}">{link_text}</a></html>',
    )


def read_manifest():
    manifest = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    versions = manifest["versions"]
    ids = [version["id"] for version in versions]
    if len(ids) != len(set(ids)) or manifest["default"] not in ids:
        raise ValueError("Version IDs must be unique and default must exist.")
    for ident in ids:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", ident) or ident in {"latest", "zh", "en"}:
            raise ValueError("Invalid or reserved version ID: " + ident)
    sources = {}
    for version in versions:
        pair = tuple(version["source"][lang] for lang in LANGUAGES)
        if pair in sources:
            print(
                f"WARNING: {sources[pair]} and {version['id']} share the same source directories; "
                "they are not independent documentation snapshots.",
                file=sys.stderr,
            )
        else:
            sources[pair] = version["id"]
    return manifest


def merge_dicts(base, override):
    """Return a recursive merge without changing either input mapping."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def flatten_variables(values, prefix=""):
    variables = {}
    for key, value in values.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            variables.update(flatten_variables(value, name))
        elif isinstance(value, (str, int, float, bool)):
            variables[name] = str(value)
    return variables


def document_variables(lang):
    base = yaml.safe_load((ROOT / "mkdocs-base.yml").read_text(encoding="utf-8")) or {}
    localized = yaml.safe_load((ROOT / f"mkdocs-{lang}.yml").read_text(encoding="utf-8")) or {}
    extra = merge_dicts(base.get("extra", {}), localized.get("extra", {}))
    return flatten_variables(extra)


def render_document_variables(value, variables):
    """Resolve documentation-name variables in Markdown exports and AI text files."""
    return VARIABLE_PATTERN.sub(lambda match: variables.get(match.group(1), match.group(0)), value)


def select_versions(manifest, requested):
    if requested == "all":
        return manifest["versions"]
    selected = [version for version in manifest["versions"] if version["id"] == requested]
    if not selected:
        available = ", ".join(version["id"] for version in manifest["versions"])
        raise ValueError(f"Unknown version {requested!r}. Available versions: {available}")
    return selected


def sitemap_index(urls):
    rows = "".join(f"<sitemap><loc>{html.escape(url)}</loc></sitemap>" for url in urls)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + (
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + rows + "</sitemapindex>\n"
    )


def build(base_url=None, production=False, languages=LANGUAGES, requested_version="all"):
    manifest = read_manifest()
    all_versions = manifest["versions"]
    versions = select_versions(manifest, requested_version)
    selected_ids = [version["id"] for version in versions]

    if base_url and not re.match(r"^https?://", base_url):
        raise ValueError("--base-url must be an HTTP(S) URL.")
    base_url = (base_url or "http://127.0.0.1:8000/").rstrip("/") + "/"

    public_urls = json.loads((ROOT / "site-urls.json").read_text(encoding="utf-8"))
    for lang in LANGUAGES:
        if lang not in public_urls or not re.match(r"^https://", public_urls[lang]):
            raise ValueError(f"site-urls.json must define an HTTPS URL for {lang}.")
        public_urls[lang] = public_urls[lang].rstrip("/") + "/"

    roots = public_urls if production else {lang: urljoin(base_url, lang + "/") for lang in LANGUAGES}
    output = ROOT / ("site-production" if production else "site")
    # Keep the live preview from overwriting public URLs in production staging.
    staging = ROOT / ".build" / ("production" if production else "preview")
    full_build = set(languages) == set(LANGUAGES) and len(versions) == len(all_versions)
    if full_build and output.exists():
        shutil.rmtree(output)

    sitemaps = {lang: [] for lang in languages}
    built_sources = []
    for version in versions:
        ident = version["id"]
        for lang in languages:
            variables = document_variables(lang)
            product_name = variables["nebula.name"]
            source = (ROOT / version["source"][lang]).resolve()
            if not source.is_relative_to(ROOT) or not source.is_dir():
                raise ValueError("Source must be an existing directory inside this repository.")
            built_sources.append(source)
            stage = staging / lang / ident / "docs"
            if stage.exists():
                shutil.rmtree(stage)
            shutil.copytree(source, stage)

            prefix = f"{lang}/{ident}/"
            site_url = urljoin(roots[lang], ident + "/")
            entries, full = [], []
            for page in sorted(source.rglob("*.md")):
                rel = page.relative_to(source)
                raw = page.read_text(encoding="utf-8")
                rendered = render_document_variables(raw, variables)
                write(stage / rel, rendered)
                public_markdown = re.sub(r"\A---\n.*?\n---\n", "", rendered, count=1, flags=re.S)
                title = next(
                    (line[2:] for line in public_markdown.splitlines() if line.startswith("# ")),
                    rel.stem,
                )
                route = rel.with_suffix("").as_posix() + "/"
                if rel.name == "index.md":
                    route = "" if rel.parent == Path(".") else rel.parent.as_posix() + "/"
                url = urljoin(site_url, route)
                write(stage / "markdown" / rel, public_markdown)
                entries.append(
                    f"- [{title}]({url}): [Markdown]({urljoin(site_url, 'markdown/' + rel.as_posix())})"
                )
                full.append(
                    f"# {title}\n\nVersion: {ident}; Language: {lang}\nSource: {url}\n\n{public_markdown}"
                )

            heading = f"# {product_name} — {ident} ({lang})\n\n"
            note = "Documentation preview. Nightly deployment and query examples await end-to-end validation.\n\n" if ident == "preview" else ""
            write(stage / "llms.txt", heading + note + "\n".join(entries) + "\n")
            write(stage / "llms-full.txt", heading + note + "\n\n---\n\n".join(full))

            config_path = ROOT / f"mkdocs-{lang}.yml"
            if not config_path.is_file():
                raise ValueError(f"Missing language configuration: {config_path.name}")
            other = "en" if lang == "zh" else "zh"
            other_available = other in languages
            config = {
                "INHERIT": str(config_path),
                "docs_dir": str(stage),
                "site_dir": str(output / prefix),
                "site_url": site_url,
                "site_description": f"{product_name}. Version: {ident}. Language: {lang}.",
                "exclude_docs": "markdown/",
                "edit_uri": f"edit/{version['ref']}/{version['source'][lang]}/",
                "theme": {"custom_dir": str(ROOT / "theme"), "language": lang},
                "extra": {
                    "gql": {"name": variables["gql.name"]},
                    "nebula": {
                        "name": product_name,
                        "short_name": variables["nebula.short_name"],
                    },
                    "preview": not production,
                    "language_url": f"../../{other}/{ident}/" if other_available else None,
                    "language_absolute": urljoin(roots[other], ident + "/")
                    if production and other_available
                    else None,
                    "official_url": "https://yueshu.com.cn/" if lang == "zh" else "https://nebula-graph.io/",
                    "switches": [
                        {
                            "title": item["title"][lang],
                            "url": f"../{item['id']}/",
                            "current": item["id"] == ident,
                        }
                        for item in versions
                    ],
                },
            }
            cfg = staging / lang / ident / "mkdocs.yml"
            write(cfg, yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
            subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "-f", str(cfg)],
                check=True,
                cwd=ROOT,
            )
            shutil.copytree(stage / "markdown", output / prefix / "markdown", dirs_exist_ok=True)
            sitemaps[lang].append(urljoin(site_url, "sitemap.xml"))

    default = manifest["default"]
    landing_version = default if default in selected_ids else selected_ids[0]
    selected_manifest = {
        "default": landing_version,
        "versions": [{"id": version["id"], "title": version["title"]} for version in versions],
    }
    manifest_json = json.dumps(selected_manifest, ensure_ascii=False, indent=2) + "\n"

    for lang in languages:
        product_name = document_variables(lang)["nebula.name"]
        redirect(output / lang / "index.html", f"{landing_version}/", product_name, lang)
        redirect(output / lang / "latest" / "index.html", f"../{landing_version}/", product_name, lang)
        if production:
            write(output / lang / "versions.json", manifest_json)
            write(
                output / lang / "llms.txt",
                f"# {product_name}\n\n"
                + "\n".join(
                    f"- [{lang} {version['id']}]({urljoin(roots[lang], version['id'] + '/llms.txt')})"
                    for version in versions
                )
                + "\n",
            )
            write(output / lang / "sitemap.xml", sitemap_index(sitemaps[lang]))

    if not production:
        landing_lang = "zh" if "zh" in languages else languages[0]
        product_name = document_variables(landing_lang)["nebula.name"]
        redirect(output / "index.html", f"{landing_lang}/{landing_version}/", product_name, landing_lang)
        write(output / "versions.json", manifest_json)
        write(
            output / "llms.txt",
            f"# {document_variables('en')['nebula.name']} documentation\n\n"
            + "\n".join(
                f"- [{lang} {version['id']}]({urljoin(roots[lang], version['id'] + '/llms.txt')})"
                for version in versions
                for lang in languages
            )
            + "\n",
        )
        write(
            output / "robots.txt",
            "User-agent: *\nDisallow: /\n" + "".join(
                f"Sitemap: {url}\n" for lang in languages for url in sitemaps[lang]
            ),
        )

    print(
        f"Built {len(versions)} version(s), {len(languages)} language(s): {output}",
        flush=True,
    )
    return sorted(set(built_sources))


def serve(port, languages, requested_version):
    base_url = f"http://127.0.0.1:{port}/"
    sources = build(base_url, False, languages, requested_version)
    manifest = read_manifest()
    preview_versions = select_versions(manifest, requested_version)
    preview_default = (
        manifest["default"]
        if any(version["id"] == manifest["default"] for version in preview_versions)
        else preview_versions[0]["id"]
    )
    lock = Lock()
    timer = None

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:
        raise RuntimeError("Install requirements-preview.txt before serving the site.") from exc

    watched_files = {
        ROOT / "versions.json",
        ROOT / "site-urls.json",
        ROOT / "mkdocs-base.yml",
        *(ROOT / f"mkdocs-{lang}.yml" for lang in LANGUAGES),
    }
    watched_dirs = {ROOT / "theme", *sources}

    def rebuild():
        nonlocal sources
        with lock:
            try:
                print("Documentation changed; rebuilding…", flush=True)
                new_sources = build(base_url, False, languages, requested_version)
                for source in new_sources:
                    if source not in watched_dirs:
                        observer.schedule(handler, str(source), recursive=True)
                        watched_dirs.add(source)
                sources = new_sources
                print("Preview updated.", flush=True)
            except Exception as exc:  # Keep the preview server alive so the writer can fix the source.
                print(f"Build failed: {exc}", file=sys.stderr, flush=True)

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            nonlocal timer
            if event.is_directory or event.event_type not in {"created", "modified", "deleted", "moved"}:
                return
            path = Path(event.src_path).resolve()
            if path not in watched_files and not any(path.is_relative_to(directory) for directory in tuple(watched_dirs)):
                return
            if timer:
                timer.cancel()
            timer = Timer(0.3, rebuild)
            timer.daemon = True
            timer.start()

    observer = Observer()
    handler = Handler()
    observer.schedule(handler, str(ROOT), recursive=False)
    for directory in watched_dirs:
        observer.schedule(handler, str(directory), recursive=True)
    observer.start()

    handler_factory = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "site"))
    print("Preview URLs:", flush=True)
    for lang in languages:
        print(f"  {urljoin(base_url, lang + '/' + preview_default + '/')}", flush=True)
    print("Markdown and navigation changes rebuild automatically. Press Ctrl+C to stop.", flush=True)
    try:
        with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler_factory) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nPreview stopped.", flush=True)
    finally:
        if timer:
            timer.cancel()
        observer.stop()
        observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "serve"], nargs="?", default="build")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--base-url", help="Local preview root; production URLs come from site-urls.json.")
    parser.add_argument("--lang", choices=["all", *LANGUAGES], default="all")
    parser.add_argument("--version", default="all", help="Version ID from versions.json, or all.")
    parser.add_argument("--production", action="store_true", help="Build both official language sites.")
    args = parser.parse_args()

    languages = LANGUAGES if args.lang == "all" else (args.lang,)
    if args.production and (args.base_url or args.command == "serve" or args.lang != "all" or args.version != "all"):
        parser.error("Production is always a full build. Use: docs.py build --production")
    if args.command == "serve":
        serve(args.port, languages, args.version)
    else:
        build(args.base_url or f"http://127.0.0.1:{args.port}/", args.production, languages, args.version)
