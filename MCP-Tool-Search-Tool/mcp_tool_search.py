"""
Tool Search with MCP Servers: Dynamic Tool Discovery from Remote MCP Servers

This implementation demonstrates how to combine Tool Search with MCP (Model Context Protocol)
servers, allowing Claude to discover and execute tools from remote services like GitHub,
filesystem operations, web search, and databases.

Key Features:
- Connects to multiple MCP servers
- Dynamically fetches available tools from each server
- Uses tool search to find relevant tools
- Executes tools via MCP protocol
- Supports environment-specific configuration
"""

import anthropic
from anthropic import Anthropic
import json
import os
import sys
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import argparse
import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Model configuration
MODEL = "claude-sonnet-4-5-20250929"

# Initialize Anthropic client
claude_client = Anthropic()

print("✓ Claude client initialized")


import py_toon_format

class MCPToolSearchManager:
    """Manages MCP server connections and tool search integration."""
    
    def __init__(self, config_path: str = "mcp_servers_config.json", debug: bool = False, defer_loading: bool = False, use_toon: bool = False):
        """
        Initialize the MCP Tool Search Manager.
        
        Args:
            config_path: Path to MCP servers configuration JSON
            debug: Enable debug logging
            defer_loading: Whether to defer loading of tools (default: False)
            use_toon: Whether to use TOON format for tool results (default: False)
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.sessions = {}
        self.all_tools = []
        self.tool_to_server = {}  # Maps tool name to server name
        self.transports = {}  # Store transport contexts
        self.debug = debug
        self.defer_loading = defer_loading
        self.use_toon = use_toon
        
        print(f"✓ Loaded configuration for {len(self.config['mcp_servers'])} MCP servers")
    
    def _load_config(self) -> Dict:
        """Load MCP server configuration from JSON file."""
        config_path = os.path.join(os.path.dirname(__file__), self.config_path)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Replace environment variable placeholders
        for server in config['mcp_servers']:
            if 'env' in server:
                for key, value in server['env'].items():
                    if value.startswith('${') and value.endswith('}'):
                        env_var = value[2:-1]
                        server['env'][key] = os.getenv(env_var, '')
            
            # Replace in args
            if 'args' in server:
                server['args'] = [
                    os.getenv(arg[2:-1], '') if arg.startswith('${') and arg.endswith('}') else arg
                    for arg in server['args']
                ]
        
        return config
    
    async def connect_to_server(self, server_config: Dict, timeout: int = 30) -> Optional[ClientSession]:
        """
        Connect to an MCP server.
        
        Args:
            server_config: Server configuration dictionary
            timeout: Connection timeout in seconds (default: 30)
            
        Returns:
            ClientSession if successful, None otherwise
        """
        server_name = server_config['name']
        stdio_context = None
        
        try:
            print(f"\n🔄 Connecting to {server_name}...")
            print(f"   Command: {server_config['command']} {' '.join(server_config.get('args', []))}")
            print(f"   (Timeout: {timeout} seconds | May take 1-3 minutes on first run)")
            
            if self.debug:
                print(f"   [DEBUG] Creating server parameters...")
            
            server_params = StdioServerParameters(
                command=server_config['command'],
                args=server_config.get('args', []),
                env=server_config.get('env', {})
            )
            
            if self.debug:
                print(f"   [DEBUG] Server params: {server_params}")
                print(f"   [DEBUG] Creating stdio_client context...")
            
            # Create stdio_client context
            stdio_context = stdio_client(server_params)
            
            if self.debug:
                print(f"   [DEBUG] Entering stdio_context...")
            
            # Enter context OUTSIDE of timeout to avoid cancel scope issues
            stdio, write = await stdio_context.__aenter__()
            
            try:
                # Create session
                session = ClientSession(stdio, write)
                
                if self.debug:
                    print(f"   [DEBUG] Entering session context...")
                await session.__aenter__()
                
                # Use timeout only for session initialization
                with anyio.fail_after(timeout):
                    if self.debug:
                        print(f"   [DEBUG] Initializing session...")
                    await session.initialize()
                    
                print(f"✓ Successfully connected to {server_name}")
                
                # Store context
                self.transports[server_name] = stdio_context
                return session
                    
            except TimeoutError:
                print(f"✗ Connection to {server_name} timed out after {timeout} seconds")
                print(f"   Try: 1) Check internet connection, 2) Verify credentials, 3) Test server manually")
                # Clean up
                await stdio_context.__aexit__(None, None, None)
                return None
            except Exception as e:
                # Clean up on other errors
                await stdio_context.__aexit__(None, None, None)
                raise e
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Connection to {server_name} interrupted by user")
            raise
        except Exception as e:
            print(f"✗ Failed to connect to {server_name}")
            print(f"   Error: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   (Server may need credentials or may not be available)")
            return None
    
    async def fetch_tools_from_server(self, server_name: str, session: ClientSession) -> List[Dict]:
        """
        Fetch available tools from an MCP server.
        
        Args:
            server_name: Name of the MCP server
            session: Active client session
            
        Returns:
            List of tool definitions
        """
        try:
            tools_response = await session.list_tools()
            tools = []
            
            for tool in tools_response.tools:
                # Convert MCP tool format to Anthropic tool format
                tool_def = {
                    "name": f"{server_name}_{tool.name}",  # Prefix with server name
                    "description": tool.description or f"Tool from {server_name} MCP server",
                    "input_schema": tool.inputSchema,
                    "defer_loading": self.defer_loading  # Use configured setting
                }
                tools.append(tool_def)
                
                # Track which server owns this tool
                self.tool_to_server[tool_def['name']] = {
                    'server': server_name,
                    'original_name': tool.name,
                    'session': session
                }
            
            print(f"   ✓ Fetched {len(tools)} tools from {server_name}")
            return tools
            
        except Exception as e:
            print(f"✗ Failed to fetch tools from {server_name}: {e}")
            return []
    
    async def initialize_all_servers(self):
        """Connect to all configured MCP servers and fetch their tools."""
        print("\n" + "="*80)
        print("INITIALIZING MCP SERVERS")
        print("="*80)
        print(f"Attempting to connect to {len(self.config['mcp_servers'])} servers...")
        print("(First-time setup may take several minutes to download servers)\n")
        
        for server_config in self.config['mcp_servers']:
            server_name = server_config['name']
            session = await self.connect_to_server(server_config)
            
            if session:
                self.sessions[server_name] = session
                print(f"   📥 Fetching tools from {server_name}...")
                tools = await self.fetch_tools_from_server(server_name, session)
                self.all_tools.extend(tools)
        
        print("\n" + "="*80)
        print("INITIALIZATION COMPLETE")
        print("="*80)
        print(f"✓ Successfully connected to {len(self.sessions)}/{len(self.config['mcp_servers'])} servers")
        print(f"✓ Total tools available: {len(self.all_tools)}")
        
        if len(self.sessions) < len(self.config['mcp_servers']):
            failed = len(self.config['mcp_servers']) - len(self.sessions)
            print(f"⚠️ {failed} server(s) failed to connect")
        print("="*80 + "\n")
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """
        Execute a tool via its MCP server.
        
        Args:
            tool_name: Name of the tool (with server prefix)
            arguments: Tool arguments
            
        Returns:
            Tool execution result as JSON string
        """
        if tool_name not in self.tool_to_server:
            return self._encode_result({"error": f"Unknown tool: {tool_name}"})
        
        tool_info = self.tool_to_server[tool_name]
        session = tool_info['session']
        original_tool_name = tool_info['original_name']
        
        try:
            result = await session.call_tool(original_tool_name, arguments)
            
            # Convert MCP result to string
            if hasattr(result, 'content'):
                # Extract text content from result
                content_parts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_parts.append(item.text)
                content_str = "\n".join(content_parts) if content_parts else str(result.content)
                
                # Try to parse as JSON to allow TOON optimization
                try:
                    content_data = json.loads(content_str)
                except:
                    content_data = content_str
            
                return self._encode_result({
                    "success": True,
                    "result": content_data
                })
            else:
                return self._encode_result({
                    "success": True,
                    "result": str(result)
                })
                
        except Exception as e:
            return self._encode_result({
                "success": False,
                "error": str(e)
            })

    def _encode_result(self, data: Dict) -> str:
        """Encode result as JSON or TOON based on configuration."""
        if self.use_toon:
            return py_toon_format.encode(data)
        return json.dumps(data)
    
    async def cleanup(self):
        """Close all MCP server connections."""
        # Close sessions first
        for session in self.sessions.values():
            try:
                await session.__aexit__(None, None, None)
            except BaseException:
                pass
                
        if not self.transports:
            return
            
        for server_name, transport_context in self.transports.items():
            try:
                await transport_context.__aexit__(None, None, None)
                print(f"  ✓ Closed {server_name}")
            except BaseException:
                # Silently ignore cleanup errors (context may already be closed)
                pass
    
    def create_tool_library_with_search(self, search_method: str = "regex") -> List[Dict]:
        """
        Create tool library with search tool for Claude API.
        
        Args:
            search_method: "regex" or "bm25"
            
        Returns:
            List of tools including search tool
        """
        # Add search tool
        if search_method == "regex":
            search_tool = {
                "type": "tool_search_tool_regex_20251119",
                "name": "tool_search_tool_regex"
            }
        else:
            search_tool = {
                "type": "tool_search_tool_bm25_20251119",
                "name": "tool_search_tool_bm25"
            }
        
        # Combine search tool with all MCP tools
        return [search_tool] + self.all_tools


async def run_mcp_tool_search_conversation(
    mcp_manager: MCPToolSearchManager,
    user_query: str,
    search_method: str = "regex",
    max_turns: int = 10
):
    """
    Run a conversation using MCP tools with tool search.
    
    Args:
        mcp_manager: Initialized MCP tool search manager
        user_query: User's question
        search_method: Tool search method ("regex" or "bm25")
        max_turns: Maximum conversation turns
    """
    print(f"\n{'='*80}")
    print(f"USER: {user_query}")
    print(f"Search Method: {search_method.upper()}")
    print(f"{'='*80}\n")
    
    # Create tool library with search
    tools = mcp_manager.create_tool_library_with_search(search_method)
    
    # Initialize conversation
    messages = [{"role": "user", "content": user_query}]
    
    # Token tracking
    total_input_tokens = 0
    total_output_tokens = 0
    total_tool_search_requests = 0
    
    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")
        
        try:
            # Call Claude with MCP tools
            response = claude_client.messages.create(
                model=MODEL,
                max_tokens=2048,
                tools=tools,
                messages=messages,
                extra_headers={
                    "anthropic-beta": "advanced-tool-use-2025-11-20"
                }
            )
        except Exception as e:
            print(f"\n❌ Error calling API: {e}")
            print(f"   Error type: {type(e).__name__}")
            break
        
        # Validate response
        if not response.content:
            print("\n⚠️ Warning: Response has no content")
            print(f"   Stop reason: {response.stop_reason}")
            break
        
        # Track token usage
        usage = response.usage
        turn_input_tokens = usage.input_tokens
        turn_output_tokens = usage.output_tokens
        turn_tool_search_requests = 0
        
        if hasattr(usage, 'server_tool_use') and usage.server_tool_use:
            if hasattr(usage.server_tool_use, 'tool_search_requests'):
                turn_tool_search_requests = usage.server_tool_use.tool_search_requests
        
        total_input_tokens += turn_input_tokens
        total_output_tokens += turn_output_tokens
        total_tool_search_requests += turn_tool_search_requests
        
        # Display usage
        print(f"\n📊 Token usage for this turn:")
        print(f"   Input tokens: {turn_input_tokens}")
        print(f"   Output tokens: {turn_output_tokens}")
        if turn_tool_search_requests > 0:
            print(f"   Tool search requests: {turn_tool_search_requests}")
        
        # Add response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # Handle response
        if response.stop_reason == "end_turn":
            print("\n✓ Conversation complete\n")
            for block in response.content:
                if block.type == "text":
                    print(f"ASSISTANT: {block.text}")
            break
        
        elif response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if block.type == "text":
                    print(f"\nASSISTANT: {block.text}")
                
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    # Check if this is a built-in search tool
                    if tool_name in ["tool_search_tool_regex", "tool_search_tool_bm25"]:
                        print(f"\n🔍 Tool search: {tool_input.get('query', 'N/A')}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": ""
                        })
                    else:
                        # Execute MCP tool
                        print(f"\n🔧 Executing MCP tool: {tool_name}")
                        print(f"   Input: {json.dumps(tool_input, indent=2)}")
                        
                        result = await mcp_manager.execute_tool(tool_name, tool_input)
                        
                        print(f"   ✅ Result: {result[:200]}..." if len(result) > 200 else f"   ✅ Result: {result}")
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result
                        })
            
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        
        else:
            print(f"\n⚠️ Unexpected stop reason: {response.stop_reason}")
            break
    
    # Display summary
    print(f"\n{'='*80}")
    print("📊 TOKEN USAGE SUMMARY")
    print(f"{'='*80}")
    print(f"Total input tokens:  {total_input_tokens}")
    print(f"Total output tokens: {total_output_tokens}")
    print(f"Total tokens:        {total_input_tokens + total_output_tokens}")
    if total_tool_search_requests > 0:
        print(f"Tool search requests: {total_tool_search_requests}")
    print(f"{'='*80}\n")


async def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="MCP Tool Search - Dynamic tool discovery from remote MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python mcp_tool_search.py
  
  # Direct query
  python mcp_tool_search.py --query "Search GitHub for Python repositories"
  
  # Choose search method
  python mcp_tool_search.py --query "List files in workspace" --method bm25
        """
    )
    
    parser.add_argument("-q", "--query", type=str, help="Your question for Claude")
    parser.add_argument("-m", "--method", choices=["regex", "bm25"], default="regex", help="Tool search method")
    parser.add_argument("--max-turns", type=int, default=10, help="Maximum conversation turns")
    parser.add_argument("--config", type=str, default="mcp_servers_config.json", help="MCP server configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--defer-mcp-tools-loading", action="store_true", help="Enable deferred tool loading (default: False)")
    parser.add_argument("--toon", action="store_true", help="Use TOON format for tool results (default: False)")
    
    args = parser.parse_args()
    
    # Initialize MCP manager
    print("\n" + "="*80)
    print("MCP TOOL SEARCH - Remote Tool Discovery & Execution")
    print("="*80)
    print(f"Deferred Loading: {'ENABLED' if args.defer_mcp_tools_loading else 'DISABLED'}")
    print(f"TOON Format: {'ENABLED' if args.toon else 'DISABLED'}")
    
    mcp_manager = MCPToolSearchManager(
        config_path=args.config, 
        debug=args.debug,
        defer_loading=args.defer_mcp_tools_loading,
        use_toon=args.toon
    )
    
    try:
        # Connect to MCP servers and fetch tools
        await mcp_manager.initialize_all_servers()
        
        if len(mcp_manager.all_tools) == 0:
            print("\n⚠️ No tools available. Check your MCP server configuration and environment variables.")
            return
        
        # Get query
        if args.query:
            query = args.query
        else:
            print("\n" + "="*80)
            print("Ask a question and Claude will search MCP tools to help you.")
            print(f"Available servers: {', '.join(mcp_manager.sessions.keys())}")
            print("="*80 + "\n")
            
            query = input("Enter your question: ").strip()
            
            if not query:
                print("\n⚠️ No question provided. Exiting.")
                return
        
        # Run conversation
        await run_mcp_tool_search_conversation(
            mcp_manager,
            query,
            search_method=args.method,
            max_turns=args.max_turns
        )
    
    finally:
        # Cleanup
        await mcp_manager.cleanup()
        print("\n✓ MCP connections closed")


if __name__ == "__main__":
    asyncio.run(main())
