# NebulaGraph Database Developer Edition documentation

悦数图数据库开发版公开文档工程。包含中英文首页、认识开发版、Docker Compose 快速开始、首次查询、贡献指南及 AI 文档入口。配套 Compose 文件与不含真实密码的环境变量模板位于各语言的 `get-started/files/`。教程使用 nightly 镜像，尚未完成镜像上的端到端验证；公网镜像获取方式与支持平台仍待确认。开发版目前没有额外的硬件配置要求。GQL、REST API 等公共参考模块尚未导入。当前配置中的 `v5.3.2` 暂时与 `preview` 共用源文件，还不是独立的历史版本快照。

## 本地预览

推荐 Python 3.11 或 3.12。仅使用本仓库，不需要私有仓库或发布凭证。第一次运行：

```sh
make setup
make serve
```

访问：
- 中文：http://127.0.0.1:8001/zh/preview/
- English：http://127.0.0.1:8001/en/preview/

修改 Markdown、`.nav.yml`、配置或主题后会自动重新构建，不需要停止服务。按 `Ctrl+C` 停止。

只预览一种语言可以减少构建量：

```sh
make serve-zh
make serve-en
```

指定其他端口或版本：`make serve-en PORT=8010 VERSION=v5.3.2`。
需要同时检查版本下拉框时运行 `make serve-all`；日常写作无需构建全部历史版本。

## 日常编辑

示例统一使用 ngql 内置的 `movie` 数据集。数据模型和加载注意事项见各语言的 `get-started/dataset.md`，首次加载与查询见 `get-started/first-query.md`。后续 GQL、REST API、SDK 示例沿用同一模型；写操作使用独立练习数据，避免修改其他教程依赖的原始数据。

- 中文：`developer-docs-zh/`
- 英文：`developer-docs-en/`
- 首页：各语言目录的 `index.md`
- 公共 MkDocs 配置：`mkdocs-base.yml`
- 中英文配置：`mkdocs-zh.yml`、`mkdocs-en.yml`
- 导航：各文档目录中的 `.nav.yml`
- 样式、版本和语言控件：`theme/main.html`
- 版本来源：`versions.json`
- 正式中英文网址：`site-urls.json`

网页编辑按钮指向对应源文件。GitHub 登录、fork 和 PR 审核由 GitHub 处理，本地修改须推送后才会反映到 GitHub。

现有 `requirements.txt` 的用户修改保留；新框架使用较小的 `requirements-preview.txt`，无需安装 PDF 或企业版插件。

## 增加大量目录和文档

中文和英文使用相同的相对路径。例如：

```text
developer-docs-zh/gql-reference/match.md
developer-docs-en/gql-reference/match.md
```

新增顶层目录会被根目录的 `.nav.yml` 自动发现。需要调整目录名称或页面顺序时，在新目录中增加自己的 `.nav.yml`：

```yaml
nav:
  - 概述: index.md
  - MATCH: match.md
  - RETURN: return.md
  - "*"
```

结尾的 `"*"` 会自动补充尚未手工排序的新页面。中文和英文分别维护各自的显示名称，但文件路径必须尽量一致。完整贡献步骤见 `CONTRIBUTING.md`。

普通作者只编辑 Markdown 和 `.nav.yml`，不需要修改 `scripts/docs.py`。

## 多版本

为方便首期维护，采用 **同一分支内的版本目录快照**，无需在多个 Git 分支间操作。版本选择菜单只显示真实配置的版本，不用虚构 5.3/5.4 内容来演示。

添加正式版本时：
1. 研发确认产品版本、支持范围及发布内容。
2. 将对应中英文完整文档整理到 `releases/<版本>/zh/` 和 `releases/<版本>/en/`，独立于 preview 内容。
3. 在 `versions.json` 的 versions 数组增加一项，指定 id、双语 title、source 路径和编辑使用的 Git ref。
4. 所有版本保持相同基础页面路径；新增页面同步调整导航。缺失页面时会进入 404。
5. 需要默认展示正式版本时，修改 default。重新构建全部版本。

配置示意（版本号以实际产品为准）：

```json
{
  "id": "5.3",
  "title": {"zh": "5.3", "en": "5.3"},
  "source": {"zh": "releases/5.3/zh", "en": "releases/5.3/en"},
  "ref": "master"
}
```

每个版本输出独立 HTML、搜索索引、Markdown、llms.txt 和 llms-full.txt。
`/zh/latest/` 和 `/en/latest/` 是默认版本首页跳转入口；不提供任意深层 latest 路径。
纠错可以修改既有版本；发布时可创建 Git tag 记录快照。

## 构建与公开发布

```sh
make check
```

结果在 `site/`。默认是预览构建，robots 和页面 noindex 阻止预览站被主动索引。

正式网站采用两个域名，地址记录在 `site-urls.json`。只生成发布文件（不会上传网站）：

```sh
make release
```

| 发布文件目录 | 对应公开地址 |
|---|---|
| `site-production/zh/` 内的全部内容 | `https://yueshu.com.cn/docs-dev/` |
| `site-production/en/` 内的全部内容 | `https://nebula-graph.io/docs-dev/` |

部署时不要把 `zh`、`en` 目录名加入公开路径。例如中文预览版最终位于
`https://yueshu.com.cn/docs-dev/preview/`，英文预览版位于
`https://nebula-graph.io/docs-dev/preview/`。两个站点入口分别跳到默认版本。
语言切换使用跨域绝对地址，保留版本和页面；版本切换仍在当前语言站点内。
`latest/` 仅提供默认版本首页跳转。

本地预览仍输出到 `site/`，保留 `/zh/`、`/en/` 路径；正式构建不会覆盖本地预览。
正式产物应通过正式域名访问，直接在本地打开它会导致语言切换跳到公网。

正式构建的页面使用各自域名的 canonical、站点地图和 AI 索引。
因为文档部署在 `/docs-dev/` 子路径，抓取规则必须由官网根目录的 `/robots.txt` 管理：
请官网维护者确认允许抓取 `/docs-dev/`，并登记语言站点的站点地图索引：
`https://yueshu.com.cn/docs-dev/sitemap.xml` 和
`https://nebula-graph.io/docs-dev/sitemap.xml`。
不要用文档构建产物覆盖官网原有 robots.txt；正式语言产物不生成该文件。

CI 检查本地预览和双域名正式构建，保存预览产物，不自动部署到任何服务器。旧服务器部署工作流已停用。
正式发布前需确认仓库 LICENSE、域名、产品信息以及对应部署教程。未擅自选择文档或软件许可证。

## AI 与搜索

每语言/版本提供 `llms.txt`、`llms-full.txt` 和 `markdown/*.md`，每个正式站点的 `/docs-dev/llms.txt` 提供该语言的版本索引。正式构建使用公开绝对链接和站点地图；官网抓取规则需由官网维护者配置。内容在静态 HTML 中，不依赖运行 JavaScript 获取正文。不能保证特定 AI 平台收录。

## English

Run `make setup`, then `make serve-en`.
The public repository builds independently. Edit `developer-docs-en/` and submit a pull request.
The bilingual introduction and quick start include Compose downloads and a first-query tutorial.
Nightly image access, platform requirements, and end-to-end validation remain to be confirmed.
Shared GQL, REST API, and client reference modules are not included yet.
