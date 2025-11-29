"""
Programmatic Tool Calling - Budget Compliance Example

This demonstrates Anthropic's Programmatic Tool Calling feature where Claude writes
Python code to orchestrate tools, keeping intermediate results out of context.

Example: "Which team members exceeded their Q3 travel budget?"
"""

import anthropic
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import random
import argparse
import sys

# Load environment variables
load_dotenv()

# Constants
MODEL = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5 - Supports programmatic tool calling

# Initialize Claude client
client = anthropic.Anthropic()

print("✓ Client initialized successfully")


# Mock data generators for realistic demonstrations
def generate_team_members(department: str) -> List[Dict[str, Any]]:
    """Generate mock team member data."""
    names = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", 
             "Emma Brown", "Frank Miller", "Grace Lee", "Henry Taylor",
             "Iris Chen", "Jack Anderson"]
    levels = ["junior", "mid-level", "senior", "lead"]
    
    members = []
    for i, name in enumerate(names):
        members.append({
            "id": f"EMP{1000 + i}",
            "name": name,
            "department": department,
            "level": random.choice(levels)
        })
    return members


def generate_expenses(user_id: str, quarter: str) -> List[Dict[str, Any]]:
    """Generate mock expense data."""
    expense_types = ["flight", "hotel", "meals", "taxi", "conference"]
    num_expenses = random.randint(10, 25)
    
    expenses = []
    for i in range(num_expenses):
        expenses.append({
            "id": f"EXP{i+1}",
            "user_id": user_id,
            "type": random.choice(expense_types),
            "amount": round(random.uniform(50, 800), 2),
            "date": f"2024-{quarter}",
            "description": f"{random.choice(expense_types)} expense"
        })
    return expenses


def generate_budget(level: str) -> Dict[str, Any]:
    """Generate mock budget data by employee level."""
    budgets = {
        "junior": {"level": "junior", "travel_limit": 5000, "quarterly_limit": 1500},
        "mid-level": {"level": "mid-level", "travel_limit": 8000, "quarterly_limit": 2500},
        "senior": {"level": "senior", "travel_limit": 12000, "quarterly_limit": 4000},
        "lead": {"level": "lead", "travel_limit": 15000, "quarterly_limit": 5000}
    }
    return budgets.get(level, budgets["junior"])


