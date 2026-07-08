''' Performs comprehensive analysis on CSV datasets using only the standard library. '''

import csv
import math
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Union, Optional


class DataAnalyzer:
    """Analyzes CSV data using only Python standard library."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.data = []
        self.headers = []
        self.column_types = {}
        self.stats = {}
        
    def load_data(self) -> None:
        """Load CSV data with proper handling of quoted fields and embedded commas."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.headers = reader.fieldnames or []
                self.data = [row for row in reader]
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    
    def infer_type(self, column_values: List[str]) -> str:
        """Infer the data type of a column."""
        # Filter out empty strings and whitespace-only values
        non_empty = [v.strip() for v in column_values if v and v.strip()]
        
        if not non_empty:
            return "empty"
        
        # Check if all values can be parsed as integers
        try:
            all(int(v) for v in non_empty)
            return "integer"
        except ValueError:
            pass
        
        # Check if all values can be parsed as floats
        try:
            all(self._try_float(v) for v in non_empty)
            return "float"
        except ValueError:
            pass
        
        # Check if all values look like dates (simple check)
        date_patterns = ['/', '-', ' ']
        if all(any(char in v for char in date_patterns) for v in non_empty):
            return "date"
        
        # Otherwise, treat as string
        return "string"
    
    def _try_float(self, value: str) -> float:
        """Attempt to convert a string to float, handling common formats."""
        cleaned = value.strip()
        # Remove currency symbols and commas
        cleaned = cleaned.replace('$', '').replace(',', '')
        # Handle percentage signs
        if cleaned.endswith('%'):
            cleaned = cleaned[:-1]
        return float(cleaned)
    
    def _clean_numeric(self, value: str) -> Optional[float]:
        """Clean and convert a value to float, return None if not possible."""
        if not value or not value.strip():
            return None
        
        cleaned = value.strip()
        # Remove common non-numeric characters
        cleaned = cleaned.replace('$', '').replace(',', '').replace('%', '')
        
        # Handle parentheses for negative numbers
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def analyze_numeric(self, values: List[float]) -> Dict[str, Union[float, int]]:
        """Compute statistics for numeric columns."""
        # Filter out None values
        valid_values = [v for v in values if v is not None]
        n = len(valid_values)
        
        if n == 0:
            return {
                "count": 0,
                "mean": None,
                "min": None,
                "max": None,
                "std": None,
                "median": None,
                "total_missing": len(values) - n
            }
        
        sorted_values = sorted(valid_values)
        
        # Basic statistics
        mean = sum(sorted_values) / n
        min_val = sorted_values[0]
        max_val = sorted_values[-1]
        
        # Median
        if n % 2 == 0:
            median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            median = sorted_values[n//2]
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in sorted_values) / n
        std = math.sqrt(variance)
        
        return {
            "count": n,
            "mean": mean,
            "min": min_val,
            "max": max_val,
            "std": std,
            "median": median,
            "total_missing": len(values) - n
        }
    
    def analyze_categorical(self, values: List[str]) -> Dict[str, Union[int, List[tuple]]]:
        """Compute statistics for categorical columns."""
        # Filter out empty strings
        valid_values = [v.strip() for v in values if v and v.strip()]
        n = len(valid_values)
        
        if n == 0:
            return {
                "count": 0,
                "unique": 0,
                "mode": None,
                "mode_freq": 0,
                "top_5": [],
                "total_missing": len(values)
            }
        
        # Count frequencies
        counter = Counter(valid_values)
        
        # Mode and frequency
        mode_items = counter.most_common(1)
        mode = mode_items[0][0] if mode_items else None
        mode_freq = mode_items[0][1] if mode_items else 0
        
        # Top 5
        top_5 = counter.most_common(5)
        
        return {
            "count": n,
            "unique": len(counter),
            "mode": mode,
            "mode_freq": mode_freq,
            "top_5": top_5,
            "total_missing": len(values) - n
        }
    
    def analyze_all(self) -> None:
        """Perform complete analysis of the dataset."""
        if not self.data:
            print("No data loaded. Please load data first.")
            return
        
        # Overall stats
        total_rows = len(self.data)
        total_cols = len(self.headers)
        
        print("=" * 80)
        print(f"DATASET OVERVIEW: {self.filename}")
        print("=" * 80)
        print(f"Total rows: {total_rows:,}")
        print(f"Total columns: {total_cols}")
        print()
        
        # Analyze each column
        for idx, header in enumerate(self.headers):
            print(f"\n{'=' * 80}")
            print(f"COLUMN {idx+1}: {header}")
            print("-" * 80)
            
            # Extract column values
            column_values = [row.get(header, '').strip() for row in self.data]
            
            # Count missing values
            missing_count = sum(1 for v in column_values if not v or not v.strip())
            total_non_missing = len(column_values) - missing_count
            
            print(f"Missing values: {missing_count} ({missing_count/len(column_values)*100:.1f}%)")
            print(f"Non-missing values: {total_non_missing:,}")
            
            # Try to detect type
            if total_non_missing == 0:
                inferred_type = "empty"
                print(f"Inferred type: EMPTY")
                self.column_types[header] = "empty"
                continue
            
            # Infer data type
            inferred_type = self.infer_type(column_values)
            self.column_types[header] = inferred_type
            print(f"Inferred type: {inferred_type.upper()}")
            
            # Analyze based on type
            if inferred_type in ["integer", "float"]:
                # Clean and convert to numeric
                numeric_values = [self._clean_numeric(v) for v in column_values]
                stats = self.analyze_numeric(numeric_values)
                
                print(f"\nNumeric Statistics:")
                print(f"  Count: {stats['count']:,}")
                if stats['mean'] is not None:
                    print(f"  Mean: {stats['mean']:,.2f}")
                    print(f"  Median: {stats['median']:,.2f}")
                    print(f"  Min: {stats['min']:,.2f}")
                    print(f"  Max: {stats['max']:,.2f}")
                    print(f"  Std Dev: {stats['std']:,.2f}")
                else:
                    print("  No valid numeric values found")
                
                self.stats[header] = stats
                
            else:
                # Categorical analysis
                stats = self.analyze_categorical(column_values)
                
                print(f"\nCategorical Statistics:")
                print(f"  Count: {stats['count']:,}")
                print(f"  Unique values: {stats['unique']:,}")
                
                if stats['mode'] is not None:
                    print(f"  Most frequent: '{stats['mode']}' ({stats['mode_freq']:,} occurrences)")
                    print(f"  Top 5 values:")
                    for val, freq in stats['top_5']:
                        pct = (freq / stats['count']) * 100
                        print(f"    '{val}': {freq:,} ({pct:.1f}%)")
                
                self.stats[header] = stats
    
    def get_summary(self) -> None:
        """Print a concise summary of the analysis."""
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total rows: {len(self.data):,}")
        print(f"Total columns: {len(self.headers)}")
        
        # Column type distribution
        type_counts = Counter(self.column_types.values())
        print(f"\nColumn type distribution:")
        for dtype, count in type_counts.most_common():
            print(f"  {dtype}: {count}")
        
        # Overall missing values
        total_missing = sum(
            1 for row in self.data 
            for val in row.values() 
            if not val or not val.strip()
        )
        total_cells = len(self.data) * len(self.headers)
        print(f"\nOverall missing values: {total_missing:,} ({total_missing/total_cells*100:.1f}%)")
        
        # Most missing columns
        print(f"\nColumns with most missing values:")
        missing_stats = []
        for header in self.headers:
            stats = self.stats.get(header, {})
            missing = stats.get('total_missing', 
                               sum(1 for row in self.data if not row.get(header, '').strip()))
            missing_stats.append((header, missing))
        
        missing_stats.sort(key=lambda x: x[1], reverse=True)
        for header, missing in missing_stats[:5]:
            if missing > 0:
                pct = (missing / len(self.data)) * 100
                print(f"  {header}: {missing:,} ({pct:.1f}%)")


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python pure_python_stats.py <csv_file>")
        print("\nExample: python pure_python_stats.py data.csv")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyzer = DataAnalyzer(filename)
    analyzer.load_data()
    analyzer.analyze_all()
    analyzer.get_summary()


if __name__ == "__main__":
    main()
