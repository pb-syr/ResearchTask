#!/usr/bin/env python3
"""
Pandas Statistical Analysis of Political Advertising Dataset

This script analyzes the dataset using Pandas and compares results with the
pure Python implementation.

Author: Your Name
Date: 2026-07-09
"""

import pandas as pd
import numpy as np
import sys
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# Helper Functions
# ============================================================================

def clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean numeric columns that might contain formatting characters.
    """
    numeric_like_columns = [
        'estimated_audience_size', 'impressions', 'spend'
    ]
    
    for col in numeric_like_columns:
        if col in df.columns:
            # Try to convert to numeric, handling formatting
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
            df[col] = df[col].str.replace(r'{.*}', '', regex=True)  # Remove dictionary patterns
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def print_section(title: str, char: str = '=') -> None:
    """
    Print a formatted section header.
    """
    print("\n" + char * 80)
    print(f"{title}")
    print(char * 80)


def compare_results(pandas_results: Dict, python_results: Dict) -> None:
    """
    Compare Pandas results with Pure Python results.
    """
    print_section("COMPARISON: Pandas vs Pure Python", "-")
    
    # Compare numeric columns
    numeric_columns = ['estimated_audience_size', 'impressions', 'spend']
    
    for col in numeric_columns:
        if col in pandas_results and col in python_results:
            print(f"\nColumn: {col}")
            
            # Compare statistics
            panda_stats = pandas_results[col]
            python_stats = python_results[col]
            
            for stat in ['mean', 'median', 'min', 'max', 'std', 'count']:
                p_val = panda_stats.get(stat)
                py_val = python_stats.get(stat)
                
                if p_val is not None and py_val is not None:
                    # Check if values are close (allow for floating point differences)
                    if isinstance(p_val, (int, float)) and isinstance(py_val, (int, float)):
                        if abs(p_val - py_val) > 0.01 and py_val != 0:
                            print(f"  ⚠️  {stat}: Pandas={p_val:.4f}, Python={py_val:.4f} (difference: {abs(p_val-py_val):.4f})")
                        else:
                            print(f"  ✓ {stat}: Pandas={p_val:.4f}, Python={py_val:.4f}")
                    else:
                        print(f"  ✓ {stat}: Pandas={p_val}, Python={py_val}")
                else:
                    print(f"  ⚠️  {stat}: Pandas={p_val}, Python={py_val}")
    
    print("\nComparison complete. Differences may be due to:")
    print("  • Rounding differences in standard deviation")
    print("  • Different handling of missing values")
    print("  • Different type inference")


# ============================================================================
# Main Analysis Class
# ============================================================================

class PandasAnalyzer:
    """
    Analyzes the dataset using Pandas.
    """
    
    def __init__(self, filename: str):
        self.filename = filename
        self.df = None
        self.results = {}
        
    def load(self) -> None:
        """
        Load the dataset using Pandas.
        """
        try:
            self.df = pd.read_csv(self.filename)
            print(f"✅ Loaded {len(self.df):,} rows and {len(self.df.columns)} columns")
            
            # Clean numeric columns
            self.df = clean_numeric_columns(self.df)
            
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    
    def analyze_structure(self) -> None:
        """
        Analyze and display basic structure of the dataset.
        """
        print_section("1. DATASET STRUCTURE")
        
        print("\nShape:")
        print(f"  Rows: {self.df.shape[0]:,}")
        print(f"  Columns: {self.df.shape[1]:,}")
        
        print("\nData Types:")
        print(self.df.dtypes)
        
        print("\nData Types Summary:")
        dtype_counts = self.df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} columns")
        
        print("\nFirst 5 rows:")
        print(self.df.head())
        
        print("\nColumn names:")
        for i, col in enumerate(self.df.columns, 1):
            print(f"  {i}. {col}")
    
    def analyze_missing_values(self) -> None:
        """
        Analyze missing values in the dataset.
        """
        print_section("2. MISSING VALUES ANALYSIS")
        
        missing_counts = self.df.isnull().sum()
        missing_percentages = (self.df.isnull().sum() / len(self.df)) * 100
        
        missing_df = pd.DataFrame({
            'Missing Count': missing_counts,
            'Missing Percentage': missing_percentages
        })
        
        # Only show columns with missing values
        missing_df = missing_df[missing_df['Missing Count'] > 0]
        
        if len(missing_df) > 0:
            print("\nColumns with missing values:")
            print(missing_df.sort_values('Missing Percentage', ascending=False))
        else:
            print("\n✅ No missing values found in any column.")
        
        print(f"\nTotal missing values: {self.df.isnull().sum().sum():,}")
        print(f"Total cells: {self.df.shape[0] * self.df.shape[1]:,}")
        print(f"Overall missing percentage: {(self.df.isnull().sum().sum() / (self.df.shape[0] * self.df.shape[1])) * 100:.2f}%")
    
    def analyze_numeric_columns(self) -> Dict[str, Any]:
        """
        Analyze numeric columns and return statistics.
        """
        print_section("3. NUMERIC COLUMN STATISTICS")
        
        # Select numeric columns (including those that might have been converted)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        numeric_stats = {}
        
        for col in numeric_cols:
            print(f"\n📊 Column: {col}")
            
            # Skip if all values are NaN
            if self.df[col].isnull().all():
                print("  ⚠️  All values are missing")
                continue
            
            stats = {
                'count': self.df[col].count(),
                'mean': self.df[col].mean(),
                'median': self.df[col].median(),
                'min': self.df[col].min(),
                'max': self.df[col].max(),
                'std': self.df[col].std(),
                'null_count': self.df[col].isnull().sum(),
                'null_percentage': (self.df[col].isnull().sum() / len(self.df)) * 100
            }
            
            numeric_stats[col] = stats
            
            print(f"  Count: {stats['count']:,}")
            print(f"  Mean: {stats['mean']:.4f}")
            print(f"  Median: {stats['median']:.4f}")
            print(f"  Min: {stats['min']:.4f}")
            print(f"  Max: {stats['max']:.4f}")
            print(f"  Std Dev: {stats['std']:.4f}")
            print(f"  Null Count: {stats['null_count']:,} ({stats['null_percentage']:.1f}%)")
        
        return numeric_stats
    
    def analyze_categorical_columns(self) -> Dict[str, Any]:
        """
        Analyze categorical columns and return statistics.
        """
        print_section("4. CATEGORICAL COLUMN STATISTICS")
        
        # Select categorical columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        categorical_stats = {}
        
        for col in categorical_cols:
            print(f"\n📊 Column: {col}")
            
            # Skip if all values are NaN
            if self.df[col].isnull().all():
                print("  ⚠️  All values are missing")
                continue
            
            non_null = self.df[col].dropna()
            
            if len(non_null) == 0:
                print("  ⚠️  No non-null values")
                continue
            
            # Get value counts
            value_counts = non_null.value_counts()
            unique_count = len(value_counts)
            mode = value_counts.index[0] if len(value_counts) > 0 else None
            mode_count = value_counts.iloc[0] if len(value_counts) > 0 else 0
            top_5 = value_counts.head(5)
            
            stats = {
                'count': len(non_null),
                'unique': unique_count,
                'mode': mode,
                'mode_count': mode_count,
                'top_5': top_5,
                'null_count': self.df[col].isnull().sum(),
                'null_percentage': (self.df[col].isnull().sum() / len(self.df)) * 100
            }
            
            categorical_stats[col] = stats
            
            print(f"  Count: {stats['count']:,}")
            print(f"  Unique values: {stats['unique']:,}")
            if mode is not None:
                print(f"  Mode: '{mode}' (frequency: {mode_count:,})")
            print(f"  Null Count: {stats['null_count']:,} ({stats['null_percentage']:.1f}%)")
            print(f"  Top 5 values by frequency:")
            for value, freq in top_5.items():
                print(f"    • {value[:50] + '...' if len(str(value)) > 50 else value}: {freq:,}")
        
        return categorical_stats
    
    def generate_summary_stats(self) -> None:
        """
        Generate summary statistics using DataFrame.describe().
        """
        print_section("5. SUMMARY STATISTICS (DESCRIBE)")
        
        print("\nNumeric columns summary:")
        print(self.df.describe())
        
        print("\nCategorical columns summary:")
        print(self.df.describe(include=['object']))
    
    def analyze_complex_columns(self) -> None:
        """
        Analyze columns with complex data structures (lists, dicts).
        """
        print_section("6. COMPLEX COLUMN ANALYSIS")
        
        # Columns that might contain lists or dicts
        complex_cols = ['publisher_platforms', 'illuminating_mentions']
        
        for col in complex_cols:
            if col in self.df.columns:
                print(f"\n📊 Column: {col}")
                
                # Show sample values
                sample_values = self.df[col].dropna().head(10)
                print(f"  Sample values (first 10):")
                for val in sample_values:
                    print(f"    • {val[:100] if len(str(val)) > 100 else val}")
                
                # Check if values are strings that look like lists or dicts
                sample_str = self.df[col].dropna().iloc[0] if len(self.df[col].dropna()) > 0 else ""
                if isinstance(sample_str, str) and sample_str.startswith('['):
                    print(f"  Column appears to contain list data")
                elif isinstance(sample_str, str) and sample_str.startswith('{'):
                    print(f"  Column appears to contain dictionary data")
                
                # Count null values
                null_count = self.df[col].isnull().sum()
                print(f"  Null count: {null_count:,} ({null_count/len(self.df)*100:.1f}%)")
    
    def run_analysis(self) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.
        """
        print_section("PANDAS STATISTICAL ANALYSIS")
        print(f"File: {self.filename}")
        
        self.analyze_structure()
        self.analyze_missing_values()
        
        numeric_stats = self.analyze_numeric_columns()
        categorical_stats = self.analyze_categorical_columns()
        
        self.generate_summary_stats()
        self.analyze_complex_columns()
        
        return {
            'numeric': numeric_stats,
            'categorical': categorical_stats
        }
    
    def export_results(self, results: Dict[str, Any], filename: str) -> None:
        """
        Export analysis results to a text file.
        """
        # Redirect print to file
        import sys
        from contextlib import redirect_stdout
        
        with open(filename, 'w', encoding='utf-8') as f:
            with redirect_stdout(f):
                # Re-run analysis with output redirected
                self.analyze_structure()
                self.analyze_missing_values()
                self.analyze_numeric_columns()
                self.analyze_categorical_columns()
                self.generate_summary_stats()
                self.analyze_complex_columns()
        
        print(f"\nResults exported to: {filename}")


