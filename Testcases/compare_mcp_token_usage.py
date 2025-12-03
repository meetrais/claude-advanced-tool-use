import subprocess
import re
import json
import os
import sys
from datetime import datetime

# Path to the MCP tool search script
MCP_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'MCP-Tool-Search-Tool', 'mcp_tool_search.py')
WORKING_DIR = os.path.join(os.path.dirname(__file__), '..', 'MCP-Tool-Search-Tool')

def run_mcp_script(query: str, defer: bool = False) -> dict:
    """
    Run the MCP tool search script and parse token usage.
    
    Args:
        query: The query to run
        defer: Whether to use deferred loading (--defer-mcp-tools-loading)
        
    Returns:
        Dictionary containing input_tokens, output_tokens, total_tokens
    """
    cmd = [sys.executable, MCP_SCRIPT_PATH, "--query", query]
    if defer:
        cmd.append("--defer-mcp-tools-loading")
        
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run the process and capture output
        # Set PYTHONIOENCODING to utf-8 to avoid encoding errors
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            cmd, 
            cwd=WORKING_DIR,
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            env=env
        )
        
        output = result.stdout
        
        # Check for errors
        if result.returncode != 0:
            print(f"Error running script: {result.stderr}")
            return None
            
        # Parse token usage from output
        # Looking for:
        # ================================================================================
        # 📊 TOKEN USAGE SUMMARY
        # ================================================================================
        # Total input tokens:  7932
        # Total output tokens: 303
        # Total tokens:        8235
        
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        
        input_match = re.search(r"Total input tokens:\s+(\d+)", output)
        if input_match:
            input_tokens = int(input_match.group(1))
            
        output_match = re.search(r"Total output tokens:\s+(\d+)", output)
        if output_match:
            output_tokens = int(output_match.group(1))
            
        total_match = re.search(r"Total tokens:\s+(\d+)", output)
        if total_match:
            total_tokens = int(total_match.group(1))
            
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "defer": defer
        }
        
    except Exception as e:
        print(f"Exception running script: {e}")
        return None

def main():
    print("\n" + "="*80)
    print("MCP TOOL SEARCH TOKEN USAGE COMPARISON")
    print("="*80)
    
    query = "Give me details about my GitHub repos."
    print(f"Test Query: {query}\n")
    
    # Run without defer (Baseline)
    print("1. Running WITHOUT deferred loading (Baseline)...")
    baseline_results = run_mcp_script(query, defer=False)
    
    if not baseline_results:
        print("Failed to run baseline test.")
        return

    print(f"   Input: {baseline_results['input_tokens']}, Output: {baseline_results['output_tokens']}, Total: {baseline_results['total_tokens']}\n")
    
    # Run with defer
    print("2. Running WITH deferred loading...")
    defer_results = run_mcp_script(query, defer=True)
    
    if not defer_results:
        print("Failed to run deferred test.")
        return

    print(f"   Input: {defer_results['input_tokens']}, Output: {defer_results['output_tokens']}, Total: {defer_results['total_tokens']}\n")
    
    # Compare results
    print("="*80)
    print("COMPARISON RESULTS")
    print("="*80)
    
    print(f"{'Metric':<20} {'Baseline (No Defer)':<20} {'Deferred Loading':<20} {'Difference':<15} {'% Savings':<15}")
    print("-" * 90)
    
    metrics = ["input_tokens", "output_tokens", "total_tokens"]
    for metric in metrics:
        base = baseline_results[metric]
        deferred = defer_results[metric]
        diff = base - deferred
        pct = (diff / base * 100) if base > 0 else 0
        
        print(f"{metric:<20} {base:<20} {deferred:<20} {diff:<15} {pct:.1f}%")
        
    print("-" * 90)
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "baseline": baseline_results,
        "deferred": defer_results
    }
    
    output_file = os.path.join(os.path.dirname(__file__), "mcp_comparison_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
