---
hide:
  - toc
---
<div class="de-breadcrumb">{{nebula.name}}</div>
<div class="de-intro" markdown>
# {{nebula.name}}文档

从内置的 `movie` 数据集开始学习图数据库：查询一部电影，再找到参演它的演员。通过 Docker Compose 启动单机开发环境，无需申请产品 License 文件。
</div>

## 快速开始 {#quick-start}

[进入快速开始 →](get-started/index.md){ .md-button .md-button--primary }

按照教程准备环境、连接数据库、加载数据并完成查询。无需提前掌握 {{gql.name}}，也无需手工创建服务组。

!!! note "预览文档"

    教程使用 `nightly` 镜像，尚未完成完整流程验证。开始前请检查[部署前提](get-started/deploy.md)。文档菜单中的版本号不能作为产品发布或兼容性的依据。

## 文档导览

<div class="de-grid" markdown>
<div class="de-card" markdown>
<div class="de-number">01 / INTRODUCTION</div>
### {{nebula.short_name}}简介
了解{{nebula.short_name}}能做什么、使用限制，以及点、边和图的含义。
<div class="de-card-bottom" markdown>
[阅读产品介绍 →](introduction.md)
</div>
</div>
<div class="de-card" markdown>
<div class="de-number">02 / DEPLOY</div>
### 启动开发环境
下载 Docker Compose 文件，设置自己的登录密码，启动配套容器。
<div class="de-card-bottom" markdown>
[开始部署 →](get-started/deploy.md)
</div>
</div>
<div class="de-card" markdown>
<div class="de-number">03 / FIRST QUERY</div>
### 完成首次查询
加载内置的 `movie` 数据集，查询电影及其演员。
<div class="de-card-bottom" markdown>
[连接并查询 →](get-started/first-query.md)
</div>
</div>
</div>

## 使用限制 {#edition-compare}

{{nebula.short_name}}提供固定的单机配置，面向学习、开发与测试。请阅读[功能与限制](limitations.md)，确认它符合您的需求。

## 问题反馈与文档贡献 {#contribute-section}

启动失败时，先查看[部署问题排查](get-started/deploy.md#troubleshooting)；查询失败时，查看[查询问题排查](get-started/first-query.md#troubleshooting)。

发现文档错误或缺少说明，欢迎按[贡献指南](contributing.md)提交反馈。您也可以[通过 AI 阅读文档](ai.md)。
