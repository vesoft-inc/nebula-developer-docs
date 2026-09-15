# Basic concepts

A graph database uses **nodes** to represent things and **edges** to represent relationships. This page uses the same `movie` dataset as the quick start: actors act in movies, users watch movies, and movies belong to genres.

```text
Actor ──acts in──→ Movie ←──watches── User
                    │
                 has genre
                    ↓
                  Genre
```

You do not need to memorize the entire structure. The first query uses only actors and movies. See [Example dataset](get-started/dataset.md) for the full model.

## Nodes, edges, and properties

A **node** represents an object, such as an actor or a movie. **Properties** describe it, such as a movie's `id` and `name`.

An **edge** connects two nodes. An `Act` edge points from an actor to a movie and records that the actor appeared in it. Edges can also have properties: `rate` on a `Watch` edge records a user's rating of a movie.

The dataset uses `id` as the node **primary key** to distinguish nodes of the same type. Movie names can repeat, so an ID usually identifies a specific movie more clearly than its name alone.

## Types and labels

A **type** defines the structure of a node or edge, such as `Actor` and `Movie`. A **label** lets you match nodes or edges carrying a particular label.

Actors, directors, and users have different types: `Actor`, `Director`, and `User`. All three share the `Person` label. Therefore:

- `@Actor` specifies the actor type.
- `:Person` matches by label and can include actors, directors, and users.

Do not interpret `:Person` as “actors only.” Also, `User` has only an `id` property, not the `name` and `birthDate` properties defined for actors.

## Graph types and graphs

A **graph type** defines the node types, edge types, and properties a graph can contain. `movie_type` defines the movie dataset's structure.

A **graph** holds actual data. `movie` stores the movies, actors, and relationships.

The `ngql` command `:play movie` creates both objects and inserts the built-in data. You do not need to create them manually in the quick start.

## What a Schema does

A Schema is a namespace for organizing graph types and graphs. Think of it as a directory in the database, not a folder on your computer.

The docs load data into `/default_schema` by default:

```text
/default_schema
├── movie_type   Graph type: defines the movie data structure
└── movie        Graph: stores the actual data
```

Select the Schema before loading so data does not go into another location. See [Load the movie dataset](get-started/first-query.md#load).

## Sessions and selecting a graph

After connecting, you execute {{gql.name}} statements in a session. Selecting a graph tells subsequent queries which data to use.

!!! note "Loading data and selecting a graph are separate steps"

    After `:play movie` completes, run `SESSION SET GRAPH movie`. After reconnecting, select the Schema and graph again, but do not reload the data. See [Resume your work](get-started/first-query.md#resume) for the commands.

## Next step

Follow the [Quick start](get-started/index.md) to load `movie` and run your first movie query.
