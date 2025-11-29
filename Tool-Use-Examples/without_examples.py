"""
Support Ticket System - WITHOUT Tool Use Examples (Baseline)

This demonstrates traditional tool calling using only JSON Schema.
Shows common failure modes:
- Inconsistent date formats
- Varying ID conventions
- Unclear when to use nested structures
- Poor parameter correlations
"""

import anthropic
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_ticket_tool_definition():
    """Returns the create_ticket tool definition WITHOUT input_examples.
    
    This uses the minimal schema from Anthropic's reference documentation,
    without helpful descriptions. This demonstrates the challenge: the schema
    is valid, but doesn't convey usage patterns.
    """
    return {
        "name": "create_ticket",
        "input_schema": {
            "type": "object",
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

def create_ticket(title, priority=None, labels=None, reporter=None, due_date=None, escalation=None):
    """Mock function to create a ticket (simulates API call)."""
    ticket = {
        "id": "TICKET-001",
        "title": title,
        "status": "open",
        "created_at": "2024-11-28T20:00:00Z"
    }
    
    if priority:
        ticket["priority"] = priority
    if labels:
        ticket["labels"] = labels
    if reporter:
        ticket["reporter"] = reporter
    if due_date:
        ticket["due_date"] = due_date
    if escalation:
        ticket["escalation"] = escalation
    
    return ticket

def process_tool_call(tool_name, tool_input):
    """Process the tool call and return results."""
    if tool_name == "create_ticket":
        result = create_ticket(**tool_input)
        return result
    else:
        return {"error": f"Unknown tool: {tool_name}"}

def main():
    """Main function to run the ticket creation assistant."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print("=" * 70)
    print("Support Ticket System - WITHOUT Tool Use Examples (Baseline)")
    print("=" * 70)
    print("\nThis version uses only JSON Schema definitions.")
    print("You may see inconsistencies in:")
    print("  - Date formats (various formats)")
    print("  - ID conventions (inconsistent patterns)")
    print("  - Nested structure usage (unclear when to populate)")
    print("  - Parameter correlations (weak relationships)")
    print("\n" + "=" * 70)
    print("\nExamples to try:")
    print('  - "Create a critical ticket for login page returning 500 error, reported by Jane Smith, email jane@acme.com"')
    print('  - "Create a feature request for dark mode from Alex Chen"')
    print('  - "Create a ticket to update API docs"')
    print("=" * 70)
    
    # Get user input
    user_request = input("\nEnter your ticket request: ").strip()
    
    if not user_request:
        print("No request provided. Exiting.")
        return
    
    print(f"\n{'─' * 70}")
    print("Processing your request...")
    print(f"{'─' * 70}\n")
    
    # Create the conversation
    messages = [{"role": "user", "content": user_request}]
    tools = [get_ticket_tool_definition()]
    
    # Call Claude
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )
    
    # Process the response
    print("Claude's Analysis:")
    for block in response.content:
        if hasattr(block, "text") and block.text:
            print(f"  {block.text}")
        elif block.type == "tool_use":
            print(f"\n{'─' * 70}")
            print("Tool Call Details:")
            print(f"{'─' * 70}")
            print(f"Tool: {block.name}")
            print(f"\nParameters:")
            print(json.dumps(block.input, indent=2))
            
            # Execute the tool
            result = process_tool_call(block.name, block.input)
            
            print(f"\n{'─' * 70}")
            print("Ticket Created:")
            print(f"{'─' * 70}")
            print(json.dumps(result, indent=2))
            
            # Get final response from Claude
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                }]
            })
            
            final_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=tools,
                messages=messages
            )
            
            print(f"\n{'─' * 70}")
            print("Final Response:")
            print(f"{'─' * 70}")
            for final_block in final_response.content:
                if hasattr(final_block, "text"):
                    print(final_block.text)
    
    print(f"\n{'═' * 70}")
    print("⚠️  ANALYSIS: Without tool use examples, you may notice:")
    print("   - Inconsistent formatting conventions")
    print("   - Unclear parameter usage patterns")
    print("   - Missing correlations between related fields")
    print(f"{'═' * 70}\n")

if __name__ == "__main__":
    main()
