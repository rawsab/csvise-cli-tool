# CSV Display and Debugging Tool
# Rawsab Said
# Version 1.1.0

import csv
import sys
import re
import json
import click
from collections import Counter
from typing import List, Tuple

from .config import CONFIG, load_config
from .utils import log_debug, log_verbose, set_debug_mode, set_verbose_mode
from .delimiter import detect_delimiter
from .cleaning import clean_field, apply_string_case
from .types import detect_type, determine_majority_type
from .formatter import format_and_output_csv
from .rich_formatter import format_and_output_csv_rich, show_file_info, show_error_message, show_success_message
from .cleaning_ops import DataCleaner
from .statistics import DataAnalyzer
from .rich_analysis import display_statistics_rich, display_cleaning_operations_rich, show_analysis_menu

CUSTOM_DELIMITER = None
DISPLAY_TABLE = False
SAVE_TO_FILE = None

def clean_field(field):
    original_field = field
    field = field.strip()
    field = re.sub(r'\s+', ' ', field)

    if CONFIG["string_case"] == "upper":
        field = field.upper()
    elif CONFIG["string_case"] == "lower":
        field = field.lower()

    if original_field != field:
        log_verbose(f"Cleaning field: '{original_field}' -> '{field}'")
    return field

def detect_type(value, expected_type=None):
    if value.lower() in ['true', 'false']:
        return 'bool'
    if value.isdigit():
        return 'int'
    try:
        float(value)
        if expected_type == 'int' and '.' not in value:
            return 'int'
        return 'float'
    except ValueError:
        pass
    return 'str'

def determine_majority_type(types, threshold=0.7):
    type_counts = Counter(types)
    most_common_type, count = type_counts.most_common(1)[0]
    log_verbose(f"Determining majority type from: {types} -> {most_common_type} (count: {count})")
    if count / len(types) >= threshold:
        return most_common_type
    return None

def apply_string_case(value, case_type):
    if case_type == "upper":
        return value.upper()
    elif case_type == "lower":
        return value.lower()
    return value

