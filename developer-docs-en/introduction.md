# Meet {{nebula.short_name}}

{{nebula.name}} provides a single-host graph database environment for learning how to model relationships, write queries, and evaluate your application.

For example, use the built-in `movie` dataset to find a movie's actors. Actors and movies are **nodes**. The “acts in” relationship between them is an **edge**.

## What you can do

- **Learn graph databases and {{gql.name}}.** {{gql.name}} is a language for working with graph data. Create a graph, insert nodes and edges, and query their relationships.
- **Develop and evaluate applications.** Try data models, queries, and application connections on one host.
- **Prepare automated tests.** Use a development environment for functional testing. Connection methods and client versions must match your product version.

{{nebula.short_name}} is intended for learning, development, and testing. The terms supplied with the software define permitted use.

## Where to start

If this is your first time using the product, go to the [Quick start](get-started/index.md). It takes you through preparing your environment, starting the database, connecting, loading `movie`, and querying it. You do not need to read every concept first.

To learn about the product before starting:

1. Read [Basic concepts](concepts.md) for a movie-and-actor example of nodes, edges, types, labels, and graphs.
2. Check [Capabilities and limits](limitations.md) to decide whether {{nebula.short_name}} fits your task.

## What to know about deployment

{{nebula.short_name}} supports Docker Compose deployment only. Docker runs software in containers. Docker Compose starts the required containers from a configuration file. A single-host deployment can contain more than one container.

The supplied Docker Compose file initializes a service group on first startup: database services that work together. You do not need to create the service group yourself or request or configure a product license file. See [Capabilities and limits](limitations.md) for the fixed deployment limits.
