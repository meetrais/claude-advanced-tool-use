"""
Traditional Tool Use: All Tools Provided Upfront

This implementation demonstrates the traditional approach to tool use with Claude,
where ALL tools are provided in every API call. This serves as a baseline for
comparison with the tool search approaches.
"""

import anthropic
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import argparse
import sys
import os

# Load environment variables from .env file
load_dotenv()

# Define model constant for easy updates
MODEL = "claude-sonnet-4-5-20250929"

# Initialize Claude client (API key loaded from environment)
client = anthropic.Anthropic()

print("✓ Client initialized successfully")


# Load tool library from JSON file
def load_tools_from_json() -> List[Dict[str, Any]]:
    """Load tool definitions from the shared tools_library.json file."""
    # Get the path to the JSON file (one level up from this script)
    json_path = os.path.join(os.path.dirname(__file__), '..', 'tools_library.json')
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return data['tools']


# Load all tools from JSON
TOOL_LIBRARY = load_tools_from_json()

print(f"✓ Loaded {len(TOOL_LIBRARY)} tools from tools_library.json")


def mock_tool_execution(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Generate realistic mock responses for any tool execution.
    
    This is a universal mock that works for all tools by generating
    appropriate fake data based on common patterns.
    
    Args:
        tool_name: Name of the tool being executed
        tool_input: Input parameters for the tool
    
    Returns:
        Mock response string appropriate for the tool
    """
    # Create a generic success response with some fake data
    result = {
        "status": "success",
        "tool": tool_name,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Add specific mock data based on tool categories
    if "weather" in tool_name or "forecast" in tool_name:
        location = tool_input.get("location", "Unknown Location")
        result.update({
            "location": location,
            "temperature": random.randint(60, 85),
            "conditions": random.choice(["sunny", "partly cloudy", "cloudy", "rainy"]),
            "humidity": random.randint(40, 80),
        })
        
    elif "stock" in tool_name or "crypto" in tool_name:
        symbol = tool_input.get("ticker") or tool_input.get("symbol", "UNKNOWN")
        result.update({
            "symbol": symbol,
            "price": round(random.uniform(100, 500), 2),
            "change": round(random.uniform(-5, 5), 2),
            "volume": random.randint(1000000, 10000000),
        })
        
    elif "currency" in tool_name:
        amount = tool_input.get("amount", 100)
        from_curr = tool_input.get("from_currency", "USD")
        to_curr = tool_input.get("to_currency", "EUR")
        rate = random.uniform(0.8, 1.2)
        result.update({
            "original_amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "exchange_rate": round(rate, 4),
            "converted_amount": round(amount * rate, 2),
        })
        
    elif "interest" in tool_name or "mortgage" in tool_name:
        principal = tool_input.get("principal") or tool_input.get("loan_amount", 10000)
        rate = tool_input.get("rate") or tool_input.get("interest_rate", 5)
        years = tool_input.get("years") or tool_input.get("loan_term_years", 10)
        final_amount = principal * (1 + rate / 100) ** years
        result.update({
            "principal": principal,
            "rate": rate,
            "years": years,
            "final_amount": round(final_amount, 2),
            "total_interest": round(final_amount - principal, 2),
        })
        
    elif "email" in tool_name or "sms" in tool_name:
        to = tool_input.get("to") or tool_input.get("phone_number", ["recipient@example.com"])
        result.update({
            "message_id": f"msg_{random.randint(1000, 9999)}",
            "status": "sent",
            "recipients": to if isinstance(to, list) else [to],
            "sent_at": datetime.now().isoformat(),
        })
        
    elif "calendar" in tool_name or "event" in tool_name or "meeting" in tool_name:
        title = tool_input.get("title", "Meeting")
        result.update({
            "event_id": f"evt_{random.randint(1000, 9999)}",
            "title": title,
            "status": "created",
            "attendees": tool_input.get("attendees", []),
        })
        
    elif "file" in tool_name:
        path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("directory_path", "/unknown")
        result.update({
            "path": path,
            "size_bytes": random.randint(1000, 100000),
            "modified": datetime.now().isoformat(),
        })
        
    elif "search" in tool_name or "find" in tool_name:
        query = tool_input.get("query") or tool_input.get("pattern", "")
        num_results = random.randint(5, 20)
        result.update({
            "query": query,
            "results_count": num_results,
            "results": [f"Result {i+1}" for i in range(min(num_results, 3))],
        })
        
    elif "flight" in tool_name or "hotel" in tool_name or "travel" in tool_name:
        origin = tool_input.get("origin") or tool_input.get("location", "Unknown")
        destination = tool_input.get("destination", "Unknown")
        result.update({
            "origin": origin,
            "destination": destination,
            "options_found": random.randint(5, 15),
            "price_range": f"${random.randint(200, 800)} - ${random.randint(900, 2000)}",
        })
        
    elif "product" in tool_name or "shop" in tool_name or "cart" in tool_name:
        product_id = tool_input.get("product_id", "PROD123")
        result.update({
            "product_id": product_id,
            "price": round(random.uniform(20, 500), 2),
            "in_stock": random.choice([True, True, True, False]),
            "rating": round(random.uniform(3.5, 5.0), 1),
        })
    
    # Add the tool inputs to the result for reference
    result["inputs"] = tool_input
    
    return json.dumps(result)


print("✓ Universal mock tool execution function created")


def run_conversation(user_query: str, max_turns: int = 10) -> None:
    """
    Run a conversation with Claude using traditional tool use (all tools provided upfront).
    
    Args:
        user_query: The user's question or request
        max_turns: Maximum number of conversation turns
    """
    print(f"\n{'='*80}")
    print(f"USER: {user_query}")
    print(f"{'='*80}\n")
    
    # Initialize messages
    messages = [{"role": "user", "content": user_query}]
    
    # Initialize token usage tracking
    total_input_tokens = 0
    total_output_tokens = 0
    
    turn = 0
    while turn < max_turns:
        turn += 1
        print(f"\n--- Turn {turn} ---")
        
        try:
            # Call Claude with ALL tools provided upfront
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                tools=TOOL_LIBRARY,  # All tools sent with every request
                messages=messages,
            )
        except Exception as e:
            print(f"\n❌ Error calling API: {e}")
            print(f"   Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                print(f"   HTTP Status: {getattr(e.response, 'status_code', 'N/A')}")
            print(f"\n   Last message sent had {len(messages)} message(s)")
            if messages:
                print(f"   Last message role: {messages[-1]['role']}")
                print(f"   Last message content type: {type(messages[-1]['content'])}")
            break
        
        # Validate response has content
        if not response.content:
            print("\n⚠️ Warning: Response has no content")
            print(f"   Stop reason: {response.stop_reason}")
            break
        
        # Track token usage for this turn
        usage = response.usage
        turn_input_tokens = usage.input_tokens
        turn_output_tokens = usage.output_tokens
        
        # Accumulate totals
        total_input_tokens += turn_input_tokens
        total_output_tokens += turn_output_tokens
        
        # Display turn usage
        print(f"\n📊 Token usage for this turn:")
        print(f"   Input tokens: {turn_input_tokens}")
        print(f"   Output tokens: {turn_output_tokens}")
        
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # Handle different stop reasons
        if response.stop_reason == "end_turn":
            print("\n✓ Conversation complete\n")
            # Print final response
            for block in response.content:
                if block.type == "text":
                    print(f"ASSISTANT: {block.text}")
            break
            
        elif response.stop_reason == "tool_use":
            # Handle tool use requests
            tool_results = []
            
            for block in response.content:
                if block.type == "text":
                    print(f"\nASSISTANT: {block.text}")
                
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    print(f"\n🔧 Tool invocation: {tool_name}")
                    print(f"   Input: {json.dumps(tool_input, indent=2)}")
                    
                    # Execute the tool
                    mock_result = mock_tool_execution(tool_name, tool_input)
                    
                    # Print a preview of the result
                    if len(mock_result) > 150:
                        print(f"   ✅ Mock result: {mock_result[:150]}...")
                    else:
                        print(f"   ✅ Mock result: {mock_result}")
                    
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": mock_result,
                        }
                    )
            
            # Add tool results to messages if any
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        
        elif response.stop_reason == "max_tokens":
            print("\n⚠️ Reached max tokens limit")
            break
        
        else:
            print(f"\n⚠️ Unexpected stop reason: {response.stop_reason}")
            break
    
    if turn >= max_turns:
        print(f"\n⚠️ Reached maximum turns ({max_turns})")
    
    # Display token usage summary
    print(f"\n{'='*80}")
    print("📊 TOKEN USAGE SUMMARY")
    print(f"{'='*80}")
    print(f"Total input tokens:  {total_input_tokens}")
    print(f"Total output tokens: {total_output_tokens}")
    print(f"Total tokens:        {total_input_tokens + total_output_tokens}")
    print(f"{'='*80}\n")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Traditional Tool Use - All tools provided upfront (baseline)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for input)
  python without_tool_search.py
  
  # Ask a question directly
  python without_tool_search.py --query "What's the weather in Tokyo?"
  
  # Run examples
  python without_tool_search.py --examples
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Your question or request for Claude to process"
    )
    
    parser.add_argument(
        "-e", "--examples",
        action="store_true",
        help="Run the built-in example demonstrations"
    )
    
    parser.add_argument(
        "-m", "--max-turns",
        type=int,
        default=10,
        help="Maximum number of conversation turns (default: 10)"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, enter interactive mode
    if not args.query and not args.examples:
        print("\n" + "="*80)
        print("Traditional Tool Use (Baseline)")
        print("="*80)
        print("\nAll tools are provided upfront in every API call.\n")
        
        query = input("Enter your question: ").strip()
        
        if query:
            print("\n" + "="*80)
            run_conversation(query, max_turns=args.max_turns)
        else:
            print("\n⚠️ No question provided. Exiting.")
            sys.exit(0)
    
    # Run examples if requested via command line
    elif args.examples:
        print("\n" + "="*80)
        print("Traditional Tool Use Examples (Baseline)")
        print("="*80)
        
        # Example 1: Weather Query
        print("\n### Example 1: Weather Query ###")
        run_conversation(
            "What's the weather like in Tokyo?",
            max_turns=args.max_turns
        )
        
        # Example 2: Finance Query
        print("\n### Example 2: Finance Query ###")
        run_conversation(
            "If I invest $10,000 at 5% annual interest for 10 years with monthly compounding, how much will I have?",
            max_turns=args.max_turns
        )
        
        # Example 3: Mixed Query
        print("\n### Example 3: Mixed Query ###")
        run_conversation(
            "What's the current stock price of AAPL and what's the weather in San Francisco?",
            max_turns=args.max_turns
        )
    
    # Process user query if provided via command line
    elif args.query:
        run_conversation(args.query, max_turns=args.max_turns)


if __name__ == "__main__":
    main()
