"""
Programmatic Tool Calling - Data Analysis Example

This demonstrates how Programmatic Tool Calling handles large datasets efficiently
by processing data in the code execution environment and returning only summaries.

Example: "What are the top 5 products by revenue this quarter?"
"""

import anthropic
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import argparse
import sys

# Load environment variables
load_dotenv()

# Constants
MODEL = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5 - Supports programmatic tool calling

# Initialize Claude client
client = anthropic.Anthropic()

print("✓ Client initialized successfully")


# Mock data generators
def generate_sales_data(quarter: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """Generate mock sales transaction data."""
    products = [f"PROD{str(i).zfill(3)}" for i in range(1, 51)]
    regions = ["North", "South", "East", "West"]
    
    sales = []
    for i in range(limit):
        sale_date = datetime.now() - timedelta(days=random.randint(1, 90))
        sales.append({
            "transaction_id": f"TXN{str(i+1).zfill(6)}",
            "product_id": random.choice(products),
            "region": random.choice(regions),
            "quantity": random.randint(1, 20),
            "unit_price": round(random.uniform(10, 500), 2),
            "date": sale_date.strftime("%Y-%m-%d"),
            "quarter": quarter
        })
    return sales


def generate_customer_data(customer_ids: List[str]) -> List[Dict[str, Any]]:
    """Generate mock customer data."""
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    
    customers = []
    for cid in customer_ids:
        customers.append({
            "customer_id": cid,
            "name": f"Customer {cid}",
            "tier": random.choice(tiers),
            "lifetime_value": round(random.uniform(1000, 50000), 2),
            "join_date": (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d")
        })
    return customers


def generate_product_data(product_ids: List[str]) -> List[Dict[str, Any]]:
    """Generate mock product catalog data."""
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]
    
    products = []
    for pid in product_ids:
        products.append({
            "product_id": pid,
            "name": f"Product {pid}",
            "category": random.choice(categories),
            "cost": round(random.uniform(5, 250), 2),
            "retail_price": round(random.uniform(10, 500), 2)
        })
    return products


# Tool definitions with allowed_callers
TOOLS = [
    {
        "type": "code_execution_20250825",
        "name": "code_execution"
    },
    {
        "name": "fetch_sales_data",
        "description": """Fetch sales transaction data for a given quarter.
        
WARNING: Can return 1000+ transaction records. Use code to aggregate/filter.

Returns:
    List of transaction objects, each containing:
    - transaction_id (str): Unique transaction ID
    - product_id (str): Product identifier
    - region (str): Sales region (North/South/East/West)
    - quantity (int): Units sold
    - unit_price (float): Price per unit
    - date (str): Transaction date (YYYY-MM-DD)
    - quarter (str): Quarter identifier
""",
        "input_schema": {
            "type": "object",
            "properties": {
                "quarter": {
                    "type": "string",
                    "description": "Quarter to fetch (e.g., 'Q3', 'Q4')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max records to return (default: 1000)"
                }
            },
            "required": ["quarter"]
        },
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "fetch_customer_data",
        "description": """Fetch customer information by customer IDs.
        
Returns:
    List of customer objects, each containing:
    - customer_id (str): Customer identifier
    - name (str): Customer name
    - tier (str): Customer tier (Bronze/Silver/Gold/Platinum)
    - lifetime_value (float): Total customer value in USD
    - join_date (str): Date customer joined (YYYY-MM-DD)
""",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of customer IDs to fetch"
                }
            },
            "required": ["customer_ids"]
        },
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "fetch_product_data",
        "description": """Fetch product catalog information.
        
Returns:
    List of product objects, each containing:
    - product_id (str): Product identifier
    - name (str): Product name
    - category (str): Product category
    - cost (float): Cost to produce/acquire
    - retail_price (float): Retail selling price
""",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of product IDs to fetch"
                }
            },
            "required": ["product_ids"]
        },
        "allowed_callers": ["code_execution_20250825"]
    }
]


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Execute a tool and return JSON result."""
    print(f"   🔧 Executing: {tool_name}")
    print(f"      Input: {json.dumps(tool_input)}")
    
    if tool_name == "fetch_sales_data":
        quarter = tool_input["quarter"]
        limit = tool_input.get("limit", 1000)
        result = generate_sales_data(quarter, limit)
        
    elif tool_name == "fetch_customer_data":
        result = generate_customer_data(tool_input["customer_ids"])
        
    elif tool_name == "fetch_product_data":
        result = generate_product_data(tool_input["product_ids"])
        
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    result_json = json.dumps(result)
    print(f"      ✅ Result: {len(result_json)} bytes, {len(result)} records")
    return result_json


def run_conversation(user_query: str, max_turns: int = 10) -> None:
    """Run a conversation with programmatic tool calling."""
    print(f"\n{'='*80}")
    print(f"USER QUERY: {user_query}")
    print(f"{'='*80}\n")
    
    messages = [{"role": "user", "content": user_query}]
    
    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")
        
        # Call Claude with code execution enabled
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=TOOLS,
            messages=messages,
            # Enable the beta feature - ONLY need advanced-tool-use header
            extra_headers={"anthropic-beta": "advanced-tool-use-2025-11-20"}
        )
        
        # Add assistant response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # Check stop reason
        if response.stop_reason == "end_turn":
            print("\n✓ Conversation complete\n")
            for block in response.content:
                if block.type == "text":
                    print(f"CLAUDE: {block.text}")
            break
        
        elif response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if block.type == "text":
                    print(f"\nCLAUDE: {block.text}")
                
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    # Check if called from code execution (for logging only)
                    caller = getattr(block, 'caller', None)
                    if caller:
                        print(f"\n📝 Tool called from code: {tool_name}")
                        print(f"   Caller: {caller}")
                    else:
                        print(f"\n🔧 Tool call: {tool_name}")
                    
                    # Execute tool based on name
                    if tool_name == "code_execution":
                        # Code execution - API handles this
                        code = tool_input.get("code", "")
                        print(f"\n💻 Code Execution:")
                        print(f"{'─'*80}")
                        print(code)
                        print(f"{'─'*80}")
                        # Don't add tool_result for code_execution - API manages it
                        continue
                    
                    elif tool_name in ["fetch_sales_data", "fetch_customer_data", "fetch_product_data"]:
                        # Execute our custom tool
                        result = execute_tool(tool_name, tool_input)
                        
                        # Always add tool result (even if called from code)
                        # API requires tool_result blocks for all tool_use blocks
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result
                        })
                        
                        if caller:
                            print(f"   ℹ️  Result will be available in code execution environment")
                    
                    else:
                        print(f"   ⚠️  Unknown tool: {tool_name}")
            
            # Send tool results back
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
        description="Programmatic Tool Calling - Data Analysis Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with command-line query
  python data_analysis.py --query "What are the top 5 products by revenue?"
  
  # Run and be prompted for input
  python data_analysis.py
  
  # With custom max turns
  python data_analysis.py --query "Show regional sales breakdown" --max-turns 5
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Your question about sales data"
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
        print("Programmatic Tool Calling - Data Analysis Demo")
        print("="*80)
        print("\nThis demo shows how Claude processes large datasets efficiently")
        print("by aggregating data in code before returning results.\n")
        print("Example queries:")
        print("  - What are the top 5 products by revenue this quarter?")
        print("  - Show me total sales by region for Q4")
        print("  - Which product categories have the best profit margins?")
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
