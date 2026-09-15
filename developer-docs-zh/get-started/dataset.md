# 示例数据集：movie

本文档统一使用 `ngql` 内置的 `movie` 数据集。它包含电影、演员、导演、用户和电影类别，适合练习“某部电影有哪些演员”“某位用户看过哪些电影”等查询。

首次使用，请按[连接并完成首次查询](first-query.md)加载数据。无需另行下载 CSV 文件，也无需手工创建图类型、图或逐条插入数据。

## 数据模型

```text
演员 Actor ─────Act（参演）─────→ 电影 Movie
导演 Director ──Direct（执导）──→ 电影 Movie
用户 User ──────Watch（观看）───→ 电影 Movie
电影 Movie ─────WithGenre──────→ 类别 Genre
```

箭头表示边的方向。例如，`Act` 从演员指向电影；查询某部电影的演员时，也要按这个方向匹配。

### 点类型

| 类型 | 表示什么 | 标签 | 属性 | 主键 |
| --- | --- | --- | --- | --- |
| `User` | 用户 | `Person` | `id` | `id` |
| `Actor` | 演员 | `Person` | `id`、`name`、`birthDate` | `id` |
| `Director` | 导演 | `Person` | `id`、`name`、`birthDate` | `id` |
| `Movie` | 电影 | `Movie` | `id`、`name` | `id` |
| `Genre` | 电影类别 | `Genre` | `id`、`name` | `id` |

`id` 是整数编号，用于区分同一类型的点；`name` 是字符串名称；`birthDate` 是日期。用户类型只有 `id`，不能假设每个带 `Person` 标签的点都有姓名或出生日期。

### 边类型

| 类型 | 关系 | 方向 | 标签 | 属性 |
| --- | --- | --- | --- | --- |
| `Watch` | 用户观看电影 | `User` → `Movie` | `Watch` | `rate`：浮点数评分 |
| `Act` | 演员参演电影 | `Actor` → `Movie` | `Act` | 无 |
| `Direct` | 导演执导电影 | `Director` → `Movie` | `Direct` | 无 |
| `WithGenre` | 电影属于某个类别 | `Movie` → `Genre` | `WithGenre` | 无 |

!!! note "类型和标签不是一回事"

    `Actor`、`Director` 和 `User` 是不同类型，但都带有 `Person` 标签。`@Actor` 指定演员类型；`:Person` 按标签匹配，范围还包括导演和用户。更多解释见[基本概念](../concepts.md)。

## 数据加载行为 {#load-behavior}

在 `ngql` 中执行 `:play movie` 时，客户端会在**您选择的 Schema** 中完成以下操作：

1. 创建图类型 `movie_type`。
2. 创建使用该类型的图 `movie`。
3. 写入内置的点和边。

全文默认使用 `/default_schema`。这个路径是数据库中的命名空间，不是开发机上的文件夹。

`movie` 是图名，`Movie` 是图中的一种点类型，请保留名称和大小写。加载后还需要执行 `SESSION SET GRAPH movie`，让后续查询使用这张图。完整操作只在[首次查询教程](first-query.md#load)维护，其他章节引用该步骤。

!!! warning "不要把加载命令当成可重复执行的刷新命令"

    如果 `movie_type` 或 `movie` 已存在，重新执行 `:play movie` 可能因同名对象而失败。加载中途失败也可能留下图类型、图或部分数据。看到图名不代表数据已经加载完整；不要忽略加载错误，也不要只删除 `movie` 后直接重试，因为 `movie_type` 仍可能存在。

## 数据集使用约定

快速开始先加载数据并运行只读查询。之后阅读 {{gql.name}}、API 或 SDK 示例时，可以继续使用这张 `movie` 图，无需为每个章节重新加载。

学习写入、更新和删除时，应使用该教程明确指定的练习数据或独立 Schema，避免修改后续查询依赖的原始数据。`:play movie` 是 `ngql` 的客户端命令，不是 {{gql.name}} 语句，不能直接作为数据库查询发送到 REST API 或 SDK。

客户端版本不同，内置数据可能发生变化。请使用配套版本的 `ngql`；查询结果不一致时，先核对版本和数据是否被修改，不要仅凭电影名称或总点数判断数据库出错。

## 重新加载数据集 {#reload}

如果加载中断或数据已被修改，先决定是否需要保留原来的数据。下面介绍保留原数据、在另一个 Schema 中重新练习的方法。

在 `ngql` 中执行：

```sql
CREATE SCHEMA /movie_practice
```

`/movie_practice` 是本例使用的新命名空间。如果已经存在，请改用未使用过的名称，并在下一条命令中使用同一名称，不要删除已有 Schema。

```sql
SESSION SET SCHEMA /movie_practice
```

然后按[首次查询的加载步骤](first-query.md#load)执行 `:play movie` 并检查结果。完成后，这份数据位于 `/movie_practice`；后续示例中的 `SESSION SET SCHEMA /default_schema` 应改为 `SESSION SET SCHEMA /movie_practice`。

此方法会额外存储一份数据，不会修复或清除原 Schema 中的内容。如果创建 Schema 失败，应先处理错误，不要继续加载到原来的位置。
