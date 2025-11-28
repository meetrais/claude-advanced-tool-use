"""
Tool Search with Embeddings: Scaling Claude to Thousands of Tools

This implementation demonstrates how to use semantic tool search to scale Claude applications
from dozens to thousands of tools by dynamically discovering relevant capabilities on demand.
"""

import anthropic
from sentence_transformers import SentenceTransformer
import numpy as np
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
claude_client = anthropic.Anthropic()

# Load the SentenceTransformer model
# all-MiniLM-L6-v2 is a lightweight model with 384 dimensional embeddings
# It will be downloaded from HuggingFace on first use
print("Loading SentenceTransformer model...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("✓ Clients initialized successfully")


# Define our tool library with 2 domains
TOOL_LIBRARY = [
    # Weather Tools
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
    },
    # Finance Tools
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
    },
]

print(f"✓ Defined {len(TOOL_LIBRARY)} tools in the library")


def tool_to_text(tool: Dict[str, Any]) -> str:
    """
    Convert a tool definition into a text representation for embedding.
    Combines the tool name, description, and parameter information.
    """
    text_parts = [
        f"Tool: {tool['name']}",
        f"Description: {tool['description']}",
    ]

    # Add parameter information
    if "input_schema" in tool and "properties" in tool["input_schema"]:
        params = tool["input_schema"]["properties"]
        param_descriptions = []
        for param_name, param_info in params.items():
            param_desc = param_info.get("description", "")
            param_type = param_info.get("type", "")
            param_descriptions.append(
                f"{param_name} ({param_type}): {param_desc}"
            )

        if param_descriptions:
            text_parts.append("Parameters: " + ", ".join(param_descriptions))

    return "\n".join(text_parts)


# Create embeddings for all tools
print("Creating embeddings for all tools...")

tool_texts = [tool_to_text(tool) for tool in TOOL_LIBRARY]

# Embed all tools at once using SentenceTransformer
# The model returns normalized embeddings by default
tool_embeddings = embedding_model.encode(tool_texts, convert_to_numpy=True)

print(f"✓ Created embeddings with shape: {tool_embeddings.shape}")
print(f"  - {tool_embeddings.shape[0]} tools")
print(f"  - {tool_embeddings.shape[1]} dimensions per embedding")


def search_tools(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for tools using semantic similarity.

    Args:
        query: Natural language description of what tool is needed
        top_k: Number of top tools to return

    Returns:
        List of tool definitions most relevant to the query
    """
    # Embed the query using SentenceTransformer
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)

    # Calculate cosine similarity using dot product
    # SentenceTransformer returns normalized embeddings, so dot product = cosine similarity
    similarities = np.dot(tool_embeddings, query_embedding)

    # Get top k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    # Return the corresponding tools with their scores
    results = []
    for idx in top_indices:
        results.append(
            {"tool": TOOL_LIBRARY[idx], "similarity_score": float(similarities[idx])}
        )

    return results


# The tool_search tool definition
TOOL_SEARCH_DEFINITION = {
    "name": "tool_search",
    "description": "Search for available tools that can help with a task. Returns tool definitions for matching tools. Use this when you need a tool but don't have it available yet.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language description of what kind of tool you need (e.g., 'weather information', 'currency conversion', 'stock prices')",
            },
            "top_k": {
                "type": "number",
                "description": "Number of tools to return (default: 5)",
            },
        },
        "required": ["query"],
    },
}

print("✓ Tool search definition created")


def handle_tool_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Handle a tool_search invocation and return tool references.

    Returns a list of tool_reference content blocks for discovered tools.
    """
    # Search for relevant tools
    results = search_tools(query, top_k=top_k)

    # Create tool_reference objects instead of full definitions
    tool_references = [
        {"type": "tool_reference", "tool_name": result["tool"]["name"]}
        for result in results
    ]

    print(f"\n🔍 Tool search: '{query}'")
    print(f"   Found {len(tool_references)} tools:")
    for i, result in enumerate(results, 1):
        print(
            f"   {i}. {result['tool']['name']} (similarity: {result['similarity_score']:.3f})"
        )

    return tool_references


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


print("✓ Mock tool execution function created")


def run_tool_search_conversation(user_message: str, max_turns: int = 5) -> None:
    """
    Run a conversation with Claude using the tool search pattern.

    Args:
        user_message: The initial user message
        max_turns: Maximum number of conversation turns
    """
    print(f"\n{'='*80}")
    print(f"USER: {user_message}")
    print(f"{'='*80}\n")

    # Initialize conversation with only tool_search available
    messages = [{"role": "user", "content": user_message}]

    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")

        # Call Claude with current message history
        response = claude_client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOL_LIBRARY + [TOOL_SEARCH_DEFINITION],
            messages=messages,
            # IMPORTANT: This beta header enables tool definitions in tool results
            extra_headers={
                "anthropic-beta": "advanced-tool-use-2025-11-20"
            },
        )

        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})

        # Check if we're done
        if response.stop_reason == "end_turn":
            print("\n✓ Conversation complete\n")
            # Print final response
            for block in response.content:
                if block.type == "text":
                    print(f"ASSISTANT: {block.text}")
            break

        # Handle tool uses
        if response.stop_reason == "tool_use":
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

                    if tool_name == "tool_search":
                        # Handle tool search
                        query = tool_input["query"]
                        top_k = tool_input.get("top_k", 5)

                        # Get tool references
                        tool_references = handle_tool_search(query, top_k)

                        # Create tool result with tool_reference content blocks
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": tool_references,
                            }
                        )
                    else:
                        # Execute the discovered tool with mock data
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

            # Add tool results to messages
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            print(f"\nUnexpected stop reason: {response.stop_reason}")
            break

    print(f"\n{'='*80}\n")


