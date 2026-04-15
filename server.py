"""Fixed MCP Server — all Sekrd findings remediated."""

import os
import subprocess
import json

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

ALLOWED_PATHS = ["/home/user/projects", "/tmp"]
ALLOWED_DOMAINS = ["api.openai.com"]

TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from allowed project directories.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    {
        "name": "execute_command",
        "description": "Run a safe command.",
        "inputSchema": {"type": "object", "properties": {"command": {"type": "string", "enum": ["ls", "pwd", "date"]}}, "required": ["command"]},
    },
]

async def handle_read_file(path):
    real = os.path.realpath(path)
    if not any(real.startswith(a) for a in ALLOWED_PATHS):
        return "Error: path outside allowed directories"
    return open(real).read()

async def handle_execute_command(command):
    if command not in ["ls", "pwd", "date"]:
        return "Error: command not allowed"
    result = subprocess.run([command], capture_output=True, text=True, timeout=10)
    return result.stdout

def main():
    import sys
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            if msg.get("method") == "tools/list":
                print(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": {"tools": TOOLS}}), flush=True)
        except Exception:
            pass

if __name__ == "__main__":
    main()
