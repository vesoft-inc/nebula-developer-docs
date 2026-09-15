---
hide:
  - toc
---
<div class="de-breadcrumb">nebula-docs / developer-edition / overview</div>
<div class="de-intro" markdown>
# 悦数图数据库开发版文档

面向开发者的单机图数据库环境，用于学习 GQL、探索关联数据与验证应用集成。通过 Docker Compose 部署，无需申请或配置产品 License 文件。
</div>

## 开始使用开发版 {#quick-start}

<div class="de-terminal">
<div class="de-terminal-bar"><span>DEVELOPER EDITION / 文档预览</span><span>部署教程准备中</span></div>
<div class="de-terminal-lines">01  了解产品定位与单机使用边界
02  Docker Compose 部署指南 · 即将提供
03  连接数据库并执行首次查询 · 即将提供</div>
</div>

<div class="de-grid" markdown>
<div class="de-fact" markdown>
**Docker Compose**
唯一支持的部署方式
</div>
<div class="de-fact" markdown>
**单机 · 单服务组**
预先初始化服务组，只能添加一个 Host
</div>
<div class="de-fact" markdown>
**文档框架预览**
尚不对应正式发布的产品镜像
</div>
</div>

## 核心开发任务

<div class="de-grid" markdown>
<div class="de-card" markdown>
<div class="de-number">01 / GET STARTED</div>
### 认识开发版
先了解开发版的产品定位、使用范围和文档内容，部署步骤将在下一阶段加入。
<div class="de-card-bottom" markdown>
<span class="de-pending">产品概览</span>
[阅读介绍 →](introduction.md)
</div>
</div>
<div class="de-card" markdown>
<div class="de-number">02 / GQL & API</div>
### 查阅语法与接口
GQL 参考和 REST API 将按开发版对应版本提供。当前尚未导入公共参考内容。
<div class="de-card-bottom" markdown>
<span class="de-pending">参考内容准备中</span>
[了解版本规则 →](versions.md)
</div>
</div>
<div class="de-card" markdown>
<div class="de-number">03 / SDK & TOOLS</div>
### 连接应用与数据
后续提供 SDK、连接器及 ngql/ngctl 文档。现有公开内容可通过 Markdown 和 AI 索引读取。
<div class="de-card-bottom" markdown>
<span class="de-pending">集成文档准备中</span>
[AI 文档入口 →](ai.md)
</div>
</div>
</div>

## 开发版能力边界 {#edition-compare}

| 评估维度 | 开发版当前范围 | 使用说明 |
| --- | --- | --- |
| 安装部署 | 仅 Docker Compose | 镜像、端口与资源要求随部署指南提供 |
| Meta 与主机 | 单 Meta、单 Host | 不提供多机部署路径 |
| 服务组 | 单 Service Group，提前初始化 | 无需从创建多个服务组开始 |
| Part 与副本 | 单 Part、单副本 | 不支持调整副本数 |
| License 文件 | 无需申请或配置 | 软件使用范围以正式产品条款为准 |
| GQL、API 与 SDK | 文档将在后续加入 | 具体支持范围以对应版本说明为准 |

[查看完整限制说明 →](limitations.md)

## 编辑此文档与参与共建 {#contribute-section}

<div class="de-contribute" markdown>
<div markdown>
**一起完善开发版文档**

文档源码公开维护。发现笔误、缺少说明或示例？欢迎提交修改申请，由维护者审核后发布。
</div>
<div class="de-actions" markdown>
[贡献指南](contributing.md)
[提交文档 Issue ↗](https://github.com/vesoft-inc/nebula-developer-docs/issues)
</div>
</div>
