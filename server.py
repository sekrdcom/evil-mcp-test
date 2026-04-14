"""Sekrd MCP Test Server — FIXED version.

All 5 vulnerabilities found by Sekrd MCP scanner have been addressed.
Expected result: 0 MCP findings on rescan.
"""

import json
import os
import sys


# FIX 1: Removed hardcoded API key — use environment variable
def get_openai_key():
    return os.environ.get("OPENAI_API_KEY", "")


# --- Tool definitions (MCP protocol) ---

TOOLS = [
    {
        # FIX 2: Removed <instructions> prompt injection from description
        # FIX 3: Added path whitelist (allowedPaths) to schema
        "name": "read_file",
        "description": "Read a file from the allowed project directory.",
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
        # FIX 5: Removed shell execution and network access
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
        "description": "Search for a pattern in source files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "directory": {
                    "type": "string",
                    "allowedPaths": ["/home/user/project"],
                },
            },
            "required": ["pattern"],
        },
    },
]


# --- Safe tool handlers ---

async def handle_read_file(path: str) -> str:
    """Read file only from allowed directory."""
    allowed = "/home/user/project"
    full_path = os.path.normpath(os.path.join(allowed, path))
    if not full_path.startswith(allowed):
        return "Error: path outside allowed directory"
    return open(full_path).read()


async def handle_list_files(directory: str = ".") -> str:
    """List files safely without shell."""
    allowed = "/home/user/project"
    full_path = os.path.normpath(os.path.join(allowed, directory))
    if not full_path.startswith(allowed):
        return "Error: path outside allowed directory"
    return "\n".join(os.listdir(full_path))


# --- MCP Protocol (JSON-RPC over stdio) ---

def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            if msg.get("method") == "tools/list":
                response = {"jsonrpc": "2.0", "id": msg["id"], "result": {"tools": TOOLS}}
                print(json.dumps(response), flush=True)
        except Exception:
            pass


if __name__ == "__main__":
    main()
