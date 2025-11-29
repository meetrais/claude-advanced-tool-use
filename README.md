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

## Feature Comparison

| Feature | Token Savings | Accuracy Gain | Latency | Best Use Case |
|---------|--------------|---------------|---------|---------------|
| **Tool Use Examples** | Minimal | +18% (72%→90%) | Same | Complex tools with usage patterns |
| **Tool Search Tool** | High | Maintained | Same | 50+ tools, dynamic discovery |
| **Programmatic Calling** | -37% | +10% | Lower | Large datasets, multi-step workflows |

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

---

**Built with Claude Sonnet 4** | **Updated November 2024**
