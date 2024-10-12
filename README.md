# 🛠️ CSV Tools

## 💻 Setup
Download `csvtools.py` (recommended to add to project directory) and run commands in terminal.

## 💡 Features
Run the following command, replacing `<filename.csv>` with path to target file and add flags for the following functionalities:
```
python3 csvtools.py <filename.csv> [-display] [-debug] [-v] [-dl delimiter] [-stf output.txt]
```
- `-display` : Displays a formatted table output of the CSV data.
- `-debug` : Enables debug output for troubleshooting purposes, including information on incomplete data and type mismatches.
- `-v` : Activates verbose mode, provides detailed logs about script operations.
- `-dl delimiter` : Sets a custom delimiter for splitting fields in target CSV file.
- `-stf output.txt` : Saves script output to a file (change `output.txt` to desired file to save in).

### Custom Delimiter Example:
```
python3 csvtools.py data.csv -display -dl ";"
```
Displays a formatted table output of `data.csv` where the fields in raw data are separated by ";" (semicolon).

### ⚙️ Configuration
Customize default behaviour of the script with `csvtoolsConfig.json` (ensure it is in the same directory as `csvtools.py`).
```jsonc
{
    // additional delimiters to automatically detect
    "additional_delimiters": ["|", ";", "###"],

    // -display flag prints table starting at this index
    "start_index": 1,

    // setting to null prints all rows
    "num_rows_to_print": null,

    // table display formatting customization
    "display_column_lines": true,
    "display_row_lines": false,

    "check_type_mismatches": true,

    "string_case": "default"  // options: "default", "upper", "lower"
}
```

## 🗓️ Upcoming Features
- Data normalization
- Duplicate row detection
- Interactive issue handling
- Pandas integration for data analysis
