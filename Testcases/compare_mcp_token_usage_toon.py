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
    print("\n" + "="*100)
    print("COMPREHENSIVE MCP TOKEN USAGE COMPARISON")
    print("="*100)
    print("Comparing three strategies:")
    print("1. Baseline: Load all tools upfront (JSON)")
    print("2. Deferred: Load tools on demand (JSON)")
    print("3. Deferred + TOON: Load tools on demand (TOON format)")
    print("-" * 100)
    
    queries = [
        {
            "name": "GitHub Repos",
            "query": "Give me details about my GitHub repos.",
            "description": "Tests GitHub MCP server tool retrieval"
        },
        {
            "name": "Filesystem List",
            "query": "List the files in the current directory.",
            "description": "Tests Filesystem MCP server"
        },
        {
            "name": "Brave Search",
            "query": "Search for 'latest python version' on the web.",
            "description": "Tests Brave Search MCP server"
        },
        {
            "name": "File Content (Large)",
            "query": "Read the contents of 'mcp_tool_search.py' in the MCP-Tool-Search-Tool directory.",
            "description": "Tests retrieving large file content"
        }
    ]
    
    all_results = []
    
    for q in queries:
        print(f"\n\nRunning Test: {q['name']}")
        print(f"Query: {q['query']}")
        print("-" * 50)
        
        # 1. Baseline
        print("1. Running Baseline...")
        base = run_mcp_script(q['query'], defer=False, toon=False)
        if not base: continue
        
        # 2. Deferred
        print("2. Running Deferred...")
        defer = run_mcp_script(q['query'], defer=True, toon=False)
        if not defer: continue
        
        # 3. Deferred + TOON
        print("3. Running Deferred + TOON...")
        toon = run_mcp_script(q['query'], defer=True, toon=True)
        if not toon: continue
        
        all_results.append({
            "query": q,
            "base": base,
            "defer": defer,
            "toon": toon
        })
    
    # Print Comprehensive Summary
    print("\n" + "="*100)
    print("COMPARISON SUMMARY")
    print("="*100)
    
    for res in all_results:
        name = res['query']['name']
        base = res['base']
        defer = res['defer']
        toon = res['toon']
        
        # Calculate savings vs Baseline (Total)
        b_total = base['total_tokens']
        d_total = defer['total_tokens']
        t_total = toon['total_tokens']
        
        d_save = b_total - d_total
        d_pct = (d_save / b_total * 100) if b_total > 0 else 0
        
        t_save = b_total - t_total
        t_pct = (t_save / b_total * 100) if b_total > 0 else 0
        
        print(f"\nTest Case: {name}")
        print("-" * 90)
        print(f"{'Strategy':<34} {'Input':<11} {'Output':<11} {'Total':<11} {'Savings':<11}")
        print("-" * 90)
        
        # Baseline
        print(f"1) MCP Baseline(JSON)             {base['input_tokens']:<11} {base['output_tokens']:<11} {b_total:<11} {'-':<11}")
        
        # Deferred
        print(f"2) MCP Differ Tool Loading(JSON)  {defer['input_tokens']:<11} {defer['output_tokens']:<11} {d_total:<11} {f'{d_save} ({d_pct:.1f}%)':<11}")
        
        # TOON
        print(f"3) MCP Differ Tool Loading(TOON)  {toon['input_tokens']:<11} {toon['output_tokens']:<11} {t_total:<11} {f'{t_save} ({t_pct:.1f}%)':<11}")
        print("-" * 90)

    # Save results
    output_file = os.path.join(os.path.dirname(__file__), "mcp_comprehensive_results.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
        
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    main()
