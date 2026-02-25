# Paper/Zotero Skills Installer

Use this one-liner (similar style to internship-scout):

```bash
curl -fsSL https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/install.sh | bash
```

It installs these skills into your OpenClaw workspace:

- ieee-zotero-save
- literature-research-orchestrator
- literature-summary-agent
- pdf
- zotero-library

## Optional flags

```bash
curl -fsSL https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/install.sh | bash -s -- --dest "$HOME/.openclaw/workspace/skills"
```

## Manual install

```bash
git clone https://github.com/sdyzjx/paper-zotero-skills-installer.git
cp -R paper-zotero-skills-installer/skills/* ~/.openclaw/workspace/skills/
```
