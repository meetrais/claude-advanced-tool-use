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
