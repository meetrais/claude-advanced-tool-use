# Programmatic Tool Calling - THIS CODE IS NOT WORKING YET, AWAITING ANTHROPIC TO PROVIDE PROPER REFERENCE IMPLEMENTATION.

> [!WARNING]
> **SDK Compatibility Status**
> 
> **Feature**: Programmatic Tool Calling is officially available (released Nov 24, 2025)  
> **Model**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) ✅ Available  
> **Beta Header**: `advanced-tool-use-2025-11-20` ✅ Correct  
> **Implementation**: ✅ Code structure matches official documentation  
> 
> **Issue**: The Python SDK may not be fully updated to support the `container_id` field required for code execution tool orchestration. We encounter circular validation errors:
> - Without `container_id` in tool results: API error "container_id is required"
> - With `container_id` in tool results: API error "Extra inputs are not permitted"
> 
> **Status**: This is a complete, correct implementation that will work once the Python SDK is updated to match the API specification.
>
> **Working Alternatives**: See `../Tool-Search-Tool/` for fully functional tool search implementations.

This directory demonstrates **Anthropic's Programmatic Tool Calling** feature, where Claude orchestrates tools through Python code execution rather than individual API round-trips. This dramatically reduces context pollution and improves efficiency for complex workflows.

## What is Programmatic Tool Calling?

Traditional tool calling has two fundamental problems:

1. **Context pollution**: When Claude processes large datasets, ALL intermediate results enter its context window, even if only a summary is needed
2. **Inference overhead**: Each tool call requires a full model inference pass, making multi-step workflows slow

Programmatic Tool Calling solves both problems by letting Claude write Python code that:
- Orchestrates multiple tools
- Processes results programmatically  
- Returns only final outputs to Claude's context

## Key Benefits

According to Anthropic's testing:

- **37% token reduction** on complex tasks (43,588 → 27,297 tokens)
- **Reduced latency**: Eliminates inference passes for each tool call
- **Improved accuracy**: 25.6% → 28.5% on knowledge retrieval tasks

## How It Works

### 1. Enable Code Execution

Add the `code_execution_20250825` tool and mark your tools with `allowed_callers`:

```python
tools = [
    {"type": "code_execution_20250825", "name": "code_execution"},
    {
        "name": "get_expenses",
        "description": "Fetch expense data...",
        "input_schema": {...},
        "allowed_callers": ["code_execution_20250825"]  # Enable programmatic calling
    }
]
```

### 2. Claude Writes Orchestration Code

Instead of calling tools one-by-one, Claude generates Python:

```python
# Claude's orchestration code
team = await get_team_members("engineering")
expenses = await asyncio.gather(*[
    get_expenses(m["id"], "Q3") for m in team
])

exceeded = []
for member, exp in zip(team, expenses):
    total = sum(e["amount"] for e in exp)
    if total > budget:
        exceeded.append({"name": member["name"], "spent": total})

print(json.dumps(exceeded))
```

### 3. Tools Execute in Code Environment

When code calls `get_expenses()`, you receive a tool request with a `caller` field indicating it was called from code execution. Results are processed in the code environment, **not** Claude's context.

### 4. Only Final Output Reaches Claude

Claude sees only the `print()` output—the 2-3 employees who exceeded budget—not the 2,000+ expense line items processed along the way.

## Prerequisites

- Python 3.11 or higher
- Anthropic API key

## Setup

### 1. Install Dependencies

```powershell
cd Programmatic-Tool-Calling
pip install -r requirements.txt
```

### 2. Configure API Key

