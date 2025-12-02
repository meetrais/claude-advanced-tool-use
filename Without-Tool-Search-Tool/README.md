# Traditional Tool Use (Baseline)

This folder contains a **baseline implementation** of Claude's tool use without any tool search features. All tools are provided upfront in every API call, representing the traditional approach.

## Purpose

This implementation serves as a **comparison baseline** to demonstrate the differences between:

- **Traditional Approach (this folder)**: All tools sent with every API request
- **Tool Search Approach** (Tool-Search-Tool folder): Tools discovered dynamically on demand

## Key Characteristics

### Traditional Approach (Without Tool Search)

✅ **Simple Setup** - No embeddings or search infrastructure needed  
✅ **Straightforward** - Direct tool definitions sent to API  
❌ **Limited Scalability** - All tools sent every time (context window limits)  
❌ **Higher Token Costs** - All tool definitions consume input tokens on every call  
❌ **Fixed Tool Set** - Must know all tools upfront

## What's Included

- `without_tool_search.py` - Main implementation using traditional tool use
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and add your Anthropic API key
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Interactive Mode

Simply run the script and enter your question:

```bash
python without_tool_search.py
```

### Command-Line Query

Ask a question directly:

```bash
python without_tool_search.py --query "What's the weather in Tokyo?"
```

### Run Examples

Execute built-in example demonstrations:

```bash
python without_tool_search.py --examples
```

### Help

View all available options:

```bash
python without_tool_search.py --help
```

## Available Tools

The baseline implementation includes 8 tools across 2 domains:

### Weather Tools (4)
- `get_weather` - Current weather for a location
- `get_forecast` - Multi-day weather forecast
- `get_timezone` - Timezone and current time
- `get_air_quality` - Air quality index and pollutants

### Finance Tools (4)
- `get_stock_price` - Current stock price and market data
- `convert_currency` - Currency conversion with exchange rates
- `calculate_compound_interest` - Investment growth calculator
- `get_market_news` - Recent financial news

## Token Usage Tracking

The implementation includes comprehensive token usage tracking:

- **Per-turn metrics** - Input/output tokens for each API call
- **Total summary** - Cumulative token usage for the entire conversation
- **Comparison ready** - Use these metrics to compare with tool search approaches

## Example Output

```
================================================================================
USER: Convert 500 EUR to USD
================================================================================

--- Turn 1 ---

📊 Token usage for this turn:
   Input tokens: 1234
   Output tokens: 156

🔧 Tool invocation: convert_currency
   Input: {
     "amount": 500,
     "from_currency": "EUR",
     "to_currency": "USD"
   }
   ✅ Mock result: {"original_amount": 500, "from_currency": "EUR", ...}

--- Turn 2 ---

📊 Token usage for this turn:
   Input tokens: 1456
   Output tokens: 89

✓ Conversation complete

ASSISTANT: Based on the current exchange rate, 500 EUR = 596.01 USD.

================================================================================
📊 TOKEN USAGE SUMMARY
================================================================================
Total input tokens:  2690
Total output tokens: 245
Total tokens:        2935
================================================================================
```

## Comparison with Tool Search

### Token Usage Comparison

**Traditional Approach (this implementation):**
- Every API call includes ALL tool definitions in input tokens
- Higher token costs as you add more tools
- Context window consumed by tool definitions

**Tool Search Approach:**
- Only relevant tools loaded on demand
- Lower input token costs
- More efficient use of context window
- Scales to hundreds or thousands of tools

### When to Use Each Approach

**Use Traditional Approach When:**
- You have a small, fixed set of tools (< 20)
- Tools are frequently used
- Simplicity is preferred over optimization

**Use Tool Search When:**
- You have many tools (20+)
- Tools are domain-specific or specialized
- Optimizing token costs is important
- Scaling to hundreds/thousands of tools

## Next Steps

After running this baseline, try the tool search implementations:

1. **With Embeddings** - `Tool-Search-Tool/using-embeddings.py`  
   Uses semantic search to find relevant tools

2. **With Regex/BM25** - `Tool-Search-Tool/using-regex-or-bm25.py`  
   Uses Anthropic's built-in search tools

Compare the token usage between approaches to see the efficiency gains!

## Resources

- [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Claude API Reference](https://docs.anthropic.com/en/api/messages)
