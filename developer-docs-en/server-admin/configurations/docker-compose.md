# Docker Compose configuration

This page explains the deployment files supplied with {{nebula.name}}. For your first deployment, follow the [deployment tutorial](../../get-started/deploy.md). Use this page to understand or adjust configuration values.

## Configuration files

Place these two files in the same directory:

| File | Purpose | First deployment |
| --- | --- | --- |
| [compose.yaml](../../get-started/files/compose.yaml) | Defines containers, networking, ports, and data locations | Save the supplied file |
| [.env template](../../get-started/files/env.example) | Supplies image and password values | Save as `.env` and set `ROOT_PASSWORD` |

For example, `IMAGE_TAG=nightly` in `.env` supplies the value for `${IMAGE_TAG}` below:

```yaml
image: ${IMAGE_PREFIX}-metad:${IMAGE_TAG}
```

`${SERVICE_GROUP:-dev_cluster}` uses `dev_cluster` when the variable is unset or empty. Variables set in your terminal take precedence over `.env`. Values take effect where the configuration references them; adding a variable alone does not change a database setting. See [Docker environment variables](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/).

## Environment variables {#environment}

### Variables in the template

| Variable | Template value | Purpose and usage |
| --- | --- | --- |
| `IMAGE_PREFIX` | `reg.vesoft-inc.com/vesoft-ng/nebula-dev` | Database image prefix, followed by `-metad`, `-graphd`, or `-storaged` |
| `IMAGE_TAG` | `nightly` | Tag for those three database images |
| `ROOT_PASSWORD` | `<your-password>` | Initial `root` password; replace the placeholder |

The `ngctl` and `ngql` image addresses are specified separately in `compose.yaml`, with their tags fixed to `nightly`. Changing `IMAGE_TAG` does not change these tools. Use the supplied values for your first deployment. Changing versions requires compatible database and tool images.

See [Set your sign-in password](../../get-started/deploy.md). With existing data, use the database's existing password for `ROOT_PASSWORD`; editing `.env` does not reset it.

### Optional variables

These variables have defaults in `compose.yaml`. You do not need to add them to `.env` for your first deployment.

| Variable | Default | Scope |
| --- | --- | --- |
| `SERVICE_GROUP` | `dev_cluster` | Service group initialized by `ngctl`; keep the original name with existing data |
| `TZ` | `UTC` | Timezone environment variable passed to `metad` and `ngctl`; the file does not pass it to other containers |

## Services and fields

Each entry under `services` defines a container service:

| Service | Purpose |
| --- | --- |
| `metad` | Stores database metadata |
| `graphd` | Accepts connections and executes {{gql.name}} queries |
| `storaged` | Stores nodes, edges, and properties |
| `ngctl` | Sets the initial password and initializes the service group |
| `ngql` | Provides the interactive query client |

The following values describe the supplied file, rather than general database defaults.

| Field | Use in this file |
| --- | --- |
| `image` | Container image |
| `pull_policy: missing` | Pulls images missing locally; does not refresh an existing image with the same tag on every startup |
| `container_name` | Container name |
| `environment` | Environment variables passed into the container, such as the initialization password |
| `entrypoint` | Startup entry point for tool containers |
| `command` | Database startup arguments or tool scripts |
| `volumes` | Maps development machine directories to container directories |
| `ports` | Maps container ports to development machine ports |
| `networks`, `network_mode` | Container networking |
| `depends_on`, `healthcheck` | Startup dependencies and checks |
| `restart: unless-stopped` | Container restart policy; manually stopped containers remain stopped |