@click.group()
@click.version_option('1.2.0', prog_name="CSV Display and Debugging Tool")
def cli():
    """CSVise: CLI Tools for Tabular Data"""
    pass

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--display', is_flag=True, help="Displays a formatted table of the CSV data.")
@click.option('--debug', is_flag=True, help="Enables debugging output for troubleshooting purposes.")
@click.option('--verbose', '-v', is_flag=True, help="Activates verbose mode, providing detailed logs about script operations.")
@click.option('--delimiter', '-dl', help="Sets a custom delimiter for splitting fields in the target file.")
@click.option('--save-to-file', '-stf', help="Saves the printed output to a specified file.")
@click.option('--rich', is_flag=True, help="Use Rich formatting for enhanced CLI output (colors, tables, panels). [default]")
@click.option('--classic', is_flag=True, help="Use classic plain text formatting.")
def display(filename, display, debug, verbose, delimiter, save_to_file, rich, classic):
    """Display and debug CSV files."""
    CUSTOM_DELIMITER = None
    DISPLAY_TABLE = False
    SAVE_TO_FILE = None

    if debug:
        set_debug_mode(True)
    if verbose:
        set_verbose_mode(True)
    if display:
        DISPLAY_TABLE = True
    if delimiter:
        CUSTOM_DELIMITER = delimiter
    if save_to_file:
        SAVE_TO_FILE = save_to_file

    load_config()

    try:
        _format_csv(filename, CUSTOM_DELIMITER, DISPLAY_TABLE, SAVE_TO_FILE, rich, classic)
    except ValueError as e:
        if not classic:
            show_error_message(str(e))
        else:
            raise click.ClickException(str(e))

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--columns', '-c', help="Comma-separated list of columns to analyze. If not specified, analyzes all columns.")
@click.option('--correlations', is_flag=True, help="Show correlation matrix for numeric columns.")
@click.option('--outliers', is_flag=True, help="Detect outliers in numeric columns.")
@click.option('--distribution', is_flag=True, help="Show value distribution for categorical columns.")
@click.option('--verbose', '-v', is_flag=True, help="Activates verbose mode.")
@click.option('--classic', is_flag=True, help="Use classic plain text formatting.")
def analyze(filename, columns, correlations, outliers, distribution, verbose, classic):
    """Analyze CSV data with comprehensive statistics."""
    
    if verbose:
        set_verbose_mode(True)
    
    load_config()
    
    try:
        # Load and process CSV data
        rows, headers = _load_csv_data(filename)
        
        if not rows:
            show_error_message("The file is empty or could not be processed.")
            return
        
        # Initialize analyzer
        analyzer = DataAnalyzer(rows, headers)
        
        # Determine which columns to analyze
        columns_to_analyze = None
        if columns:
            columns_to_analyze = [col.strip() for col in columns.split(',')]
        
        # Display statistics
        if not classic:
            display_statistics_rich(analyzer, columns_to_analyze, correlations)
        else:
            _display_statistics_classic(analyzer, columns_to_analyze, correlations)
            
    except Exception as e:
        if not classic:
            show_error_message(str(e))
        else:
            raise click.ClickException(str(e))

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--remove-duplicates', is_flag=True, help="Remove duplicate rows.")
@click.option('--normalize-whitespace', is_flag=True, help="Normalize whitespace in all columns.")
@click.option('--standardize-case', type=click.Choice(['upper', 'lower', 'title', 'sentence']), help="Standardize text case.")
@click.option('--fill-missing', type=click.Choice(['empty', 'mode', 'mean', 'median', 'custom']), help="Fill missing values using specified strategy.")
@click.option('--fill-value', help="Custom value to use when filling missing values.")
@click.option('--remove-empty-rows', type=float, help="Remove rows with specified fraction of empty cells (0.0 to 1.0).")
@click.option('--output', '-o', help="Output file for cleaned data.")
@click.option('--verbose', '-v', is_flag=True, help="Activates verbose mode.")
@click.option('--classic', is_flag=True, help="Use classic plain text formatting.")
def clean(filename, remove_duplicates, normalize_whitespace, standardize_case, fill_missing, fill_value, remove_empty_rows, output, verbose, classic):
    """Clean CSV data using various operations."""
    
    if verbose:
        set_verbose_mode(True)
    
    load_config()
    
    try:
        # Load and process CSV data
        rows, headers = _load_csv_data(filename)
        
        if not rows:
            show_error_message("The file is empty or could not be processed.")
            return
        
        # Initialize cleaner
        cleaner = DataCleaner(rows, headers)
        
        # Perform cleaning operations
        operations_performed = []
        
        if remove_duplicates:
            cleaned_rows, removed_count = cleaner.remove_duplicates()
            operations_performed.append(f"Removed {removed_count} duplicates")
        
        if normalize_whitespace:
            modified_count = cleaner.normalize_whitespace()
            operations_performed.append(f"Normalized whitespace in {modified_count} cells")
        
        if standardize_case:
            modified_count = cleaner.standardize_case(standardize_case)
            operations_performed.append(f"Standardized case to {standardize_case} in {modified_count} cells")
        
        if fill_missing:
            strategy = fill_missing
            if fill_missing == 'custom' and not fill_value:
                show_error_message("Custom fill strategy requires --fill-value parameter")
                return
            modified_count = cleaner.fill_missing_values(strategy, fill_value or '')
            operations_performed.append(f"Filled {modified_count} missing values using {strategy} strategy")
        
        if remove_empty_rows is not None:
            cleaned_rows, removed_count = cleaner.remove_empty_rows(remove_empty_rows)
            operations_performed.append(f"Removed {removed_count} empty rows")
        
        # Display results
        if not classic:
            display_cleaning_operations_rich(cleaner, operations_performed)
        else:
            _display_cleaning_classic(cleaner, operations_performed)
        
        # Save cleaned data if output specified
        if output:
            _save_cleaned_data(cleaner.rows, headers, output)
            show_success_message(f"Cleaned data saved to {output}")
            
    except Exception as e:
        if not classic:
            show_error_message(str(e))
        else:
            raise click.ClickException(str(e))