# ============================================================================
# Comparison Function
# ============================================================================

def compare_with_python(pandas_results: Dict, python_file: str = 'analysis_results_pure_python.txt') -> None:
    """
    Compare Pandas results with the pure Python results file.
    """
    print_section("COMPARISON WITH PURE PYTHON RESULTS", "-")
    
    # Try to load the pure Python results file
    try:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n✅ Pure Python results file found.")
            print("Please manually verify that the results match the Pandas analysis above.")
            print("\nKey things to check:")
            print("  1. Missing values counts match")
            print("  2. Mean, median, and standard deviation values are consistent")
            print("  3. Categorical value frequencies are the same")
            print("  4. Unique value counts match")
    except FileNotFoundError:
        print(f"\n⚠️  Pure Python results file '{python_file}' not found.")
        print("Please run pure_python_stats.py first to generate the comparison file.")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    Main entry point for the script.
    """
    filename = 'C:/Users/purte/OneDrive - Syracuse University/Documents/OPT RA Work Record/fb_ads_president_scored_anon.csv'
    
    # Create and load the analyzer
    analyzer = PandasAnalyzer(filename)
    
    try:
        analyzer.load()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Run analysis
    results = analyzer.run_analysis()
    
    # Export results
    analyzer.export_results(results, 'analysis_results_pandas.txt')
    
    # Compare with pure Python
    compare_with_python(results)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
