# Token Usage Comparison Test Suite

This folder contains automated tests that compare token usage across different tool search implementations.

## What It Tests

The test suite compares token usage between:

1. **Traditional Approach** (`Without-Tool-Search-Tool/without_tool_search.py`)
   - All tools provided upfront

2. **Embeddings Search** (`Tool-Search-Tool/using-embeddings.py`)
   - Semantic tool discovery

3. **Regex Search** (`Tool-Search-Tool/using-regex-or-bm25.py --method regex`)
   - Pattern-based tool discovery

4. **BM25 Search** (`Tool-Search-Tool/using-regex-or-bm25.py --method bm25`)
   - Probabilistic ranking tool discovery

## Test Queries

The suite includes 5 different query types:

1. **Single Weather Query** - Simple query requiring one weather tool
2. **Single Finance Query** - Simple query requiring one finance tool
3. **Compound Interest Calculation** - Complex finance query
4. **Mixed Domain Query** - Requires tools from both domains
5. **Multi-Tool Finance Query** - Requires multiple finance tools

## Setup

1. **Prerequisites**: Make sure all three implementations are set up with `.env` files containing your Anthropic API key.

2. **Install dependencies**:
   ```bash
   cd Testcases
   pip install -r requirements.txt
   ```

   Or use a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Environment variables**: The test will use the `.env` file from any of the implementation folders.

## Running Tests

### Run all tests

```bash
python compare_token_usage.py
```

This will:
- Run all 5 test queries against all 4 implementations
- Display a comprehensive comparison table
- Save detailed results to `comparison_results.json`

### Expected Output

```
================================================================================
TOOL SEARCH TOKEN USAGE COMPARISON TEST SUITE
================================================================================

Running tests across all implementations...
This may take a few minutes as it makes actual API calls.

Running Test 1/5: Single Weather Query
Query: What's the weather in Tokyo?
  - Running traditional (baseline)...
  - Running with embeddings...
  - Running with regex search...
  - Running with BM25 search...
  ✅ Test completed

...

================================================================================
TOKEN USAGE COMPARISON RESULTS
================================================================================

### Single Weather Query ###
Query: What's the weather in Tokyo?
Description: Simple query requiring one weather tool

------------------------------------------------------------------------------------------------------------------------
Method                         Input        Output       Total        Searches     Turns    Savings     
------------------------------------------------------------------------------------------------------------------------
Traditional (Baseline)         1234         156          1390         -            2        -           
Embeddings Search              856          152          1008         1            2        382 (27.5%) 
Regex Search                   834          150          984          1            2        406 (29.2%) 
BM25 Search                    834          150          984          1            2        406 (29.2%) 
------------------------------------------------------------------------------------------------------------------------

...

✅ Results saved to: comparison_results.json

================================================================================
COMPARISON TEST SUITE COMPLETE
================================================================================
```

## Understanding Results

### Comparison Table Columns

- **Method**: The implementation being tested
- **Input**: Total input tokens used
- **Output**: Total output tokens generated
- **Total**: Sum of input + output tokens
- **Searches**: Number of tool search requests made
- **Turns**: Number of conversation turns
- **Savings**: Token savings vs traditional approach (absolute and percentage)

### Key Metrics

**Token Savings**: Tool search approaches typically save 20-40% of tokens compared to the traditional approach, especially as the number of tools increases.

**Tool Search Requests**: Shows how many times the model searched for tools. More searches mean more dynamic tool discovery.

**Turns**: Should be similar across all approaches for the same query, showing they achieve the same result.

## Results File

The test saves detailed results to `comparison_results.json` with:

- Timestamp of when tests were run
- All test queries used
- Complete token usage breakdown for each query and method
- Raw data for further analysis

Example structure:
```json
{
  "timestamp": "2025-12-01T20:30:00",
  "test_queries": [...],
  "results": [
    {
      "name": "Single Weather Query",
      "query": "What's the weather in Tokyo?",
      "traditional": {
        "input_tokens": 1234,
        "output_tokens": 156,
        "total_tokens": 1390,
        "turns": 2
      },
      "embeddings": {
        "input_tokens": 856,
        "output_tokens": 152,
        "total_tokens": 1008,
        "tool_search_requests": 1,
        "turns": 2
      },
      ...
    }
  ]
}
```

## Important Notes

### API Costs

⚠️ **Warning**: This test suite makes real API calls to Anthropic's Claude API. Each test query is run 4 times (once per implementation), so running all 5 test queries = 20 API calls total.

Estimated cost: ~$0.10-0.30 per full test run (varies by response length)

### Rate Limits

If you hit rate limits, the tests will fail. Consider:
- Adding delays between tests
- Running fewer test queries
- Using a higher rate limit tier

### Test Duration

Expected runtime: 2-5 minutes depending on API response times and network latency.

## Customization

### Add Your Own Test Queries

Edit the `TEST_QUERIES` list in `compare_token_usage.py`:

```python
TEST_QUERIES = [
    {
        "name": "My Custom Test",
        "query": "Your question here",
        "description": "What this test demonstrates"
    },
    # ... more queries
]
```

