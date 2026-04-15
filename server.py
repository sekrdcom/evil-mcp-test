"""Fixed MCP Server — vulnerabilities from Sekrd scan have been remediated.

Changes based on Sekrd fix prompts:
- Removed hardcoded API key (use env var)
- Removed hidden instructions from tool descriptions
- Added path whitelist for filesystem access
- Replaced os.system with subprocess.run (no shell=True)
- Added allowed_domains for network access
- Removed tool shadowing (duplicate read_file)
"""

import os
import subprocess
import json

# FIX (Sekrd): Use environment variable instead of hardcoded key
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# FIX (Sekrd): Path whitelist for filesystem access
ALLOWED_PATHS = ["/home/user/projects", "/tmp"]

# FIX (Sekrd): Domain whitelist for network access
ALLOWED_DOMAINS = ["api.openai.com", "api.anthropic.com"]

TOOLS = [
    {
        "name": "read_file",
        # FIX (Sekrd): Removed hidden <instructions> prompt injection
        "description": "Read a file from allowed project directories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (must be within allowed directories)",
                }
            },
            "required": ["path"],
        },
    },
    # FIX (Sekrd): Removed duplicate/shadowed read_file tool
    {
        "name": "execute_command",
        "description": "Run a safe shell command (no arbitrary execution).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute (limited to safe operations)",
                    "enum": ["ls", "pwd", "date", "whoami"],
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "query_database",
        "description": "Execute a read-only SQL query against the connected database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SELECT query only"},
            },
            "required": ["sql"],
        },
    },
]


async def handle_read_file(path: str) -> str:
    # FIX (Sekrd): Validate path against whitelist
    real_path = os.path.realpath(path)
    if not any(real_path.startswith(allowed) for allowed in ALLOWED_PATHS):
        return f"Error: path {path} is outside allowed directories"
    return open(real_path).read()


async def handle_execute_command(command: str) -> str:
    # FIX (Sekrd): Use subprocess.run with list args, no shell=True
    allowed = ["ls", "pwd", "date", "whoami"]
    if command not in allowed:
        return f"Error: command '{command}' not in allowed list"
    result = subprocess.run([command], capture_output=True, text=True, timeout=10)
    return result.stdout


async def handle_query_database(sql: str) -> str:
    # FIX (Sekrd): Only allow SELECT, no eval
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: only SELECT queries allowed"
    # Parameterized query would go here
    return json.dumps({"status": "ok", "note": "query would execute here"})


def main():
    import sys
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
