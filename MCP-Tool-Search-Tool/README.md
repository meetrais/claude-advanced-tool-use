# MCP Tool Search - Remote Tool Discovery & Execution

This implementation demonstrates how to combine **Tool Search** with **MCP (Model Context Protocol) servers**, enabling Claude to discover and execute tools from remote services like GitHub, filesystems, databases, and web search APIs.

## What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open protocol that standardizes how AI applications connect to external data sources and tools. MCP servers expose tools, resources, and prompts that AI models can discover and use.

## What This Implementation Does

This combines two powerful features:

1. **Tool Search**: Claude dynamically discovers relevant tools from large libraries
2. **MCP Integration**: Tools are executed on remote MCP servers (GitHub, databases, filesystems, etc.)

Instead of defining tools locally, this implementation:
- Connects to multiple MCP servers
- Fetches available tools from each server
- Uses tool search to find relevant tools
- Executes tools remotely via MCP protocol

## Architecture

```
┌─────────────────┐
│     Claude      │
│  (Tool Search)  │
└────────┬────────┘
         │ Discovers & Calls Tools
         ▼
┌─────────────────┐
│  MCP Tool       │
│  Search Manager │
└────────┬────────┘
         │ Manages Connections
         ▼
┌─────────────────────────────────────┐
│          MCP Servers                │
├─────────────────────────────────────┤
│ • GitHub (repos, issues, PRs)       │
│ • Filesystem (read/write files)     │
│ • Brave Search (web search)         │
│ • PostgreSQL (database queries)     │
│ • ...custom servers...              │
└─────────────────────────────────────┘
```

## Available MCP Servers

### Pre-configured Servers

1. **GitHub** - Repository management, issues, pull requests, code search
   - Requires: GITHUB_TOKEN
   - Tools: create_pr, search_repos, list_issues, etc.

2. **Filesystem** - Read and write files in specified directories
   - Requires: WORKSPACE_PATH
   - Tools: read_file, write_file, list_directory, etc.

3. **Brave Search** - Web search capabilities
   - Requires: BRAVE_API_KEY
   - Tools: web_search, news_search, etc.

4. **PostgreSQL** - Database operations
   - Requires: POSTGRES_CONNECTION_STRING
   - Tools: query, insert, update, etc.

### Adding Custom MCP Servers

Edit `mcp_servers_config.json` to add your own MCP servers:

```json
{
  "mcp_servers": [
    {
      "name": "my_server",
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      },
      "description": "My custom MCP server"
    }
  ]
}
```

## Setup

### 1. Install Dependencies

```bash
cd MCP-Tool-Search-Tool
pip install -r requirements.txt
```

### 2. Install Node.js and MCP Servers

MCP servers typically run via `npx`. Install Node.js if you haven't:

