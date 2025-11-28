# Tool Search for Claude - Two Approaches

This directory contains **two different implementations** for scaling Claude applications with tool search. Both enable Claude to dynamically discover tools on demand, reducing context usage by 90%+ while supporting thousands of tools.

## Choose Your Approach

### 1. Client-Side Embeddings (`using-embeddings.py`)
**Best for**: Full control, custom semantic search, experimentation

Client-side semantic search using SentenceTransformer embeddings. You compute embeddings locally and return matching tools via `tool_reference` blocks.

**Pros:**
- ✅ Full control over search algorithm
- ✅ Custom embedding models
- ✅ Works with any embedding provider
- ✅ Rich semantic understanding

**Cons:**
- ❌ Requires additional dependencies (SentenceTransformer, NumPy, PyTorch)
- ❌ More setup complexity
- ❌ Client manages embeddings

### 2. Built-in Regex/BM25 (`using-regex-or-bm25.py`)
**Best for**: Minimal setup, native integration, production use

Uses Anthropic's native tool search with `defer_loading`. The API automatically handles tool discovery using regex or BM25 algorithms.

**Pros:**
- ✅ Minimal dependencies (just Anthropic SDK)
- ✅ Native API integration
- ✅ No embedding management
- ✅ Choice of regex or BM25 search
- ✅ Optimized by Anthropic

**Cons:**
- ❌ Less customization
- ❌ Fixed to Anthropic's algorithms

---

## Quick Start

**For embeddings approach:**
```powershell
pip install -r requirements.txt
python using-embeddings.py
```

**For built-in search:**
```powershell
pip install anthropic python-dotenv
python using-regex-or-bm25.py
```

Both scripts support interactive mode and command-line arguments!

---

# Using Embeddings Implementation

## Overview

Client-side semantic search using SentenceTransformer. You provide Claude a custom `tool_search` tool that computes similarity and returns matching tools.

## Prerequisites

