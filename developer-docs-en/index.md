---
hide:
  - toc
---
<div class="de-breadcrumb">{{nebula.name}}</div>
<div class="de-intro" markdown>
# {{nebula.name}}

Learn graph databases with the built-in `movie` dataset: find a movie, then find its actors. Start a single-host development environment with Docker Compose, without requesting a product license file.
</div>

## First time here? Start with a query {#quick-start}

[Follow the quick start →](get-started/index.md){ .md-button .md-button--primary }

Prepare your environment, connect, load the data, and run a query. You do not need to know {{gql.name}} or create a service group yourself.

!!! note "Documentation preview"

    The tutorial uses `nightly` images and awaits end-to-end validation. Check the [deployment prerequisites](get-started/deploy.md) first. Version menu entries do not establish product release status or compatibility.

## Find what you need

<div class="de-grid" markdown>
<div class="de-card" markdown>
<div class="de-number">01 / INTRODUCTION</div>
### Meet {{nebula.short_name}}
Learn what {{nebula.short_name}} is for, its limits, and what nodes, edges, and graphs mean.
<div class="de-card-bottom" markdown>
[Read the introduction →](introduction.md)
</div>
</div>
<div class="de-card" markdown>
<div class="de-number">02 / DEPLOY</div>
### Start your development environment
Download the Docker Compose file, set your own password, and start the supplied containers.
<div class="de-card-bottom" markdown>
[Deploy the database →](get-started/deploy.md)
</div>
</div>
<div class="de-card" markdown>
<div class="de-number">03 / FIRST QUERY</div>
### Run your first query
Load the built-in `movie` dataset and query movies and their actors.
<div class="de-card-bottom" markdown>
[Connect and query →](get-started/first-query.md)
</div>
</div>
</div>

## Check the limits before you start {#edition-compare}

{{nebula.short_name}} provides a fixed single-host configuration for learning, development, and testing. Read [Capabilities and limits](limitations.md) to check that it fits your needs.

## Get help or improve the docs {#contribute-section}

For startup failures, see [deployment troubleshooting](get-started/deploy.md#troubleshooting). For query failures, see [query troubleshooting](get-started/first-query.md#troubleshooting).

Found a documentation error or missing explanation? Follow the [contribution guide](contributing.md) to send feedback. You can also [read the docs with AI](ai.md).
