# Docker Compose 配置说明

本文介绍{{nebula.name}}配套部署文件中的配置项。首次部署请先按[部署教程](../../get-started/deploy.md)操作；需要了解参数含义或调整配置时，再查阅本页。

## 配置文件的关系

将以下两个文件放在同一目录中：

| 文件 | 用途 | 首次部署需要的操作 |
| --- | --- | --- |
| [compose.yaml](../../get-started/files/compose.yaml) | 定义启动哪些容器，以及网络、端口和数据保存位置 | 保存配套文件 |
| [.env 模板](../../get-started/files/env.example) | 为配置文件提供镜像和密码参数 | 保存为 `.env`，设置 `ROOT_PASSWORD` |

例如，`.env` 中的 `IMAGE_TAG=nightly` 为以下配置中的 `${IMAGE_TAG}` 提供值：

```yaml
image: ${IMAGE_PREFIX}-metad:${IMAGE_TAG}
```

`${SERVICE_GROUP:-dev_cluster}` 表示变量未设置或为空时使用 `dev_cluster`。终端中已设置的同名变量会优先于 `.env`。`.env` 中的值通过配置文件的引用生效；仅添加一个变量并不会自动修改数据库设置。语法见 [Docker 环境变量说明](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)。

## 环境变量 {#environment}

### 模板中的变量

| 变量 | 模板值 | 用途与使用说明 |
| --- | --- | --- |
| `IMAGE_PREFIX` | `reg.vesoft-inc.com/vesoft-ng/nebula-dev` | 数据库镜像名前缀，分别拼接 `-metad`、`-graphd`、`-storaged` |
| `IMAGE_TAG` | `nightly` | 上述三个数据库镜像的标签 |
| `ROOT_PASSWORD` | `<your-password>` | 首次初始化设置的 `root` 密码，必须替换占位符 |

`ngctl` 和 `ngql` 的镜像地址在 `compose.yaml` 中单独指定，标签固定为 `nightly`。修改 `IMAGE_TAG` 不会改变这两个工具的镜像。首次部署请使用配套值；更换版本需要使用相互兼容的数据库和工具镜像。

密码设置方法见[设置登录密码](../../get-started/deploy.md)。已有数据时，`ROOT_PASSWORD` 应与数据库现有密码一致；只修改 `.env` 不会重置密码。

### 可选变量

以下变量已在 `compose.yaml` 中设置默认值，首次部署无需添加到 `.env`。

| 变量 | 默认值 | 作用范围 |
| --- | --- | --- |
| `SERVICE_GROUP` | `dev_cluster` | `ngctl` 初始化的服务组名称；已有数据时保留原名称 |
| `TZ` | `UTC` | 传给 `metad` 和 `ngctl` 容器的时区环境变量；本文件未将其传给其他容器 |

## 服务与配置字段

`services` 下的每一项定义一个容器服务：

| 服务名称 | 用途 |
| --- | --- |
| `metad` | 保存数据库元数据 |
| `graphd` | 接收连接并执行 {{gql.name}} 查询 |
| `storaged` | 保存点、边及其属性 |
| `ngctl` | 设置首次登录密码并初始化服务组 |
| `ngql` | 提供交互式查询客户端 |

常用配置字段如下。这里的值来自配套文件，不代表数据库参数的通用默认值。

| 字段 | 本文件中的作用 |
| --- | --- |
| `image` | 指定容器使用的镜像 |
| `pull_policy: missing` | 本地缺少镜像时拉取；不会在每次启动时刷新已有的同标签镜像 |
| `container_name` | 指定容器名称 |
| `environment` | 向容器传入环境变量，例如初始化密码 |
| `entrypoint` | 为工具容器指定启动入口 |
| `command` | 为数据库服务提供启动参数，或为工具容器指定脚本 |
| `volumes` | 将开发机目录映射到容器目录 |
| `ports` | 将容器端口映射到开发机 |
| `networks`、`network_mode` | 设置容器之间的网络连接方式 |
| `depends_on`、`healthcheck` | 设置启动依赖和检查条件 |
| `restart: unless-stopped` | 设置容器重启策略；手工停止的容器保持停止 |