def _format_csv(filename, CUSTOM_DELIMITER, DISPLAY_TABLE, SAVE_TO_FILE, use_rich=True, use_classic=False):
    # Determine which formatter to use (Rich by default, unless classic is explicitly requested)
    if use_classic:
        print(f"Opening CSV file: {filename}")
    else:
        show_file_info(filename)
    with open(filename, 'r') as file:
        sample_row = file.readline()
        delimiter = detect_delimiter(sample_row, CUSTOM_DELIMITER)
        file.seek(0)

        if CUSTOM_DELIMITER:
            rows = [line.strip().split(CUSTOM_DELIMITER) for line in file]
            rows = [[clean_field(item) for item in row] for row in rows]
        elif delimiter in [r'\t+', r' +']:
            rows = [re.split(delimiter, line.strip()) for line in file]
        else:
            reader = csv.reader(file, delimiter=delimiter)
            rows = list(reader)

    if not rows:
        print("The file is empty.")
        return

    print(f"Number of rows read: {len(rows)}")
    log_verbose(f"Detected columns: {rows[0]}", section_break=True)

    cleaned_rows = []
    for i, row in enumerate(rows):
        cleaned_row = [clean_field(item) for item in row]
        cleaned_rows.append(cleaned_row)

    rows = cleaned_rows

    expected_length = len(rows[0])
    col_widths = [0] * expected_length

    for row in rows:
        row.extend([''] * (expected_length - len(row)))

    for row in rows:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(item)) + 2)

    log_verbose(f"Formatted column display widths: {col_widths}")

    incorrect_length_rows = []
    type_mismatches = []

    column_types = [[] for _ in range(expected_length)]
    for row in rows[1:]:
        for i, item in enumerate(row):
            column_types[i].append(detect_type(item))

    expected_types = [determine_majority_type(types) for types in column_types]

    log_verbose(f"Expected types: {expected_types}\n", section_break=True)

    # Check for incorrect length and type mismatches
    for row_number, row in enumerate(rows[CONFIG["start_index"]:], start=CONFIG["start_index"]):
        actual_length = len([item for item in row if item.strip() != ''])
        if actual_length != expected_length:
            incorrect_length_rows.append((row_number, actual_length))
        for i, item in enumerate(row):
            if CONFIG["check_type_mismatches"]:
                actual_type = detect_type(item, expected_types[i])
                if expected_types[i] and actual_type != expected_types[i]:
                    type_mismatches.append((row_number, i + 1, actual_type, expected_types[i]))

    from .utils import DEBUG_MODE
    
    # Choose formatter based on user preference (Rich by default, unless classic is explicitly requested)
    if use_classic:
        format_and_output_csv(
            rows,
            expected_types,
            col_widths,
            DISPLAY_TABLE,
            SAVE_TO_FILE,
            DEBUG_MODE,
            incorrect_length_rows,
            type_mismatches
        )

def _load_csv_data(filename: str) -> Tuple[List[List[str]], List[str]]:
    """Load CSV data and return rows and headers."""
    with open(filename, 'r') as file:
        sample_row = file.readline()
        delimiter = detect_delimiter(sample_row, None)
        file.seek(0)
        
        if delimiter in [r'\t+', r' +']:
            import re
            rows = [re.split(delimiter, line.strip()) for line in file]
        else:
            import csv
            reader = csv.reader(file, delimiter=delimiter)
            rows = list(reader)
    
    if not rows:
        return [], []
    
    headers = rows[0]
    data_rows = rows[1:]
    
    return data_rows, headers

def _display_statistics_classic(analyzer, columns=None, show_correlations=False):
    """Display statistics in classic text format."""
    if not columns:
        columns = analyzer.headers
    
    print("=== DATA QUALITY REPORT ===")
    quality_report = analyzer.get_data_quality_report()
    print(f"Overall Quality Score: {quality_report['overall_quality_score']:.1%}")
    print(f"Completeness: {quality_report['completeness_score']:.1%}")
    print(f"Consistency: {quality_report['consistency_score']:.1%}")
    print(f"Uniqueness: {quality_report['uniqueness_score']:.1%}")
    print()
    
    for column in columns:
        if column in analyzer.headers:
            stats = analyzer.get_column_statistics(column)
            print(f"=== STATISTICS FOR {column} ===")
            print(f"Data Type: {stats.get('data_type', 'unknown')}")
            print(f"Total Values: {stats.get('total_values', 0)}")
            print(f"Non-empty Values: {stats.get('non_empty_values', 0)}")
            print(f"Missing Percentage: {stats.get('missing_percentage', 0):.1f}%")
            
            if stats.get('data_type') == 'numeric':
                print(f"Min: {stats.get('min')}")
                print(f"Max: {stats.get('max')}")
                print(f"Mean: {stats.get('mean')}")
                print(f"Median: {stats.get('median')}")
                print(f"Std Dev: {stats.get('std_dev')}")
            print()

def _display_cleaning_classic(cleaner, operations_performed):
    """Display cleaning results in classic text format."""
    print("=== CLEANING OPERATIONS SUMMARY ===")
    summary = cleaner.get_cleaning_summary()
    print(f"Total Operations: {summary['total_operations']}")
    print(f"Original Rows: {summary['original_row_count']}")
    print(f"Final Rows: {summary['final_row_count']}")
    print()
    print("Operations Performed:")
    for operation in operations_performed:
        print(f"  • {operation}")

def _save_cleaned_data(rows: List[List[str]], headers: List[str], output_file: str):
    """Save cleaned data to a new CSV file."""
    import csv
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)
