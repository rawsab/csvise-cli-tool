# CSV Display and Debugging Tool
# Rawsab Said
# Version 1.1.0

import csv
import sys
import re
import json
import click
from collections import Counter

from .config import CONFIG, load_config
from .utils import log_debug, log_verbose, set_debug_mode, set_verbose_mode
from .delimiter import detect_delimiter
from .cleaning import clean_field, apply_string_case
from .types import detect_type, determine_majority_type
from .formatter import format_and_output_csv

CUSTOM_DELIMITER = None
DISPLAY_TABLE = False
SAVE_TO_FILE = None

def detect_delimiter(sample_row):
    if CUSTOM_DELIMITER:
        log_verbose(f"Using custom delimiter: {CUSTOM_DELIMITER}\n", section_break=True)
        return CUSTOM_DELIMITER
    log_verbose(f"Detecting delimiter from sample row: {sample_row}")

    for delim in CONFIG["additional_delimiters"]:
        if delim in sample_row:
            log_verbose(f"Delimiter detected from config: {delim}")
            return delim

    if re.search(r'\t{2,}', sample_row):
        log_verbose("Delimiter detected: Tabs")
        return r'\t+'
    elif re.search(r' {2,}', sample_row):
        log_verbose("Delimiter detected: Spaces")
        return r' +'
    elif ',' in sample_row:
        log_verbose("Delimiter detected: ,")
        return ','
    else:
        raise ValueError("Supported delimiters are multiple tabs, multiple spaces, or comma. Use -dl flag for custom delimiter.")

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

@click.command()
@click.argument('filename')
@click.option('--display', is_flag=True, help="Displays a formatted table of the CSV data.")
@click.option('--debug', is_flag=True, help="Enables debugging output for troubleshooting purposes.")
@click.option('--verbose', '-v', is_flag=True, help="Activates verbose mode, providing detailed logs about script operations.")
@click.option('--delimiter', '-dl', help="Sets a custom delimiter for splitting fields in the target file.")
@click.option('--save_to_file', '-stf', help="Saves the printed output to a specified file.")
@click.version_option('1.1.0', prog_name="CSV Display and Debugging Tool")
def main(filename, display, debug, verbose, delimiter, save_to_file):
    global CUSTOM_DELIMITER, DISPLAY_TABLE, SAVE_TO_FILE

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
        format_csv(filename)
    except ValueError as e:
        print(f"Error: {e}")

def format_csv(filename):
    print(f"Opening CSV file: {filename}")
    with open(filename, 'r') as file:
        sample_row = file.readline()
        delimiter = detect_delimiter(sample_row)
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

    format_and_output_csv(
        rows,
        expected_types,
        col_widths,
        DISPLAY_TABLE,
        SAVE_TO_FILE,
        getattr(sys.modules['csvtools.utils'], 'DEBUG_MODE', False),
        incorrect_length_rows,
        type_mismatches
    )

if __name__ == "__main__":
    main()
