# CSV Display and Debugging Tool
# Rawsab Said
# Version 1.0.9

import csv
import sys
import re
import json
from collections import Counter

DEBUG_MODE = False
VERBOSE_MODE = False
CUSTOM_DELIMITER = None
DISPLAY_TABLE = False
SAVE_TO_FILE = None

VALID_FLAGS = ['-debug', '-v', '-dl', '-display', '-stf']

CONFIG_FILE = 'csvtoolsConfig.json'

CONFIG = {
    "additional_delimiters": [],
    "start_index": 1,
    "num_rows_to_print": None,
    "display_column_lines": False,
    "display_row_lines": False,
    "check_type_mismatches": True,
    "string_case": "default"
}

def log_debug(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def log_verbose(message, section_break=False):
    if VERBOSE_MODE:
        if section_break:
            print()
        print(f"[VERBOSE] {message}")

def load_config():
    global CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            user_config = json.load(f)
            CONFIG.update(user_config)
            log_verbose(f"Loaded configuration: {CONFIG}", section_break=True)
    except FileNotFoundError:
        log_verbose(f"Configuration file {CONFIG_FILE} not found. Using default settings.", section_break=True)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {CONFIG_FILE}. Using default settings.")
    except Exception as e:
        print(f"Error loading configuration: {e}. Using default settings.")

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

def format_csv(filename):
    print(f"Opening CSV file: {filename}")
    with open(filename, 'r') as file:
        sample_row = file.readline()
        delimiter = detect_delimiter(sample_row)
        file.seek(0)

        # Read rows based on delimiter
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

    # Clean rows and log verbose if needed
    cleaned_rows = []
    for i, row in enumerate(rows):
        cleaned_row = [clean_field(item) for item in row]
        if cleaned_row != row:
            cleaned_rows.append(cleaned_row)

    if cleaned_rows:
        log_verbose(f"Cleaned rows: {cleaned_rows}", section_break=True)

    expected_length = len(rows[0])
    col_widths = [0] * expected_length

    # Extend rows to match expected length
    for row in rows:
        row.extend([''] * (expected_length - len(row)))

    # Determine column widths for formatting
    for row in rows:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(item)) + 2)

    log_verbose(f"Formatted column display widths: {col_widths}")
    output = []

    incorrect_length_rows = []
    type_mismatches = []

    # Determine data types for each column
    column_types = [[] for _ in range(expected_length)]
    for row in rows[1:]:
        for i, item in enumerate(row):
            column_types[i].append(detect_type(item))

    expected_types = [determine_majority_type(types) for types in column_types]

    log_verbose(f"Expected types: {expected_types}\n", section_break=True)

    if DISPLAY_TABLE:
        print("Starting to format table for display...")
        row_number_width = len(str(len(rows) - 1))
        start_index = CONFIG["start_index"]
        num_rows_to_print = CONFIG["num_rows_to_print"] or (len(rows) - start_index)

        separator_char = " " if not CONFIG["display_column_lines"] else "|"
        header_row = f"{' ' * row_number_width} {separator_char} " + f" {separator_char} ".join(
            f"{apply_string_case(rows[0][i], CONFIG['string_case']):<{col_widths[i]}}" for i in range(expected_length)
        )
        output.append(header_row)
        separator = f"{'--' * row_number_width}-" + "+".join('-' * (width + 2) for width in col_widths)
        output.append(separator)

        # Add rows to output
        print(f"Adding formatted rows to output, starting from index {start_index}...")
        for row_number, row in enumerate(rows[start_index:start_index + num_rows_to_print], start=start_index):
            actual_length = len([item for item in row if item.strip() != ''])

            if actual_length != expected_length:
                incorrect_length_rows.append((row_number, actual_length))

            for i, item in enumerate(row):
                if CONFIG["check_type_mismatches"]:
                    actual_type = detect_type(item, expected_types[i])
                    if expected_types[i] and actual_type != expected_types[i]:
                        type_mismatches.append((row_number, i + 1, actual_type, expected_types[i]))

            formatted_row = f"{row_number:<{row_number_width}} {separator_char} " + f" {separator_char} ".join(
                f"{apply_string_case(row[i], CONFIG['string_case']):<{col_widths[i]}}" for i in range(expected_length)
            )
            output.append(formatted_row)
            print(f"Formatted row {row_number}: {formatted_row}")  # Debugging line
            if CONFIG["display_row_lines"]:
                output.append('-' * len(formatted_row))

    # If in debug mode, show issues
    if DEBUG_MODE:
        if incorrect_length_rows:
            output.append("\nROWS WITH INCORRECT LENGTH:")
            for row_number, actual_length in incorrect_length_rows:
                output.append(f"Row {row_number} is of length {actual_length}, expected {expected_length}")

        if type_mismatches:
            output.append("\nROWS WITH POTENTIAL TYPE MISMATCHES:")
            for row_number, column, actual_type, expected_type in type_mismatches:
                output.append(f"Row {row_number}, Column {column}: Found {actual_type}, expected {expected_type}")

        output.append(f"\nTotal number of rows with incorrect length: {len(incorrect_length_rows)}")
        output.append(f"Total number of type mismatches: {len(type_mismatches)}")
    output.append("")

    # Print or save output
    if not output:
        print("No output was generated. Please check the configuration settings.")
    elif SAVE_TO_FILE:
        with open(SAVE_TO_FILE, 'w') as file:
            file.write('\n'.join(output))
        print(f"Output saved to {SAVE_TO_FILE}")
    else:
        print("Formatted CSV Output:\n" + '\n'.join(output))

def check_unknown_flags():
    for arg in sys.argv[2:]:
        if arg.startswith('-') and arg not in VALID_FLAGS:
            print(f"Unknown flag: {arg}")
            sys.exit(1)

def main():
    print("Test: CSV Display and Debugging Tool started")

    if len(sys.argv) < 2:
        print("To use script: python3 csvtools.py <filename.csv> [-display] [-debug] [-v] [-dl delimiter] [-stf output.txt]")
        sys.exit(1)

    print(f"Arguments passed: {sys.argv}")

    csv_filename = sys.argv[1]
    check_unknown_flags()

    load_config()

    print("Config loaded successfully.")

    if '-debug' in sys.argv:
        DEBUG_MODE = True
        print("Debug mode enabled.")
    if '-v' in sys.argv:
        VERBOSE_MODE = True
        print("Verbose mode enabled.")
    if '-display' in sys.argv:
        DISPLAY_TABLE = True
        print("Display table enabled.")
    if '-dl' in sys.argv:
        dl_index = sys.argv.index('-dl') + 1
        if dl_index < len(sys.argv):
            CUSTOM_DELIMITER = sys.argv[dl_index].strip()
            print(f"Custom delimiter set to: {CUSTOM_DELIMITER}")
        else:
            print("Please provide a custom delimiter after the -dl flag.")
            sys.exit(1)
    if '-stf' in sys.argv:
        stf_index = sys.argv.index('-stf') + 1
        if stf_index < len(sys.argv):
            SAVE_TO_FILE = sys.argv[stf_index].strip()
            print(f"Output will be saved to: {SAVE_TO_FILE}")
        else:
            print("Please provide a file name after the -stf flag.")
            sys.exit(1)

    try:
        print(f"Formatting CSV file: {csv_filename}")
        format_csv(csv_filename)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
