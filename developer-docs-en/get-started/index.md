# Quick start

Use the `movie` dataset built into `ngql` to find a movie's actors. You do not need to know {{gql.name}} or create the data manually before starting.

## Follow these two steps

1. **[Deploy with Docker Compose](deploy.md):** Check Docker, prepare the release files, and start the database.
2. **[Connect and run your first query](first-query.md):** Connect with `ngql`, load `movie`, and query a movie and its actors.

If you already have a reachable {{nebula.short_name}} instance and the supplied `ngql` container, start at step 2.

## Where to run commands

Each code block identifies where to run it. Use the correct window:

| Location | What it is for | Example |
| --- | --- | --- |
| Development machine terminal | Check Docker, manage containers, and start `ngql` | `docker compose version` |
| The `ngql` interactive console | Send {{gql.name}} statements to the database | `RETURN 1 AS result` |

A value in angle brackets, such as `<name>`, is a placeholder you must replace. Do not enter the brackets. In contrast, `movie` is the graph name used by this tutorial; keep it as written. `:play movie` runs only in `ngql`; it is not a general {{gql.name}} statement.

## How to check completion

You have completed the exercise when you find movie ID `3`, Shadows in Paradise, and follow its acting relationships to find its actors. The tutorial provides expected results and explains how to reconnect and repeat queries.

[Example dataset](dataset.md) is the shared description of the model and loading behavior. Later {{gql.name}}, API, and SDK examples use the same data, so you do not need to reload it for each chapter.

**Next: [Deploy with Docker Compose →](deploy.md)**
