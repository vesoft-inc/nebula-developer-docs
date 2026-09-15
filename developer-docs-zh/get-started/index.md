# 快速开始

本教程使用 `ngql` 内置的 `movie` 数据集，带您查询“某部电影有哪些演员”。不需要提前掌握 {{gql.name}}，也不需要先手工创建数据。

## 操作流程

1. **[使用 Docker Compose 部署](deploy.md)**：检查 Docker、准备发行文件、启动数据库。
2. **[连接并完成首次查询](first-query.md)**：使用 `ngql` 连接，加载 `movie`，再查询电影及其演员。

如果{{nebula.short_name}}和配套的 `ngql` 容器已经启动，可以直接从第 2 步开始。

## 命令执行环境

教程会在代码块前说明操作位置。两种窗口不要混用：

| 位置 | 用来做什么 | 示例 |
| --- | --- | --- |
| 开发机终端 | 检查 Docker、管理容器、启动 `ngql` | `docker compose version` |
| `ngql` 的交互窗口 | 向数据库发送 {{gql.name}} 语句 | `RETURN 1 AS result` |

命令中的 `<名称>` 是需要替换的占位符，不要把尖括号原样输入。查询示例中的 `movie` 是实际使用的图名，无需替换。`:play movie` 只在 `ngql` 中执行，不是通用的 {{gql.name}} 语句。

## 完成标准

当您查到编号为 `3` 的电影 Shadows in Paradise，并沿着参演关系查到它的演员时，就完成了这次练习。教程会提供预期结果，以及重新连接和重复练习时的处理方式。

[示例数据集](dataset.md)统一说明数据模型和加载行为。后续 {{gql.name}}、API 和 SDK 示例沿用这份数据，不必为每个章节重新加载。

**下一步：[使用 Docker Compose 部署 →](deploy.md)**
