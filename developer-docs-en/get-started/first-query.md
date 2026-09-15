# Connect and run your first query

Load the `movie` dataset built into `ngql`, query a movie, and find its actors. You do not need to learn graph creation or insert syntax first.

## Before you start

- Start the supplied containers by following the [deployment tutorial](deploy.md).
- Have the password you set as `ROOT_PASSWORD` in `.env`.
- Use a Schema where `movie` has not been loaded. If you already loaded it, follow the instructions below to continue querying.

!!! note "Example validation"

    This is a preview tutorial for the supplied `nightly` environment. Validation of the full workflow is pending. The tables below describe the results expected from the example data. If your results differ, follow the troubleshooting steps at the end of this page.

## 1. Connect to the database {#connect}

In **the development machine's terminal**, open the practice directory containing `compose.yaml` and run:

```bash
docker compose exec ngql ngql --host graph-cluster --port 9669 --user root
```

The first `ngql` is the container service name. The second is the client command inside that container. `graph-cluster` is an address on the supplied container network, and `9669` is the query port. Do not replace it with the development machine's IP address. See [Docker Compose exec](https://docs.docker.com/reference/cli/docker/compose/exec/) for running a command in a container.

At the `Password` prompt, enter the password you set in `.env` and press Enter. Input is not displayed. Do not include the single quotes surrounding the password in `.env`.

Once connected, you are in the `ngql` interactive console. **Run the following {{gql.name}} statements there, not in the development machine's ordinary terminal.** Run one code block at a time and resolve any error before continuing.

First, run a query that does not read graph data:

```sql
RETURN 1 AS result
```

It should return a column named `result` with the value `1`. This checks sign-in and basic query execution. The loading and query steps below also check access to graph data.

## 2. Choose where to load the data

In `ngql`, select the default Schema. A Schema is a namespace for graphs and graph types, not a folder on the development machine.

```sql
SESSION SET SCHEMA /default_schema
```

List existing graph types and graphs separately:

```sql
SHOW GRAPH TYPES
```

```sql
SHOW GRAPHS
```

Before the first load, check that neither the graph type `movie_type` nor the graph `movie` exists here.

!!! note "Already loaded movie?"

    If the previous load succeeded, [select the graph and query it](#select-graph) without reloading. If objects remain from a failed load or belong to another task, read [Load another copy if needed](dataset.md#reload) first.

## 3. Load the movie dataset {#load}

In `ngql`, run:

```text
:play movie
```

The command uses data built into the client. It creates `movie_type` and `movie` and inserts nodes and edges. You do not need to create the graph manually or download a data file.

When loading starts, the client displays:

```text
Playing dataset: movie...
```

Wait for it to finish. On success, it displays:

```text
Play dataset: movie done.
```

Resolve any error before continuing. `Playing dataset` alone does not mean loading has finished. Do not keep running `:play movie` again. See [What loading does](dataset.md#load-behavior) for existing-name conflicts and interrupted loads.

After a successful load, run:

```sql
SHOW GRAPHS
```

The result should include graph `movie`, graph type `movie_type`, and Schema `/default_schema`. A listed graph is only one check. Next, verify that you can query its data.

## 4. Select the graph and find a movie {#select-graph}

After loading, run this in the same `ngql` window:

```sql
SESSION SET GRAPH movie
```

!!! note "Do not skip selecting the graph"

    `:play movie` does not select a graph for this interactive session. Select `movie` explicitly so subsequent queries use it.

Find the movie with ID `3`:

```sql
MATCH (m@Movie {id: 3}) RETURN m.id AS movie_id, m.name AS movie
```

- `MATCH` finds nodes matching the pattern.
- `@Movie` specifies the movie type.
- `{id: 3}` specifies the movie ID.
- `RETURN` selects properties to display; `AS` names the result columns.

The supplied data should return:

| movie_id | movie |
| --- | --- |
| 3 | Shadows in Paradise |

Using an ID avoids ambiguity between movies with the same name. `movie` is the graph name; `Movie` is a node type. Keep the capitalization.

## 5. Find the movie's actors

Copy the full block into `ngql`, including the opening and closing `'''`. These markers tell the client to submit multiple lines as one statement. They are not part of {{gql.name}} syntax.

```sql
'''
MATCH (a@Actor)-[:Act]->(m@Movie {id: 3})
RETURN a.id AS actor_id, a.name AS actor, m.name AS movie
ORDER BY actor_id
'''
```

`(a@Actor)-[:Act]->(m@Movie)` matches an actor connected to a movie through an acting relationship. The arrow points from actor to movie. `ORDER BY actor_id` sorts by actor ID so you can compare results.

The supplied data should return:

| actor_id | actor | movie |
| --- | --- | --- |
| 4826 | Matti Pellonpää | Shadows in Paradise |
| 4828 | Sakari Kuosmanen | Shadows in Paradise |
| 5999 | Kati Outinen | Shadows in Paradise |

You have now loaded data, queried a node, and queried relationships. Continue using the same `movie` graph in later chapters.

## Exit and resume your work {#resume}

In `ngql`, run:

```text
:exit
```

This exits the client without stopping the database or deleting data. To pause the database, see [Pause and restart your exercise](deploy.md#stop-start).

Next time, follow the [connection step](#connect), then run:

```sql
SESSION SET SCHEMA /default_schema
```

```sql
SESSION SET GRAPH movie
```

Continue with the queries in step 4 or 5. **Do not run `:play movie` again.** If you loaded into another Schema, use that path in the first statement.

## Repeat queries and preserve the example data {#reset}

The queries on this page do not modify data, so you can repeat them. If loading was interrupted or data changed, follow [Load another copy if needed](dataset.md#reload) to practice in a separate Schema without deleting data you need to keep.

Later API and SDK examples use this graph too. However, `:play movie` runs only in `ngql`; do not send it as a {{gql.name}} query through an API or SDK.

## Troubleshooting {#troubleshooting}

| Symptom | What to do |
| --- | --- |
| The terminal reports that `ngql` is not running | Check containers and initialization logs in the [deployment tutorial](deploy.md#troubleshooting) |
| Connection fails or is refused | Use the complete `docker compose exec` command on this page, then check `graphd` status and logs |
| Password is rejected | Enter the actual `.env` password without surrounding quotes. With reused data, use the existing database password |
| `:play movie` reports that the dataset is missing | Check that you use the supplied `ngql` client, not an ordinary terminal or another query tool |
| Loading reports that an object already exists | Do not reload. If the previous load succeeded, select the graph. If it failed, see [Load another copy if needed](dataset.md#reload) |
| No graph is selected or `movie` cannot be found | Select the Schema used for loading and the `movie` graph. Use `SHOW GRAPHS` to check its location |
| The movie query works but the actor query is empty | Check `Act` direction and capitalization, loading errors, and whether data was modified. A graph's existence alone does not prove a complete load |
| Multiline input keeps waiting | Check that both `'''` markers and all lines between them were copied |
| Results differ from the example | Check the `ngql` version and whether data was modified, then verify movie ID `3` |

If the problem persists, follow the [contribution guide](../contributing.md) to report a documentation issue. Include image versions, the failing step, statements, and sanitized errors. Do not include passwords or a complete `.env` file.
