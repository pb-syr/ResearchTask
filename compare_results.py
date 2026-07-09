#!/usr/bin/env python3
"""
Compare results from Pure Python and Pandas analyses.
"""

import re
import sys
from typing import Dict, List, Tuple


def parse_python_results(filename: str) -> Dict:
    """
    Parse the pure Python results file to extract key statistics.
    """
    results = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract column statistics using regex patterns
        pattern = r'(\d+)\. Column: (.+?)\n   Type: (.+?)\n   Null count: ([\d,]+) \(([\d.]+)%\)\n   Non-null count: ([\d,]+)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            col_num, col_name, col_type, null_count, null_pct, non_null = match
            results[col_name] = {
                'type': col_type,
                'null_count': int(null_count.replace(',', '')),
                'null_pct': float(null_pct),
                'non_null': int(non_null.replace(',', ''))
            }
            
            # Try to extract numeric stats
            if col_type in ['numeric', 'integer']:
                stats_pattern = r'Mean: ([\d.]+)\n.*?Median: ([\d.]+)\n.*?Min: ([\d.]+)\n.*?Max: ([\d.]+)\n.*?Std Dev: ([\d.]+)'
                stats_match = re.search(stats_pattern, content)
                if stats_match:
                    results[col_name].update({
                        'mean': float(stats_match.group(1)),
                        'median': float(stats_match.group(2)),
                        'min': float(stats_match.group(3)),
                        'max': float(stats_match.group(4)),
                        'std': float(stats_match.group(5))
                    })
            
            # Try to extract categorical stats
            if col_type == 'categorical':
                cat_pattern = r'Unique values: ([\d,]+)\n   Mode: \'(.+?)\' \(frequency: ([\d,]+)\)'
                cat_match = re.search(cat_pattern, content)
                if cat_match:
                    results[col_name].update({
                        'unique': int(cat_match.group(1).replace(',', '')),
                        'mode': cat_match.group(2),
                        'mode_freq': int(cat_match.group(3).replace(',', ''))
                    })
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    
    return results


def parse_pandas_results(filename: str) -> Dict:
    """
    Parse the Pandas results file to extract key statistics.
    """
    results = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract column statistics using regex patterns
        # This is more complex for Pandas output, so we'll use a simpler approach
        
        # Find all column sections
        col_pattern = r'📊 Column: (.+?)\n  Count: ([\d,]+)\n  Mean: ([\d.]+)\n  Median: ([\d.]+)\n  Min: ([\d.]+)\n  Max: ([\d.]+)\n  Std Dev: ([\d.]+)\n  Null Count: ([\d,]+) \(([\d.]+)%\)'
        matches = re.findall(col_pattern, content)
        
        for match in matches:
            col_name = match[0]
            results[col_name] = {
                'count': int(match[1].replace(',', '')),
                'mean': float(match[2]),
                'median': float(match[3]),
                'min': float(match[4]),
                'max': float(match[5]),
                'std': float(match[6]),
                'null_count': int(match[7].replace(',', '')),
                'null_pct': float(match[8])
            }
            
        # Also try to capture categorical stats
        cat_pattern = r'📊 Column: (.+?)\n  Count: ([\d,]+)\n  Unique values: ([\d,]+)\n  Mode: \'(.+?)\' \(frequency: ([\d,]+)\)'
        cat_matches = re.findall(cat_pattern, content)
        
        for match in cat_matches:
            col_name = match[0]
            if col_name not in results:
                results[col_name] = {}
            results[col_name].update({
                'unique': int(match[2].replace(',', '')),
                'mode': match[3],
                'mode_freq': int(match[4].replace(',', ''))
            })
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    
    return results


def compare_numeric_stats(python_stats: Dict, pandas_stats: Dict) -> List[Tuple[str, str]]:
    """
    Compare numeric statistics between Python and Pandas results.
    """
    differences = []
    numeric_cols = ['estimated_audience_size', 'impressions', 'spend']
    
    for col in numeric_cols:
        if col in python_stats and col in pandas_stats:
            py = python_stats[col]
            pd = pandas_stats[col]
            
            for stat in ['mean', 'median', 'min', 'max', 'std', 'count']:
                if stat in py and stat in pd:
                    py_val = py[stat]
                    pd_val = pd[stat]
                    
                    if isinstance(py_val, (int, float)) and isinstance(pd_val, (int, float)):
                        diff = abs(py_val - pd_val)
                        if diff > 0.01 and py_val != 0:
                            differences.append((col, stat, py_val, pd_val, diff))
    
    return differences


def main():
    """
    Compare the two analysis results.
    """
    print("=" * 80)
    print("COMPARING PURE PYTHON AND PANDAS RESULTS")
    print("=" * 80)
    
    # Parse results
    python_results = parse_python_results('analysis_results_pure_python.txt')
    pandas_results = parse_pandas_results('analysis_results_pandas.txt')
    
    if not python_results:
        print("\n⚠️  Pure Python results not found. Please run pure_python_stats.py first.")
        sys.exit(1)
    
    if not pandas_results:
        print("\n⚠️  Pandas results not found. Please run pandas_stats.py first.")
        sys.exit(1)
    
    print(f"\n✅ Pure Python results: {len(python_results)} columns")
    print(f"✅ Pandas results: {len(pandas_results)} columns")
    
    # Find common columns
    common_cols = set(python_results.keys()) & set(pandas_results.keys())
    print(f"\nCommon columns: {len(common_cols)}")
    
    # Compare numeric statistics
    differences = compare_numeric_stats(python_results, pandas_results)
    
    if differences:
        print("\n⚠️  Differences found in numeric statistics:")
        for col, stat, py_val, pd_val, diff in differences:
            print(f"  • {col}.{stat}: Python={py_val:.4f}, Pandas={pd_val:.4f} (diff={diff:.4f})")
        print("\nPossible reasons for differences:")
        print("  • Rounding in standard deviation calculation")
        print("  • Different handling of missing values")
        print("  • Different type conversion for mixed columns")
    else:
        print("\n✅ All numeric statistics match!")
    
    # Compare categorical statistics
    print("\n" + "-" * 80)
    print("Categorical Statistics Comparison:")
    print("-" * 80)
    
    for col in common_cols:
        if 'unique' in python_results[col] and 'unique' in pandas_results[col]:
            py_unique = python_results[col]['unique']
            pd_unique = pandas_results[col]['unique']
            
            if py_unique == pd_unique:
                print(f"{col}: unique values match ({py_unique})")
            else:
                print(f"{col}: unique values differ (Python={py_unique}, Pandas={pd_unique})")
    
    print("\nComparison complete!")
    print("The results should be highly consistent between both implementations.")


if __name__ == "__main__":
    main()
