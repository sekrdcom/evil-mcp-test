"""MCP Server — fixed version for Sekrd scanner testing."""
import json
import os

TOOLS = [
    {"name": "read_file",
     "description": "Read a file within the allowed project directory.",
     "inputSchema": {
         "type": "object",
         "properties": {
             "path": {"type": "string", "description": "Relative path within project directory"}
         },
         "required": ["path"]
     }},
]

ALLOWED_DIR = os.path.abspath(".")

async def handle_read_file(path):
    full = os.path.abspath(path)
    if not full.startswith(ALLOWED_DIR):
        raise ValueError("Access denied: path outside project directory")
    with open(full) as f:
        return f.read()

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
