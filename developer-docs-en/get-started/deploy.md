# Deploy with Docker Compose

Start {{nebula.short_name}} on one development machine. In this guide, the development machine is a Windows, macOS, or Linux host that runs Docker Compose.

Run all commands on this page in **the development machine's terminal**. The query tutorial explains when to switch to `ngql`.

## {{nebula.short_name}} deployment architecture

{{nebula.short_name}} uses a single-machine architecture. The supplied Docker Compose file starts these containers:

| Component | Purpose | Configuration in this deployment |
| --- | --- | --- |
| Meta (`metad`) | Stores database metadata such as Schemas, graph types, and service groups | One Meta service |
| Graph (`graphd`) | Accepts client connections, authenticates users, and runs {{gql.name}} queries | One Graph service |
| Storage (`storaged`) | Stores vertices, edges, and their properties | One Storage service, one data partition, and one replica |
| `ngctl` | Manages database services | Sets the `root` password and creates and initializes the service group automatically |
| `ngql` | Command-line client for connecting to Graph and running {{gql.name}} statements | Runs as a container; no separate installation is required |

A **data partition** is a logical unit that the database uses to divide graph data. One data partition means that the instance's graph data is not divided among multiple partitions for storage. A data partition is not a disk partition or a Docker data directory. Having one data partition also does not mean that you can create only one graph or load only one dataset.

A **service group** is a logical unit that organizes Graph and Storage services. A **Host** here is a service address registered with the service group so that Meta can locate the Graph and Storage services. It is not an additional computer or the development machine's operating-system hostname.

In the supplied configuration, `graph-cluster` is a hostname inside the Docker network and represents this set of single-machine services. The configuration creates a service group named `dev_cluster`, adds `graph-cluster` and its Graph and Storage services, and then initializes the group. {{nebula.short_name}} allows only one registered Host, so you cannot add a second service address to expand the instance. You do not need to change `graph-cluster` or run these management operations yourself.

Startup proceeds as follows:

1. Docker Compose starts the Meta service.
2. `ngctl` sets the database password and initializes the `dev_cluster` service group.
3. After the service group is initialized, Docker Compose starts Storage, Graph, and `ngql`.
4. You use `ngql` to connect to Graph and then run {{gql.name}} statements.

`ngql` is a client tool; {{gql.name}} is the query language sent to the database. The next page uses the `movie` dataset built into `ngql` to run your first query. See [Limitations](../limitations.md) for other {{nebula.short_name}} deployment limits.

## Before you start

{{nebula.short_name}} currently has no additional hardware requirements. Check that Docker runs on the development machine and prepare the following:

