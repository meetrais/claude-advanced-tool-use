"""
Token Usage Comparison Test Suite

This script compares token usage across different tool search implementations:
1. Traditional (all tools upfront)
2. Tool Search with Embeddings
3. Tool Search with Regex/BM25

Tests multiple query types to demonstrate different scaling characteristics.
"""

import sys
import os
import importlib.util
import json
from typing import Dict, List, Tuple
from datetime import datetime
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test queries covering different scenarios
TEST_QUERIES = [
    {
        "name": "Single Weather Query",
        "query": "What's the weather in Tokyo?",
        "description": "Simple query requiring one weather tool"
    },
    {
        "name": "Single Finance Query",
        "query": "Convert 500 EUR to USD",
        "description": "Simple query requiring one finance tool"
    },
    {
        "name": "Compound Interest Calculation",
        "query": "If I invest $10,000 at 5% annual interest for 10 years with monthly compounding, how much will I have?",
        "description": "Complex finance query"
    },
    {
        "name": "Mixed Domain Query",
        "query": "What's the current stock price of AAPL and what's the weather in San Francisco?",
        "description": "Query requiring tools from both domains"
    },
    {
        "name": "Multi-Tool Finance Query",
        "query": "Get the stock price of GOOGL and calculate interest on $5000 at 3% for 5 years",
        "description": "Query requiring multiple finance tools"
    },
]


