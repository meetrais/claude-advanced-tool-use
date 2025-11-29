"""
Tool Search with Built-in Regex/BM25: Scaling Claude with Native Tool Discovery

This implementation demonstrates how to use Anthropic's built-in tool search features
(regex or BM25) to scale Claude applications. Tools are marked with defer_loading=True,
and the API automatically handles tool discovery and loading on demand.
"""

import anthropic
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import argparse
import sys

# Load environment variables from .env file
load_dotenv()

# Define model constant for easy updates
MODEL = "claude-sonnet-4-5-20250929"

# Initialize Claude client (API key loaded from environment)
client = anthropic.Anthropic()

print("✓ Client initialized successfully")


# Define our comprehensive tool library with defer_loading
# All tools except the search tool itself are marked as deferred
def create_tool_library(search_method: str = "regex") -> List[Dict[str, Any]]:
    """
    Create the tool library with the appropriate search tool.
    
    Args:
        search_method: Either "regex" or "bm25"
    
    Returns:
        List of tool definitions including the search tool
    """
    
    # Choose the appropriate search tool
    if search_method == "regex":
        search_tool = {
            "type": "tool_search_tool_regex_20251119",
            "name": "tool_search_tool_regex"
        }
    else:  # bm25
        search_tool = {
            "type": "tool_search_tool_bm25_20251119",
            "name": "tool_search_tool_bm25"
        }
    
    # Define all available tools with defer_loading=True
    tools = [
        # The search tool itself (not deferred)
        search_tool,
        
        # Weather Tools (deferred)
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature",
                    },
                },
                "required": ["location"],
            },
            "defer_loading": True
        },
        {
            "name": "get_forecast",
            "description": "Get the weather forecast for multiple days ahead",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state",
                    },
                    "days": {
                        "type": "number",
                        "description": "Number of days to forecast (1-10)",
                    },
                },
                "required": ["location", "days"],
            },
            "defer_loading": True #<= Deferred loading
        },
        {
            "name": "get_timezone",
            "description": "Get the current timezone and time for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or timezone identifier",
                    }
                },
                "required": ["location"],
            },
            "defer_loading": True #<= Deferred loading
        },
        {
            "name": "get_air_quality",
            "description": "Get current air quality index and pollutant levels for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates",
                    }
                },
                "required": ["location"],
            },
            "defer_loading": True #<= Deferred loading
        },
        
        # Finance Tools (deferred)
        {
            "name": "get_stock_price",
            "description": "Get the current stock price and market data for a given ticker symbol",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL)",
                    },
                    "include_history": {
                        "type": "boolean",
                        "description": "Include historical data",
                    },
                },
                "required": ["ticker"],
            },
            "defer_loading": True #<= Deferred loading
        },
        {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another using current exchange rates",
            "input_schema": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount to convert",
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (e.g., USD)",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g., EUR)",
                    },
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
            "defer_loading": True #<= Deferred loading
        },
        {
            "name": "calculate_compound_interest",
            "description": "Calculate compound interest for investments over time",
            "input_schema": {
                "type": "object",
                "properties": {
                    "principal": {
                        "type": "number",
                        "description": "Initial investment amount",
                    },
                    "rate": {
                        "type": "number",
                        "description": "Annual interest rate (as percentage)",
                    },
                    "years": {"type": "number", "description": "Number of years"},
                    "frequency": {
                        "type": "string",
                        "enum": ["daily", "monthly", "quarterly", "annually"],
                        "description": "Compounding frequency",
                    },
                },
                "required": ["principal", "rate", "years"],
            },
            "defer_loading": True #<= Deferred loading
        },
        {
            "name": "get_market_news",
            "description": "Get recent financial news and market updates for a specific company or sector",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Company name, ticker symbol, or sector",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of news articles to return",
                    },
                },
                "required": ["query"],
            },
            "defer_loading": True #<= Deferred loading
        },
    ]
    
    return tools


