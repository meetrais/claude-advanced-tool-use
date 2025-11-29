"""
Support Ticket System - WITH Tool Use Examples (Enhanced)

This demonstrates tool calling with input_examples that teach Claude:
- Correct date formats (YYYY-MM-DD)
- Proper ID conventions (USR-XXXXX)
- Appropriate nested structure usage
- Strong parameter correlations

Expected accuracy improvement: 72% → 90%
"""

import anthropic
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_ticket_tool_definition():
    """Returns the create_ticket tool definition WITH input_examples."""
    return {
        "name": "create_ticket",
        "description": """Creates a support ticket in the system. 
        
        Required fields: title
        Optional fields: priority, labels, reporter (with nested contact info), due_date, escalation settings
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Brief description of the ticket"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Priority level of the ticket"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for categorizing the ticket"
                },
                "reporter": {
                    "type": "object",
                    "description": "Information about the person reporting the ticket",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "User identifier"
                        },
                        "name": {
                            "type": "string",
                            "description": "User's full name"
                        },
                        "contact": {
                            "type": "object",
                            "description": "Contact information",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Email address"
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "Phone number"
                                }
                            }
                        }
                    }
                },
                "due_date": {
                    "type": "string",
                    "description": "Target completion date"
                },
                "escalation": {
                    "type": "object",
                    "description": "Escalation settings for urgent issues",
                    "properties": {
                        "level": {
                            "type": "integer",
                            "description": "Escalation level (1-3)"
                        },
                        "notify_manager": {
                            "type": "boolean",
                            "description": "Whether to notify the manager"
                        },
                        "sla_hours": {
                            "type": "integer",
                            "description": "SLA response time in hours"
                        }
                    }
                }
            },
            "required": ["title"]
        },
        # 🔑 KEY FEATURE: Tool Use Examples
        "input_examples": [
            # Example 1: Critical production bug - full details, escalation, tight SLA
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
                    "notify_manager": True,
                    "sla_hours": 4
                }
            },
            # Example 2: Feature request - reporter info, no escalation
            {
                "title": "Add dark mode support",
                "labels": ["feature-request", "ui"],
                "reporter": {
                    "id": "USR-67890",
                    "name": "Alex Chen"
                }
            },
            # Example 3: Simple internal task - minimal fields
            {
                "title": "Update API documentation"
            }
        ]
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
    print("Support Ticket System - WITH Tool Use Examples (Enhanced)")
    print("=" * 70)
    print("\nThis version includes input_examples that teach Claude:")
    print("  ✅ Correct date formats (YYYY-MM-DD)")
    print("  ✅ Proper ID conventions (USR-XXXXX)")
    print("  ✅ Appropriate nested structure usage")
    print("  ✅ Strong parameter correlations")
    print("\n  Expected accuracy: 90% (vs 72% without examples)")
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
    
    # Call Claude with beta header for advanced tool use features
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=tools,
        messages=messages,
        extra_headers={
            "anthropic-beta": "advanced-tool-use-2025-11-20"
        }
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
                messages=messages,
                extra_headers={
                    "anthropic-beta": "advanced-tool-use-2025-11-20"
                }
            )
            
            print(f"\n{'─' * 70}")
            print("Final Response:")
            print(f"{'─' * 70}")
            for final_block in final_response.content:
                if hasattr(final_block, "text"):
                    print(final_block.text)
    
    print(f"\n{'═' * 70}")
    print("✅ ANALYSIS: With tool use examples, you should see:")
    print("   - Consistent YYYY-MM-DD date format")
    print("   - Proper USR-XXXXX ID convention")
    print("   - Appropriate nested contact info for critical issues")
    print("   - Correct escalation correlation with priority level")
    print(f"{'═' * 70}\n")

if __name__ == "__main__":
    main()