- Install and start Docker with the `docker compose` command available. See the [Docker installation instructions](https://docs.docker.com/compose/install/).
- Use a development machine with an AMD64 (x86_64) or ARM64 processor architecture.
- Ensure Docker can reach the image registry specified in the supplied files.

## 1. Check Docker

Open a terminal and run these commands separately:

```bash
docker compose version
```

This should show the Docker Compose version. If `docker` or `compose` cannot be found, complete the tool installation first.

```bash
docker info
```

This should return information about the Docker service. If it cannot connect, start Docker first. If access is denied, resolve your account's permission to access Docker.

## 2. Save the supplied files {#release-files}

Create a new folder on the development machine, such as `nebula-dev-quickstart`. Download these files into it:

- [Docker Compose configuration](files/compose.yaml): Save as `compose.yaml`.
- [Environment template](files/env.example): Save as `.env`, not `env.example`.

The directory should contain:

```text
nebula-dev-quickstart/
├── compose.yaml
└── .env
```

`.env` is a text file. Some file managers hide files whose names start with a dot. Check that it was not saved as `.env.txt`.

`compose.yaml` defines the services and how they run; `.env` supplies image settings and the sign-in password. For your first deployment, set the password in `.env`. See [Docker Compose configuration](../server-admin/configurations/docker-compose.md) for field meanings and the effects of changes.

## 3. Set your sign-in password

Open `.env` in a text editor. It contains:

```dotenv
IMAGE_PREFIX=reg.vesoft-inc.com/vesoft-ng/nebula-dev
IMAGE_TAG=nightly
ROOT_PASSWORD='<your-password>'
```

Replace `<your-password>` with your own database password, keeping the single quotes. Do not use the placeholder as a password. You will use this password to sign in as `root` on the next page.

Single quotes preserve characters such as `$` literally. If the password contains a single quote, escape it according to [Docker environment file syntax](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/#env-file-syntax). Do not share or commit a `.env` file containing a real password.

The other two settings specify the database image prefix and tag. This template uses `nightly`; the Docker Compose file also fixes the `ngctl` and `ngql` images to `nightly`. Keep the matching values for this exercise rather than changing just one component's version.

!!! warning "Editing .env does not reset the database password"

    During first initialization, the script attempts to set the initial `root` password to `ROOT_PASSWORD`. With existing database data, use that database's existing password. Editing `.env` alone does not reset it and can leave the initialization script waiting for sign-in. The default service group name is `dev_cluster`; do not change it when reusing data either.

## 4. Check configuration and start

In your terminal, open the folder you created. Replace `<quickstart-directory>` with its actual path:

```bash
cd "<quickstart-directory>"
```

Check the configuration:

```bash
docker compose config --quiet
```

Resolve errors and unset-variable warnings before continuing. No output is normal. This command does not start the database. See [Docker Compose configuration validation](https://docs.docker.com/reference/cli/docker/compose/config/).

!!! note "Settings not taking effect?"

    Check that `.env` is next to `compose.yaml` and has the correct filename. Variables already set in your terminal override matching `.env` values. Do not share full configuration output without `--quiet`; it can contain your password.

Start the environment:

```bash
docker compose up -d
```

`-d` runs the containers in the background. Startup downloads images that are missing locally. If a pull fails, see [Troubleshoot startup](#troubleshooting). See also [Docker Compose startup](https://docs.docker.com/reference/cli/docker/compose/up/).

## 5. Check startup

In the same terminal and directory, run:

```bash
docker compose ps --all
```

Check the `SERVICE` and `STATUS` columns for these five services:

| Service | Purpose | What to check |
| --- | --- | --- |
| `metad` | Stores metadata such as database definitions | Stays running without repeated restarts |
| `ngctl` | Sets the sign-in password and creates and initializes the default service group | Running with its health check passing |
| `storaged` | Stores graph data | Stays running without repeated restarts |
| `graphd` | Receives and executes queries | Stays running without repeated restarts |
| `ngql` | Provides the command-line query client | Stays running |

Docker Compose starts `storaged` and `graphd` after the `ngctl` health check passes, then starts `ngql`. A running `ngql` container only means the client container has started; it does not prove that database sign-in or queries work. See [Docker Compose container status](https://docs.docker.com/reference/cli/docker/compose/ps/).

!!! note "Do not assume port 9669 on the development machine is the connection port"

    Docker assigns host ports dynamically for this configuration, so the published port in `PORTS` might not be `9669`. The next page connects from the supplied `ngql` container using the fixed internal address `graph-cluster:9669`. You do not need to guess the host port. Graph and Storage share Meta's network, so port mappings appear on the `metad` row.

**Next: [Connect and run your first query →](first-query.md)**

## Troubleshoot startup {#troubleshooting}

From the directory containing `compose.yaml`, inspect logs:

```bash
docker compose logs --tail 100
```

Logs include service names. For initialization issues, inspect `ngctl` alone:

```bash
docker compose logs --tail 100 ngctl
```

| Symptom | What to check first |
| --- | --- |
| Image pull fails | Check the image name, tag, and network connection. Do not substitute another edition's image |
| Container name is already in use | Run `docker ps -a` to find existing containers. Check their purpose before taking action; do not delete another instance |
| Configuration is missing or variables are unset | Check that the terminal is in the practice directory and `.env` has the correct name and contents |
| `ngctl` keeps printing `waiting for Meta` | Check `metad` logs. If reusing a `data` directory, check that `.env` has the database's existing password |
| `ngctl` health check fails and later services do not start | Inspect `ngctl` and `metad` logs; resolve sign-in or service group initialization errors first |
| Services keep restarting | Inspect service logs and Docker's available resources. Preserve the errors; do not delete `data` to experiment with a fix |

After correcting files or the environment, repeat the configuration check and startup in step 4. See [Docker Compose logs](https://docs.docker.com/reference/cli/docker/compose/logs/).

## Pause and restart your exercise {#stop-start}

After finishing the queries, run this in the development machine's terminal, in the practice directory:

```bash
docker compose stop
```

This stops containers without deleting them. To use them again, run:

```bash
docker compose start
```

Check status again, then [resume your work](first-query.md#resume). Use `up -d`, not `start`, for the initial deployment. See [stop](https://docs.docker.com/reference/cli/docker/compose/stop/) and [start](https://docs.docker.com/reference/cli/docker/compose/start/).

Data is stored in `data/meta` and `data/storage` inside the practice directory. Runtime logs are stored in `logs`.

!!! warning "Keep data to continue using your existing database"

    Do not delete `data` or copy only the Docker Compose file to a new directory and expect to find your existing graph there. Pausing does not require deleting containers or data. Keeping a local directory is not a backup or high-availability guarantee.

## Remove the services

When you no longer need the current instance, open the directory containing `compose.yaml` in the development machine's terminal and run:

```bash
docker compose down
```

This command stops and removes the supplied containers and Docker network. It does not remove downloaded images or the `data` and `logs` directories in your practice directory. To deploy again with the existing data, keep the entire practice directory and run `docker compose up -d`.

To permanently remove the instance and its data, first confirm that you no longer need the data, and then delete the entire practice directory. Docker Compose cannot recover that data after deletion.
