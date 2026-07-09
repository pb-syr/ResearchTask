#!/usr/bin/env python3
"""
Pure Python Statistical Analysis of Political Advertising Dataset

This script loads and analyzes the dataset using only Python's standard library.
No third-party packages (Pandas, NumPy, etc.) are used.

Author: Your Name
Date: 2026-07-09
"""

import csv
import math
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Tuple, Union
import re


# ============================================================================
# Helper Functions
# ============================================================================

def is_numeric(value: str) -> bool:
    """
    Check if a string value can be interpreted as a number.
    Handles various formats including negative numbers, decimals, scientific notation,
    and common formatting like currency and percentages.
    """
    if not value or value.strip() == '':
        return False
    
    # Remove common formatting characters
    cleaned = value.strip().replace(',', '').replace('$', '').replace('%', '')
    
    # Try to convert to float
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def safe_float(value: str) -> Optional[float]:
    """
    Safely convert a string to float, returning None if conversion fails.
    Handles various number formats including currency and percentages.
    """
    if not value or value.strip() == '':
        return None
    
    # Remove common formatting characters
    cleaned = value.strip().replace(',', '').replace('$', '').replace('%', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def safe_int(value: str) -> Optional[int]:
    """
    Safely convert a string to int, returning None if conversion fails.
    """
    if not value or value.strip() == '':
        return None
    
    # Remove common formatting characters
    cleaned = value.strip().replace(',', '').replace('$', '').replace('%', '')
    
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def compute_numeric_stats(values: List[float]) -> Dict[str, Any]:
    """
    Compute statistics for a list of numeric values.
    
    Returns a dictionary with:
    - count: number of non-null values
    - mean: arithmetic mean
    - min: minimum value
    - max: maximum value
    - std: standard deviation (population)
    - median: median value
    """
    if not values:
        return {
            'count': 0,
            'mean': None,
            'min': None,
            'max': None,
            'std': None,
            'median': None
        }
    
    # Sort values for median calculation
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    # Calculate median
    if n % 2 == 1:
        median = sorted_values[n // 2]
    else:
        median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    
    # Calculate mean
    mean = sum(values) / n
    
    # Calculate standard deviation (population)
    variance = sum((x - mean) ** 2 for x in values) / n
    std = math.sqrt(variance) if variance >= 0 else None
    
    return {
        'count': n,
        'mean': mean,
        'min': min(values),
        'max': max(values),
        'std': std,
        'median': median
    }


def compute_categorical_stats(values: List[str]) -> Dict[str, Any]:
    """
    Compute statistics for a list of categorical values.
    
    Returns a dictionary with:
    - count: number of non-null values
    - unique: number of unique values
    - mode: most frequent value
    - mode_count: frequency of mode
    - top_5: top 5 values by frequency (as list of tuples)
    """
    # Filter out empty/None values
    valid_values = [v for v in values if v and v.strip()]
    
    if not valid_values:
        return {
            'count': 0,
            'unique': 0,
            'mode': None,
            'mode_count': 0,
            'top_5': []
        }
    
    # Count frequencies
    counter = Counter(valid_values)
    
    # Get mode and its frequency
    mode, mode_count = counter.most_common(1)[0] if counter else (None, 0)
    
    # Get top 5 values
    top_5 = counter.most_common(5)
    
    return {
        'count': len(valid_values),
        'unique': len(counter),
        'mode': mode,
        'mode_count': mode_count,
        'top_5': top_5
    }


def infer_column_type(values: List[str]) -> str:
    """
    Infer the data type of a column based on its values.
    
    Possible types:
    - 'numeric': all values can be converted to numbers
    - 'integer': all values can be converted to integers
    - 'mixed': values are of different types
    - 'categorical': all values are strings
    - 'empty': no non-null values
    """
    # Get non-null values
    valid_values = [v for v in values if v and v.strip()]
    
    if not valid_values:
        return 'empty'
    
    # Check if all values are numeric
    numeric_values = [v for v in valid_values if is_numeric(v)]
    
    if len(numeric_values) == len(valid_values):
        # Check if all are integers
        all_integers = all(safe_int(v) is not None for v in valid_values)
        return 'integer' if all_integers else 'numeric'
    
    # Check for mixed types (some numeric, some not)
    if numeric_values:
        return 'mixed'
    
    # Otherwise, it's categorical
    return 'categorical'


def clean_string_for_display(value: str, max_length: int = 50) -> str:
    """
    Clean a string for display by truncating if necessary.
    """
    if not value:
        return ''
    
    str_value = str(value)
    if len(str_value) > max_length:
        return str_value[:max_length] + '...'
    return str_value


# ============================================================================
# Main Analysis Class
# ============================================================================

class DatasetAnalyzer:
    """
    Analyzes a dataset using only Python's standard library.
    """
    
    def __init__(self, filename: str):
        self.filename = filename
        self.rows = []
        self.headers = []
        self.column_data = defaultdict(list)
        self.row_count = 0
        self.column_count = 0
        
    def load(self) -> None:
        """
        Load the dataset from a CSV file.
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.headers = reader.fieldnames
                self.column_count = len(self.headers)
                
                for row in reader:
                    self.rows.append(row)
                    self.row_count += 1
                    
                    # Populate column_data for easy analysis
                    for header in self.headers:
                        value = row.get(header, '')
                        self.column_data[header].append(value)
                        
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    
    def analyze_column(self, column_name: str, values: List[str]) -> Dict[str, Any]:
        """
        Analyze a single column, determining its type and computing appropriate statistics.
        """
        # Get non-null values
        non_null = [v for v in values if v and v.strip()]
        
        # Determine column type
        col_type = infer_column_type(values)
        
        result = {
            'column_name': column_name,
            'type': col_type,
            'null_count': len(values) - len(non_null),
            'null_percentage': (len(values) - len(non_null)) / len(values) * 100 if values else 0
        }
        
        if col_type in ['numeric', 'integer']:
            # Convert to float for numeric analysis
            numeric_values = [safe_float(v) for v in non_null if safe_float(v) is not None]
            stats = compute_numeric_stats(numeric_values)
            result.update(stats)
            
        elif col_type == 'mixed':
            # For mixed columns, try to extract numeric values
            numeric_values = [safe_float(v) for v in non_null if safe_float(v) is not None]
            if numeric_values:
                stats = compute_numeric_stats(numeric_values)
                result.update(stats)
                result['mixed_numeric_count'] = len(numeric_values)
            else:
                # If no numeric values, treat as categorical
                categorical_stats = compute_categorical_stats(non_null)
                result.update(categorical_stats)
                result['type'] = 'categorical'
            
            # Also provide categorical stats for the string portions
            categorical_stats = compute_categorical_stats(non_null)
            result['categorical_unique'] = categorical_stats['unique']
            result['categorical_mode'] = categorical_stats['mode']
            result['categorical_mode_count'] = categorical_stats['mode_count']
            
        else:
            # Categorical analysis
            categorical_values = [str(v) for v in non_null]
            stats = compute_categorical_stats(categorical_values)
            result.update(stats)
            
        return result
    
    def analyze_dataset(self) -> Dict[str, Any]:
        """
        Analyze the entire dataset, computing statistics for each column.
        """
        results = {
            'row_count': self.row_count,
            'column_count': self.column_count,
            'columns': {}
        }
        
        # Analyze each column
        for column in self.headers:
            values = self.column_data[column]
            results['columns'][column] = self.analyze_column(column, values)
        
        return results
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Print the analysis results in a readable format.
        """
        print("=" * 80)
        print("DATASET STATISTICAL ANALYSIS - PURE PYTHON")
        print("=" * 80)
        print(f"\nDataset Overview:")
        print(f"  • Total rows: {results['row_count']:,}")
        print(f"  • Total columns: {results['column_count']}")
        print("-" * 80)
        
        # Print column-by-column analysis
        for i, (column, stats) in enumerate(results['columns'].items(), 1):
            print(f"\n{i}. Column: {column}")
            print(f"   Type: {stats['type']}")
            print(f"   Null count: {stats['null_count']:,} ({stats['null_percentage']:.1f}%)")
            print(f"   Non-null count: {stats['count']:,}")
            
            if stats['type'] in ['numeric', 'integer']:
                print(f"   Statistics:")
                if stats['mean'] is not None:
                    print(f"     • Mean: {stats['mean']:.4f}")
                else:
                    print(f"     • Mean: N/A")
                if stats['median'] is not None:
                    print(f"     • Median: {stats['median']:.4f}")
                else:
                    print(f"     • Median: N/A")
                if stats['min'] is not None:
                    print(f"     • Min: {stats['min']:.4f}")
                else:
                    print(f"     • Min: N/A")
                if stats['max'] is not None:
                    print(f"     • Max: {stats['max']:.4f}")
                else:
                    print(f"     • Max: N/A")
                if stats['std'] is not None:
                    print(f"     • Std Dev: {stats['std']:.4f}")
                else:
                    print(f"     • Std Dev: N/A")
                    
            elif stats['type'] == 'mixed':
                print(f"   Statistics (numeric portion):")
                if stats.get('mean') is not None:
                    print(f"     • Mean: {stats['mean']:.4f} (based on {stats.get('mixed_numeric_count', 0)} numeric values)")
                else:
                    print(f"     • Mean: N/A")
                if stats.get('median') is not None:
                    print(f"     • Median: {stats['median']:.4f}")
                else:
                    print(f"     • Median: N/A")
                if stats.get('min') is not None:
                    print(f"     • Min: {stats['min']:.4f}")
                else:
                    print(f"     • Min: N/A")
                if stats.get('max') is not None:
                    print(f"     • Max: {stats['max']:.4f}")
                else:
                    print(f"     • Max: N/A")
                if stats.get('std') is not None:
                    print(f"     • Std Dev: {stats['std']:.4f}")
                else:
                    print(f"     • Std Dev: N/A")
                print(f"   Categorical statistics:")
                print(f"     • Unique values: {stats.get('categorical_unique', 0):,}")
                if stats.get('categorical_mode'):
                    print(f"     • Mode: '{clean_string_for_display(stats['categorical_mode'])}' (frequency: {stats.get('categorical_mode_count', 0)})")
                
            else:
                print(f"   Unique values: {stats['unique']:,}")
                if stats['mode'] is not None:
                    print(f"   Mode: '{clean_string_for_display(stats['mode'])}' (frequency: {stats['mode_count']})")
                print(f"   Top 5 values by frequency:")
                if stats['top_5']:
                    for value, freq in stats['top_5']:
                        print(f"     • {clean_string_for_display(value)}: {freq}")
                else:
                    print("     • No values found")
            
            print("-" * 80)
    
    def export_results(self, results: Dict[str, Any], filename: str) -> None:
        """
        Export analysis results to a text file.
        """
        import io
        output = io.StringIO()
        
        # Redirect print to string buffer
        import contextlib
        with contextlib.redirect_stdout(output):
            self.print_results(results)
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output.getvalue())
        
        print(f"\nResults exported to: {filename}")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    Main entry point for the script.
    """
    filename = 'C:/Users/purte/OneDrive - Syracuse University/Documents/OPT RA Work Record/fb_ads_president_scored_anon.csv'
    
    print("Loading dataset...")
    
    # Create and load the analyzer
    analyzer = DatasetAnalyzer(filename)
    
    try:
        analyzer.load()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"Loaded {analyzer.row_count:,} rows and {analyzer.column_count} columns.")
    print("\nAnalyzing dataset...")
    
    # Analyze the dataset
    results = analyzer.analyze_dataset()
    
    # Print results
    analyzer.print_results(results)
    
    # Export to file
    analyzer.export_results(results, 'analysis_results_pure_python.txt')
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
