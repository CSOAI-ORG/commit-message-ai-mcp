#!/usr/bin/env python3
"""Generate conventional commit messages from diffs and descriptions. — MEOK AI Labs."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, re
from datetime import datetime, timezone
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

COMMIT_TYPES = {
    "feat": {"description": "A new feature", "semver": "minor", "changelog": "Features"},
    "fix": {"description": "A bug fix", "semver": "patch", "changelog": "Bug Fixes"},
    "docs": {"description": "Documentation only changes", "semver": None, "changelog": "Documentation"},
    "style": {"description": "Code style changes (formatting, semicolons)", "semver": None, "changelog": "Styles"},
    "refactor": {"description": "Code refactoring without feature/fix", "semver": None, "changelog": "Refactoring"},
    "perf": {"description": "Performance improvements", "semver": "patch", "changelog": "Performance"},
    "test": {"description": "Adding or fixing tests", "semver": None, "changelog": "Tests"},
    "build": {"description": "Build system or dependencies", "semver": None, "changelog": "Build"},
    "ci": {"description": "CI configuration changes", "semver": None, "changelog": "CI"},
    "chore": {"description": "Other changes (no src/test)", "semver": None, "changelog": "Chores"},
    "revert": {"description": "Reverts a previous commit", "semver": "patch", "changelog": "Reverts"},
}

TYPE_KEYWORDS = {
    "fix": ["fix", "bug", "error", "crash", "issue", "patch", "resolve", "correct", "repair"],
    "feat": ["add", "new", "feature", "implement", "create", "introduce", "support"],
    "refactor": ["refactor", "restructure", "clean", "improve", "simplify", "reorganize", "extract"],
    "docs": ["doc", "readme", "comment", "documentation", "guide", "wiki", "changelog"],
    "test": ["test", "spec", "coverage", "assert", "mock", "fixture"],
    "perf": ["perf", "performance", "optimize", "speed", "fast", "cache", "lazy"],
    "style": ["style", "format", "lint", "whitespace", "indent", "semicolon"],
    "ci": ["ci", "pipeline", "workflow", "deploy", "github actions", "jenkins"],
    "build": ["build", "dependency", "package", "webpack", "vite", "rollup", "npm", "pip"],
    "chore": ["chore", "misc", "update", "bump", "release"],
}

SCOPES_BY_FILE_PATTERN = {
    r"auth|login|session|password": "auth",
    r"api|endpoint|route|controller": "api",
    r"ui|component|view|page|template": "ui",
    r"db|migration|model|schema|query": "db",
    r"test|spec|fixture": "test",
    r"config|setting|env": "config",
    r"docker|k8s|deploy|ci": "infra",
    r"doc|readme|changelog": "docs",
}


def _detect_type(text: str) -> str:
    text_lower = text.lower()
    scores = defaultdict(int)
    for commit_type, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[commit_type] += 1
    if scores:
        return max(scores, key=scores.get)
    return "chore"


def _detect_scope(text: str) -> str:
    text_lower = text.lower()
    for pattern, scope in SCOPES_BY_FILE_PATTERN.items():
        if re.search(pattern, text_lower):
            return scope
    return ""


def _is_breaking(text: str) -> bool:
    indicators = ["breaking", "BREAKING CHANGE", "incompatible", "remove api",
                   "drop support", "migration required", "not backward"]
    return any(ind.lower() in text.lower() for ind in indicators)


@mcp.tool()
def generate_commit_message(changes_description: str, commit_type: str = "auto",
                             scope: str = "", breaking: bool = False, api_key: str = "") -> str:
    """Generate a conventional commit message from a description. Auto-detects type, scope, and breaking changes."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    detected_type = commit_type if commit_type != "auto" else _detect_type(changes_description)
    detected_scope = scope or _detect_scope(changes_description)
    is_breaking = breaking or _is_breaking(changes_description)

    subject = changes_description.strip().split("\n")[0][:72]
    if subject[0:1].isupper():
        subject = subject[0].lower() + subject[1:]
    subject = subject.rstrip(".")

    scope_part = f"({detected_scope})" if detected_scope else ""
    bang = "!" if is_breaking else ""
    message = f"{detected_type}{scope_part}{bang}: {subject}"

    body_lines = changes_description.strip().split("\n")[1:]
    body = "\n".join(line.strip() for line in body_lines if line.strip()) if body_lines else ""
    footer = "BREAKING CHANGE: " + subject if is_breaking else ""

    full_message = message
    if body:
        full_message += f"\n\n{body}"
    if footer:
        full_message += f"\n\n{footer}"

    type_info = COMMIT_TYPES.get(detected_type, COMMIT_TYPES["chore"])
    return {
        "message": full_message,
        "subject_line": message,
        "type": detected_type,
        "scope": detected_scope,
        "breaking": is_breaking,
        "semver_impact": "major" if is_breaking else type_info["semver"],
        "changelog_section": type_info["changelog"],
        "char_count": len(message),
        "valid": len(message) <= 72,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def analyze_diff(diff_text: str, api_key: str = "") -> str:
    """Parse a git diff and produce a structured summary with files changed, additions, deletions, and suggested commit type."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    lines = diff_text.split("\n")
    files_changed = []
    additions = 0
    deletions = 0
    current_file = None

    for line in lines:
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[1].strip()
                files_changed.append(current_file)
        elif line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1

    all_files_text = " ".join(files_changed)
    suggested_type = _detect_type(all_files_text + " " + diff_text[:500])
    suggested_scope = _detect_scope(all_files_text)

    file_types = defaultdict(int)
    for f in files_changed:
        ext = os.path.splitext(f)[1] if "." in f else "no_ext"
        file_types[ext] += 1

    size = "small" if additions + deletions < 20 else "medium" if additions + deletions < 100 else "large"

    return {
        "files_changed": files_changed,
        "total_files": len(files_changed),
        "additions": additions,
        "deletions": deletions,
        "net_change": additions - deletions,
        "change_size": size,
        "file_types": dict(file_types),
        "suggested_type": suggested_type,
        "suggested_scope": suggested_scope,
        "is_breaking": _is_breaking(diff_text),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def suggest_type(description: str, api_key: str = "") -> str:
    """Suggest the best conventional commit type for a change description with confidence scoring."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    text_lower = description.lower()
    scores = {}
    for commit_type, keywords in TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[commit_type] = score

    if not scores:
        return {"suggested_type": "chore", "confidence": 0.3, "all_scores": {},
                "available_types": list(COMMIT_TYPES.keys()),
                "description": COMMIT_TYPES["chore"]["description"],
                "timestamp": datetime.now(timezone.utc).isoformat()}

    total = sum(scores.values())
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    best_type = ranked[0][0]
    confidence = round(ranked[0][1] / max(total, 1), 2)

    alternatives = [{"type": t, "score": s, "description": COMMIT_TYPES[t]["description"]}
                     for t, s in ranked[1:4]]

    return {
        "suggested_type": best_type,
        "confidence": min(confidence, 1.0),
        "description": COMMIT_TYPES[best_type]["description"],
        "semver_impact": COMMIT_TYPES[best_type]["semver"],
        "alternatives": alternatives,
        "breaking_detected": _is_breaking(description),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def validate_conventional(message: str, api_key: str = "") -> str:
    """Validate a commit message against the Conventional Commits specification and report issues."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    errors = []
    warnings = []
    lines = message.strip().split("\n")
    subject = lines[0] if lines else ""

    pattern = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_-]+\))?(!)?: .+"
    match = re.match(pattern, subject)
    if not match:
        errors.append("Subject line does not match conventional commit format: type(scope): description")
    else:
        parsed_type = match.group(1)
        if parsed_type not in COMMIT_TYPES:
            errors.append(f"Unknown type '{parsed_type}'. Valid: {', '.join(COMMIT_TYPES.keys())}")

    if len(subject) > 72:
        warnings.append(f"Subject line is {len(subject)} chars (recommended max 72)")
    if len(subject) > 100:
        errors.append(f"Subject line is {len(subject)} chars (hard limit 100)")

    if subject and subject[-1] == ".":
        warnings.append("Subject line should not end with a period")
    if subject and subject.split(": ", 1)[-1][0:1].isupper():
        warnings.append("Description after type should start with lowercase")

    if len(lines) > 1 and lines[1].strip() != "":
        warnings.append("Second line should be blank (separating subject from body)")

    has_breaking_footer = any(line.startswith("BREAKING CHANGE:") for line in lines)
    has_bang = "!" in subject.split(":")[0] if ":" in subject else False

    return {
        "valid": len(errors) == 0,
        "subject": subject,
        "errors": errors,
        "warnings": warnings,
        "parsed": {
            "type": match.group(1) if match else None,
            "scope": (match.group(2) or "").strip("()") if match else None,
            "breaking": has_bang or has_breaking_footer,
            "description": subject.split(": ", 1)[-1] if ": " in subject else subject,
        },
        "char_count": len(subject),
        "body_present": len(lines) > 2,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    mcp.run()
