# 连接并完成首次查询

本页带您加载 `ngql` 内置的 `movie` 数据集，查询一部电影，再找到参演这部电影的演员。无需先学习建图和写入语法。

## 前提条件

- 已按[部署教程](deploy.md)启动配套容器。
- 知道 `.env` 中 `ROOT_PASSWORD` 对应的密码。
- 准备在未加载过 `movie` 的 Schema 中练习；已经加载过时，按下方说明继续查询。

!!! note "示例验证范围"

    本页是配套 `nightly` 环境的预览教程，完整流程尚待验证。下方表格给出按示例数据应得到的结果；如果实际结果不同，请按本页末尾的排查步骤检查。

## 1. 连接数据库 {#connect}

在**开发机终端**中进入 `compose.yaml` 所在的练习目录，执行：

```bash
docker compose exec ngql ngql --host graph-cluster --port 9669 --user root
```

第一个 `ngql` 是容器服务名称，第二个 `ngql` 是容器内的客户端命令。`graph-cluster` 是配套容器网络中的地址，`9669` 是查询端口。此命令不需要改成开发机的 IP 地址。容器内执行命令的方式见 [Docker Compose exec](https://docs.docker.com/reference/cli/docker/compose/exec/)。

看到 `Password` 提示后，输入您在 `.env` 中设置的密码。输入内容不会显示；输入完按 Enter。不要把 `.env` 中包围密码的单引号也输入进去。

连接后会进入 `ngql` 交互窗口。**从下一条开始，{{gql.name}} 语句都在这个窗口执行，不在开发机的普通终端执行。** 每次执行一个代码块，确认没有错误后再继续。

先执行一个不读取图数据的查询：

```sql
RETURN 1 AS result
```

应返回一列 `result`，值为 `1`。这说明能够登录并执行基本查询；后面的加载和查询步骤还会检查图数据是否可用。

## 2. 选择目标 Schema

在 `ngql` 中选择默认 Schema。Schema 是组织图和图类型的命名空间，不是开发机上的文件夹。

```sql
SESSION SET SCHEMA /default_schema
```

分别查看已有的图类型和图：

```sql
SHOW GRAPH TYPES
```

```sql
SHOW GRAPHS
```

第一次加载前，确认这里没有 `movie_type` 图类型和 `movie` 图。

!!! note "已经加载过 movie？"

    如果上次加载成功，可以直接[选择图并查询](#select-graph)。不要重新执行加载命令。如果是中途加载失败留下的对象，或同名对象用于其他用途，请先阅读[重新加载说明](dataset.md#reload)。

## 3. 加载 movie 数据集 {#load}

在 `ngql` 中执行：

```text
:play movie
```

这个命令使用客户端内置的数据，自动创建 `movie_type` 和 `movie`，并写入点和边。无需手工建图或下载数据文件。

命令开始时会显示：

```text
Playing dataset: movie...
```

等待执行结束。成功时会显示：

```text
Play dataset: movie done.
```

如果出现错误，先处理错误，不要把 `Playing dataset` 当作加载完成，也不要反复执行 `:play movie`。该命令的同名对象处理和失败影响见[加载命令做了什么](dataset.md#load-behavior)。

加载成功后执行：

```sql
SHOW GRAPHS
```

结果中应出现图 `movie`，其图类型为 `movie_type`，所属 Schema 为 `/default_schema`。图已列出只是检查之一，接下来还需要确认能查询到数据。

## 4. 选择图并查询电影 {#select-graph}

加载完成后，在同一个 `ngql` 窗口中执行：

```sql
SESSION SET GRAPH movie
```

!!! note "不要跳过选择图"

    `:play movie` 不会替您设置这个交互会话使用的图。显式选择 `movie` 后，后面的查询才会使用它。

先查找编号为 `3` 的电影：

```sql
MATCH (m@Movie {id: 3}) RETURN m.id AS movie_id, m.name AS movie
```

- `MATCH` 查找符合条件的点。
- `@Movie` 指定电影类型。
- `{id: 3}` 指定电影编号。
- `RETURN` 选择要显示的属性，`AS` 为结果列命名。

配套数据中的结果应为：

| movie_id | movie |
| --- | --- |
| 3 | Shadows in Paradise |

这里用编号而不是片名定位电影，避免同名电影带来的歧义。`movie` 是图名，`Movie` 是点类型名称，注意大小写。

## 5. 查询参演演员

完整复制下面的代码块到 `ngql`，包括首尾的 `'''`。这两个标记告诉客户端将多行作为一条语句提交，不是 {{gql.name}} 语法的一部分。

```sql
'''
MATCH (a@Actor)-[:Act]->(m@Movie {id: 3})
RETURN a.id AS actor_id, a.name AS actor, m.name AS movie
ORDER BY actor_id
'''
```

`(a@Actor)-[:Act]->(m@Movie)` 表示“演员通过参演关系连接到电影”。箭头从演员指向电影。`ORDER BY actor_id` 按演员编号排序，便于核对结果。

配套数据中的结果应为：

| actor_id | actor | movie |
| --- | --- | --- |
| 4826 | Matti Pellonpää | Shadows in Paradise |
| 4828 | Sakari Kuosmanen | Shadows in Paradise |
| 5999 | Kati Outinen | Shadows in Paradise |

到这里，您已完成加载数据、查询点和查询关系。后续章节可以继续使用同一张 `movie` 图。

## 退出并恢复查询 {#resume}

在 `ngql` 中执行：

```text
:exit
```

这只退出客户端，不停止数据库，也不删除数据。需要暂停数据库时，按[暂停练习和再次启动](deploy.md#stop-start)操作。

下次按[连接步骤](#connect)重新连接后，依次执行：

```sql
SESSION SET SCHEMA /default_schema
```

```sql
SESSION SET GRAPH movie
```

然后从第 4 或第 5 步继续查询，**无需再次执行 `:play movie`**。如果数据实际位于其他 Schema，将第一条命令的路径改为加载时使用的路径。

## 重复查询与数据保留 {#reset}

本页的查询不会修改数据，可以反复执行。若加载中断或数据被改动，请按[重新加载说明](dataset.md#reload)在独立 Schema 中练习，避免误删需要保留的数据。

后续 API 和 SDK 示例也使用这份图数据，但 `:play movie` 只能在 `ngql` 中执行，不能当作 {{gql.name}} 查询发送给 API 或 SDK。

## 查询问题排查 {#troubleshooting}

| 现象 | 如何处理 |
| --- | --- |
| 终端提示 `ngql` 服务未运行 | 返回[部署教程](deploy.md#troubleshooting)检查容器和初始化日志 |
| 连接失败或被拒绝 | 使用本页完整的 `docker compose exec` 命令，检查 `graphd` 状态与日志 |
| 密码错误 | 输入 `.env` 中密码的实际内容，不含两侧单引号；沿用旧数据时使用原数据库密码 |
| `:play movie` 报数据集不存在 | 确认使用配套的 `ngql` 客户端，不要将该命令输入普通终端或其他查询工具 |
| 加载时提示对象已存在 | 不要重复加载。上次已成功则直接选择图；上次失败则参考[重新加载说明](dataset.md#reload) |
| 提示未选择图或找不到 `movie` | 重新选择加载时使用的 Schema 和 `movie` 图；用 `SHOW GRAPHS` 检查位置 |
| 电影查询有结果，演员查询为空 | 检查 `Act` 方向和大小写、加载是否报错、数据是否被修改，不要仅凭图存在判断完整加载 |
| 多行输入一直等待 | 检查是否完整复制首尾的 `'''` 和中间所有行 |
| 结果与示例不同 | 先核对 `ngql` 版本和数据是否被修改，再核对电影编号 `3` |

仍无法解决时，可按[贡献指南](../contributing.md)反馈文档问题。附上镜像版本、失败步骤、语句和脱敏错误信息，不要附上密码或完整 `.env`。
