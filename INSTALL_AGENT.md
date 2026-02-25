# Install paper-zotero-skills

Follow these steps to install the paper/Zotero skill bundle into your OpenClaw workspace.

## ⚠️ Platform Notice

Some skills in this bundle have platform-specific dependencies:

| Skill | macOS | Linux | Windows |
|---|---|---|---|
| `ieee-zotero-save` | ✅ Full support | ⚠️ See below | ❌ Not supported |
| `pdf` | ✅ Full support | ✅ Full support | ⚠️ See below |
| `zotero-library` | ✅ Full support | ✅ Full support | ⚠️ See below |
| `literature-summary-agent` | ✅ Full support | ✅ Full support | ⚠️ See below |
| `literature-research-orchestrator` | ✅ Full support | ✅ Full support | ⚠️ See below |

**If the user is on Linux:**
- `ieee-zotero-save` uses `chrome-osascript-ops` for browser control, which requires macOS `osascript`.
- Ask the user if they'd like to adapt the skill using a Playwright or Selenium-based browser controller instead.
- All other skills work on Linux without modification.

**If the user is on Windows:**
- Inform the user that this bundle is not tested on Windows.
- Path separators and shell scripts (`.sh`) may need adaptation.
- Recommend using WSL2 as a compatibility layer.

## Steps

### 1. Check prerequisites

```bash
# Python 3.8+
python3 --version

# For pdf skill: pdftoppm (poppler)
which pdftoppm || echo "missing: install with 'brew install poppler' (macOS) or 'apt install poppler-utils' (Linux)"

# For literature-summary-agent: LaTeX
which latexmk || echo "missing: install MacTeX (macOS) or texlive-full (Linux)"

# For ieee-zotero-save: check env vars are set
[ -n "$IEEE_INSTITUTION_USERNAME" ] && echo "✅ IEEE_INSTITUTION_USERNAME set" || echo "⚠️  IEEE_INSTITUTION_USERNAME not set — add to ~/.zshrc"
[ -n "$IEEE_INSTITUTION_PASSWORD" ] && echo "✅ IEEE_INSTITUTION_PASSWORD set" || echo "⚠️  IEEE_INSTITUTION_PASSWORD not set — add to ~/.zshrc"
```

### 2. Set credentials (ieee-zotero-save only)

Add to your `~/.zshrc` (or `~/.bashrc`):

```bash
export IEEE_INSTITUTION_USERNAME="your_student_id"
export IEEE_INSTITUTION_PASSWORD="your_password"
```

Then reload: `source ~/.zshrc`

### 3. Install the skills

**Option A — curl installer (recommended):**

```bash
curl -fsSL https://raw.githubusercontent.com/sdyzjx/paper-zotero-skills-installer/main/install.sh | bash
```

**Option B — git clone (for development/customization):**

```bash
git clone https://github.com/sdyzjx/paper-zotero-skills-installer.git /tmp/paper-zotero-skills-installer
cp -R /tmp/paper-zotero-skills-installer/skills/* ~/.openclaw/workspace/skills/
```

### 4. Confirm installation

```bash
for skill in ieee-zotero-save literature-research-orchestrator literature-summary-agent pdf zotero-library; do
  [ -f "$HOME/.openclaw/workspace/skills/$skill/SKILL.md" ] \
    && echo "✅ $skill" \
    || echo "❌ $skill — missing"
done
```

### 5. Verify Zotero is running

```bash
curl -s http://127.0.0.1:23119/connector/ping | python3 -m json.tool 2>/dev/null \
  && echo "✅ Zotero Connector reachable" \
  || echo "❌ Zotero not running — open Zotero desktop app first"
```

## Requirements

| Dependency | Required by | Install |
|---|---|---|
| Python 3.8+ | all skills | pre-installed on macOS/Linux |
| `pdftoppm` (poppler) | `pdf` | `brew install poppler` / `apt install poppler-utils` |
| LaTeX (`latexmk`) | `literature-summary-agent` | `brew install --cask mactex` / `apt install texlive-full` |
| Zotero desktop app | `ieee-zotero-save`, `zotero-library` | https://www.zotero.org/download/ |
| Google Chrome + osascript | `ieee-zotero-save` | macOS only |
| `IEEE_INSTITUTION_USERNAME` env var | `ieee-zotero-save` | see Step 2 |
| `IEEE_INSTITUTION_PASSWORD` env var | `ieee-zotero-save` | see Step 2 |

## Usage

Once installed, trigger skills by telling your agent:

- 「帮我保存这篇 IEEE 论文到 Zotero」
- 「总结这篇文献」
- 「帮我调研 xxx 方向的文献」
- 「查看我的 Zotero 论文库」
- 「读这个 PDF」
