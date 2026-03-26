#!/usr/bin/env python3
"""Manage the POC session audit trail.

Provides subcommands for initializing, recording, exporting, and summarizing
audit log entries. Audit data is stored as JSON files in a temp directory,
with one file per session.

Subcommands:
  init    - Initialize a new audit log for a session
  log     - Add an entry to an existing audit log
  export  - Export the complete audit log as Markdown
  summary - Print summary statistics for a session

Timestamps are in UTC ISO 8601 format.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Directory for audit log files
AUDIT_DIR = Path(tempfile.gettempdir()) / "entra-poc-audit"

# Valid action types
VALID_ACTIONS = {
    "mcp-read",
    "mcp-write",
    "configuration",
    "validation",
    "prerequisite-check",
    "documentation",
    "script-generation",
    "recommendation",
    "mode-change",
    "error",
    "note",
}


def _get_log_path(session_id: str) -> Path:
    """Return the file path for a session's audit log."""
    # Sanitize session ID for use as filename
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)
    return AUDIT_DIR / f"audit-{safe_id}.json"


def _utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_log(session_id: str) -> dict[str, Any]:
    """Load an existing audit log. Exits if not found."""
    path = _get_log_path(session_id)
    if not path.exists():
        print(
            f'Error: No audit log found for session "{session_id}". '
            "Run `init` first.",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error: Failed to read audit log: {exc}", file=sys.stderr)
        sys.exit(2)


def _save_log(session_id: str, data: dict[str, Any]) -> None:
    """Save an audit log to disk."""
    path = _get_log_path(session_id)
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"Error: Failed to write audit log: {exc}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Subcommand: init
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new audit log for a session."""
    session_id = args.session_id
    path = _get_log_path(session_id)

    # Create audit directory if needed
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    if path.exists() and not args.force:
        print(
            f'Error: Audit log already exists for session "{session_id}". '
            "Use --force to overwrite.",
            file=sys.stderr,
        )
        sys.exit(1)

    now = _utc_now()
    data: dict[str, Any] = {
        "session_id": session_id,
        "mode": args.mode,
        "tenant": args.tenant or None,
        "created": now,
        "updated": now,
        "entries": [],
    }

    _save_log(session_id, data)
    print(f"Audit log initialized for session {session_id}")
    print(f"  Mode: {args.mode}")
    if args.tenant:
        print(f"  Tenant: {args.tenant}")
    print(f"  File: {path}")


# ---------------------------------------------------------------------------
# Subcommand: log
# ---------------------------------------------------------------------------

def cmd_log(args: argparse.Namespace) -> None:
    """Add an entry to an existing audit log."""
    session_id = args.session_id
    data = _load_log(session_id)

    # Validate action type (allow custom types with a warning)
    action = args.action
    if action not in VALID_ACTIONS:
        print(
            f'Warning: Action type "{action}" is not a recognized type. '
            f"Known types: {', '.join(sorted(VALID_ACTIONS))}",
            file=sys.stderr,
        )

    now = _utc_now()
    entry: dict[str, Any] = {
        "timestamp": now,
        "action": action,
        "component": args.component,
        "details": args.details,
    }

    # Optional fields
    if args.mcp_call:
        entry["mcp_call"] = args.mcp_call
    if args.result:
        entry["result"] = args.result
    if args.rollback:
        entry["rollback"] = args.rollback

    data["entries"].append(entry)
    data["updated"] = now

    _save_log(session_id, data)

    entry_num = len(data["entries"])
    print(f"Entry #{entry_num} added to session {session_id}")
    print(f"  Action: {action}")
    print(f"  Component: {args.component}")


# ---------------------------------------------------------------------------
# Subcommand: export
# ---------------------------------------------------------------------------

def cmd_export(args: argparse.Namespace) -> None:
    """Export the complete audit log as Markdown."""
    session_id = args.session_id
    data = _load_log(session_id)

    report = _generate_export(data)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Audit log exported to {args.output}", file=sys.stderr)
    else:
        print(report)


def _generate_export(data: dict[str, Any]) -> str:
    """Generate the full Markdown audit log export."""
    lines: list[str] = []
    entries = data["entries"]

    # Title and metadata
    lines.append("# POC Session Audit Log")
    lines.append("")
    lines.append(f"**Session ID:** {data['session_id']}  ")
    lines.append(f"**Operation Mode:** {data['mode']}  ")
    if data.get("tenant"):
        lines.append(f"**Tenant:** {data['tenant']}  ")
    lines.append(f"**Started:** {data['created']}  ")
    lines.append(f"**Last Updated:** {data['updated']}  ")
    lines.append(f"**Total Entries:** {len(entries)}")
    lines.append("")

    if not entries:
        lines.append("*No audit entries recorded.*")
        lines.append("")
        return "\n".join(lines)

    # Summary statistics
    lines.append("## Summary")
    lines.append("")
    action_counts: dict[str, int] = {}
    component_set: set[str] = set()
    for entry in entries:
        action = entry["action"]
        action_counts[action] = action_counts.get(action, 0) + 1
        component_set.add(entry["component"])

    lines.append("| Action Type | Count |")
    lines.append("|-------------|-------|")
    for action in sorted(action_counts.keys()):
        lines.append(f"| {action} | {action_counts[action]} |")
    lines.append("")
    lines.append(f"**Components touched:** {len(component_set)}")
    lines.append("")

    # Timeline
    lines.append("## Audit Trail")
    lines.append("")
    lines.append("| # | Timestamp | Action | Component | Details |")
    lines.append("|---|-----------|--------|-----------|---------|")

    for i, entry in enumerate(entries, 1):
        ts = entry["timestamp"]
        action = entry["action"]
        component = entry["component"]
        details = entry["details"]
        # Truncate long details for the table
        if len(details) > 80:
            details_display = details[:77] + "..."
        else:
            details_display = details
        # Escape pipe characters in details
        details_display = details_display.replace("|", "\\|")
        lines.append(f"| {i} | {ts} | {action} | {component} | {details_display} |")

    lines.append("")

    # Detailed entries (full information for each entry)
    lines.append("## Detailed Entries")
    lines.append("")

    for i, entry in enumerate(entries, 1):
        lines.append(f"### Entry {i}")
        lines.append("")
        lines.append(f"- **Timestamp:** {entry['timestamp']}")
        lines.append(f"- **Action:** {entry['action']}")
        lines.append(f"- **Component:** {entry['component']}")
        lines.append(f"- **Details:** {entry['details']}")
        if entry.get("mcp_call"):
            lines.append(f"- **MCP Call:** `{entry['mcp_call']}`")
        if entry.get("result"):
            lines.append(f"- **Result:** {entry['result']}")
        if entry.get("rollback"):
            lines.append(f"- **Rollback:** {entry['rollback']}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "*Audit log exported by `audit-logger.py`. "
        "This log is part of the POC documentation deliverables.*"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Subcommand: summary
# ---------------------------------------------------------------------------

def cmd_summary(args: argparse.Namespace) -> None:
    """Print summary statistics for a session."""
    session_id = args.session_id
    data = _load_log(session_id)
    entries = data["entries"]

    print(f"Session: {data['session_id']}")
    print(f"Mode: {data['mode']}")
    if data.get("tenant"):
        print(f"Tenant: {data['tenant']}")
    print(f"Started: {data['created']}")
    print(f"Updated: {data['updated']}")
    print(f"Entries: {len(entries)}")
    print()

    if not entries:
        print("No entries recorded yet.")
        return

    # Action breakdown
    action_counts: dict[str, int] = {}
    component_counts: dict[str, int] = {}
    mcp_calls = 0
    errors = 0

    for entry in entries:
        action = entry["action"]
        action_counts[action] = action_counts.get(action, 0) + 1
        comp = entry["component"]
        component_counts[comp] = component_counts.get(comp, 0) + 1
        if entry.get("mcp_call"):
            mcp_calls += 1
        if action == "error":
            errors += 1

    print("Action breakdown:")
    for action in sorted(action_counts.keys()):
        print(f"  {action}: {action_counts[action]}")
    print()

    print("Components touched:")
    for comp in sorted(component_counts.keys()):
        print(f"  {comp}: {component_counts[comp]} entries")
    print()

    print(f"MCP calls: {mcp_calls}")
    print(f"Errors: {errors}")

    # Duration (if more than one entry)
    if len(entries) >= 2:
        try:
            first = datetime.fromisoformat(entries[0]["timestamp"].replace("Z", "+00:00"))
            last = datetime.fromisoformat(entries[-1]["timestamp"].replace("Z", "+00:00"))
            duration = last - first
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                print(f"Duration: {hours}h {minutes}m {seconds}s")
            elif minutes > 0:
                print(f"Duration: {minutes}m {seconds}s")
            else:
                print(f"Duration: {seconds}s")
        except (ValueError, KeyError):
            pass  # Skip duration if timestamps can't be parsed


# ---------------------------------------------------------------------------
# Argument parser setup
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Manage the POC session audit trail.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new audit log")
    p_init.add_argument(
        "--session-id", required=True, help="Unique session identifier"
    )
    p_init.add_argument(
        "--mode",
        required=True,
        choices=["guidance-only", "read-only", "read-write"],
        help="Operation mode for the session",
    )
    p_init.add_argument(
        "--tenant", default=None, help="Tenant domain (optional)"
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing audit log for this session",
    )

    # log
    p_log = subparsers.add_parser("log", help="Add an entry to the audit log")
    p_log.add_argument(
        "--session-id", required=True, help="Session identifier"
    )
    p_log.add_argument(
        "--action",
        required=True,
        help=(
            "Action type. Recognized types: "
            + ", ".join(sorted(VALID_ACTIONS))
        ),
    )
    p_log.add_argument(
        "--component", required=True, help="Component or feature name"
    )
    p_log.add_argument(
        "--details", required=True, help="Description of the action"
    )
    p_log.add_argument(
        "--mcp-call", default=None, help="MCP Server call made (if any)"
    )
    p_log.add_argument(
        "--result", default=None, help="Result or outcome of the action"
    )
    p_log.add_argument(
        "--rollback", default=None, help="Rollback instructions (if applicable)"
    )

    # export
    p_export = subparsers.add_parser(
        "export", help="Export audit log as Markdown"
    )
    p_export.add_argument(
        "--session-id", required=True, help="Session identifier"
    )
    p_export.add_argument(
        "--output", default=None, help="Output file path (default: stdout)"
    )

    # summary
    p_summary = subparsers.add_parser(
        "summary", help="Print summary statistics"
    )
    p_summary.add_argument(
        "--session-id", required=True, help="Session identifier"
    )

    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(2)

    dispatch = {
        "init": cmd_init,
        "log": cmd_log,
        "export": cmd_export,
        "summary": cmd_summary,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
