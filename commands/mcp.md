---
description: Test and validate MCP server projects
---

You are validating an MCP server to catch issues before users hit them.

## First: Is This Actually an MCP Server?

Before doing anything, check if this project **builds** an MCP server:

**Signs it IS an MCP server project:**
- `@modelcontextprotocol/sdk` in package.json dependencies
- `mcp` or `mcp[cli]` in pyproject.toml/requirements.txt
- Files importing `McpServer`, `FastMCP`, `createSdkMcpServer`
- Tool registrations with `@mcp.tool()` or `server.registerTool()`

**Signs it is NOT an MCP server (skip this command):**
- Project only **consumes** MCP tools (e.g., `mcp__stripe__*` in agent configs)
- Uses `claude-agent-sdk` but not `@modelcontextprotocol/sdk`
- Has `.mcp.json` config files but no server implementation

**If this isn't an MCP server project:**
> "This project consumes MCP tools but doesn't build an MCP server. Use `/agent` instead to audit the agent architecture, or run `/mcp` in your actual MCP server projects (like mcp-posthog, ahrefs-mcp-server)."

Stop here. Don't try to validate something that doesn't exist.

---

## MCP Basics

**Model Context Protocol** connects AI applications to external systems. An MCP server exposes:
- **Tools**: Functions the LLM can call (like API endpoints)
- **Resources**: Data the LLM can read (like files)
- **Prompts**: Reusable templates

**SDK is recommended but not required.** You can implement JSON-RPC directly, but the official SDKs handle protocol complexity.

## Check SDK Versions

Don't assume versions - **check the source**:

**TypeScript:** Check latest on npm
```bash
npm view @modelcontextprotocol/sdk version
```

**Python:** Check latest on PyPI
```bash
pip index versions mcp 2>/dev/null | head -1 || curl -s https://pypi.org/pypi/mcp/json | grep -o '"version":"[^"]*"' | head -1
```

Compare against what the project uses in `package.json` or `pyproject.toml`. If significantly behind (especially major versions), recommend updating.

## What to Validate

### 1. SDK Version

Check `package.json` or `pyproject.toml` for MCP SDK version. Compare against latest (use commands above).

Look for:
- **Major version behind**: Likely missing important features, breaking changes
- **Many minor versions behind**: May have bug fixes worth getting
- **Pinned to exact version** (`1.8.0` vs `^1.8.0`): Might be intentional, ask why

### 2. Tool Definitions

Find all tool registrations. Check each for:

**Name:** Descriptive and action-oriented?
- Good: `get_user_events`, `create_dashboard`
- Bad: `fetch`, `do_action`

**Description:** Explains WHEN to use, not just WHAT it does?
- Good: "Get events for a user. Use after identifying the user ID. Returns last 100 events with timestamps."
- Bad: "Gets events."

**Parameters:** Typed with descriptions?

**TypeScript (Zod):**
```typescript
{
  user_id: z.string().describe("User ID from identify call"),
  limit: z.number().optional().describe("Max events to return, default 100")
}
```

**Python (FastMCP):**
```python
@mcp.tool()
async def get_events(user_id: str, limit: int = 100) -> str:
    """Get events for a user.

    Args:
        user_id: User ID from identify call
        limit: Max events to return
    """
```

### 3. Transport Configuration

**STDIO (local servers):**
- NEVER write to stdout - it corrupts JSON-RPC messages
- Use `console.error()` (TS) or `logging` (Python) instead
- Search for `console.log`, `print()`, `println!` in the codebase

**HTTP/SSE (remote servers):**
- Standard logging is fine
- Check authentication setup (OAuth, API keys)

### 4. Error Handling

Does the server handle errors gracefully?
- API failures should return structured error messages
- Network timeouts should be caught
- Invalid parameters should return helpful errors

Bad:
```typescript
const data = await fetch(url); // throws on failure
```

Good:
```typescript
try {
  const response = await fetch(url);
  if (!response.ok) {
    return { error: `API returned ${response.status}` };
  }
} catch (e) {
  return { error: `Network error: ${e.message}` };
}
```

### 5. Configuration

Check for:
- `.env.example` with all required variables documented
- Clear README with setup instructions
- Claude Desktop config example with absolute paths

## Testing the Server

### Quick smoke test:

**TypeScript:**
```bash
npm run build && node dist/index.js
# Should start without errors, wait for JSON-RPC input
```

**Python:**
```bash
uv run python server.py
# or: mcp dev server.py
```

### Using MCP Inspector:

```bash
npx @anthropic/mcp-inspector
```

This provides a UI to test tool calls without needing Claude.

### Check Claude Desktop logs:

```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Server not appearing | JSON syntax error in config | Validate JSON, use absolute paths |
| Tool calls fail silently | stdout logging in STDIO mode | Replace console.log with console.error |
| Connection timeout | Server crashes on startup | Check build, run manually to see errors |
| "Tool not found" | Capability not registered | Verify tool registration in server setup |

## What to Report

After analysis, report:

**SDK status:** Current vs latest, upgrade recommended?

**Tool quality:** Are definitions clear enough for Claude to use correctly?

**Safety issues:** stdout logging, missing error handling, exposed secrets?

**Missing pieces:** What would make this server more useful?

**Test results:** Did the server start? Did basic tool calls work?

$ARGUMENTS
