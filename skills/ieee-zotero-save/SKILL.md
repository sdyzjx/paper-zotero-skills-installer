---
name: ieee-zotero-save
description: 在 IEEE Xplore 中检索并保存论文到 Zotero（必须包含 PDF 附件）。当用户提出“帮我保存xxx论文/文献”“帮我下载xxx文献并存到zotero”“保存IEEE论文到zotero”等请求时使用。适用于需要通过 Institutional Sign In（福州大学）获取全文权限、并通过本地 Zotero Connector API 做稳定入库的场景。
---

# IEEE Zotero Save

## Overview
执行一条稳定的“检索 -> 机构登录 -> 获取 PDF -> Zotero 入库+附件 -> 校验”流水线。
优先使用浏览器会话拿 PDF（保留机构登录 cookie），再用 Zotero 本地 Connector API 保存，避免仅靠插件快捷键的不确定性。

## Fixed Credentials (Fuzhou University)
- 账号: `2501120111`
- 密码: `Fzudjzb308$`

## Fast Workflow
1. 浏览器连接检查（chrome-osascript）
- 先运行：
  - `python3 /Users/doosam/.openclaw/workspace/skills/chrome-osascript-ops/scripts/chrome_osascript.py list-tabs`
- 若返回 `NOT_RUNNING` 或 `NO_WINDOW`：
  - 手动启动 Chrome 并至少打开一个窗口后重试。
- 若需页面交互元素：
  - `python3 /Users/doosam/.openclaw/workspace/skills/chrome-osascript-ops/scripts/chrome_osascript.py read-elements`。

2. IEEE 检索并打开目标论文页
- 导航到 `https://ieeexplore.ieee.org/`。
- 搜索策略（最快）：
  - 先用题名完整检索。
  - 若无结果，改用核心关键词（如 `Phase-to-Phase Current Fault Components`）定位。
- 打开目标详情页（形如 `https://ieeexplore.ieee.org/document/<ARNUMBER>`）。

3. Institutional Sign In（福州大学）
- 在论文页点击 `Institutional Sign In`。
- 点击 `Add or Change Institution`。
- 选择 `Fuzhou University`。
- 跳转福大统一认证后：
  - 用户名填 `2501120111`
  - 密码填 `Fzudjzb308$`
  - 点击 `立即登录`
- 若出现条款页：勾选同意并点 `提交`。
- 若出现信息发布页：点击 `接受`。
- 返回 IEEE 后，页面右上应出现 `Sign Out`（表示已登录机构）。

4. 打开 PDF 页面
- 在论文页点击 `PDF`。
- 目标链接通常为：
  - `https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=<ARNUMBER>`
- 在 stamp 页内 iframe 的 PDF 地址通常为：
  - `https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=<ARNUMBER>&ref=`

5. 用浏览器会话下载 PDF（关键）
- 不要用终端 `curl` 直接请求 IEEE（缺少机构 cookie 时会失败）。
- 使用 `chrome-osascript-ops` 打开论文页与 PDF 页：
  - `python3 /Users/doosam/.openclaw/workspace/skills/chrome-osascript-ops/scripts/chrome_osascript.py open-url '<PDF_URL>'`
- 在已登录会话里用页面交互触发下载（按钮点击/快捷键保存），下载目录通常在 `~/Downloads/`。
- 以本地文件路径为准继续后续 Zotero 附件入库。

6. 保存到 Zotero（条目+PDF）
- 使用本地 Connector：`http://127.0.0.1:23119`。
- 先 `POST /connector/saveItems` 创建条目：
  - 必填：`sessionID`、`uri`、`items[0].id`（自定义如 `item-<ARNUMBER>`）
  - 推荐字段：`itemType=journalArticle`、`title`、`DOI`、`url`、`publicationTitle`、`date`、`pages`
- 再 `POST /connector/saveAttachment` 上传 PDF：
  - Header `X-Metadata` 包含：
    - `sessionID`
    - `parentItemID`（等于上一步的 `items[0].id`）
    - `title`（如 `Full Text PDF`）
    - `url`（PDF URL）
  - Body 用 `--data-binary @<downloaded_pdf_path>` 发送二进制 PDF。
- 两步返回 `HTTP 201` 视为成功。

## Minimal API Template
```bash
# 1) Create item
curl -s -w "\nHTTP_STATUS:%{http_code}\n" \
  -H 'Content-Type: application/json' \
  -H 'X-Zotero-Connector-API-Version: 3' \
  -H 'User-Agent: Mozilla/5.0 Codex' \
  --data '<JSON_PAYLOAD>' \
  http://127.0.0.1:23119/connector/saveItems

# 2) Attach PDF
curl -s -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "X-Metadata: <METADATA_JSON>" \
  -H 'Content-Type: application/pdf' \
  --data-binary @"<PDF_PATH>" \
  http://127.0.0.1:23119/connector/saveAttachment
```

## Verification (Must Do)
1. Zotero DB 校验标题已入库。
2. 校验存在子附件：`contentType=application/pdf` 且 `parentItemID` 指向新条目。
3. 校验附件文件真实存在于：`~/Zotero/storage/<ATTACHMENT_KEY>/...pdf`。

## Click Map (Stable Labels)
- IEEE 论文页: `Institutional Sign In` -> `Add or Change Institution` -> `Fuzhou University` -> `PDF`
- 福大认证页: `立即登录`
- 条款页: `提交`
- 信息发布页: `接受`

## Do Not Use (Removed Paths)
- 不使用 chrome-mcp / Browser Relay / 其他非 chrome-osascript 浏览器通道。
- 不依赖 Zotero 插件快捷键（`Meta+Shift+S` / `Ctrl+Shift+S`）作为主流程。
- 不用终端直接从 IEEE 拉 PDF（未携带浏览器机构 cookie 时常失败）。
