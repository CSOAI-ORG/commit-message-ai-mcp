<div align="center">

# Commit Message Ai MCP

**MCP server for commit message ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-commit-message-ai-mcp)](https://pypi.org/project/meok-commit-message-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Commit Message Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `generate_commit_message` | Generate a conventional commit message from a description. Auto-detects type, sc |
| `analyze_diff` | Parse a git diff and produce a structured summary with files changed, additions, |
| `suggest_type` | Suggest the best conventional commit type for a change description with confiden |
| `validate_conventional` | Validate a commit message against the Conventional Commits specification and rep |

## Installation

```bash
pip install meok-commit-message-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "commit-message-ai": {
      "command": "python",
      "args": ["-m", "meok_commit_message_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