- Download from [nodejs.org](https://nodejs.org/)
- Or use a package manager

The MCP servers will be automatically installed when first run via `npx -y`.

### 3. Configure Environment Variables

```bash
copy .env.example .env
```

Edit `.env` and add your credentials:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GITHUB_TOKEN=ghp_your_github_token_here
WORKSPACE_PATH=C:\Your\Workspace\Path
```

**Getting Tokens:**

- **GitHub**: [Create Personal Access Token](https://github.com/settings/tokens)
  - Scopes needed: `repo`, `read:org`, `read:user`
  
- **Brave Search**: [Get API Key](https://brave.com/search/api/) (optional)

- **PostgreSQL**: Your database connection string (optional)

### 4. Configure MCP Servers

Edit `mcp_servers_config.json` to enable/disable servers:

```json
{
  "mcp_servers": [
    {
      "name": "github",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "description": "GitHub MCP server..."
    }
  ]
}
```

**Note**: Remove or comment out servers you don't want to use.

## Usage

### Interactive Mode

```bash
python mcp_tool_search.py
```

You'll see which MCP servers connected successfully, then you can ask questions:

```
Enter your question: Search GitHub for popular Python AI projects
```

### Command-Line Mode

```bash
# Direct query
python mcp_tool_search.py --query "List all files in my workspace"

# Choose search method
python mcp_tool_search.py --query "Search for repositories about MCP" --method bm25

# Custom config file
python mcp_tool_search.py --config my_servers.json --query "Your question"
```

### Help

```bash
python mcp_tool_search.py --help
```

## Example Queries

### GitHub Queries

```bash
python mcp_tool_search.py --query "Search GitHub for repositories about MCP protocol"
python mcp_tool_search.py --query "Create a new issue in my repo about bug XYZ"
python mcp_tool_search.py --query "List all open pull requests in organization ABC"
```

### Filesystem Queries

```bash
python mcp_tool_search.py --query "List all Python files in my workspace"
python mcp_tool_search.py --query "Read the contents of README.md"
python mcp_tool_search.py --query "Create a new file called notes.txt with todo items"
```

### Brave Search Queries

```bash
python mcp_tool_search.py --query "Search for latest news about AI"
python mcp_tool_search.py --query "Find information about Claude API"
```

### Database Queries

```bash
python mcp_tool_search.py --query "Show me all users in the database"
python mcp_tool_search.py --query "Get sales data for last month"
```

## How It Works

### 1. Server Initialization

```python
mcp_manager = MCPToolSearchManager(config_path="mcp_servers_config.json")
await mcp_manager.initialize_all_servers()
```

- Reads configuration
- Spawns MCP server processes
- Establishes connections via stdio
- Fetches available tools from each server

### 2. Tool Discovery

```python
tools = await mcp_manager.fetch_tools_from_server(server_name, session)
```

- Each MCP server exposes its tools
- Tools are converted to Anthropic's format
- Tool names are prefixed with server name (e.g., `github_create_pr`)
- All tools marked with `defer_loading=True` for tool search

### 3. Tool Search Integration

```python
tools = mcp_manager.create_tool_library_with_search(search_method="regex")
```

- Adds `tool_search_tool_regex` or `tool_search_tool_bm25`
- Combines with all MCP tools
- Claude searches through all available tools
- Only relevant tools are loaded per query

### 4. Tool Execution

```python
result = await mcp_manager.execute_tool(tool_name, arguments)
```

- Routes tool call to appropriate MCP server
- Executes tool via MCP protocol
- Returns result to Claude
- Handles errors gracefully

## Token Usage Tracking

All token metrics are tracked and displayed:

```
📊 Token usage for this turn:
   Input tokens: 1234
   Output tokens: 156
   Tool search requests: 1

📊 TOKEN USAGE SUMMARY
Total input tokens:  2468
Total output tokens: 312
Total tokens:        2780
Tool search requests: 2
```

## Error Handling

The implementation handles common errors:

- **Server connection failures**: Continues with available servers
- **Tool execution errors**: Returns error to Claude for handling
- **Missing credentials**: Warns and skips that server
- **API errors**: Detailed debug information

## Advantages Over Traditional Tool Use

| Aspect | Traditional | MCP Tool Search |
|--------|-------------|-----------------|
| **Tool Definitions** | Hardcoded locally | Fetched from remote servers |
| **Updates** | Manual code changes | Automatic when server updates |
| **Scale** | Limited by context | Hundreds of tools across servers |
| **Real Execution** | Mocked locally | Real operations on services |
| **Integration** | Custom for each API | Standardized via MCP |

## Security Considerations

⚠️ **Important Security Notes:**

1. **Credentials**: Never commit `.env` file or expose tokens
2. **Workspace Access**: Filesystem server has full access to configured path
3. **GitHub Token**: Scope token with minimum necessary permissions
4. **Database Access**: Use read-only user when possible
5. **Validation**: Review tool calls before execution in production

## Troubleshooting

### Server Connection Failures

**Problem**: `Failed to connect to github: ...`

**Solutions**:
1. Check Node.js is installed: `node --version`
2. Verify environment variables in `.env`
3. Test manual connection: `npx -y @modelcontextprotocol/server-github`
4. Check firewall/network settings

### No Tools Available

**Problem**: `No tools available`

**Solutions**:
1. At least one server must connect successfully
2. Check logs for which servers failed
3. Verify API keys/tokens are valid
4. Try with just GitHub server first

### Tool Execution Errors

**Problem**: Tool executes but returns error

**Solutions**:
1. Check tool arguments match expected format
2. Verify permissions (GitHub token scopes, file permissions, etc.)
3. Review MCP server logs
4. Test tool directly via MCP client

## Advanced Configuration

### Custom Server Timeouts

Modify the connection logic to add timeouts:

```python
async def connect_to_server(self, server_config: Dict) -> Optional[ClientSession]:
    # Add timeout parameter
    timeout = server_config.get('timeout', 30)
    ...
```

### Selective Tool Loading

Filter which tools to include:

```python
def fetch_tools_from_server(self, server_name: str, session: ClientSession):
    ...
    # Only include tools matching pattern
    if 'search' in tool.name or 'list' in tool.name:
        tools.append(tool_def)
```

### Tool Name Aliasing

Create shorter tool names:

```python
tool_def = {
    "name": tool.name,  # Use original name instead of prefixed
    ...
}
```

## MCP Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Next Steps

1. **Test with GitHub**: Start with GitHub server for safe testing
2. **Add Custom Server**: Create your own MCP server for your API
3. **Scale Up**: Add more MCP servers as needed
4. **Production**: Add authentication, rate limiting, logging

## License

This implementation demonstrates MCP integration with Claude's Tool Search feature.