字段语法见 [Docker Compose 服务配置](https://docs.docker.com/reference/compose-file/services/)。修改 YAML 时使用空格缩进，保持字段所属层级。

### 数据库启动参数

数据库服务通过 `command` 接收以下参数：

| 参数 | 配套值 | 用途 |
| --- | --- | --- |
| `--meta_server_addrs` | `graph-cluster:9559` | Meta 服务地址 |
| `--host` | `graph-cluster` | 服务使用的主机地址 |
| `--port` | Meta 为 `9559`，Storage 为 `9779`，Graph 为 `9669` | 对应服务在容器网络中使用的端口 |
| `--data_path` | Meta 为 `/data/meta`，Storage 为 `/data/storage` | 容器内的数据保存目录 |
| `--memory_strategy` | `static` | Graph 和 Storage 使用的内存策略；首次部署保留配套值 |

这些地址与初始化脚本中的 `META_HOST`、`META_PORT`、`SERVICE_HOST` 和注册服务时的端口对应。仅修改其中一处会使服务之间的连接配置不一致。首次部署无需修改这些参数。

## 网络与连接地址 {#network}

| 名称 | 含义 |
| --- | --- |
| `dev_cluster` | 数据库服务组名称 |
| `graph-cluster-dev` | Docker Compose 配置中的网络名称 |
| `graph-cluster` | 该网络中的地址名称，用于访问数据库服务 |

Graph 和 Storage 配置了 `network_mode: service:metad`，共用 Meta 容器的网络。因此，端口映射集中写在 `metad` 下。

配套 `ngql` 在同一 Docker 网络中，通过 `graph-cluster:9669` 连接 Graph。连接步骤见[首次查询](../../get-started/first-query.md#connect)。

### 从开发机连接

配套文件的 `ports` 列出 `9559`、`9779`、`9669` 和 `19669`，只指定容器端口，由 Docker 分配开发机端口。它们不一定与容器端口相同。

如果使用开发机上的客户端，在 `compose.yaml` 所在目录的终端执行以下命令，查看 Graph 的映射端口：

```bash
docker compose port metad 9669
```

输出格式为 `地址:端口`。客户端运行在同一开发机时，连接主机填写 `127.0.0.1`，端口填写输出中的端口号。若输出地址为 `0.0.0.0`，它表示监听地址，不要将其填作客户端目标地址。仍需使用数据库用户名和密码登录。

## 数据与日志目录 {#directories}

例如：

```yaml
volumes:
  - ./data/meta:/data/meta
```

冒号左侧是开发机目录，右侧是容器目录。按本教程将两个配置文件放在同一目录时，`./` 表示 `compose.yaml` 所在目录。

| 开发机目录 | 容器目录 | 保存内容 |
| --- | --- | --- |
| `./data/meta` | `/data/meta` | Meta 数据 |
| `./data/storage` | `/data/storage` | Storage 数据，包括图数据 |
| `./logs/meta` | `/usr/local/nebula/logs` | Meta 日志 |
| `./logs/storage` | `/usr/local/nebula/logs` | Storage 日志 |
| `./logs/graph` | `/usr/local/nebula/logs` | Graph 日志 |

三个日志目录分别映射给对应容器，容器内路径相同不会混用开发机目录。

更换左侧目录会改变容器读取的数据位置，不会自动搬迁原数据。需要继续使用原数据时，保留原目录映射。停止和移除容器后的数据保留行为见[部署教程](../../get-started/deploy.md#stop-start)。

## 初始化与启动依赖

配套文件的启动顺序如下：

1. Docker Compose 启动 `metad`。`service_started` 表示容器已启动，不表示数据库已就绪。
2. `ngctl` 等待 Meta 可登录，尝试设置首次密码，然后创建服务组、注册主机和服务、初始化服务组。服务组使用 1 个副本。
3. 脚本完成后保持运行；健康检查检测到脚本末尾的等待进程后，`ngctl` 显示为健康。
4. `storaged` 和 `graphd` 等待该健康检查通过后启动；`ngql` 等待 `graphd` 容器启动后启动。

这里的健康检查用于判断初始化脚本是否执行到末尾，不会执行图查询。最终应按[首次查询](../../get-started/first-query.md)验证登录和查询。

`ngql` 容器保持运行，供您通过 `docker compose exec` 打开客户端。它不会自动加载 `movie` 数据集。

## 修改与验证配置 {#apply}

所有命令均在开发机终端、`compose.yaml` 所在目录中执行。应用配置可能重新创建容器，请在没有查询任务运行时操作。

1. 修改 `.env` 或 `compose.yaml`，保存文件。首次部署只需设置密码，其他值保留配套配置。
2. 检查配置语法和变量引用：

   ```bash
   docker compose config --quiet
   ```

   没有输出且命令成功结束表示配置检查通过，不代表数据库服务已经可用。完整配置输出可能包含密码，请勿直接分享。

3. 应用配置：

   ```bash
   docker compose up -d
   ```

   `docker compose restart` 不会应用修改后的容器配置或环境变量。更换镜像标签也不等于已完成兼容性验证或数据库升级。

4. 查看容器状态：

   ```bash
   docker compose ps --all
   ```

   然后按[验证服务状态](../../get-started/deploy.md)检查各服务，并[连接数据库](../../get-started/first-query.md#connect)验证查询。出现问题时查阅[部署问题排查](../../get-started/deploy.md#troubleshooting)。
