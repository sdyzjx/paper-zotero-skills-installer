# paper-zotero-skills-installer

Packaged OpenClaw skills for paper reading, Zotero workflows, and literature orchestration.

## Skills Included

| Skill | Description |
|---|---|
| `ieee-zotero-save` | Search IEEE Xplore, sign in via institution, save paper + PDF to Zotero |
| `pdf` | Vision-first PDF reading (PDF → PNG → page-by-page analysis) |
| `zotero-library` | Browse and search your local Zotero library via SQL |
| `literature-summary-agent` | Deep-read a single paper and generate a LaTeX summary report |
| `literature-research-orchestrator` | End-to-end multi-paper literature research pipeline |

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/install.sh | bash
```

> **Note:** `ieee-zotero-save` requires institutional credentials via environment variables.
> See [INSTALL_AGENT.md](INSTALL_AGENT.md) for setup instructions — **never hardcode credentials in skill files**.

## Via OpenClaw Agent

Send this to your agent:

```
Fetch https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/INSTALL_AGENT.md and follow the instructions to install the paper-zotero skills.
```

## Requirements

- macOS (full support) or Linux (partial — see [INSTALL_AGENT.md](INSTALL_AGENT.md))
- Python 3.8+
- Zotero desktop app with local Connector running
- For `ieee-zotero-save`: Google Chrome + `IEEE_INSTITUTION_USERNAME` / `IEEE_INSTITUTION_PASSWORD` env vars
- For `pdf`: `pdftoppm` (poppler)
- For `literature-summary-agent`: LaTeX (`latexmk`)

See [INSTALL_AGENT.md](INSTALL_AGENT.md) for full prerequisites and platform compatibility details.
