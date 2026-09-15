# 使用 Docker Compose 部署

本页带您在一台开发机上启动{{nebula.short_name}}。本文所称“开发机”，是指运行 Docker Compose 的 Windows、macOS 或 Linux 主机。

所有命令都在**开发机的终端**中执行。后续查询教程会说明何时切换到 `ngql`。

## {{nebula.short_name}}部署架构

{{nebula.short_name}}采用单机架构。配套的 Docker Compose 文件会启动以下容器：

| 组件 | 作用 | 本部署中的配置 |
| --- | --- | --- |
| Meta（`metad`） | 保存 Schema、图类型和服务组等数据库元数据 | 1 个 Meta 服务 |
| Graph（`graphd`） | 接收客户端连接、验证用户身份并执行 {{gql.name}} 查询 | 1 个 Graph 服务 |
| Storage（`storaged`） | 保存点、边及其属性 | 1 个 Storage 服务、1 个数据分片、1 个副本 |
| `ngctl` | 管理数据库服务 | 自动设置 `root` 密码，创建并初始化服务组 |
| `ngql` | 连接 Graph 服务并执行 {{gql.name}} 语句的命令行客户端 | 作为容器运行，无需单独安装 |

**数据分片**是数据库内部划分图数据的逻辑单位。1 个数据分片表示实例中的图数据只由一个逻辑分片承载，不会拆分到多个数据分片中存储。数据分片不是硬盘分区或 Docker 数据目录；1 个数据分片也不表示只能创建一个图或只能加载一个数据集。

**服务组**用于组织 Graph 和 Storage 服务。服务组中的**主机**是一个服务地址，Meta 通过该地址找到 Graph 和 Storage 服务。这里的主机不是额外的一台电脑，也不是开发机在操作系统中的主机名。

`graph-cluster` 是这份 Docker Compose 配置为主机设置的名称，也是 Docker 网络中的服务地址。配置会自动创建名为 `dev_cluster` 的服务组，将地址为 `graph-cluster` 的 Graph 和 Storage 服务加入该服务组，然后完成初始化。{{nebula.short_name}}只能注册一个主机地址，不能添加第二个地址来扩展实例。您无需修改 `graph-cluster`，也无需手工执行这些管理操作。

启动过程如下：

1. Docker Compose 启动 Meta 服务。
2. `ngctl` 设置数据库密码并初始化 `dev_cluster` 服务组。
3. 服务组初始化成功后，Docker Compose 启动 Storage、Graph 和 `ngql`。
4. 您通过 `ngql` 连接 Graph 服务，再执行 {{gql.name}} 语句。

`ngql` 是客户端工具，{{gql.name}} 是发送给数据库的查询语言，两者含义不同。下一页将使用 `ngql` 内置的 `movie` 数据集完成首次查询。{{nebula.short_name}}的其他部署限制见[使用限制](../limitations.md)。

## 前提条件

{{nebula.short_name}}目前没有额外的硬件配置要求。开始前，请确认 Docker 可以正常运行，并准备好以下环境：