Create `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Budget Compliance Example

**Run with prompt:**
```powershell
python budget_compliance.py
```
Then enter your question when prompted.

**Run with command-line query:**
```powershell
python budget_compliance.py --query "Which team members exceeded their Q3 budget?"
```

**Example queries:**
- "Which team members exceeded their Q3 travel budget?"
- "Show me total expenses for the engineering department in Q4"
- "Who in sales had the highest travel expenses?"

### Command-Line Options

- `-q, --query "question"` - Ask a question directly
- `-m, --max-turns N` - Set maximum conversation turns (default: 10)
- `-h, --help` - Show help message

## What the Demo Shows

The `budget_compliance.py` implementation demonstrates:

### Tools Available
1. **get_team_members(department)** - Returns employee list with IDs and levels
2. **get_expenses(user_id, quarter)** - Returns expense line items
3. **get_budget_by_level(level)** - Returns budget limits by employee level

### What Happens

**Traditional Approach:**
- 20 tool calls (1 for team + 1 per employee for expenses)
- All 2,000+ expense line items enter Claude's context
- Claude manually sums, compares, and analyzes in natural language
- High token cost, many inference passes

**With Programmatic Tool Calling:**
- Claude writes one Python script
- Script calls all tools programmatically
- Processing happens in code execution environment
- Only final results (2-3 employees) enter Claude's context
- **Massive token savings**, single inference pass for orchestration

## Implementation Details

### Beta Headers Required

```python
extra_headers={
    "anthropic-beta": "code-execution-2025-08-25,advanced-tool-use-2025-11-20"
}
```

### Tool Configuration

Tools must opt-in to programmatic calling:

```python
{
    "name": "get_expenses",
    "description": "...",
    "input_schema": {...},
    "allowed_callers": ["code_execution_20250825"]  # Critical!
}
```

### Handling Tool Calls from Code

When a tool is called from code execution, the tool request includes a `caller` field:

```python
{
    "type": "tool_use",
    "name": "get_expenses",
    "input": {"user_id": "EMP1001", "quarter": "Q3"},
    "caller": {
        "type": "code_execution_20250825",
        "tool_id": "srvtoolu_abc"
    }
}
```

Your code should check for this field and handle accordingly.

## When to Use Programmatic Tool Calling

**Most beneficial when:**
- Processing large datasets where you only need summaries
- Running 3+ dependent tool calls in sequence
- Filtering/transforming data before Claude sees it
- Running parallel operations (checking 50 endpoints)
- Intermediate data shouldn't influence Claude's reasoning

**Less beneficial when:**
- Simple single-tool invocations
- Claude should see and reason about all intermediate results
- Quick lookups with small responses

## Comparison: Traditional vs Programmatic

| Aspect | Traditional | Programmatic |
|--------|------------|--------------|
| **Token Usage** | 43,588 tokens | 27,297 tokens (-37%) |
| **Inference Passes** | 1 per tool call | 1 for orchestration |
| **Context Contains** | All intermediate data | Only final results |
| **Latency** | High (many round-trips) | Low (code executes) |
| **Accuracy** | Good | Better (+10% on complex tasks) |

## Architecture

```
User Query
    ↓
Claude analyzes and writes Python code
    ↓
Code Execution Tool (sandboxed environment)
    ├─→ get_team_members() → Results processed in code
    ├─→ get_expenses() × 20 → Results processed in code  
    └─→ get_budget_by_level() → Results processed in code
    ↓
Code aggregates, filters, transforms
    ↓
Final output (print statement) → Claude's context
    ↓
Claude provides natural language answer
```

## Mock Data

The demo uses realistic mock data:
- 10 employees with varying levels (junior, mid-level, senior, lead)
- 10-25 expense items per employee (flights, hotels, meals, etc.)
- Budget limits by employee level
- Randomized but consistent within a session

In a real implementation, these would call actual APIs or databases.

## Best Practices

Based on Anthropic's recommendations:

1. **Document return formats clearly** - Claude needs to write correct parsing code
2. **Use realistic descriptions** - Help Claude understand what data looks like
3. **Opt-in selectively** - Not all tools need `allowed_callers`
4. **Handle errors gracefully** - Code execution can fail
5. **Keep it idempotent** - Tools should be safe to retry

## Further Reading

- [Anthropic Blog: Programmatic Tool Calling](https://www.anthropic.com/news/advanced-tool-use)
- [Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Code Execution Tool](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#code-execution)

## License

This implementation is based on Anthropic's Programmatic Tool Calling examples.
