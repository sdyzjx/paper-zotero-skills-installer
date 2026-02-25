# paper-zotero-skills-installer

一个 OpenClaw Agent Skill 合集，覆盖论文检索、PDF 精读、Zotero 入库与文献综述全流程。

## 功能

- **IEEE 论文入库**：在 IEEE Xplore 检索目标论文，通过机构登录获取全文 PDF，自动保存条目与附件到 Zotero
- **PDF 精读**：将 PDF 逐页渲染为 PNG，逐页视觉分析，输出原文 Markdown 转录（公式、表格、图片均保留）
- **Zotero 库检索**：直接查询本地 `zotero.sqlite`，支持按关键词搜索、浏览分类、读取单篇元数据与附件路径
- **单篇精读报告**：三层 SOP 精读（问题逻辑 / 创新结构 / 验证逻辑），自动生成含公式的 LaTeX 总结报告并编译为 PDF
- **多篇文献调研**：端到端调研流水线，含选题范围确认、检索排序、PDF 获取、逐篇精读、对比综述输出

## 工作流

```
用户请求
  │
  ├─ 保存 IEEE 论文 ──→ ieee-zotero-save
  │                      (检索 → 机构登录 → PDF 下载 → Zotero 入库 → 校验)
  │
  ├─ 读 PDF ──────────→ pdf
  │                      (PDF → PNG → 逐页视觉分析 → Markdown 转录)
  │
  ├─ 查论文库 ─────────→ zotero-library
  │                      (zotero.sqlite 只读查询)
  │
  ├─ 精读单篇 ─────────→ literature-summary-agent
  │                      (Zotero 定位 → SOP 精读 → LaTeX 报告编译)
  │
  └─ 调研方向 ─────────→ literature-research-orchestrator
                         (选题确认 → 检索排序 → PDF 获取 → 逐篇精读 → 综述)
```

## 安装

### 通过 OpenClaw Agent 安装（推荐）

把以下内容发送给你的 agent：

```
Fetch https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/INSTALL_AGENT.md and follow the instructions to install the paper-zotero skills.
```

### 手动安装

```bash
curl -fsSL https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/install.sh | bash
```

或 git clone：

```bash
git clone https://github.com/sdyzjx/paper-zotero-skills-installer.git /tmp/pzsi
cp -R /tmp/pzsi/skills/* ~/.openclaw/workspace/skills/
```

> **凭据安全提示：** `ieee-zotero-save` 需要机构账号，请通过环境变量传入，**不要**在 SKILL.md 或任何文件中硬编码。
> 详见 [INSTALL_AGENT.md](INSTALL_AGENT.md)。

## 使用

直接告诉你的 agent：

- 「帮我保存这篇 IEEE 论文到 Zotero」
- 「读一下这个 PDF」
- 「查看我的 Zotero 论文库」
- 「总结这篇文献」
- 「帮我调研 xxx 方向的文献」

## 依赖

| 依赖 | 用于 | 安装方式 |
|---|---|---|
| Python 3.8+ | 所有 skill | 系统预装 |
| Zotero 桌面版 + Connector | `ieee-zotero-save`、`zotero-library` | [zotero.org/download](https://www.zotero.org/download/) |
| `pdftoppm`（poppler） | `pdf` | `brew install poppler` / `apt install poppler-utils` |
| LaTeX（`latexmk`） | `literature-summary-agent` | `brew install --cask mactex` / `apt install texlive-full` |
| Google Chrome + osascript | `ieee-zotero-save` | macOS only |
| `IEEE_INSTITUTION_USERNAME` | `ieee-zotero-save` | 环境变量，见 [INSTALL_AGENT.md](INSTALL_AGENT.md) |
| `IEEE_INSTITUTION_PASSWORD` | `ieee-zotero-save` | 环境变量，见 [INSTALL_AGENT.md](INSTALL_AGENT.md) |

平台支持：macOS 完整支持；Linux 除 `ieee-zotero-save` 外均支持；Windows 建议使用 WSL2。

## 文件结构

```
paper-zotero-skills-installer/
├── install.sh                              # 一键安装脚本
├── INSTALL_AGENT.md                        # Agent 安装引导（含平台兼容性说明）
├── README.md
└── skills/
    ├── ieee-zotero-save/
    │   ├── SKILL.md                        # Agent 操作指南
    │   └── agents/openai.yaml
    ├── pdf/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── pdf_to_png.py               # PDF → PNG 渲染
    │   │   └── init_pdf_original_md.py     # 初始化转录文件
    │   ├── references/vision-pdf-workflow.md
    │   └── assets/
    ├── zotero-library/
    │   ├── SKILL.md
    │   └── scripts/zotero_db_search.py     # SQLite 只读查询工具
    ├── literature-summary-agent/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── init_summary_project.py     # 初始化报告目录
    │   │   ├── qa_summary_tex.py           # QA 精读脚本
    │   │   └── compile_tex.sh              # LaTeX 编译
    │   ├── assets/summary_template.tex     # LaTeX 报告模板
    │   └── references/
    │       ├── sop.md                      # 三层精读 SOP
    │       └── troubleshooting.md
    └── literature-research-orchestrator/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/
            ├── intake-template.md          # 选题确认模板
            ├── output-contract.md          # 输出格式约定
            └── ranking-profiles.md         # 文献排序策略
```
