# CSV Display and Debugging Tool
# Rawsab Said
# Version 1.0.4

# TODO fix output issues with PyPI package

import csv
import sys
import re
import json
import os
from collections import Counter

DEBUG_MODE = False
VERBOSE_MODE = False
CUSTOM_DELIMITER = None
DISPLAY_TABLE = False
SAVE_TO_FILE = None

CONFIG = {}
CONFIG_FILE = os.path.expanduser("~/.csvtools/config.json")

VALID_FLAGS = ['-debug', '-v', '-dl', '-display', '-stf']

def load_config():
    global CONFIG
    if not os.path.exists(CONFIG_FILE):
        default_config_path = os.path.join(os.path.dirname(__file__), "csvtoolsConfig.json")
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(default_config_path, 'r') as f_src, open(CONFIG_FILE, 'w') as f_dst:
            f_dst.write(f_src.read())
    with open(CONFIG_FILE, 'r') as f:
        CONFIG.update(json.load(f))

def log_debug(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def log_verbose(message, section_break=False):
    if VERBOSE_MODE:
        if section_break:
            print()
        print(f"[VERBOSE] {message}")

def detect_delimiter(sample_row):
    if CUSTOM_DELIMITER:
        log_verbose(f"Using custom delimiter: {CUSTOM_DELIMITER}\n", section_break=True)
        return CUSTOM_DELIMITER
    log_verbose(f"Detecting delimiter from sample row: {sample_row}")
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

def format_csv(filename):
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

    log_verbose(f"Detected columns: {rows[0]}", section_break=True)

    cleaned_rows = []
    for i, row in enumerate(rows):
        cleaned_row = [clean_field(item) for item in row]
        if cleaned_row != row:
            cleaned_rows.append(cleaned_row)

    if cleaned_rows:
        log_verbose(f"Cleaned rows: {cleaned_rows}", section_break=True)

    expected_length = len(rows[0])
    col_widths = [0] * expected_length

    for row in rows:
        row.extend([''] * (expected_length - len(row)))

    for row in rows:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(item)) + 2)

    log_verbose(f"Formatted column display widths: {col_widths}")

    output = []

    incorrect_length_rows = []
    type_mismatches = []

    column_types = [[] for _ in range(expected_length)]
    for row in rows[1:]:
        for i, item in enumerate(row):
            column_types[i].append(detect_type(item))

    expected_types = [determine_majority_type(types) for types in column_types]

    log_verbose(f"Expected types: {expected_types}\n", section_break=True)

    if DISPLAY_TABLE:
        row_number_width = len(str(len(rows) - 1))

        header_row = f"{' ' * row_number_width} | " + " | ".join(f"{rows[0][i]:<{col_widths[i]}}" for i in range(expected_length))
        output.append(header_row)
        separator = f"{'--' * row_number_width}-" + "+".join('-' * (width + 2) for width in col_widths)
        output.append(separator)

        for row_number, row in enumerate(rows[1:], start=1):
            actual_length = len([item for item in row if item.strip() != ''])

            if actual_length != expected_length:
                incorrect_length_rows.append((row_number, actual_length))

            for i, item in enumerate(row):
                actual_type = detect_type(item, expected_types[i])
                if expected_types[i] and actual_type != expected_types[i]:
                    type_mismatches.append((row_number, i + 1, actual_type, expected_types[i]))

            formatted_row = f"{row_number:<{row_number_width}} | " + " | ".join(
                f"{row[i]:<{col_widths[i]}}" for i in range(expected_length)
            )
            output.append(formatted_row)

        if SAVE_TO_FILE:
            with open(SAVE_TO_FILE, 'w') as f:
                f.write("\n".join(output))
            print(f"Output saved to {SAVE_TO_FILE}")
        else:
            print("\n".join(output))

    if DEBUG_MODE:
        debug_output = []

        if incorrect_length_rows:
            debug_output.append("\nROWS WITH INCORRECT LENGTH:")
            for row_number, actual_length in incorrect_length_rows:
                debug_output.append(f"Row {row_number} is of length {actual_length}, expected {expected_length}")

        if type_mismatches:
            debug_output.append("\nROWS WITH POTENTIAL TYPE MISMATCHES:")
            for row_number, column, actual_type, expected_type in type_mismatches:
                debug_output.append(f"Row {row_number}, Column {column}: Found {actual_type}, expected {expected_types[column-1]}")

        debug_output.append(f"\nTotal number of rows with incorrect length: {len(incorrect_length_rows)}")
        debug_output.append(f"Total number of type mismatches: {len(type_mismatches)}")

        if debug_output:
            print("\n".join(debug_output))
    print()

def check_unknown_flags():
    for arg in sys.argv[2:]:
        if arg.startswith('-') and arg not in VALID_FLAGS:
            print(f"Unknown flag: {arg}")
            sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("To use script: csvt <filename.csv> [-display] [-debug] [-v] [-dl delimiter] [-stf output.txt]")
        sys.exit(1)

    if sys.argv[1] == "config":
        os.system(f"{os.getenv('EDITOR', 'nano')} {CONFIG_FILE}")
        sys.exit(0)

    csv_filename = sys.argv[1]
    check_unknown_flags()
    load_config()

    if '-debug' in sys.argv:
        DEBUG_MODE = True
    if '-v' in sys.argv:
        VERBOSE_MODE = True
    if '-display' in sys.argv:
        DISPLAY_TABLE = True
    if '-dl' in sys.argv:
        dl_index = sys.argv.index('-dl') + 1
        if dl_index < len(sys.argv):
            CUSTOM_DELIMITER = sys.argv[dl_index].strip()
        else:
            print("Please provide a custom delimiter after the -dl flag.")
            sys.exit(1)
    if '-stf' in sys.argv:
        stf_index = sys.argv.index('-stf') + 1
        if stf_index < len(sys.argv):
            SAVE_TO_FILE = sys.argv[stf_index].strip()
        else:
            print("Please provide a file name after the -stf flag.")
            sys.exit(1)

    try:
        format_csv(csv_filename)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
