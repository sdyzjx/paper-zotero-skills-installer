# Troubleshooting (literature-summary-agent)

## 1) PDF编译成功但内容空泛/占位符未替换
症状：PDF只有模板结构，正文缺失或仍有“待补充/TODO/{{...}}”。

处理：
1. 先执行 QA 门禁：
```bash
python3 /Users/doosam/.openclaw/workspace/skills/literature-summary-agent/scripts/qa_summary_tex.py <summary_dir>/main.tex
```
2. 若失败，按报错修复对应段落（尤其第一层/第二层/第三层）。
3. 通过后再编译。

## 2) 系统已装MacTeX但提示 latexmk/xelatex 不存在
症状：`which latexmk` 在某些shell里为空。

根因：非登录shell的 PATH 没有 `/Library/TeX/texbin`。

处理：
```bash
/Users/doosam/.openclaw/workspace/skills/literature-summary-agent/scripts/compile_tex.sh <summary_dir>
```
该脚本内部已处理 PATH。

## 3) 结构对了但证据层太泛
症状：有“问题/创新/结论”，但缺少实验设置和数字。

处理：证据层必须补齐：
- 实验设置（数据集/硬件/训练参数）
- 主结果（至少1组可核对数值）
- 基线对比
- 消融结论

## 4) 交付前最终检查
- `main.tex` 无占位符
- `deep_reading.md` 完整
- `refine_pass.md` 已记录 PASS
- `main.pdf` 可打开且内容非空
