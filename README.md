# Commit Message AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Generate conventional commit messages from diffs and descriptions

## Installation

```bash
pip install commit-message-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `generate_commit`
Generate conventional commit message (feat/fix/refactor/docs/test/chore) with auto-detection.

**Parameters:**
- `changes_description` (str): Description of changes
- `type` (str): Commit type or 'auto' for auto-detection

### `parse_diff`
Parse a git diff and summarize the changes.

**Parameters:**
- `diff_text` (str): Git diff text

### `suggest_type`
Suggest commit type based on change description.

**Parameters:**
- `description` (str): Change description

### `format_changelog`
Format a list of commits into a changelog entry.

**Parameters:**
- `commits` (str): Commit messages

## Authentication

Free tier: 30 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
