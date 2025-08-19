"""
Data Cleaning Operations Module
Provides various data cleaning and transformation functions for CSV data.
"""

import re
from typing import List, Dict, Tuple, Set, Optional, Callable
from collections import Counter
from datetime import datetime
import unicodedata
from .utils import log_verbose, log_debug
from .config import CONFIG


class DataCleaner:
    """Main class for data cleaning operations."""
    
    def __init__(self, rows: List[List[str]], headers: List[str]):
        self.rows = rows
        self.headers = headers
        self.original_rows = rows.copy()
        self.cleaning_log = []
    
    def log_operation(self, operation: str, details: str, affected_rows: List[int] = None):
        """Log a cleaning operation for reporting."""
        self.cleaning_log.append({
            'operation': operation,
            'details': details,
            'affected_rows': affected_rows or [],
            'timestamp': datetime.now().isoformat()
        })
        log_verbose(f"Cleaning operation: {operation} - {details}")
    
    def remove_duplicates(self, subset_columns: Optional[List[str]] = None, keep: str = 'first') -> Tuple[List[List[str]], int]:
        """
        Remove duplicate rows based on specified columns or all columns.
        
        Args:
            subset_columns: List of column names to consider for duplicates. If None, uses all columns.
            keep: Which duplicates to keep ('first', 'last', or 'none')
        
        Returns:
            Tuple of (cleaned_rows, number_of_duplicates_removed)
        """
        if not self.rows:
            return self.rows, 0
        
        # Convert column names to indices
        if subset_columns:
            column_indices = []
            for col_name in subset_columns:
                if col_name in self.headers:
                    column_indices.append(self.headers.index(col_name))
                else:
                    log_debug(f"Column '{col_name}' not found in headers")
            if not column_indices:
                log_debug("No valid columns specified for duplicate detection, using all columns")
                column_indices = list(range(len(self.headers)))
        else:
            column_indices = list(range(len(self.headers)))
        
        # Create a set to track seen combinations
        seen = set()
        cleaned_rows = []
        duplicates_removed = 0
        duplicate_rows = []
        
        for i, row in enumerate(self.rows):
            # Create a tuple of values for the specified columns
            key_values = tuple(row[j] if j < len(row) else '' for j in column_indices)
            
            if key_values in seen:
                duplicates_removed += 1
                duplicate_rows.append(i + 1)  # +1 for 1-based row numbering
                if keep == 'last':
                    # Remove the previous occurrence
                    for j, existing_row in enumerate(cleaned_rows):
                        existing_key = tuple(existing_row[k] if k < len(existing_row) else '' for k in column_indices)
                        if existing_key == key_values:
                            cleaned_rows.pop(j)
                            break
                    cleaned_rows.append(row)
                elif keep == 'none':
                    # Don't add this row at all
                    continue
            else:
                seen.add(key_values)
                cleaned_rows.append(row)
        
        self.rows = cleaned_rows
        self.log_operation(
            "Remove Duplicates",
            f"Removed {duplicates_removed} duplicate rows using columns: {subset_columns or 'all'}",
            duplicate_rows
        )
        
        return self.rows, duplicates_removed
    
    def normalize_whitespace(self, columns: Optional[List[str]] = None) -> int:
        """
        Normalize whitespace in specified columns or all columns.
        
        Args:
            columns: List of column names to normalize. If None, normalizes all columns.
        
        Returns:
            Number of cells modified
        """
        if not self.rows:
            return 0
        
        column_indices = self._get_column_indices(columns)
        modified_count = 0
        
        for i, row in enumerate(self.rows):
            for j in column_indices:
                if j < len(row):
                    original_value = row[j]
                    # Normalize whitespace: strip and replace multiple spaces with single space
                    normalized_value = re.sub(r'\s+', ' ', original_value.strip())
                    if original_value != normalized_value:
                        row[j] = normalized_value
                        modified_count += 1
        
        self.log_operation(
            "Normalize Whitespace",
            f"Modified {modified_count} cells in columns: {columns or 'all'}"
        )
        
        return modified_count
    
    def standardize_case(self, case_type: str = 'title', columns: Optional[List[str]] = None) -> int:
        """
        Standardize text case in specified columns.
        
        Args:
            case_type: 'upper', 'lower', 'title', 'sentence'
            columns: List of column names to process. If None, processes all text columns.
        
        Returns:
            Number of cells modified
        """
        if not self.rows:
            return 0
        
        column_indices = self._get_column_indices(columns)
        modified_count = 0
        
        for i, row in enumerate(self.rows):
            for j in column_indices:
                if j < len(row) and row[j]:
                    original_value = row[j]
                    if case_type == 'upper':
                        new_value = original_value.upper()
                    elif case_type == 'lower':
                        new_value = original_value.lower()
                    elif case_type == 'title':
                        new_value = original_value.title()
                    elif case_type == 'sentence':
                        new_value = '. '.join(s.capitalize() for s in original_value.split('. '))
                    else:
                        continue
                    
                    if original_value != new_value:
                        row[j] = new_value
                        modified_count += 1
        
        self.log_operation(
            "Standardize Case",
            f"Modified {modified_count} cells to {case_type} case in columns: {columns or 'all'}"
        )
        
        return modified_count
    
    def remove_empty_rows(self, threshold: float = 1.0) -> Tuple[List[List[str]], int]:
        """
        Remove rows that are mostly empty.
        
        Args:
            threshold: Fraction of empty cells required to remove a row (0.0 to 1.0)
        
        Returns:
            Tuple of (cleaned_rows, number_of_rows_removed)
        """
        if not self.rows:
            return self.rows, 0
        
        cleaned_rows = []
        removed_rows = []
        
        for i, row in enumerate(self.rows):
            empty_cells = sum(1 for cell in row if not cell or cell.strip() == '')
            total_cells = len(row)
            empty_ratio = empty_cells / total_cells if total_cells > 0 else 1.0
            
            if empty_ratio >= threshold:
                removed_rows.append(i + 1)  # +1 for 1-based row numbering
            else:
                cleaned_rows.append(row)
        
        rows_removed = len(self.rows) - len(cleaned_rows)
        self.rows = cleaned_rows
        
        self.log_operation(
            "Remove Empty Rows",
            f"Removed {rows_removed} rows with {threshold*100}% or more empty cells",
            removed_rows
        )
        
        return self.rows, rows_removed
    
    def fill_missing_values(self, strategy: str = 'empty', value: str = '', columns: Optional[List[str]] = None) -> int:
        """
        Fill missing or empty values using various strategies.
        
        Args:
            strategy: 'empty', 'mode', 'mean', 'median', 'custom'
            value: Custom value to use when strategy is 'custom'
            columns: List of column names to process. If None, processes all columns.
        
        Returns:
            Number of cells filled
        """
        if not self.rows:
            return 0
        
        column_indices = self._get_column_indices(columns)
        filled_count = 0
        
        for j in column_indices:
            if j >= len(self.headers):
                continue
            
            # Get all non-empty values for this column
            column_values = []
            for row in self.rows:
                if j < len(row) and row[j] and row[j].strip():
                    column_values.append(row[j])
            
            if not column_values:
                continue
            
            # Determine fill value based on strategy
            if strategy == 'mode':
                fill_value = Counter(column_values).most_common(1)[0][0]
            elif strategy == 'mean':
                try:
                    numeric_values = [float(v) for v in column_values if self._is_numeric(v)]
                    fill_value = str(sum(numeric_values) / len(numeric_values)) if numeric_values else ''
                except ValueError:
                    fill_value = ''
            elif strategy == 'median':
                try:
                    numeric_values = [float(v) for v in column_values if self._is_numeric(v)]
                    if numeric_values:
                        numeric_values.sort()
                        mid = len(numeric_values) // 2
                        fill_value = str(numeric_values[mid] if len(numeric_values) % 2 else (numeric_values[mid-1] + numeric_values[mid]) / 2)
                    else:
                        fill_value = ''
                except ValueError:
                    fill_value = ''
            elif strategy == 'custom':
                fill_value = value
            else:  # 'empty'
                fill_value = ''
            
            # Fill empty cells
            for row in self.rows:
                if j < len(row) and (not row[j] or row[j].strip() == ''):
                    row[j] = fill_value
                    filled_count += 1
        
        self.log_operation(
            "Fill Missing Values",
            f"Filled {filled_count} cells using strategy: {strategy}"
        )
        
        return filled_count
    
    def normalize_dates(self, date_columns: List[str], format: str = 'auto') -> int:
        """
        Normalize date formats in specified columns.
        
        Args:
            date_columns: List of column names containing dates
            format: Target date format ('auto', 'ISO', 'US', 'EU', etc.)
        
        Returns:
            Number of cells modified
        """
        if not self.rows:
            return 0
        
        column_indices = [self.headers.index(col) for col in date_columns if col in self.headers]
        modified_count = 0
        
        # Common date patterns
        date_patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),  # MM/DD/YYYY
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%m-%d-%Y'),  # MM-DD-YYYY
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),  # YYYY-MM-DD
            (r'(\d{1,2})/(\d{1,2})/(\d{2})', '%m/%d/%y'),  # MM/DD/YY
        ]
        
        for i, row in enumerate(self.rows):
            for j in column_indices:
                if j < len(row) and row[j]:
                    original_value = row[j]
                    normalized_value = self._normalize_date(original_value, date_patterns, format)
                    if original_value != normalized_value:
                        row[j] = normalized_value
                        modified_count += 1
        
        self.log_operation(
            "Normalize Dates",
            f"Modified {modified_count} date cells to format: {format}"
        )
        
        return modified_count
    
    def _normalize_date(self, date_str: str, patterns: List[Tuple], target_format: str) -> str:
        """Helper method to normalize a single date string."""
        try:
            for pattern, format_str in patterns:
                match = re.match(pattern, date_str)
                if match:
                    # Try to parse and reformat
                    try:
                        parsed_date = datetime.strptime(date_str, format_str)
                        if target_format == 'ISO':
                            return parsed_date.strftime('%Y-%m-%d')
                        elif target_format == 'US':
                            return parsed_date.strftime('%m/%d/%Y')
                        elif target_format == 'EU':
                            return parsed_date.strftime('%d/%m/%Y')
                        else:
                            return parsed_date.strftime('%Y-%m-%d')  # Default to ISO
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return date_str  # Return original if normalization fails
    
    def _get_column_indices(self, columns: Optional[List[str]]) -> List[int]:
        """Helper method to convert column names to indices."""
        if columns is None:
            return list(range(len(self.headers)))
        
        indices = []
        for col_name in columns:
            if col_name in self.headers:
                indices.append(self.headers.index(col_name))
            else:
                log_debug(f"Column '{col_name}' not found in headers")
        
        return indices
    
    def _is_numeric(self, value: str) -> bool:
        """Helper method to check if a string represents a number."""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def get_cleaning_summary(self) -> Dict:
        """Get a summary of all cleaning operations performed."""
        return {
            'total_operations': len(self.cleaning_log),
            'operations': self.cleaning_log,
            'final_row_count': len(self.rows),
            'original_row_count': len(self.original_rows)
        }
    
    def reset_to_original(self):
        """Reset the data to its original state."""
        self.rows = self.original_rows.copy()
        self.cleaning_log = []
        log_verbose("Reset data to original state")
