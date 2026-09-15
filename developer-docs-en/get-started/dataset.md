# Example dataset: movie

These docs use the `movie` dataset built into `ngql`. It contains movies, actors, directors, users, and genres, so you can practice queries such as finding a movie's actors or the movies a user has watched.

For your first load, follow [Connect and run your first query](first-query.md). You do not need a separate CSV download or manual steps to create the graph type, create the graph, or insert individual records.

## How the data is connected

```text
Actor ─────Act (acts in)──────────→ Movie
Director ──Direct (directs)───────→ Movie
User ──────Watch (watches)────────→ Movie
Movie ─────WithGenre (has genre)──→ Genre
```

Arrows show edge direction. For example, `Act` points from an actor to a movie. Match this direction when finding a movie's actors.

### Node types

| Type | Represents | Label | Properties | Primary key |
| --- | --- | --- | --- | --- |
| `User` | User | `Person` | `id` | `id` |
| `Actor` | Actor | `Person` | `id`, `name`, `birthDate` | `id` |
| `Director` | Director | `Person` | `id`, `name`, `birthDate` | `id` |
| `Movie` | Movie | `Movie` | `id`, `name` | `id` |
| `Genre` | Movie genre | `Genre` | `id`, `name` | `id` |

`id` is an integer that distinguishes nodes of the same type. `name` is a string, and `birthDate` is a date. The user type has only `id`; do not assume every node labeled `Person` has a name or birth date.

### Edge types

| Type | Relationship | Direction | Label | Properties |
| --- | --- | --- | --- | --- |
| `Watch` | User watches a movie | `User` → `Movie` | `Watch` | `rate`: floating-point rating |
| `Act` | Actor acts in a movie | `Actor` → `Movie` | `Act` | None |
| `Direct` | Director directs a movie | `Director` → `Movie` | `Direct` | None |
| `WithGenre` | Movie belongs to a genre | `Movie` → `Genre` | `WithGenre` | None |

!!! note "Types and labels are different"

    `Actor`, `Director`, and `User` are different types that share the `Person` label. `@Actor` specifies the actor type. `:Person` matches by label, including directors and users. See [Basic concepts](../concepts.md).

## What loading does {#load-behavior}

When you run `:play movie` in `ngql`, the client does the following in **your selected Schema**:

1. Creates the graph type `movie_type`.
2. Creates the graph `movie` using that type.
3. Inserts the built-in nodes and edges.

The docs use `/default_schema` by default. This is a database namespace, not a folder on the development machine.

`movie` is the graph name; `Movie` is a node type inside it. Keep the names and capitalization. After loading, run `SESSION SET GRAPH movie` so subsequent queries use the graph. The complete procedure is maintained in the [first-query tutorial](first-query.md#load); other chapters link to it.

!!! warning "Loading is not a repeatable refresh command"

    If `movie_type` or `movie` already exists, running `:play movie` again can fail because the names are in use. An interrupted load can leave a graph type, graph, or partial data. Seeing the graph name does not prove the load is complete. Do not ignore loading errors or delete only `movie` and retry, because `movie_type` may still exist.

## Use the dataset across chapters

The quick start loads the data and runs read-only queries. Continue using the same `movie` graph for later {{gql.name}}, API, and SDK examples. You do not need to reload it for each chapter.

For inserts, updates, and deletes, use the tutorial's specified practice records or a separate Schema. This keeps the original data available for later queries. `:play movie` is an `ngql` client command, not a {{gql.name}} statement; do not send it as a database query through a REST API or SDK.

Built-in data can change between client versions. Use the matching `ngql` version. If results differ, first check the version and whether the data has been modified. A different movie name or total node count alone does not mean the database is faulty.

## Load another copy if needed {#reload}

If loading was interrupted or data has changed, first decide whether to preserve the existing data. The following procedure keeps it and creates another copy in a separate Schema.

In `ngql`, run:

```sql
CREATE SCHEMA /movie_practice
```

`/movie_practice` is the new namespace used in this example. If it already exists, choose an unused name and use the same name in the next command. Do not delete an existing Schema.

```sql
SESSION SET SCHEMA /movie_practice
```

Then follow the [loading step](first-query.md#load) to run `:play movie` and check the results. This copy is in `/movie_practice`. In subsequent examples, replace `SESSION SET SCHEMA /default_schema` with `SESSION SET SCHEMA /movie_practice`.

This stores an additional copy. It does not repair or clear the original Schema. If Schema creation fails, resolve the error before proceeding; do not load into the original location by mistake.
