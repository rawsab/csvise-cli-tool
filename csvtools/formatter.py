from .config import CONFIG
from .utils import log_verbose
from .cleaning import apply_string_case

def format_and_output_csv(rows, expected_types, col_widths, display_table, save_to_file, debug_mode, incorrect_length_rows, type_mismatches):
    output = []
    expected_length = len(rows[0])

    if display_table:
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

        for row_number, row in enumerate(rows[start_index:start_index + num_rows_to_print], start=start_index):
            formatted_row = f"{row_number:<{row_number_width}} {separator_char} " + f" {separator_char} ".join(
                f"{apply_string_case(row[i], CONFIG['string_case']):<{col_widths[i]}}" for i in range(expected_length)
            )
            output.append(formatted_row)
            if CONFIG["display_row_lines"]:
                output.append('-' * len(formatted_row))

    if debug_mode:
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

    if save_to_file:
        with open(save_to_file, 'w') as file:
            file.write('\n'.join(output))
        print(f"Output saved to {save_to_file}")
    else:
        print('\n'.join(output))