### Modify Output Format

The `print_comparison_table()` and `save_results_to_json()` functions can be customized for different reporting formats.

## Troubleshooting

### Import Errors

If you see import errors, make sure:
- All three implementation folders have their dependencies installed
- The `.env` file with your API key is present
- You're running from the `Testcases` directory

### API Errors

If API calls fail:
- Check your API key is valid
- Verify you have sufficient credits
- Check if you're hitting rate limits

### Module Loading Errors

The test dynamically loads modules from parent directories. If this fails:
- Ensure directory structure matches the expected layout
- Run from the `Testcases` directory
- Check file paths in the script match your setup

## Next Steps

After running the tests:

1. **Analyze the results** - Look at which approach saves the most tokens for your use cases
2. **Scale testing** - Try with more tools to see how savings increase
3. **Cost optimization** - Use results to choose the best approach for your needs
4. **Custom metrics** - Extend the test suite to track additional metrics

## Resources

- [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Token Counting Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/token-counting)

---

## MCP Token Usage Comparison

This folder also contains specialized tests for comparing token usage across different MCP (Model Context Protocol) strategies, including JSON vs TOON format serialization.

### Available MCP Tests

#### 1. `compare_mcp_token_usage_toon.py`

Compares token usage across three MCP tool loading strategies with predefined test queries.

**Strategies tested:**
- **MCP Baseline (JSON)**: Load all MCP tools upfront using standard JSON format
- **MCP Deferred Tool Loading (JSON)**: Load MCP tools on-demand using JSON format
- **MCP Deferred Tool Loading (TOON)**: Load MCP tools on-demand using TOON format

**Usage:**
```bash
python compare_mcp_token_usage_toon.py
```

**Test Queries:**
- GitHub repository details
- Filesystem directory listing
- Brave web search
- Large file content reading

#### 2. `compare_json_vs_toon.py`

Performs comprehensive MCP token usage comparison across all three strategies with complex real-world queries.

**Usage:**
```bash
python compare_json_vs_toon.py
```

**Test Queries:**
- **GitHub Repository Search**: Multi-step operations (search repos + recent commits)
- **Filesystem Operations**: File discovery, reading, and summarization
- **Web Search and Analysis**: Search + analysis + summarization
- **Multi-Server Complex Task**: Coordination across multiple MCP servers

### Expected Output Format

Both scripts produce formatted comparison tables:

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

### Understanding MCP Comparison Results

**Key Differences:**
- **Baseline** loads all tools from MCP servers upfront (highest token usage)
- **Deferred (JSON)** loads tools only when needed (medium token usage)
- **Deferred (TOON)** loads tools on-demand with TOON serialization (lowest token usage)

**Savings Calculation:**
- Compares against the baseline (row 1)
- Shows both absolute token savings and percentage reduction

### Prerequisites for MCP Tests

1. **MCP Server Configuration**: Ensure `MCP-Tool-Search-Tool/mcp_servers_config.json` is properly configured

2. **Running MCP Servers**: Some tests require active MCP servers:
   ```bash
   # Example: GitHub MCP server
   npx -y @modelcontextprotocol/server-github
   ```

3. **Environment Variables**: Set required credentials in `.env` file:
   - `ANTHROPIC_API_KEY` - Your Anthropic API key
   - `GITHUB_TOKEN` - For GitHub MCP server (if using)
   - `BRAVE_API_KEY` - For Brave search MCP server (if using)

### Running MCP Tests

```bash
# Run basic MCP comparison
python compare_mcp_token_usage_toon.py

# Run comprehensive MCP comparison with complex queries
python compare_json_vs_toon.py
```

### MCP Test Results

Results are saved to JSON files:
- `compare_mcp_token_usage_toon.py` → `mcp_comprehensive_results.json`
- `compare_json_vs_toon.py` → `json_vs_toon_results.json`

### Important Notes for MCP Tests

⚠️ **Performance**: MCP tests take longer than standard tool search tests because they:
- Connect to remote MCP servers
- Load tools dynamically
- Execute actual tool operations
- Make multiple API calls per strategy

⚠️ **API Costs**: Each test query runs 3 times (one per strategy), so the comprehensive test makes 12 MCP operations total (4 queries × 3 strategies).

⚠️ **Network Requirements**: MCP tests require:
- Active internet connection
- Access to MCP server endpoints
- Valid API credentials for each MCP server

### Troubleshooting MCP Tests

**MCP Server Connection Fails:**
- Verify MCP servers are running (`npx -y @modelcontextprotocol/server-github`)
- Check `mcp_servers_config.json` configuration
- Ensure environment variables are set correctly

**Token Parsing Errors:**
- Check that `mcp_tool_search.py` completes successfully
- Verify output includes "Total tokens:" summary
- Review raw output logs for debugging

**Timeout Issues:**
- MCP servers may take 1-3 minutes on first run
- Increase timeout in server configuration if needed
- Check network connectivity and firewall settings

