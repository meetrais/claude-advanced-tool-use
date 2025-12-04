# Claude Advanced Tool Use

> **Based on**: [Anthropic's Advanced Tool Use Engineering Blog Post](https://www.anthropic.com/engineering/advanced-tool-use)

This repository contains complete, working implementations of Anthropic's **Advanced Tool Use** features, demonstrating cutting-edge capabilities for building efficient, accurate, and scalable AI applications.

## What's Included

This repository showcases three major features from Anthropic's Advanced Tool Use suite:

### 1. [Tool Use Examples](./Tool-Use-Examples)

**Improve accuracy from 72% to 90%** by providing concrete usage examples alongside JSON Schema definitions.

- **The Challenge**: JSON Schema can't express usage patterns like date formats, ID conventions, or parameter correlations
- **The Solution**: Add `input_examples` to teach Claude through concrete examples
- **Best For**: Complex nested structures, many optional parameters, domain-specific conventions

**Quick Start:**
```powershell
cd Tool-Use-Examples
pip install -r requirements.txt
# Copy .env.example to .env and add your API key
python with_examples.py
```

[Full Documentation](./Tool-Use-Examples/README.md)

---

### 2. [Tool Search Tool](./Tool-Search-Tool)

**Manage large tool libraries efficiently** by letting Claude search through hundreds of tools to find the right ones.

- **The Challenge**: Claude's context window limits you to ~20 tools per request
- **The Solution**: Store tools externally, let Claude search and retrieve only what's needed
- **Best For**: Applications with 50+ tools, dynamic tool discovery, reducing token costs

**Implementations:**
- `using-regex-or-bm25.py` - Fast text-based search (no API keys needed)
- `using-embeddings.py` - Semantic search with Voyage AI embeddings

**Quick Start:**
```powershell
cd Tool-Search-Tool
pip install -r requirements.txt
# Copy .env.example to .env and add your API key
python using-regex-or-bm25.py
```

[Full Documentation](./Tool-Search-Tool/README.md)

---

### 3. [Programmatic Tool Calling](./Programmatic-Tool-Calling)

**Reduce tokens by 37% and improve latency** by letting Claude orchestrate tools through Python code execution.

- **The Challenge**: Traditional tool calling pollutes context with intermediate results
- **The Solution**: Claude writes Python code that orchestrates tools; only final results enter context
- **Best For**: Processing large datasets, multiple dependent tool calls, parallel operations

> [!WARNING]
> **Beta Feature Notice**: This implementation is complete and correct but awaits full Python SDK support. See the folder for details and working alternatives.

**Quick Start:**
```powershell
cd Programmatic-Tool-Calling
pip install -r requirements.txt
# Copy .env.example to .env and add your API key
python budget_compliance.py
```

[Full Documentation](./Programmatic-Tool-Calling/README.md)

---

### 4. [Without Tool Search Tool](./Without-Tool-Search-Tool) 

**Baseline comparison**: See the difference with traditional tool use where all tools are provided upfront.

- **The Purpose**: Demonstrate token cost differences between approaches
- **The Setup**: Same 40 tools, traditional API usage (all tools sent every time)
- **Best For**: Understanding when tool search is worth it, cost comparison

**Quick Start:**
```powershell
cd Without-Tool-Search-Tool
pip install -r requirements.txt
# Copy .env.example to .env and add your API key
python without_tool_search.py
```

[Full Documentation](./Without-Tool-Search-Tool/README.md)

---

### 5. [Token Usage Test Suite](./Testcases) 

**Compare token usage** across all implementations with automated testing and analysis.

- **What It Does**: Runs identical queries across all 4 implementations
- **Measurements**: Input tokens, output tokens, tool search requests, turn counts
- **Analysis**: Automatic savings calculation, detailed comparison tables, JSON export
- **Best For**: Understanding real-world token savings, optimizing costs

**Quick Start:**
```powershell
cd Testcases
pip install -r requirements.txt
python compare_token_usage.py
```

**Sample Output:**
```
Traditional (Baseline)         3275     302          3577         -            2        -
Embeddings Search              2156     288          2444         1            2        1133 (31.7%)
Regex Search                   2089     291          2380         1            2        1197 (33.5%)
BM25 Search                    2101     289          2390         1            2        1187 (33.2%)
```

[Full Documentation](./Testcases/README.md)

---

### 6. [MCP Tool Search Tool](./MCP-Tool-Search-Tool) 

**Combine Tool Search with Model Context Protocol** for dynamic tool discovery from remote servers.

- **What It Does**: Integrates with MCP servers (GitHub, Filesystem, Brave Search, etc.)
- **Capabilities**: Dynamic tool fetching, deferred loading, TOON format support
- **Token Savings**: 40-50% with deferred loading + TOON format
- **Best For**: Remote tool execution, multi-server orchestration, MCP ecosystem integration

**Quick Start:**
```powershell
cd MCP-Tool-Search-Tool
pip install -r requirements.txt
# Copy .env.example to .env and add API keys
python mcp_tool_search.py --query "List my GitHub repositories"
```

**Key Features:**
- **Three Loading Strategies**:
  - Baseline: Load all MCP tools upfront (default)
  - Deferred JSON: `--defer-mcp-tools-loading` (30-40% savings)
  - Deferred TOON: `--defer-mcp-tools-loading --toon` (40-50% savings)
  
**Comparison Testing:**
```powershell
cd Testcases
# Compare all three strategies with complex MCP queries
python compare_json_vs_toon.py
```

**Sample Output:**
```
Test Case: GitHub Repository Search
------------------------------------------------------------------------------------------
Strategy                          Input       Output      Total       Savings
------------------------------------------------------------------------------------------
1) MCP Baseline(JSON)             2845        312         3157        -
2) MCP Differ Tool Loading(JSON)  1523        298         1821        1336 (42.3%)
3) MCP Differ Tool Loading(TOON)  1245        298         1543        1614 (51.1%)
------------------------------------------------------------------------------------------
```

[Full Documentation](./MCP-Tool-Search-Tool/README.md)

---

## Recent Enhancements 

### Comprehensive Token Usage Tracking

All implementations now include detailed token tracking:

- **Per-turn metrics**: See token usage after each API call
- **Tool search counters**: Track `server_tool_use.tool_search_requests`
- **Conversation summaries**: Total input/output tokens and searches
- **Example output**:
  ```
  📊 Token usage for this turn:
     Input tokens: 2156
     Output tokens: 288
     Tool search requests: 1
  
  📊 TOKEN USAGE SUMMARY
  Total input tokens:  4312
  Total output tokens: 576
  Total tokens:        4888
  Tool search requests: 2
  ```

### JSON-Based Tool Library

Centralized tool definitions for easy maintenance and scalability:

- **40 tools** across 8 domains (Weather, Finance, Communication, Calendar, Files, Data, Travel, E-commerce)
- **Unified source**: `tools_library.json` used by all implementations
- **Easy expansion**: Add new tools in one place
- **Universal mocks**: Realistic test data for all tool types

### Robust Error Handling

Production-ready error handling across all scripts:

- Try-catch blocks around API calls
- Enhanced debug information (error type, HTTP status, message context)
- Response validation (empty content detection)
- Proper handling of built-in search tools

### Real-World Savings Demonstration

With 40 tools, you can now see actual benefits:

| Scenario | Traditional | Tool Search | Savings |
|----------|-------------|-------------|---------|
| Single tool query | ~3000 tokens | ~2000 tokens | **30-35%** |
| Multi-tool query | ~3500 tokens | ~2500 tokens | **25-30%** |
| Complex query | ~4000 tokens | ~3000 tokens | **20-25%** |

*Note: With only 8 tools, Claude often skips tool search as overhead > benefit. With 40+ tools, the savings become significant!*

---

## Feature Comparison

| Feature | Token Savings | Accuracy Gain | Latency | Best Use Case |
|---------|--------------|---------------|---------|---------------|
| **Tool Use Examples** | Minimal | +18% (72%→90%) | Same | Complex tools with usage patterns |
| **Tool Search Tool** | 30-35% | Maintained | Same | 40+ tools, dynamic discovery |
| **Programmatic Calling** | -37% | +10% | Lower | Large datasets, multi-step workflows |
| **MCP Tool Search Tool** | 40-50% | Maintained | Same | Remote MCP servers, multi-server orchestration |
| **Without Tool Search** | Baseline | Baseline | Baseline | Comparison reference, <20 tools |
| **Test Suite** | N/A | N/A | N/A | Token usage analysis, cost optimization |

---

## Prerequisites

- **Python**: 3.11 or higher
- **Anthropic API Key**: [Get one here](https://console.anthropic.com/)
- **Models**: Claude Sonnet 4 (`claude-sonnet-4-20250514`) or Claude Sonnet 3.5

---

## When to Use Each Feature

### Use Tool Use Examples when:
- You have complex nested structures
- Optional parameters need clear usage patterns
- Domain-specific conventions aren't obvious from schema
- You need high accuracy on format-sensitive parameters

### Use Tool Search Tool when:
- You have 50+ tools in your application
- Users need only a subset of tools per request
- Tools change frequently or are dynamically generated
- You want to reduce token costs from large tool definitions

### Use Programmatic Tool Calling when:
- Processing large datasets where only summaries are needed
- Running 3+ dependent tool calls in sequence
- Filtering/transforming data before Claude sees it
- Running parallel operations (e.g., checking 50 endpoints)
- Intermediate data shouldn't influence Claude's reasoning

---

## Repository Structure

```
claude-advanced-tool-use/
├── Tool-Use-Examples/           # 72% → 90% accuracy with input_examples
│   ├── README.md               # Detailed documentation
│   ├── without_examples.py     # Baseline (minimal schema)
│   ├── with_examples.py        # Enhanced (schema + examples)
│   ├── requirements.txt
│   └── .env.example
│
├── Tool-Search-Tool/            # Manage 50+ tools efficiently
│   ├── README.md               # Detailed documentation
│   ├── using-regex-or-bm25.py  # Text-based search
│   ├── using-embeddings.py     # Semantic search
│   ├── requirements.txt
│   └── .env.example
│
├── Programmatic-Tool-Calling/   # -37% tokens, orchestrate via code
│   ├── README.md               # Detailed documentation
│   ├── budget_compliance.py    # Demo implementation
│   ├── requirements.txt
│   └── .env.example
│
├── MCP-Tool-Search-Tool/        # MCP + Tool Search integration
│   ├── README.md               # Detailed documentation
│   ├── mcp_tool_search.py      # Main MCP tool search script
│   ├── mcp_servers_config.json # MCP server configuration
│   ├── requirements.txt
│   └── .env.example
│
├── Without-Tool-Search-Tool/    # Baseline: all tools upfront
│   ├── README.md               # Comparison baseline docs
│   ├── without_tool_search.py  # Traditional tool use
│   ├── requirements.txt
│   └── .env.example
│
├── Testcases/                   # Token usage comparison suite
│   ├── README.md               # Test documentation
│   ├── compare_token_usage.py  # Tool search comparisons
│   ├── compare_json_vs_toon.py # MCP strategy comparisons
│   ├── compare_mcp_token_usage_toon.py # MCP token tests
│   ├── requirements.txt
│   └── comparison_results.json # Test results
│
├── tools_library.json           # Shared 40-tool library
├── IMPLEMENTATION_SUMMARY.md    # Detailed implementation docs
└── README.md                    # This file
```

---

## Getting Started

### 1. Choose Your Feature

Pick the feature that best matches your use case from the comparison above.

### 2. Navigate to the Folder

```powershell
cd Tool-Use-Examples  # or Tool-Search-Tool, or Programmatic-Tool-Calling
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure API Key

```powershell
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 5. Run the Examples

Each folder contains interactive scripts that guide you through the features.

---

## Testing the Differences

### Tool Use Examples: See the Accuracy Improvement

Run both versions with the same prompt:

```powershell
cd Tool-Use-Examples

# Without examples (72% accuracy)
python without_examples.py
# Enter: "Create a critical ticket for login page returning 500 error, reported by Jane Smith, email jane@acme.com"

# With examples (90% accuracy)
python with_examples.py
# Enter the same prompt and compare the results
```

**Watch for:**
- Date format consistency (YYYY-MM-DD vs other formats)
- ID conventions (USR-XXXXX vs inconsistent patterns)
- Nested structure usage (when to include contact info)
- Parameter correlations (critical priority → escalation settings)

### Tool Search Tool: Query Large Libraries

```powershell
cd Tool-Search-Tool

# Test with different search methods
python using-regex-or-bm25.py
# Try: "I need to find user data" (searches through 100+ tools)

python using-embeddings.py
# Try: "calculate totals" (semantic understanding)
```

**Watch for:**
- Fast tool discovery from large libraries
- Accurate tool selection based on descriptions
- Token savings from not loading all tools

---

## Learning Path

**New to Claude Tool Use?** Start here:
1. [Anthropic Tool Use Docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
2. **Start with Tool Use Examples** - Easiest to understand and implement
3. **Scale up with Tool Search Tool** - When you have many tools
4. **Optimize with Programmatic Calling** - For performance-critical applications

---

## Beta Features & Headers

Some features require beta headers:

| Feature | Beta Header | Status |
|---------|-------------|--------|
| Tool Use Examples | `advanced-tool-use-2025-11-20` | Working |
| Tool Search Tool | `advanced-tool-use-2025-11-20` | Working |
| Programmatic Calling | `advanced-tool-use-2025-11-20`<br>`code-execution-2025-08-25` | SDK pending |

---

## Best Practices

### All Features
- Use descriptive tool names and descriptions
- Test with real-world scenarios
- Handle errors gracefully
- Keep tools idempotent (safe to retry)

### Tool Use Examples
- Show variety (2-4 examples covering different scenarios)
- Use realistic data formats
- Cover minimal and maximal parameter usage
- Keep examples consistent with each other

### Tool Search Tool
- Write clear, searchable tool descriptions
- Include relevant keywords and use cases
- Test search queries your users will actually make
- Consider semantic search for natural language queries

### Programmatic Tool Calling
- Document return formats clearly
- Use realistic descriptions for code generation
- Opt-in selectively via `allowed_callers`
- Keep operations safe for code execution

---

## Additional Resources

### Primary Reference
- **[Anthropic Advanced Tool Use Engineering Blog](https://www.anthropic.com/engineering/advanced-tool-use)** - The engineering post that inspired these implementations

### Official Documentation
- [Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Claude API Reference](https://docs.anthropic.com/en/api)
- [Beta Features Guide](https://docs.anthropic.com/en/api/versioning)

---

## Contributing

Found an issue or have an improvement? Feel free to:
- Open an issue
- Submit a pull request
- Share your use cases and results

---

## License

This repository contains implementations based on Anthropic's Advanced Tool Use documentation and examples.

---

## Quick Links

- [Tool Use Examples →](./Tool-Use-Examples/README.md)
- [Tool Search Tool →](./Tool-Search-Tool/README.md)
- [Programmatic Tool Calling →](./Programmatic-Tool-Calling/README.md)
- [MCP Tool Search Tool →](./MCP-Tool-Search-Tool/README.md)
- [Without Tool Search (Baseline) →](./Without-Tool-Search-Tool/README.md) 
- [Token Usage Test Suite →](./Testcases/README.md) 
- [Implementation Summary →](./IMPLEMENTATION_SUMMARY.md) 

---

**Built with Claude Sonnet 4** | **Updated December 2024**