# Tool definitions with allowed_callers for programmatic execution
TOOLS = [
    {
        "type": "code_execution_20250825",
        "name": "code_execution"
    },
    {
        "name": "get_team_members",
        "description": """Get all members of a department.
        
Returns:
    List of team member objects, each containing:
    - id (str): Employee identifier (e.g., "EMP1001")
    - name (str): Full name
    - department (str): Department name
    - level (str): One of 'junior', 'mid-level', 'senior', 'lead'
""",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name (e.g., 'engineering', 'sales', 'marketing')"
                }
            },
            "required": ["department"]
        },
        "allowed_callers": ["code_execution_20250825"]  # Enable programmatic calling
    },
    {
        "name": "get_expenses",
        "description": """Retrieve expense line items for a specific user and quarter.
        
Returns:
    List of expense objects, each containing:
    - id (str): Expense identifier
    - user_id (str): Employee ID
    - type (str): Expense type (flight, hotel, meals, taxi, conference)
    - amount (float): Expense amount in USD
    - date (str): Date of expense
    - description (str): Expense description
""",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Employee ID (e.g., 'EMP1001')"
                },
                "quarter": {
                    "type": "string",
                    "description": "Quarter identifier (e.g., 'Q3', 'Q4')"
                }
            },
            "required": ["user_id", "quarter"]
        },
        "allowed_callers": ["code_execution_20250825"]  # Enable programmatic calling
    },
    {
        "name": "get_budget_by_level",
        "description": """Get budget limits for an employee level.
        
Returns:
    Budget object containing:
    - level (str): Employee level
    - travel_limit (float): Annual travel budget limit in USD
    - quarterly_limit (float): Quarterly travel budget limit in USD
""",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "description": "Employee level: 'junior', 'mid-level', 'senior', or 'lead'"
                }
            },
            "required": ["level"]
        },
        "allowed_callers": ["code_execution_20250825"]  # Enable programmatic calling
    }
]


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Execute a tool and return JSON result."""
    print(f"   🔧 Executing: {tool_name}")
    print(f"      Input: {json.dumps(tool_input, indent=6)}")
    
    if tool_name == "get_team_members":
        result = generate_team_members(tool_input["department"])
        
    elif tool_name == "get_expenses":
        result = generate_expenses(tool_input["user_id"], tool_input["quarter"])
        
    elif tool_name == "get_budget_by_level":
        result = generate_budget(tool_input["level"])
        
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    result_json = json.dumps(result)
    print(f"      ✅ Result: {len(result_json)} bytes")
    return result_json


def run_conversation(user_query: str, max_turns: int = 10) -> None:
    """Run a conversation with programmatic tool calling."""
    print(f"\n{'='*80}")
    print(f"USER QUERY: {user_query}")
    print(f"{'='*80}\n")
    
    messages = [{"role": "user", "content": user_query}]
    
    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")
        
        # 1. Get Raw Response to access Beta fields
        raw_response = client.messages.with_raw_response.create(
            model=MODEL,
            max_tokens=4096,
            tools=TOOLS,
            messages=messages,
            extra_headers={"anthropic-beta": "advanced-tool-use-2025-11-20"}
        )
        
        # 2. Parse JSON manually
        response_json = json.loads(raw_response.http_response.text)
        
        # 3. Parse SDK object for easy logic handling
        response = raw_response.parse()

        # --- FIX: PATCH CONTAINER ID ---
        # The 'container_id' is often top-level or needs to be explicitly propagated.
        # We look for it in the top-level 'container' field (common in code execution beta).
        container_id = None
        if "container" in response_json:
             container_id = response_json["container"].get("id")
             print(f"   [System] Container ID found: {container_id}")

        # If we found a container ID, we MUST inject it into any 'caller' fields
        # in the content blocks. The API requires this link for the next turn.
        if container_id:
            for block in response_json["content"]:
                if block.get("type") == "tool_use" and "caller" in block:
                    block["caller"]["container_id"] = container_id
        # -------------------------------

        # Add the (patched) content to history
        messages.append({"role": "assistant", "content": response_json["content"]})
        
        # Check stop reason
        if response.stop_reason == "end_turn":
            print("\n✓ Conversation complete\n")
            for block in response.content:
                if block.type == "text":
                    print(f"CLAUDE: {block.text}")
            break
        
        elif response.stop_reason == "tool_use":
            tool_results = []
            
            # Use the SDK parsed object for the loop (convenience)
            for block in response.content:
                if block.type == "text":
                    print(f"\nCLAUDE: {block.text}")
                
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    caller = getattr(block, 'caller', None)
                    if caller:
                        print(f"\n📝 Tool called from code: {tool_name}")
                    else:
                        print(f"\n🔧 Tool call: {tool_name}")
                    
                    # Execute tool based on name
                    if tool_name == "code_execution":
                        code = tool_input.get("code", "")
                        print(f"\n💻 Code Execution:") 
                        print(f"{'─'*80}")
                        print(code)
                        print(f"{'─'*80}")
                        # API handles code_execution result internally
                        continue
                    
                    elif tool_name in ["get_team_members", "get_expenses", "get_budget_by_level"]:
                        result = execute_tool(tool_name, tool_input)
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result
                        })
                        
                        if caller:
                            print(f"   ℹ️  Result will be available in code execution environment")
                    
                    else:
                        print(f"   ⚠️  Unknown tool: {tool_name}")
            
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        
        elif response.stop_reason == "max_tokens":
            print("\n⚠️  Reached max tokens")
            break
        
        else:
            print(f"\n⚠️  Unexpected stop reason: {response.stop_reason}")
            break
    
    if turn >= max_turns - 1:
        print(f"\n⚠️  Reached maximum turns ({max_turns})")
    
    print(f"\n{'='*80}\n") 

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Programmatic Tool Calling - Budget Compliance Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with command-line query
  python budget_compliance.py --query "Which team members exceeded their Q3 budget?"
  
  # Run and be prompted for input
  python budget_compliance.py
  
  # With custom max turns
  python budget_compliance.py --query "Show Q4 expenses for sales team" --max-turns 5
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Your question about budgets and expenses"
    )
    
    parser.add_argument(
        "-m", "--max-turns",
        type=int,
        default=10,
        help="Maximum conversation turns (default: 10)"
    )
    
    args = parser.parse_args()
    
    # If no query provided, prompt user for input
    if not args.query:
        print("\n" + "="*80)
        print("Programmatic Tool Calling - Budget Compliance Demo")
        print("="*80)
        print("\nThis demo shows how Claude orchestrates tools through code execution,")
        print("keeping intermediate results out of its context window.\n")
        print("Example queries:")
        print("  - Which team members exceeded their Q3 travel budget?")
        print("  - Show me total expenses for the engineering department in Q4")
        print("  - Who in sales had the highest travel expenses?")
        print("\n" + "-"*80)
        
        query = input("\nEnter your question: ").strip()
        
        if not query:
            print("\n⚠️  No question provided. Exiting.")
            sys.exit(0)
        
        run_conversation(query, max_turns=args.max_turns)
    else:
        run_conversation(args.query, max_turns=args.max_turns)


if __name__ == "__main__":
    main()