print("✓ Conversation loop implemented")


def main():
    """Main function to run examples or process user queries from command line."""
    parser = argparse.ArgumentParser(
        description="Tool Search with Embeddings - Semantic tool discovery for Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for input)
  python using-embeddings.py
  
  # Run example demonstrations
  python using-embeddings.py --examples
  
  # Ask a custom question
  python using-embeddings.py --query "What's the weather in Paris?"
  
  # Ask a question with custom max turns
  python using-embeddings.py --query "Convert 100 USD to EUR" --max-turns 3
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Your question or request for Claude to process using tool search"
    )
    
    parser.add_argument(
        "-e", "--examples",
        action="store_true",
        help="Run the built-in example demonstrations"
    )
    
    parser.add_argument(
        "-m", "--max-turns",
        type=int,
        default=5,
        help="Maximum number of conversation turns (default: 5)"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, enter interactive mode
    if not args.query and not args.examples:
        print("\n" + "="*80)
        print("Tool Search with Embeddings - Interactive Mode")
        print("="*80)
        print("\nWelcome! You can ask questions and Claude will use tool search to find")
        print("the right tools dynamically.\n")
        print("Options:")
        print("  1. Enter a custom question")
        print("  2. Run example demonstrations")
        print("  3. Exit")
        print("\n" + "-"*80)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            query = input("\nEnter your question: ").strip()
            if query:
                print("\n" + "="*80)
                run_tool_search_conversation(query, max_turns=args.max_turns)
            else:
                print("\n⚠️ No question provided. Exiting.")
                sys.exit(0)
                
        elif choice == "2":
            print("\n" + "="*80)
            print("Running Example Demonstrations")
            print("="*80)
            
            # Example 1: Weather Query
            print("\n### Example 1: Weather Query ###")
            run_tool_search_conversation("What's the weather like in Tokyo?", max_turns=args.max_turns)
            
            # Example 2: Finance Query
            print("\n### Example 2: Finance Query ###")
            run_tool_search_conversation(
                "If I invest $10,000 at 5% annual interest for 10 years with monthly compounding, how much will I have?",
                max_turns=args.max_turns
            )
            
            # Example 3: Mixed Query
            print("\n### Example 3: Mixed Query ###")
            run_tool_search_conversation(
                "What's the current stock price of AAPL and what's the weather in San Francisco?",
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
        print("Tool Search with Embeddings - Example Demonstrations")
        print("="*80)
        
        # Example 1: Weather Query
        print("\n### Example 1: Weather Query ###")
        run_tool_search_conversation("What's the weather like in Tokyo?", max_turns=args.max_turns)
        
        # Example 2: Finance Query
        print("\n### Example 2: Finance Query ###")
        run_tool_search_conversation(
            "If I invest $10,000 at 5% annual interest for 10 years with monthly compounding, how much will I have?",
            max_turns=args.max_turns
        )
        
        # Example 3: Mixed Query
        print("\n### Example 3: Mixed Query ###")
        run_tool_search_conversation(
            "What's the current stock price of AAPL and what's the weather in San Francisco?",
            max_turns=args.max_turns
        )
    
    # Process user query if provided via command line
    elif args.query:
        run_tool_search_conversation(args.query, max_turns=args.max_turns)


if __name__ == "__main__":
    main()