def load_module_from_file(filepath: str, module_name: str):
    """Dynamically load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_test_without_tool_search(query: str) -> Dict:
    """Run a test query using the traditional approach."""
    # Import the module
    module_path = os.path.join(os.path.dirname(__file__), '..', 'Without-Tool-Search-Tool', 'without_tool_search.py')
    module = load_module_from_file(module_path, 'without_tool_search')
    
    client = module.client
    messages = [{"role": "user", "content": query}]
    
    total_input_tokens = 0
    total_output_tokens = 0
    turns = 0
    
    # Run conversation
    for turn in range(10):
        turns += 1
        
        response = client.messages.create(
            model=module.MODEL,
            max_tokens=2048,
            tools=module.TOOL_LIBRARY,
            messages=messages,
        )
        
        # Track tokens
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens
        
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason == "end_turn":
            break
        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    mock_result = module.mock_tool_execution(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": mock_result,
                    })
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            break
    
    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "turns": turns
    }


def run_test_with_embeddings(query: str) -> Dict:
    """Run a test query using embeddings-based tool search."""
    # Import the module
    module_path = os.path.join(os.path.dirname(__file__), '..', 'Tool-Search-Tool', 'using-embeddings.py')
    module = load_module_from_file(module_path, 'using_embeddings')
    
    client = module.claude_client
    messages = [{"role": "user", "content": query}]
    
    total_input_tokens = 0
    total_output_tokens = 0
    total_tool_search_requests = 0
    turns = 0
    
    # Run conversation
    for turn in range(10):
        turns += 1
        
        response = client.messages.create(
            model=module.MODEL,
            max_tokens=1024,
            tools=module.TOOL_LIBRARY + [module.TOOL_SEARCH_DEFINITION],
            messages=messages,
            extra_headers={
                "anthropic-beta": "advanced-tool-use-2025-11-20"
            },
        )
        
        # Track tokens
        usage = response.usage
        total_input_tokens += usage.input_tokens
        total_output_tokens += usage.output_tokens
        
        if hasattr(usage, 'server_tool_use') and usage.server_tool_use:
            if hasattr(usage.server_tool_use, 'tool_search_requests'):
                total_tool_search_requests += usage.server_tool_use.tool_search_requests
        
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason == "end_turn":
            break
        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "tool_search":
                        tool_references = module.handle_tool_search(
                            block.input["query"],
                            block.input.get("top_k", 5)
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_references,
                        })
                    else:
                        mock_result = module.mock_tool_execution(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": mock_result,
                        })
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            break
    
    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "tool_search_requests": total_tool_search_requests,
        "turns": turns
    }


def run_test_with_regex_or_bm25(query: str, method: str = "regex") -> Dict:
    """Run a test query using regex or BM25 tool search."""
    # Import the module
    module_path = os.path.join(os.path.dirname(__file__), '..', 'Tool-Search-Tool', 'using-regex-or-bm25.py')
    module = load_module_from_file(module_path, 'using_regex_bm25')
    
    client = module.client
    tools = module.create_tool_library(method)
    messages = [{"role": "user", "content": query}]
    
    total_input_tokens = 0
    total_output_tokens = 0
    total_tool_search_requests = 0
    turns = 0
    
    # Run conversation
    for turn in range(10):
        turns += 1
        
        response = client.messages.create(
            model=module.MODEL,
            max_tokens=2048,
            tools=tools,
            messages=messages,
            extra_headers={
                "anthropic-beta": "advanced-tool-use-2025-11-20"
            }
        )
        
        # Track tokens
        usage = response.usage
        total_input_tokens += usage.input_tokens
        total_output_tokens += usage.output_tokens
        
        if hasattr(usage, 'server_tool_use') and usage.server_tool_use:
            if hasattr(usage.server_tool_use, 'tool_search_requests'):
                total_tool_search_requests += usage.server_tool_use.tool_search_requests
        
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason == "end_turn":
            break
        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name in ["tool_search_tool_regex", "tool_search_tool_bm25"]:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "",
                        })
                    else:
                        mock_result = module.mock_tool_execution(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": mock_result,
                        })
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            break
    
    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "tool_search_requests": total_tool_search_requests,
        "turns": turns
    }


def print_comparison_table(results: Dict):
    """Print a formatted comparison table."""
    print("\n" + "="*120)
    print("TOKEN USAGE COMPARISON RESULTS")
    print("="*120)
    
    for test_case in results:
        print(f"\n### {test_case['name']} ###")
        print(f"Query: {test_case['query']}")
        print(f"Description: {test_case['description']}")
        print("\n" + "-"*120)
        
        # Header
        print(f"{'Method':<30} {'Input':<12} {'Output':<12} {'Total':<12} {'Searches':<12} {'Turns':<8} {'Savings':<12}")
        print("-"*120)
        
        # Traditional baseline
        trad = test_case['traditional']
        print(f"{'Traditional (Baseline)':<30} {trad['input_tokens']:<12} {trad['output_tokens']:<12} {trad['total_tokens']:<12} {'-':<12} {trad['turns']:<8} {'-':<12}")
        
        # Embeddings
        emb = test_case['embeddings']
        emb_savings = trad['total_tokens'] - emb['total_tokens']
        emb_pct = (emb_savings / trad['total_tokens'] * 100) if trad['total_tokens'] > 0 else 0
        print(f"{'Embeddings Search':<30} {emb['input_tokens']:<12} {emb['output_tokens']:<12} {emb['total_tokens']:<12} {emb['tool_search_requests']:<12} {emb['turns']:<8} {f'{emb_savings} ({emb_pct:.1f}%)':<12}")
        
        # Regex
        regex = test_case['regex']
        regex_savings = trad['total_tokens'] - regex['total_tokens']
        regex_pct = (regex_savings / trad['total_tokens'] * 100) if trad['total_tokens'] > 0 else 0
        print(f"{'Regex Search':<30} {regex['input_tokens']:<12} {regex['output_tokens']:<12} {regex['total_tokens']:<12} {regex['tool_search_requests']:<12} {regex['turns']:<8} {f'{regex_savings} ({regex_pct:.1f}%)':<12}")
        
        # BM25
        bm25 = test_case['bm25']
        bm25_savings = trad['total_tokens'] - bm25['total_tokens']
        bm25_pct = (bm25_savings / trad['total_tokens'] * 100) if trad['total_tokens'] > 0 else 0
        print(f"{'BM25 Search':<30} {bm25['input_tokens']:<12} {bm25['output_tokens']:<12} {bm25['total_tokens']:<12} {bm25['tool_search_requests']:<12} {bm25['turns']:<8} {f'{bm25_savings} ({bm25_pct:.1f}%)':<12}")
        
        print("-"*120)


def save_results_to_json(results: Dict, filename: str = "comparison_results.json"):
    """Save results to a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    # Add metadata
    output = {
        "timestamp": datetime.now().isoformat(),
        "test_queries": TEST_QUERIES,
        "results": results
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: {filepath}")


def main():
    """Run all test cases and compare results."""
    print("\n" + "="*120)
    print("TOOL SEARCH TOKEN USAGE COMPARISON TEST SUITE")
    print("="*120)
    print("\nRunning tests across all implementations...")
    print("This may take a few minutes as it makes actual API calls.\n")
    
    results = []
    
    for i, test_query in enumerate(TEST_QUERIES, 1):
        print(f"\nRunning Test {i}/{len(TEST_QUERIES)}: {test_query['name']}")
        print(f"Query: {test_query['query']}")
        
        try:
            # Run traditional
            print("  - Running traditional (baseline)...")
            traditional_result = run_test_without_tool_search(test_query['query'])
            
            # Run embeddings
            print("  - Running with embeddings...")
            embeddings_result = run_test_with_embeddings(test_query['query'])
            
            # Run regex
            print("  - Running with regex search...")
            regex_result = run_test_with_regex_or_bm25(test_query['query'], "regex")
            
            # Run BM25
            print("  - Running with BM25 search...")
            bm25_result = run_test_with_regex_or_bm25(test_query['query'], "bm25")
            
            results.append({
                "name": test_query['name'],
                "query": test_query['query'],
                "description": test_query['description'],
                "traditional": traditional_result,
                "embeddings": embeddings_result,
                "regex": regex_result,
                "bm25": bm25_result
            })
            
            print("  ✅ Test completed")
            
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            continue
    
    # Print comparison table
    print_comparison_table(results)
    
    # Save results to JSON
    save_results_to_json(results)
    
    print("\n" + "="*120)
    print("COMPARISON TEST SUITE COMPLETE")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()