- Python 3.11 or higher
- Anthropic API key ([get one here](https://docs.anthropic.com/claude/reference/getting-started-with-the-api))

## Setup

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

Or install manually:
```powershell
pip install anthropic sentence-transformers numpy python-dotenv torch
```

### 2. Configure Environment Variables

Create or edit the `.env` file in this directory and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Interactive Mode (Recommended for Beginners)

Simply run the script without any arguments to enter interactive mode:

```powershell
python using-embeddings.py
```

You'll be presented with a menu:
1. Enter a custom question
2. Run example demonstrations
3. Exit

This is the easiest way to get started!

### Run Example Demonstrations

To see the tool search system in action with pre-built examples:

```powershell
python using-embeddings.py --examples
```

This will run three example conversations:
1. **Weather Query**: "What's the weather like in Tokyo?"
2. **Finance Query**: Compound interest calculation
3. **Mixed Query**: Stock price and weather information

### Ask Custom Questions

To ask your own questions from the command line:

```powershell
# Simple query
python using-embeddings.py --query "What's the weather in Paris?"

# Financial query
python using-embeddings.py --query "Convert 500 EUR to USD"

# Complex query
python using-embeddings.py --query "Get the stock price of GOOGL and calculate interest on $5000 at 3% for 5 years"
```

### Command-Line Options

- `-q, --query "your question"` - Ask a custom question
- `-e, --examples` - Run the built-in example demonstrations
- `-m, --max-turns N` - Set maximum conversation turns (default: 5)
- `-h, --help` - Show help message

### Examples

```powershell
# Run examples with custom max turns
python using-embeddings.py --examples --max-turns 10

# Ask a question with limited turns
python using-embeddings.py --query "What's the air quality in London?" --max-turns 3
```

## How It Works

### 1. Tool Embeddings
The system converts each tool definition into a semantic embedding using SentenceTransformer's `all-MiniLM-L6-v2` model. This lightweight model (384 dimensions) captures the meaning of each tool.

### 2. Semantic Search
When Claude calls `tool_search`, the system:
- Embeds the search query
- Calculates cosine similarity with all tool embeddings
- Returns the top-k most relevant tools

### 3. Dynamic Tool Loading
Claude receives tool definitions in tool results and can immediately use the discovered tools, enabling a scalable tool ecosystem without upfront context bloat.

## Key Features

- **Context Optimization**: Reduces initial context from thousands of tokens to just the `tool_search` definition
- **Scalable**: Works with 8 tools in this demo, but the pattern scales to hundreds or thousands
- **Semantic Discovery**: Claude can find tools using natural language queries rather than exact names
- **Mock Responses**: Includes realistic mock data for all tools (replace with real API calls in production)

## Tool Library

The implementation includes 8 tools across two domains:

### Weather Tools
- `get_weather`: Current weather for a location
- `get_forecast`: Multi-day weather forecast
- `get_timezone`: Timezone and time information
- `get_air_quality`: Air quality index and pollutants

### Finance Tools
- `get_stock_price`: Stock market data
- `convert_currency`: Currency conversion
- `calculate_compound_interest`: Investment calculations
- `get_market_news`: Financial news updates

## Customization

### Adding New Tools

Add tool definitions to the `TOOL_LIBRARY` list in `using-embeddings.py`:

```python
{
    "name": "your_tool_name",
    "description": "Clear description of what the tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param_name"]
    }
}
```

### Implementing Real Tool Execution

Replace the `mock_tool_execution` function with actual API calls or service integrations.

### Using Different Embedding Models

Change the embedding model by modifying:

```python
embedding_model = SentenceTransformer("your-model-name")
```

Consider larger models like `all-mpnet-base-v2` for better accuracy at the cost of performance.

## Architecture

```
User Query
    ↓
Claude (with tool_search)
    ↓
Semantic Search → Find relevant tools
    ↓
Return tool definitions
    ↓
Claude uses discovered tools
    ↓
Execute tools (mock/real)
    ↓
Final Response
```

## Performance Notes

- **First Run**: SentenceTransformer will download the model (~90MB)
- **Embedding Creation**: Done once at startup
- **Search Latency**: <10ms for queries against small tool libraries
- **Context Savings**: 90%+ reduction vs providing all tools upfront

## Production Considerations

1. **Cache Embeddings**: Persist embeddings to disk to avoid recomputing on every session
2. **Scale Testing**: Test with larger tool libraries (100s-1000s of tools)
3. **Hybrid Search**: Combine semantic search with keyword matching for better accuracy
4. **Tool Metadata**: Add usage stats, costs, or reliability scores to search ranking
5. **Real API Integration**: Replace mock responses with actual service calls

---

# Built-in Regex/BM25 Implementation

## Overview

Uses Anthropic's native tool search capabilities with `defer_loading: true`. The API automatically handles tool discovery using either regex pattern matching or BM25 probabilistic ranking.

## Prerequisites

- Python 3.11 or higher
- Anthropic API key

## Setup

### Install Minimal Dependencies

```powershell
pip install anthropic python-dotenv
```

The built-in approach requires **far fewer dependencies** than embeddings since it uses Anthropic's native search.

## Usage

### Interactive Mode

```powershell
python using-regex-or-bm25.py
```

You'll be prompted to:
1. Choose between custom question or examples
2. Select search method (regex or BM25)

### Command-Line Usage

**Regex search (default):**
```powershell
python using-regex-or-bm25.py --query "What's the weather in Tokyo?"
```

**BM25 search:**
```powershell
python using-regex-or-bm25.py --query "Convert 100 USD to EUR" --method bm25
```

**Run examples:**
```powershell
python using-regex-or-bm25.py --examples --method regex
```

### Command-Line Options

- `-q, --query "question"` - Ask a question
- `-e, --examples` - Run demonstrations
- `-s, --method [regex|bm25]` - Choose search method (default: regex)
- `-m, --max-turns N` - Max conversation turns (default: 10)
- `-h, --help` - Show help

## How It Works

### 1. Tools with defer_loading

Tools are marked to be loaded on demand:

```python
{
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": { ... },
    "defer_loading": True  # Loaded only when needed
}
```

### 2. Native Search Tool

The API includes the appropriate search tool:

```python
# Regex
{"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"}

# BM25
{"type": "tool_search_tool_bm25_20251119", "name": "tool_search_tool_bm25"}
```

### 3. Automatic Discovery

The API automatically:
- Searches for relevant tools when Claude needs them
- Returns `tool_reference` blocks
- Loads tools on demand
- Your code only handles actual tool executions

## Search Methods

### Regex Search
- **Best for**: Exact keyword matching, pattern-based discovery
- **Speed**: Very fast
- **Use when**: You know specific keywords in tool names/descriptions

### BM25 Search
- **Best for**: Relevance-based ranking, natural language queries
- **Speed**: Fast with better relevance scoring
- **Use when**: General purpose, complex multi-topic queries

## Configuration

Choose search method via:

1. **Interactive mode**: Select when prompted
2. **Command-line**: `--method regex` or `--method bm25`
3. **Code**: Modify `create_tool_library()` default parameter

## Comparison: Which Approach to Use?

| Criteria | Embeddings | Built-in Regex/BM25 |
|----------|-----------|-------------------|
| **Setup Complexity** | High (multiple deps) | Low (just Anthropic SDK) |
| **Dependencies** | 5+ packages | 2 packages |
| **Search Control** | Full customization | Fixed algorithms |
| **Semantic Understanding** | Excellent | Good |
| **Integration** | Manual | Native/Automatic |
| **Performance** | Client-side compute | Server-side optimized |
| **Use Case** | Research, custom needs | Production, simplicity |

**Choose Embeddings when:**
- You need custom semantic similarity
- You want to experiment with different models
- You have existing embedding infrastructure
- You need complete control over search logic

**Choose Built-in when:**
- You want minimal setup
- You prefer native Anthropic integration
- You need fast, reliable search
- You want the API to handle complexity

## Further Reading

- [Claude Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Advanced Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#advanced-tool-use)
- [Tool Search Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#tool-search)
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)

## License

These implementations are based on Anthropic's Tool Search cookbook examples.