- 已安装并启动 Docker，且可以使用 `docker compose` 命令。安装方法见 [Docker 官方说明](https://docs.docker.com/compose/install/)。
- 开发机使用 AMD64（x86_64）或 ARM64 处理器架构。
- Docker 可以访问配套文件中指定的镜像仓库。

## 1. 检查 Docker

打开终端，分别执行：

```bash
docker compose version
```

应显示 Docker Compose 的版本。若提示找不到 `docker` 或 `compose`，先完成工具安装。

```bash
docker info
```

应返回 Docker 服务的信息。若提示无法连接 Docker 服务，先启动 Docker；若提示权限不足，先解决当前账号访问 Docker 的权限问题。

## 2. 准备部署文件 {#release-files}

在开发机上创建一个新文件夹，例如 `nebula-dev-quickstart`。下载以下两个文件，并放到这个文件夹中：

- [Docker Compose 配置文件](files/compose.yaml)：保存为 `compose.yaml`。
- [环境变量模板](files/env.example)：保存为 `.env`，不要保留 `env.example` 这样的文件名。

目录应包含：

```text
nebula-dev-quickstart/
├── compose.yaml
└── .env
```

`.env` 是文本文件。部分文件管理器会隐藏以点开头的文件；保存时请确认文件名不是 `.env.txt`。

`compose.yaml` 定义要启动的服务及其运行方式；`.env` 保存镜像参数和登录密码。首次部署只需在 `.env` 中设置密码。各字段的用途和修改影响见 [Docker Compose 配置说明](../server-admin/configurations/docker-compose.md)。

## 3. 设置登录密码

用文本编辑器打开 `.env`，内容如下：

```dotenv
IMAGE_PREFIX=reg.vesoft-inc.com/vesoft-ng/nebula-dev
IMAGE_TAG=nightly
ROOT_PASSWORD='<your-password>'
```

将 `<your-password>` 替换为您自行设置的数据库密码，保留两侧单引号。不要使用占位符作为密码。记住这个密码，下一页以 `root` 用户登录时会用到。

单引号让密码中的 `$` 等字符按原样读取；若密码本身包含单引号，需按 [Docker 环境文件语法](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/#env-file-syntax)转义。不要分享或提交包含真实密码的 `.env` 文件。

其他两项分别指定数据库镜像名前缀和标签。此模板使用 `nightly`；`ngctl` 和 `ngql` 镜像也在 Docker Compose 文件中固定为 `nightly`。首次练习请保持配套值，不要只替换其中一个组件的版本。

!!! warning "修改 .env 不等于重置数据库密码"

    首次初始化时，脚本尝试将初始 `root` 密码设置为 `ROOT_PASSWORD`。已有数据库数据时，应使用该数据库现有的密码；只修改 `.env` 不会把旧密码重置为新值，可能导致初始化脚本一直等待登录。默认服务组名为 `dev_cluster`，已有数据时也不要改成另一个名称。

## 4. 验证配置并启动服务

在终端进入刚才的文件夹。将 `<quickstart-directory>` 替换为它的实际路径：

```bash
cd "<quickstart-directory>"
```

检查配置：

```bash
docker compose config --quiet
```

没有错误或变量未设置的警告后再继续；没有输出是正常的。此命令不启动数据库。详见 [Docker Compose 配置检查](https://docs.docker.com/reference/cli/docker/compose/config/)。

!!! note "配置文件没有按预期生效？"

    先检查 `.env` 是否与 `compose.yaml` 在同一目录、文件名是否正确。终端中已设置的同名环境变量会覆盖 `.env` 中的值。不要把不带 `--quiet` 的完整配置输出直接发给他人，其中可能包含密码。

启动：

```bash
docker compose up -d
```

`-d` 表示在后台运行。首次启动时会下载本地缺少的镜像。如果拉取失败，按[启动问题排查](#troubleshooting)处理。详见 [Docker Compose 启动命令](https://docs.docker.com/reference/cli/docker/compose/up/)。

## 5. 验证服务状态

仍在同一个终端和目录中执行：

```bash
docker compose ps --all
```

查看 `SERVICE` 和 `STATUS` 列。配置中包含以下五项：

| 服务 | 用途 | 应检查的状态 |
| --- | --- | --- |
| `metad` | 保存数据库定义等元数据 | 保持运行，不持续重启 |
| `ngctl` | 设置登录密码、创建并初始化默认服务组 | 运行，健康检查通过 |
| `storaged` | 存储图数据 | 保持运行，不持续重启 |
| `graphd` | 接收并执行查询 | 保持运行，不持续重启 |
| `ngql` | 提供命令行查询客户端 | 保持运行 |

`ngctl` 健康检查通过后，Docker Compose 才会启动 `storaged` 和 `graphd`；`ngql` 随后启动。`ngql` 容器运行只表示客户端容器已启动，不表示数据库登录或查询已经成功。容器状态说明见 [Docker Compose 状态命令](https://docs.docker.com/reference/cli/docker/compose/ps/)。

!!! note "不要直接把开发机的 9669 端口当作连接地址"

    这份配置让 Docker 动态分配开发机上的端口，因此 `PORTS` 列中的映射端口可能不是 `9669`。下一页从配套的 `ngql` 容器连接，使用固定的内部地址 `graph-cluster:9669`，无需猜测开发机上的端口。Graph 和 Storage 与 Meta 共用网络，端口映射显示在 `metad` 行是正常的。

**下一步：[连接并完成首次查询 →](first-query.md)**

## 部署问题排查 {#troubleshooting}

在 `compose.yaml` 所在目录查看日志：

```bash
docker compose logs --tail 100
```

日志中会包含各服务的名称。针对初始化问题，可以只查看 `ngctl`：

```bash
docker compose logs --tail 100 ngctl
```

| 现象 | 先检查什么 |
| --- | --- |
| 镜像拉取失败 | 检查镜像名称、标签和网络连接，不要换成其他版本的镜像 |
| 容器名已被占用 | 执行 `docker ps -a` 查看是否已有同名容器。确认它的用途，不要直接删除其他实例 |
| 找不到配置或提示变量未设置 | 确认终端位于练习目录，且 `.env` 文件名和内容正确 |
| `ngctl` 持续输出 `waiting for Meta` | 查看 `metad` 日志；若沿用了 `data` 目录，核对 `.env` 中是否使用原有数据库密码 |
| `ngctl` 未通过健康检查，后续服务未启动 | 查看 `ngctl` 和 `metad` 日志，先解决登录或服务组初始化错误 |
| 服务启动后持续重启 | 查看对应服务日志及 Docker 可用资源，保留错误信息；不要删除 `data` 目录来试错 |

修正文件或环境后，从第 4 步重新检查配置并启动。日志命令说明见 [Docker Compose 日志](https://docs.docker.com/reference/cli/docker/compose/logs/)。

## 停止并重新启动服务 {#stop-start}

完成查询后，如需暂停，在开发机终端的练习目录执行：

```bash
docker compose stop
```

这会停止容器而不删除它们。再次使用时执行：

```bash
docker compose start
```

重新检查状态，然后按[继续上次的练习](first-query.md#resume)连接。首次部署使用 `up -d`，不是 `start`。详见 [stop](https://docs.docker.com/reference/cli/docker/compose/stop/) 和 [start](https://docs.docker.com/reference/cli/docker/compose/start/)。

数据保存在练习目录的 `data/meta` 和 `data/storage` 中；运行日志保存在 `logs` 中。

!!! warning "保留 data 目录才能继续使用原来的数据"

    不要删除 `data`，也不要只复制 Docker Compose 文件到新目录后期待看到原来的图。暂停不需要删除容器或数据。不要把“保留本地目录”当成备份或高可用保障。

## 移除服务

如不再使用当前实例，请在开发机终端进入 `compose.yaml` 所在目录，执行：

```bash
docker compose down
```

此命令会停止并删除配套容器和 Docker 网络，但不会删除已下载的镜像，也不会删除练习目录中的 `data` 和 `logs`。如需使用原来的数据重新部署，请保留整个练习目录并再次执行 `docker compose up -d`。

如需彻底删除当前实例及其数据，请先确认数据无需保留，再删除整个练习目录。删除后无法通过 Docker Compose 恢复其中的数据。
