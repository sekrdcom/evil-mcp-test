# Evil MCP Test Server

Intentionally vulnerable MCP server for testing [Sekrd](https://sekrd.com) scanner.

**DO NOT use in production.** This contains deliberate security flaws:

1. Tool poisoning (hidden `<instructions>` in tool description)
2. Tool shadowing (duplicate `read_file` tool name)
3. Overpermissioned filesystem access (no path whitelist)
4. Data exfiltration flow (database + webhook without domain restriction)
5. Hardcoded OpenAI API key in source
6. Command injection (os.system + subprocess with string concat + eval)

## Expected Sekrd findings

A deep scan with MCP provider should detect all 6+ vulnerabilities
and return a BLOCK verdict.
