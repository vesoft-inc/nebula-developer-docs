# Contributing to the documentation

The public documentation is written in Markdown. Normal documentation changes do not require editing Python.

## Add a page

1. Add the Chinese page under `developer-docs-zh/`.
2. Add the English page at the same relative path under `developer-docs-en/`.
3. Link to other documentation with relative `.md` links.
4. Run `make serve` and check both languages.

Keeping the same relative path in both languages allows the language switcher to stay on the corresponding page.

## Add a section with many pages

Create the same directory in both language trees. Put a `.nav.yml` file in each directory to define that section's localized title and page order. For example:

```text
developer-docs-zh/gql-reference/
├── .nav.yml
├── index.md
├── match.md
└── return.md
```

```yaml
nav:
  - 概述: index.md
  - MATCH: match.md
  - RETURN: return.md
  - "*"
```

The final `"*"` automatically includes new pages that have not yet been explicitly ordered. The root `.nav.yml` files also append new top-level directories automatically.

## Preview and validate

```sh
make setup       # first time only
make serve       # both languages, preview version
make serve-zh    # Chinese only
make serve-en    # English only
make serve-all   # all languages and versions
make check       # all configured languages and versions
```

Set another port or version when needed:

```sh
make serve-en PORT=8010 VERSION=v5.3.2
```

The preview automatically rebuilds after Markdown, `.nav.yml`, configuration, or theme changes.

## Release

`make release` generates separate deployable artifacts in `site-production/zh/` and `site-production/en/`. It does not upload or publish them.

Do not edit `.build/`, `site/`, or `site-production/`; they are generated and overwritten.
