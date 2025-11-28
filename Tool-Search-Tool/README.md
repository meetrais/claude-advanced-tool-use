# Tool Search with Embeddings

This implementation demonstrates how to scale Claude applications from dozens to thousands of tools using semantic tool search. Instead of providing all tool definitions upfront, Claude can dynamically discover relevant tools on demand, reducing context usage by 90%+ while enabling applications that scale to thousands of tools.

## Overview

Semantic tool search treats tools as discoverable resources. You give Claude a single `tool_search` tool that returns relevant capabilities on demand, cutting context usage dramatically while maintaining full functionality.

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

## Further Reading

- [Claude Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Tool Search Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#tool-search)
- [SentenceTransformers Documentation](https://www.sbert.net/)

## License

This implementation is based on Anthropic's Tool Search cookbook example.
