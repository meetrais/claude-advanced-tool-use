# Tool Use Examples

This directory demonstrates Anthropic's **Tool Use Examples** feature, which dramatically improves Claude's accuracy when working with complex tools by providing concrete usage examples alongside JSON Schema definitions.

## The Challenge

JSON Schema excels at defining structure—types, required fields, allowed enums—but it can't express **usage patterns**: when to include optional parameters, which combinations make sense, or what conventions your API expects.

Consider a support ticket API:

```json
{
  "name": "create_ticket",
  "input_schema": {
    "properties": {
      "title": {"type": "string"},
      "priority": {"enum": ["low", "medium", "high", "critical"]},
      "labels": {"type": "array", "items": {"type": "string"}},
      "reporter": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "contact": {
            "type": "object",
            "properties": {
              "email": {"type": "string"},
              "phone": {"type": "string"}
            }
          }
        }
      },
      "due_date": {"type": "string"},
      "escalation": {
        "type": "object",
        "properties": {
          "level": {"type": "integer"},
          "notify_manager": {"type": "boolean"},
          "sla_hours": {"type": "integer"}
        }
      }
    },
    "required": ["title"]
  }
}
```

The schema defines what's valid, but leaves critical questions unanswered:

- **Format ambiguity**: Should `due_date` use "2024-11-06", "Nov 6, 2024", or "2024-11-06T00:00:00Z"?
- **ID conventions**: Is `reporter.id` a UUID, "USR-12345", or just "12345"?
- **Nested structure usage**: When should Claude populate `reporter.contact`?
- **Parameter correlations**: How do `escalation.level` and `escalation.sla_hours` relate to `priority`?

These ambiguities can lead to **malformed tool calls** and **inconsistent parameter usage**.

## The Solution

**Tool Use Examples** let you provide sample tool calls directly in your tool definitions. Instead of relying on schema alone, you show Claude concrete usage patterns:

```json
{
  "name": "create_ticket",
  "input_schema": { /* same schema as above */ },
  "input_examples": [
    {
      "title": "Login page returns 500 error",
      "priority": "critical",
      "labels": ["bug", "authentication", "production"],
      "reporter": {
        "id": "USR-12345",
        "name": "Jane Smith",
        "contact": {
          "email": "jane@acme.com",
          "phone": "+1-555-0123"
        }
      },
      "due_date": "2024-11-06",
      "escalation": {
        "level": 2,
        "notify_manager": true,
        "sla_hours": 4
      }
    },
    {
      "title": "Add dark mode support",
      "labels": ["feature-request", "ui"],
      "reporter": {
        "id": "USR-67890",
        "name": "Alex Chen"
      }
    },
    {
      "title": "Update API documentation"
    }
  ]
}
```

From these three examples, Claude learns:

- **Format conventions**: Dates use YYYY-MM-DD, user IDs follow USR-XXXXX, labels use kebab-case
- **Nested structure patterns**: How to construct the reporter object with its nested contact object
- **Optional parameter correlations**: Critical bugs have full contact info + escalation with tight SLAs; feature requests have reporter but no contact/escalation; internal tasks have title only

**Result**: In Anthropic's internal testing, tool use examples improved accuracy from **72% to 90%** on complex parameter handling.

## When to Use Tool Use Examples

Tool Use Examples add tokens to your tool definitions, so they're most valuable when accuracy improvements outweigh the additional cost.

**Most beneficial when:**
- Complex nested structures where valid JSON doesn't imply correct usage
- Tools with many optional parameters and inclusion patterns matter
- APIs with domain-specific conventions not captured in schemas
- Similar tools where examples clarify which one to use (e.g., `create_ticket` vs `create_incident`)

**Less beneficial when:**
- Simple single-parameter tools with obvious usage
- Standard formats like URLs or emails that Claude already understands
- Validation concerns better handled by JSON Schema constraints

## Prerequisites

- Python 3.11 or higher
- Anthropic API key

## Setup

### 1. Install Dependencies

```powershell
cd Tool-Use-Examples
pip install -r requirements.txt
```

### 2. Configure API Key