def mock_tool_execution(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Generate realistic mock responses for tool executions.
    
    Args:
        tool_name: Name of the tool being executed
        tool_input: Input parameters for the tool
    
    Returns:
        Mock response string appropriate for the tool
    """
    # Weather tools
    if tool_name == "get_weather":
        location = tool_input.get("location", "Unknown")
        unit = tool_input.get("unit", "fahrenheit")
        temp = (
            random.randint(15, 30)
            if unit == "celsius"
            else random.randint(60, 85)
        )
        conditions = random.choice(["sunny", "partly cloudy", "cloudy", "rainy"])
        return json.dumps(
            {
                "location": location,
                "temperature": temp,
                "unit": unit,
                "conditions": conditions,
                "humidity": random.randint(40, 80),
                "wind_speed": random.randint(5, 20),
            }
        )

    elif tool_name == "get_forecast":
        location = tool_input.get("location", "Unknown")
        days = int(tool_input.get("days", 5))
        forecast = []
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append(
                {
                    "date": date,
                    "high": random.randint(20, 30),
                    "low": random.randint(10, 20),
                    "conditions": random.choice(
                        ["sunny", "cloudy", "rainy", "partly cloudy"]
                    ),
                }
            )
        return json.dumps({"location": location, "forecast": forecast})

    elif tool_name == "get_timezone":
        location = tool_input.get("location", "Unknown")
        return json.dumps(
            {
                "location": location,
                "timezone": "UTC+9",
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "utc_offset": "+09:00",
            }
        )

    elif tool_name == "get_air_quality":
        location = tool_input.get("location", "Unknown")
        aqi = random.randint(20, 150)
        categories = {
            (0, 50): "Good",
            (51, 100): "Moderate",
            (101, 150): "Unhealthy for Sensitive Groups",
        }
        category = next(
            cat for (low, high), cat in categories.items() if low <= aqi <= high
        )
        return json.dumps(
            {
                "location": location,
                "aqi": aqi,
                "category": category,
                "pollutants": {
                    "pm25": random.randint(5, 50),
                    "pm10": random.randint(10, 100),
                    "o3": random.randint(20, 80),
                },
            }
        )

    # Finance tools
    elif tool_name == "get_stock_price":
        ticker = tool_input.get("ticker", "UNKNOWN")
        return json.dumps(
            {
                "ticker": ticker,
                "price": round(random.uniform(100, 500), 2),
                "change": round(random.uniform(-5, 5), 2),
                "change_percent": round(random.uniform(-2, 2), 2),
                "volume": random.randint(1000000, 10000000),
                "market_cap": f"${random.randint(100, 1000)}B",
            }
        )

    elif tool_name == "convert_currency":
        amount = tool_input.get("amount", 0)
        from_currency = tool_input.get("from_currency", "USD")
        to_currency = tool_input.get("to_currency", "EUR")
        # Mock exchange rate
        rate = random.uniform(0.8, 1.2)
        converted = round(amount * rate, 2)
        return json.dumps(
            {
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": round(rate, 4),
                "converted_amount": converted,
            }
        )

    elif tool_name == "calculate_compound_interest":
        principal = tool_input.get("principal", 0)
        rate = tool_input.get("rate", 0)
        years = tool_input.get("years", 0)
        frequency = tool_input.get("frequency", "monthly")

        # Calculate compound interest
        n_map = {"daily": 365, "monthly": 12, "quarterly": 4, "annually": 1}
        n = n_map.get(frequency, 12)
        final_amount = principal * (1 + rate / 100 / n) ** (n * years)
        interest_earned = final_amount - principal

        return json.dumps(
            {
                "principal": principal,
                "rate": rate,
                "years": years,
                "compounding_frequency": frequency,
                "final_amount": round(final_amount, 2),
                "interest_earned": round(interest_earned, 2),
            }
        )

    elif tool_name == "get_market_news":
        query = tool_input.get("query", "")
        limit = tool_input.get("limit", 5)
        news = []
        for i in range(min(limit, 5)):
            news.append(
                {
                    "title": f"{query} - News Article {i+1}",
                    "source": random.choice(
                        [
                            "Bloomberg",
                            "Reuters",
                            "Financial Times",
                            "Wall Street Journal",
                        ]
                    ),
                    "published": (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "summary": f"Latest developments regarding {query}...",
                }
            )
        return json.dumps({"query": query, "articles": news, "count": len(news)})

    # Default fallback
    else:
        return json.dumps(
            {
                "status": "executed",
                "tool": tool_name,
                "message": f"Tool {tool_name} executed successfully with input: {json.dumps(tool_input)}",
            }
        )


def run_conversation(user_query: str, search_method: str = "regex", max_turns: int = 10) -> None:
    """
    Run a conversation with Claude using built-in tool search.
    
    Args:
        user_query: The user's question or request
        search_method: Either "regex" or "bm25"
        max_turns: Maximum number of conversation turns
    """
    print(f"\n{'='*80}")
    print(f"USER: {user_query}")
    print(f"Search Method: {search_method.upper()}")
    print(f"{'='*80}\n")
    
    # Create the tool library with the chosen search method
    tools = create_tool_library(search_method)
    
    # Initialize messages
    messages = [{"role": "user", "content": user_query}]
    
    turn = 0
    while turn < max_turns:
        turn += 1
        print(f"\n--- Turn {turn} ---")
        
        # Call Claude with all tool definitions (most are deferred)
        # IMPORTANT: Requires beta header for advanced tool use features
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            tools=tools,
            messages=messages,
            extra_headers={
                "anthropic-beta": "advanced-tool-use-2025-11-20"
            }
        )
        
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
                    
                    # The API handles tool_search_tool_regex and tool_search_tool_bm25 automatically
                    # We only need to handle our actual executable tools
                    if tool_name in ["tool_search_tool_regex", "tool_search_tool_bm25"]:
                        print(f"   ℹ️  Search tool handled automatically by API")
                        # The API will automatically return tool_reference blocks
                        # No need to provide a result for this
                        continue
                    
                    # Execute our custom tools
                    else:
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
    
    print(f"\n{'='*80}\n")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Tool Search with Built-in Regex/BM25 - Native tool discovery for Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for input)
  python using-regex-or-bm25.py
  
  # Ask a question with regex search (default)
  python using-regex-or-bm25.py --query "What's the weather in Tokyo?"
  
  # Ask a question with BM25 search
  python using-regex-or-bm25.py --query "Convert 100 USD to EUR" --method bm25
  
  # Run examples
  python using-regex-or-bm25.py --examples --method regex
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
        "-s", "--method",
        type=str,
        choices=["regex", "bm25"],
        default="regex",
        help="Tool search method: 'regex' or 'bm25' (default: regex)"
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
        print("Tool Search with Built-in Regex/BM25 - Interactive Mode")
        print("="*80)
        print("\nThis implementation uses Anthropic's built-in tool search features.")
        print("Tools are marked with defer_loading=True and loaded on demand.\n")
        print("Options:")
        print("  1. Enter a custom question")
        print("  2. Run example demonstrations")
        print("  3. Exit")
        print("\n" + "-"*80)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            query = input("\nEnter your question: ").strip()
            if not query:
                print("\n⚠️ No question provided. Exiting.")
                sys.exit(0)
            
            print("\nChoose search method:")
            print("  1. Regex (pattern matching)")
            print("  2. BM25 (probabilistic ranking)")
            method_choice = input("\nEnter your choice (1-2, default: 1): ").strip()
            
            search_method = "bm25" if method_choice == "2" else "regex"
            
            print("\n" + "="*80)
            run_conversation(query, search_method=search_method, max_turns=args.max_turns)
            
        elif choice == "2":
            print("\nChoose search method:")
            print("  1. Regex (pattern matching)")
            print("  2. BM25 (probabilistic ranking)")
            method_choice = input("\nEnter your choice (1-2, default: 1): ").strip()
            
            search_method = "bm25" if method_choice == "2" else "regex"
            
            print("\n" + "="*80)
            print(f"Running Example Demonstrations with {search_method.upper()}")
            print("="*80)
            
            # Example 1: Weather Query
            print("\n### Example 1: Weather Query ###")
            run_conversation(
                "What's the weather like in Tokyo?",
                search_method=search_method,
                max_turns=args.max_turns
            )
            
            # Example 2: Finance Query
            print("\n### Example 2: Finance Query ###")
            run_conversation(
                "If I invest $10,000 at 5% annual interest for 10 years with monthly compounding, how much will I have?",
                search_method=search_method,
                max_turns=args.max_turns
            )
            
            # Example 3: Mixed Query
            print("\n### Example 3: Mixed Query ###")
            run_conversation(
                "What's the current stock price of AAPL and what's the weather in San Francisco?",
                search_method=search_method,
                max_turns=args.max_turns
            )
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            sys.exit(0)
            
        else:
            print("\n⚠️ Invalid choice. Exiting.")
            sys.exit(1)
    
    # Run examples if requested via command line
    elif args.examples:
        print("\n" + "="*80)
        print(f"Tool Search Examples with {args.method.upper()}")
        print("="*80)
        
        # Example 1: Weather Query
        print("\n### Example 1: Weather Query ###")
        run_conversation(
            "What's the weather like in Tokyo?",
            search_method=args.method,
            max_turns=args.max_turns
        )
        
        # Example 2: Finance Query
        print("\n### Example 2: Finance Query ###")
        run_conversation(
            "If I invest $10,000 at 5% annual interest for 10 years with monthly compounding, how much will I have?",
            search_method=args.method,
            max_turns=args.max_turns
        )
        
        # Example 3: Mixed Query
        print("\n### Example 3: Mixed Query ###")
        run_conversation(
            "What's the current stock price of AAPL and what's the weather in San Francisco?",
            search_method=args.method,
            max_turns=args.max_turns
        )
    
    # Process user query if provided via command line
    elif args.query:
        run_conversation(args.query, search_method=args.method, max_turns=args.max_turns)


if __name__ == "__main__":
    main()
