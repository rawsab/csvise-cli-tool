# CSV Display and Debugging Tool
# Rawsab Said
# Version 1.0.1

import csv
import sys
import re
from collections import Counter

DEBUG_MODE = False
VERBOSE_MODE = False

def log_debug(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def log_verbose(message, section_break=False):
    if VERBOSE_MODE:
        if section_break:
            print()
        print(f"[VERBOSE] {message}")

def detect_delimiter(sample_row):
    log_verbose(f"Detecting delimiter from sample row: {sample_row}", section_break=True)
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
        raise ValueError("[UNSUPPORTED DELIMITER] Supported delimiters are multiple tabs, multiple spaces, or comma.")

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

        if delimiter in [r'\t+', r' +']:
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
    print()

    incorrect_length_rows = []
    type_mismatches = []

    column_types = [[] for _ in range(expected_length)]
    for row in rows[1:]:
        for i, item in enumerate(row):
            column_types[i].append(detect_type(item))

    expected_types = [determine_majority_type(types) for types in column_types]

    log_verbose(f"Expected types: {expected_types}", section_break=True)
    if VERBOSE_MODE:
        print()

    header_row = "   | " + " | ".join(f"{rows[0][i]:<{col_widths[i]}}" for i in range(expected_length))
    print(header_row)
    separator = "   -" + "+".join('-' * (width + 2) for width in col_widths)
    print(separator)

    for row_number, row in enumerate(rows[1:], start=1):
        actual_length = len([item for item in row if item.strip() != ''])

        if actual_length != expected_length:
            incorrect_length_rows.append((row_number, actual_length))

        for i, item in enumerate(row):
            actual_type = detect_type(item, expected_types[i])
            if expected_types[i] and actual_type != expected_types[i]:
                type_mismatches.append((row_number, i + 1, actual_type, expected_types[i]))

        formatted_row = f"{row_number:<2} | " + " | ".join(
            f"{row[i]:<{col_widths[i]}}" for i in range(expected_length)
        )
        print(formatted_row)

    if DEBUG_MODE:
        if incorrect_length_rows:
            print("\nROWS WITH INCORRECT LENGTH:")
            for row_number, actual_length in incorrect_length_rows:
                print(f"Row {row_number} is of length {actual_length}, expected {expected_length}")

        if type_mismatches:
            print("\nROWS WITH POTENTIAL TYPE MISMATCHES:")
            for row_number, column, actual_type, expected_type in type_mismatches:
                print(f"Row {row_number}, Column {column}: Found {actual_type}, expected {expected_type}")

        print(f"\nTotal number of rows with incorrect length: {len(incorrect_length_rows)}")
        print(f"Total number of type mismatches: {len(type_mismatches)}")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("TO USE SCRIPT: python3 csvdisplay.py <filename.csv> [-debug] [-v]")
        sys.exit(1)

    csv_filename = sys.argv[1]
    if '-debug' in sys.argv:
        DEBUG_MODE = True
    if '-v' in sys.argv:
        VERBOSE_MODE = True

    try:
        format_csv(csv_filename)
    except ValueError as e:
        print(f"Error: {e}")
