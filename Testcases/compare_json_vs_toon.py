import subprocess
import re
import json
import os
import sys
from datetime import datetime

# Path to the MCP tool search script
MCP_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'MCP-Tool-Search-Tool', 'mcp_tool_search.py')
WORKING_DIR = os.path.join(os.path.dirname(__file__), '..', 'MCP-Tool-Search-Tool')

def run_mcp_script(query: str, defer: bool = False, toon: bool = False) -> dict:
    """
    Run the MCP tool search script and parse token usage.
    
    Args:
        query: The query to run
        defer: Whether to use deferred loading (--defer-mcp-tools-loading)
        toon: Whether to use TOON format (--toon)
        
    Returns:
        Dictionary containing input_tokens, output_tokens, total_tokens
    """
    cmd = [sys.executable, MCP_SCRIPT_PATH, "--query", query]
    if defer:
        cmd.append("--defer-mcp-tools-loading")
    if toon:
        cmd.append("--toon")
        
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
            
        if total_tokens == 0 and "Total tokens:" not in output:
             print("Warning: Could not parse token usage from output.")
             print("Raw Output Preview:")
             print(output[:1000]) # Print first 1000 chars
            
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "defer": defer,
            "toon": toon
        }
        
    except Exception as e:
        print(f"Exception running script: {e}")
        return None

def main():
    print("\n" + "="*90)
    print("MCP JSON vs TOON FORMAT COMPARISON")
    print("="*90)
    print("Comparing three strategies:")
    print("1. Baseline: Load all MCP tools upfront (JSON)")
    print("2. Deferred: Load MCP tools on demand (JSON)")
    print("3. Deferred + TOON: Load MCP tools on demand (TOON format)")
    print("-" * 90)
    
    # Complex queries that will trigger MCP tool loading
    queries = [
        {
            "name": "GitHub Repository Search",
            "query": "Search my GitHub repositories for projects related to Python and machine learning, then show me the most recent commits.",
            "description": "Tests GitHub MCP server with complex multi-step operations"
        },
        {
            "name": "Filesystem Operations",
            "query": "List all Python files in the current directory, read the contents of the largest one, and summarize what it does.",
            "description": "Tests Filesystem MCP server with file discovery and reading"
        },
        {
            "name": "Web Search and Analysis",
            "query": "Search the web for the latest developments in Claude AI capabilities, and create a summary of the top 3 findings.",
            "description": "Tests Brave Search MCP server with web queries"
        },
        {
            "name": "Multi-Server Complex Task",
            "query": "Find Python files in this project using filesystem tools, search GitHub for similar projects, and search the web for best practices related to the topics you find.",
            "description": "Tests coordination across multiple MCP servers"
        }
    ]
    
    all_results = []
    
    for q in queries:
        print(f"\n\nRunning Test: {q['name']}")
        print(f"Query: {q['query']}")
        print("-" * 50)
        
        # 1. Baseline (no flags)
        print("1. Running MCP Baseline (JSON)...")
        baseline = run_mcp_script(q['query'], defer=False, toon=False)
        if not baseline: 
            print("   ⚠️ Baseline test failed, skipping this query")
            continue
        
        # 2. Deferred (JSON)
        print("2. Running MCP Deferred Tool Loading (JSON)...")
        defer_json = run_mcp_script(q['query'], defer=True, toon=False)
        if not defer_json: 
            print("   ⚠️ Deferred JSON test failed, skipping this query")
            continue
        
        # 3. Deferred + TOON
        print("3. Running MCP Deferred Tool Loading (TOON)...")
        defer_toon = run_mcp_script(q['query'], defer=True, toon=True)
        if not defer_toon: 
            print("   ⚠️ Deferred TOON test failed, skipping this query")
            continue
        
        all_results.append({
            "query": q,
            "baseline": baseline,
            "defer_json": defer_json,
            "defer_toon": defer_toon
        })
    
    # Print Comprehensive Summary
    print("\n" + "="*90)
    print("COMPARISON SUMMARY")
    print("="*90)
    
    for res in all_results:
        name = res['query']['name']
        baseline = res['baseline']
        defer_json = res['defer_json']
        defer_toon = res['defer_toon']
        
        # Calculate savings vs Baseline (Total)
        b_total = baseline['total_tokens']
        dj_total = defer_json['total_tokens']
        dt_total = defer_toon['total_tokens']
        
        dj_save = b_total - dj_total
        dj_pct = (dj_save / b_total * 100) if b_total > 0 else 0
        
        dt_save = b_total - dt_total
        dt_pct = (dt_save / b_total * 100) if b_total > 0 else 0
        
        print(f"\nTest Case: {name}")
        print("-" * 90)
        print(f"{'Strategy':<34} {'Input':<11} {'Output':<11} {'Total':<11} {'Savings':<11}")
        print("-" * 90)
        
        # Baseline
        print(f"1) MCP Baseline(JSON)             {baseline['input_tokens']:<11} {baseline['output_tokens']:<11} {b_total:<11} {'-':<11}")
        
        # Deferred JSON
        print(f"2) MCP Differ Tool Loading(JSON)  {defer_json['input_tokens']:<11} {defer_json['output_tokens']:<11} {dj_total:<11} {f'{dj_save} ({dj_pct:.1f}%)':<11}")
        
        # Deferred TOON
        print(f"3) MCP Differ Tool Loading(TOON)  {defer_toon['input_tokens']:<11} {defer_toon['output_tokens']:<11} {dt_total:<11} {f'{dt_save} ({dt_pct:.1f}%)':<11}")
        print("-" * 90)

    # Save results
    output_file = os.path.join(os.path.dirname(__file__), "json_vs_toon_results.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
        
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    main()
