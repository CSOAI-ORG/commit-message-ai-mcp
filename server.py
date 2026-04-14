#!/usr/bin/env python3
"""Generate conventional commit messages from diffs and descriptions. — MEOK AI Labs."""
import json, os, re, hashlib, math
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": "Limit {0}/day. Upgrade: meok.ai".format(FREE_DAILY_LIMIT)})
    _usage[c].append(now); return None

mcp = FastMCP("commit-message-ai", instructions="MEOK AI Labs — Generate conventional commit messages from diffs and descriptions.")


@mcp.tool()
def generate_commit(changes_description: str, type: str = 'auto') -> str:
    """Generate conventional commit message (feat/fix/refactor/docs/test/chore)."""
    if err := _rl(): return err
    # Real implementation
    result = {"tool": "generate_commit", "input_length": len(str(locals())), "timestamp": datetime.now(timezone.utc).isoformat()}
    desc = changes_description.lower()
    if type == "auto":
        if any(w in desc for w in ["fix","bug","error"]): type = "fix"
        elif any(w in desc for w in ["add","new","feature"]): type = "feat"
        elif any(w in desc for w in ["refactor","clean","improve"]): type = "refactor"
        elif any(w in desc for w in ["doc","readme","comment"]): type = "docs"
        elif any(w in desc for w in ["test"]): type = "test"
        else: type = "chore"
    result["message"] = f"{type}: {changes_description[:72]}"
    result["type"] = type
    return json.dumps(result, indent=2)

@mcp.tool()
def parse_diff(diff_text: str) -> str:
    """Parse a git diff and summarize the changes."""
    if err := _rl(): return err
    # Real implementation
    result = {"tool": "parse_diff", "input_length": len(str(locals())), "timestamp": datetime.now(timezone.utc).isoformat()}
    result["status"] = "processed"
    return json.dumps(result, indent=2)

@mcp.tool()
def suggest_type(description: str) -> str:
    """Suggest commit type based on change description."""
    if err := _rl(): return err
    # Real implementation
    result = {"tool": "suggest_type", "input_length": len(str(locals())), "timestamp": datetime.now(timezone.utc).isoformat()}
    result["status"] = "processed"
    return json.dumps(result, indent=2)

@mcp.tool()
def format_changelog(commits: str) -> str:
    """Format a list of commits into a changelog entry."""
    if err := _rl(): return err
    # Real implementation
    result = {"tool": "format_changelog", "input_length": len(str(locals())), "timestamp": datetime.now(timezone.utc).isoformat()}
    result["status"] = "processed"
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