See [Docker Compose service configuration](https://docs.docker.com/reference/compose-file/services/) for field syntax. Use spaces for YAML indentation and preserve the nesting of fields.

### Database startup arguments

Database services receive these arguments through `command`:

| Argument | Supplied value | Purpose |
| --- | --- | --- |
| `--meta_server_addrs` | `graph-cluster:9559` | Meta address |
| `--host` | `graph-cluster` | Host address used by the service |
| `--port` | Meta: `9559`; Storage: `9779`; Graph: `9669` | Service port inside the container network |
| `--data_path` | Meta: `/data/meta`; Storage: `/data/storage` | Data directory inside the container |
| `--memory_strategy` | `static` | Memory strategy for Graph and Storage; keep the supplied value initially |

These addresses correspond to `META_HOST`, `META_PORT`, `SERVICE_HOST`, and the service registration ports in the initialization script. Changing only one location creates inconsistent connection settings. No changes are needed for your first deployment.

## Network and connection addresses {#network}

| Name | Meaning |
| --- | --- |
| `dev_cluster` | Database service group name |
| `graph-cluster-dev` | Network name in the Docker Compose configuration |
| `graph-cluster` | Address name used to reach database services inside that network |

Graph and Storage use `network_mode: service:metad` to share Meta's container network. Port mappings are therefore configured under `metad`.

The supplied `ngql` connects to Graph at `graph-cluster:9669` inside that network. See [Connect to the database](../../get-started/first-query.md#connect).

### Connect from the development machine

The supplied `ports` entries list `9559`, `9779`, `9669`, and `19669`. They specify container ports only; Docker assigns development machine ports, which can differ.

For a client on the development machine, run this command in the directory containing `compose.yaml` to find Graph's mapped port:

```bash
docker compose port metad 9669
```

The output has the form `address:port`. For a client on the same development machine, use `127.0.0.1` as the host and the returned port number. If the address is `0.0.0.0`, it is a listening address, not the client destination. A database username and password are still required.

## Data and log directories {#directories}

For example:

```yaml
volumes:
  - ./data/meta:/data/meta
```

The left side is the development machine directory; the right side is the container directory. With both configuration files in one directory as in this tutorial, `./` refers to the directory containing `compose.yaml`.

| Development machine directory | Container directory | Contents |
| --- | --- | --- |
| `./data/meta` | `/data/meta` | Meta data |
| `./data/storage` | `/data/storage` | Storage data, including graph data |
| `./logs/meta` | `/usr/local/nebula/logs` | Meta logs |
| `./logs/storage` | `/usr/local/nebula/logs` | Storage logs |
| `./logs/graph` | `/usr/local/nebula/logs` | Graph logs |

Each log mapping belongs to its corresponding container. The identical container paths do not mix development machine directories.

Changing the left-hand directory changes where the container reads data; it does not migrate existing data. Keep the original mapping to continue using your data. See the [deployment tutorial](../../get-started/deploy.md#stop-start) for data retention when stopping or removing containers.

## Initialization and startup dependencies

The supplied file starts services in this order:

1. Docker Compose starts `metad`. `service_started` means the container has started, not that the database is ready.
2. `ngctl` waits for Meta sign-in, attempts to set the initial password, and creates the service group, registers its host and services, and initializes it with one replica.
3. The script stays running after initialization. Its health check detects the waiting process at the end of the script and marks `ngctl` healthy.
4. `storaged` and `graphd` start after that check passes. `ngql` starts after the `graphd` container has started.

This health check indicates that the initialization script reached its final step. It does not run a graph query. Complete the [first query](../../get-started/first-query.md) to verify sign-in and querying.

The `ngql` container stays running so that you can open the client with `docker compose exec`. It does not automatically load `movie`.

## Apply and verify changes {#apply}

Run all commands in the development machine's terminal, in the directory containing `compose.yaml`. Applying changes can recreate containers; do this when no queries are running.

1. Edit `.env` or `compose.yaml` and save it. For an initial deployment, set the password and keep other supplied values.
2. Validate configuration syntax and variable references:

   ```bash
   docker compose config --quiet
   ```

   Successful completion with no output means configuration validation passed, not that the database is available. Full configuration output can contain passwords; do not share it directly.

3. Apply the configuration:

   ```bash
   docker compose up -d
   ```

   `docker compose restart` does not apply edited container configuration or environment variables. Changing an image tag does not establish compatibility or complete a database upgrade.

4. Inspect container status:

   ```bash
   docker compose ps --all
   ```

   Follow [Check startup](../../get-started/deploy.md), then [connect](../../get-started/first-query.md#connect) to verify querying. For errors, see [deployment troubleshooting](../../get-started/deploy.md#troubleshooting).
