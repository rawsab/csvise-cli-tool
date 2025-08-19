"""
Enhanced Statistics Module
Provides comprehensive statistical analysis and data quality metrics for CSV data.
"""

import math
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter, defaultdict
from statistics import mean, median, mode, stdev, variance
from .utils import log_verbose, log_debug
from .config import CONFIG


class DataAnalyzer:
    """Main class for data analysis and statistics."""
    
    def __init__(self, rows: List[List[str]], headers: List[str]):
        self.rows = rows
        self.headers = headers
        self.analysis_cache = {}
    
    def get_column_statistics(self, column_name: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a specific column.
        
        Args:
            column_name: Name of the column to analyze
        
        Returns:
            Dictionary containing various statistics
        """
        if column_name not in self.headers:
            return {'error': f'Column "{column_name}" not found'}
        
        column_index = self.headers.index(column_name)
        column_values = [row[column_index] if column_index < len(row) else '' for row in self.rows]
        
        # Determine data type
        data_type = self._infer_data_type(column_values)
        
        stats = {
            'column_name': column_name,
            'data_type': data_type,
            'total_values': len(column_values),
            'non_empty_values': len([v for v in column_values if v and v.strip()]),
            'empty_values': len([v for v in column_values if not v or not v.strip()]),
            'unique_values': len(set(v for v in column_values if v and v.strip())),
            'missing_percentage': self._calculate_missing_percentage(column_values)
        }
        
        if data_type == 'numeric':
            stats.update(self._get_numeric_statistics(column_values))
        elif data_type == 'date':
            stats.update(self._get_date_statistics(column_values))
        elif data_type == 'categorical':
            stats.update(self._get_categorical_statistics(column_values))
        
        return stats
    
    def get_all_column_statistics(self) -> Dict[str, Dict]:
        """
        Get statistics for all columns.
        
        Returns:
            Dictionary with column names as keys and statistics as values
        """
        all_stats = {}
        for header in self.headers:
            all_stats[header] = self.get_column_statistics(header)
        return all_stats
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive data quality report.
        
        Returns:
            Dictionary containing overall data quality metrics
        """
        total_rows = len(self.rows)
        total_cells = total_rows * len(self.headers) if total_rows > 0 else 0
        
        # Calculate overall statistics
        empty_cells = 0
        duplicate_rows = 0
        inconsistent_lengths = 0
        
        for row in self.rows:
            empty_cells += sum(1 for cell in row if not cell or not cell.strip())
            if len(row) != len(self.headers):
                inconsistent_lengths += 1
        
        # Check for duplicate rows
        seen_rows = set()
        for row in self.rows:
            row_tuple = tuple(cell.strip() if cell else '' for cell in row)
            if row_tuple in seen_rows:
                duplicate_rows += 1
            seen_rows.add(row_tuple)
        
        # Calculate quality scores
        completeness_score = (total_cells - empty_cells) / total_cells if total_cells > 0 else 0
        consistency_score = (total_rows - inconsistent_lengths) / total_rows if total_rows > 0 else 0
        uniqueness_score = (total_rows - duplicate_rows) / total_rows if total_rows > 0 else 0
        
        overall_quality_score = (completeness_score + consistency_score + uniqueness_score) / 3
        
        return {
            'overall_quality_score': overall_quality_score,
            'completeness_score': completeness_score,
            'consistency_score': consistency_score,
            'uniqueness_score': uniqueness_score,
            'total_rows': total_rows,
            'total_columns': len(self.headers),
            'total_cells': total_cells,
            'empty_cells': empty_cells,
            'duplicate_rows': duplicate_rows,
            'inconsistent_lengths': inconsistent_lengths,
            'missing_percentage': (empty_cells / total_cells * 100) if total_cells > 0 else 0
        }
    
    def get_correlation_matrix(self, numeric_columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate correlation matrix for numeric columns.
        
        Args:
            numeric_columns: List of column names to include. If None, uses all numeric columns.
        
        Returns:
            Dictionary representing correlation matrix
        """
        if not numeric_columns:
            numeric_columns = []
            for header in self.headers:
                stats = self.get_column_statistics(header)
                if stats.get('data_type') == 'numeric':
                    numeric_columns.append(header)
        
        if len(numeric_columns) < 2:
            return {}
        
        # Extract numeric data
        numeric_data = {}
        for col in numeric_columns:
            col_index = self.headers.index(col)
            values = []
            for row in self.rows:
                if col_index < len(row) and row[col_index]:
                    try:
                        values.append(float(row[col_index]))
                    except ValueError:
                        continue
            numeric_data[col] = values
        
        # Calculate correlations
        correlation_matrix = {}
        for col1 in numeric_columns:
            correlation_matrix[col1] = {}
            for col2 in numeric_columns:
                if col1 == col2:
                    correlation_matrix[col1][col2] = 1.0
                else:
                    correlation_matrix[col1][col2] = self._calculate_correlation(
                        numeric_data[col1], numeric_data[col2]
                    )
        
        return correlation_matrix
    
    def get_outliers(self, column_name: str, method: str = 'iqr', threshold: float = 1.5) -> List[Tuple[int, float]]:
        """
        Detect outliers in a numeric column.
        
        Args:
            column_name: Name of the column to analyze
            method: 'iqr' (Interquartile Range) or 'zscore'
            threshold: Threshold for outlier detection
        
        Returns:
            List of tuples (row_index, value) for outliers
        """
        if column_name not in self.headers:
            return []
        
        stats = self.get_column_statistics(column_name)
        if stats.get('data_type') != 'numeric':
            return []
        
        column_index = self.headers.index(column_name)
        numeric_values = []
        row_indices = []
        
        for i, row in enumerate(self.rows):
            if column_index < len(row) and row[column_index]:
                try:
                    value = float(row[column_index])
                    numeric_values.append(value)
                    row_indices.append(i)
                except ValueError:
                    continue
        
        if len(numeric_values) < 4:
            return []
        
        outliers = []
        
        if method == 'iqr':
            q1 = self._percentile(numeric_values, 25)
            q3 = self._percentile(numeric_values, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            for i, value in enumerate(numeric_values):
                if value < lower_bound or value > upper_bound:
                    outliers.append((row_indices[i] + 1, value))  # +1 for 1-based indexing
        
        elif method == 'zscore':
            mean_val = mean(numeric_values)
            std_val = stdev(numeric_values) if len(numeric_values) > 1 else 0
            
            if std_val > 0:
                for i, value in enumerate(numeric_values):
                    z_score = abs((value - mean_val) / std_val)
                    if z_score > threshold:
                        outliers.append((row_indices[i] + 1, value))
        
        return outliers
    
    def get_value_distribution(self, column_name: str, top_n: int = 10) -> Dict[str, Any]:
        """
        Get value distribution for a column.
        
        Args:
            column_name: Name of the column to analyze
            top_n: Number of top values to return
        
        Returns:
            Dictionary containing distribution information
        """
        if column_name not in self.headers:
            return {'error': f'Column "{column_name}" not found'}
        
        column_index = self.headers.index(column_name)
        values = [row[column_index] if column_index < len(row) else '' for row in self.rows]
        
        # Filter out empty values
        non_empty_values = [v for v in values if v and v.strip()]
        
        if not non_empty_values:
            return {
                'column_name': column_name,
                'total_values': len(values),
                'non_empty_values': 0,
                'top_values': [],
                'distribution': {}
            }
        
        # Count occurrences
        value_counts = Counter(non_empty_values)
        total_non_empty = len(non_empty_values)
        
        # Get top values
        top_values = value_counts.most_common(top_n)
        
        # Calculate distribution
        distribution = {}
        for value, count in value_counts.items():
            distribution[value] = {
                'count': count,
                'percentage': (count / total_non_empty) * 100
            }
        
        return {
            'column_name': column_name,
            'total_values': len(values),
            'non_empty_values': total_non_empty,
            'unique_values': len(value_counts),
            'top_values': [(value, count, (count / total_non_empty) * 100) for value, count in top_values],
            'distribution': distribution
        }
    
    def _infer_data_type(self, values: List[str]) -> str:
        """Infer the data type of a column based on its values."""
        if not values:
            return 'unknown'
        
        # Check if it's numeric
        numeric_count = 0
        date_count = 0
        total_non_empty = 0
        
        for value in values:
            if not value or not value.strip():
                continue
            
            total_non_empty += 1
            
            # Check if numeric
            try:
                float(value)
                numeric_count += 1
            except ValueError:
                pass
            
            # Check if date (basic check)
            if self._looks_like_date(value):
                date_count += 1
        
        if total_non_empty == 0:
            return 'unknown'
        
        numeric_ratio = numeric_count / total_non_empty
        date_ratio = date_count / total_non_empty
        
        if numeric_ratio > 0.8:
            return 'numeric'
        elif date_ratio > 0.5:
            return 'date'
        else:
            return 'categorical'
    
    def _looks_like_date(self, value: str) -> bool:
        """Basic check if a string looks like a date."""
        import re
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}-\d{1,2}-\d{2,4}'
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    def _calculate_missing_percentage(self, values: List[str]) -> float:
        """Calculate the percentage of missing/empty values."""
        if not values:
            return 100.0
        
        empty_count = sum(1 for v in values if not v or not v.strip())
        return (empty_count / len(values)) * 100
    
    def _get_numeric_statistics(self, values: List[str]) -> Dict[str, Any]:
        """Get statistics for numeric data."""
        numeric_values = []
        for value in values:
            if value and value.strip():
                try:
                    numeric_values.append(float(value))
                except ValueError:
                    continue
        
        if not numeric_values:
            return {
                'min': None, 'max': None, 'mean': None, 'median': None,
                'std_dev': None, 'variance': None, 'q1': None, 'q3': None
            }
        
        numeric_values.sort()
        
        return {
            'min': min(numeric_values),
            'max': max(numeric_values),
            'mean': mean(numeric_values),
            'median': median(numeric_values),
            'std_dev': stdev(numeric_values) if len(numeric_values) > 1 else 0,
            'variance': variance(numeric_values) if len(numeric_values) > 1 else 0,
            'q1': self._percentile(numeric_values, 25),
            'q3': self._percentile(numeric_values, 75),
            'range': max(numeric_values) - min(numeric_values)
        }
    
    def _get_date_statistics(self, values: List[str]) -> Dict[str, Any]:
        """Get statistics for date data."""
        # Basic date statistics - could be enhanced with proper date parsing
        return {
            'date_format_detected': True,
            'unique_dates': len(set(v for v in values if v and v.strip()))
        }
    
    def _get_categorical_statistics(self, values: List[str]) -> Dict[str, Any]:
        """Get statistics for categorical data."""
        non_empty_values = [v for v in values if v and v.strip()]
        value_counts = Counter(non_empty_values)
        
        return {
            'most_common_value': value_counts.most_common(1)[0] if value_counts else None,
            'least_common_value': min(value_counts.items(), key=lambda x: x[1]) if value_counts else None,
            'entropy': self._calculate_entropy(value_counts)
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            mean_x = mean(x)
            mean_y = mean(y)
            
            numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
            denominator_x = sum((xi - mean_x) ** 2 for xi in x)
            denominator_y = sum((yi - mean_y) ** 2 for yi in y)
            
            if denominator_x == 0 or denominator_y == 0:
                return 0.0
            
            return numerator / math.sqrt(denominator_x * denominator_y)
        except:
            return 0.0
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of a list of values."""
        if not values:
            return 0.0
        
        values.sort()
        index = (percentile / 100) * (len(values) - 1)
        
        if index.is_integer():
            return values[int(index)]
        else:
            lower = values[int(index)]
            upper = values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_entropy(self, value_counts: Counter) -> float:
        """Calculate Shannon entropy for categorical data."""
        total = sum(value_counts.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in value_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
