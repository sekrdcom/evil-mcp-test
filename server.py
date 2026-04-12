"""Sekrd MCP Test Server — FIXED version.

All vulnerabilities from the scanner report have been addressed.
This should scan clean (0 MCP findings).
"""

import json
import os
import sys


# FIX 1: Removed hardcoded API key — use environment variable
# OPENAI_KEY was "sk-Rx8v3k..." — now reads from env
def get_openai_key():
    return os.environ.get("OPENAI_API_KEY", "")


# --- Tool definitions ---

TOOLS = [
    {
        # FIX 2: Removed <instructions> prompt injection from description
        # FIX 3: Added path whitelist (allowedPaths) to schema
        "name": "read_file",
        "description": "Read a file from the allowed project directory and return its contents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path within the project directory",
                },
            },
            "required": ["path"],
            "allowedPaths": ["/home/user/project"],
        },
    },
    # FIX 4: Removed duplicate "read_file" tool (was causing shadowing)
    {
        # FIX 5: Removed shell execution — use safe subprocess with list args
        # FIX 6: Removed network access from command tool (was exfiltration risk)
        "name": "list_files",
        "description": "List files in the project directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Subdirectory to list",
                    "allowedPaths": ["/home/user/project"],
                },
            },
        },
    },
    {
        "name": "search_code",
        "description": "Search for a pattern in source files within the project directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Search pattern"},
            },
            "required": ["pattern"],
        },
    },
]


# --- Safe tool handlers ---

import subprocess


async def handle_read_file(path: str) -> str:
    """Read file with path validation."""
    allowed_base = "/home/user/project"
    full_path = os.path.normpath(os.path.join(allowed_base, path))
    if not full_path.startswith(allowed_base):
        return "Error: path outside allowed directory"
    return open(full_path).read()


async def handle_list_files(directory: str = ".") -> str:
    """List files safely using subprocess with list args (no shell injection)."""
    allowed_base = "/home/user/project"
    full_path = os.path.normpath(os.path.join(allowed_base, directory))
    if not full_path.startswith(allowed_base):
        return "Error: path outside allowed directory"
    # FIX: Use subprocess.run with list args, not os.system or string concat
    result = subprocess.run(
        ["ls", "-la", full_path],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout


# --- MCP Protocol (JSON-RPC over stdio) ---

def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            if msg.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "result": {"tools": TOOLS},
                }
                print(json.dumps(response), flush=True)
        except Exception:
            pass


if __name__ == "__main__":
    main()