Create `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Without Tool Use Examples (Baseline)

```powershell
python without_examples.py
```

Then enter your request when prompted. This version uses only JSON Schema and will show common failure modes:
- Inconsistent date formats
- Varying ID conventions
- Unclear when to use nested structures
- Poor parameter correlations

**Example prompts to try:**
- "Create a critical ticket for login page returning 500 error, reported by Jane Smith, email jane@acme.com"
- "Create a feature request for dark mode from Alex Chen"
- "Create a ticket to update API docs"

### With Tool Use Examples (Enhanced)

```powershell
python with_examples.py
```

Then enter your request when prompted. This version includes `input_examples` and will show:
- Consistent YYYY-MM-DD date formats
- Proper USR-XXXXX ID conventions
- Appropriate nested structure usage
- Correct priority-escalation correlations

**Try the same prompts** as above and compare the results!

## What the Demo Shows

Both implementations (`without_examples.py` and `with_examples.py`) provide the same `create_ticket` tool, but with different definitions:

### Tool Capabilities

**create_ticket** - Creates a support ticket with:
- `title` (required) - Brief description
- `priority` - low, medium, high, or critical
- `labels` - Array of tags
- `reporter` - User info with optional nested contact details
- `due_date` - Target completion date
- `escalation` - Escalation settings for urgent issues

### Comparison

| Aspect | Without Examples | With Examples |
|--------|-----------------|---------------|
| **Accuracy** | ~72% | ~90% |
| **Date Formats** | Inconsistent | YYYY-MM-DD |
| **ID Conventions** | Varies | USR-XXXXX |
| **Nested Usage** | Unclear patterns | Appropriate depth |
| **Correlations** | Weak | Strong |

## Implementation Details

### Beta Header Required

Tool Use Examples is a beta feature that requires the `advanced-tool-use-2025-11-20` beta header:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    tools=tools,
    messages=messages,
    extra_headers={
        "anthropic-beta": "advanced-tool-use-2025-11-20"
    }
)
```

Without this header, the API will reject the `input_examples` field with an error:
```
tools.0.custom.input_examples: Extra inputs are not permitted
```

### Tool Definition Structure

**Without examples (minimal schema, no descriptions):**
```python
tools = [
    {
        "name": "create_ticket",
        "input_schema": {
            "properties": {
                "title": {"type": "string"},
                "priority": {"enum": ["low", "medium", "high", "critical"]},
                "labels": {"type": "array", "items": {"type": "string"}},
                "reporter": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "contact": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string"},
                                "phone": {"type": "string"}
                            }
                        }
                    }
                },
                "due_date": {"type": "string"},
                "escalation": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "integer"},
                        "notify_manager": {"type": "boolean"},
                        "sla_hours": {"type": "integer"}
                    }
                }
            },
            "required": ["title"]
        }
    }
]
```

**The schema is valid, but leaves critical questions unanswered:**
- What date format should `due_date` use?
- What pattern should `reporter.id` follow?
- When should Claude populate the nested `contact` object?
- How do `priority` and `escalation` relate?

**With examples (same minimal schema + input_examples):**
```python
tools = [
    {
        "name": "create_ticket",
        "input_schema": {
            # Same minimal schema as above
        },
        "input_examples": [
            {
                "title": "Login page returns 500 error",
                "priority": "critical",
                "labels": ["bug", "authentication", "production"],
                "reporter": {
                    "id": "USR-12345",  # ✅ Shows ID pattern
                    "name": "Jane Smith",
                    "contact": {
                        "email": "jane@acme.com",
                        "phone": "+1-555-0123"
                    }
                },
                "due_date": "2024-11-06",  # ✅ Shows date format
                "escalation": {  # ✅ Shows critical → escalation correlation
                    "level": 2,
                    "notify_manager": True,
                    "sla_hours": 4
                }
            },
            {
                "title": "Add dark mode support",
                "labels": ["feature-request", "ui"],
                "reporter": {
                    "id": "USR-67890",
                    "name": "Alex Chen"  # ✅ No contact for feature requests
                }
            },
            {
                "title": "Update API documentation"  # ✅ Minimal for simple tasks
            }
        ]
    }
]
```

**The examples teach Claude the patterns the schema cannot express.**

## Best Practices

Based on Anthropic's recommendations:

1. **Show variety** - Include examples for different scenarios (critical bugs, features, simple tasks)
2. **Demonstrate patterns** - Each example should teach a specific usage pattern
3. **Keep it realistic** - Use actual data formats and conventions from your system
4. **Cover edge cases** - Show minimal and maximal parameter usage
5. **Be consistent** - Examples should follow the same conventions
6. **Don't over-document** - 2-4 well-chosen examples are usually sufficient

## Further Reading

- [Anthropic Blog: Advanced Tool Use](https://www.anthropic.com/news/advanced-tool-use)
- [Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Tool Use Examples Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use#tool-use-examples)

## License

This implementation is based on Anthropic's Tool Use Examples documentation.
