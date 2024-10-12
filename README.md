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
Displays a formatted table output of `data.csv` where the fields in raw data are separated by `;` (semicolon).

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

## Example Output
```
[VERBOSE] Detecting delimiter from sample row: Name,Age,Occupation

[VERBOSE] Delimiter detected: ,

[VERBOSE] Detected columns: ['Name', 'Age', 'Occupation']
[VERBOSE] Cleaning field: ' 30' -> '30'
[VERBOSE] Cleaning field: ' Engineer' -> 'Engineer'
[VERBOSE] Cleaning field: ' Designer' -> 'Designer'
[VERBOSE] Cleaning field: ' Manager' -> 'Manager'
[VERBOSE] Cleaning field: ' 28' -> '28'
[VERBOSE] Cleaning field: ' 7' -> '7'
[VERBOSE] Cleaning field: '  40.5 ' -> '40.5'
[VERBOSE] Cleaning field: ' Developer' -> 'Developer'
[VERBOSE] Cleaning field: ' 20  ' -> '20'
[VERBOSE] Cleaning field: ' Student' -> 'Student'
[VERBOSE] Cleaning field: '45 ' -> '45'
[VERBOSE] Cleaning field: '   Retired' -> 'Retired'

[VERBOSE] Cleaned rows: [['Alice', '30', 'Engineer'], ['Bob', '25', 'Designer'], ['Charlie', 'Manager'], ['Diana', '28', '7'], ['Edward', '40.5', 'Developer'], ['Frank', '20', 'Student'], ['George', '45', 'Retired']]
[VERBOSE] Formatted column display widths: [9, 10, 12]
[VERBOSE] Determining majority type from: ['str', 'str', 'str', 'str', 'str', 'str', 'str'] -> str (count: 7)
[VERBOSE] Determining majority type from: ['int', 'int', 'str', 'int', 'float', 'int', 'int'] -> int (count: 5)
[VERBOSE] Determining majority type from: ['str', 'str', 'str', 'int', 'str', 'str', 'str'] -> str (count: 6)

[VERBOSE] Expected types: ['str', 'float', 'str']

  | Name      | Age        | Occupation  
--------------+------------+--------------
1 | Alice     |  30        |  Engineer   
2 | Bob       | 25         |  Designer   
3 | Charlie   |  Manager   |             
4 | Diana     |  28        |  7          
5 | Edward    |   40.5     |  Developer  
6 | Frank     |  20        |  Student    
7 | George    | 45         |    Retired  

ROWS WITH INCORRECT LENGTH:
Row 3 is of length 2, expected 3

ROWS WITH POTENTIAL TYPE MISMATCHES:
Row 3, Column 2: Found str, expected int
Row 4, Column 3: Found int, expected str

Total number of rows with incorrect length: 1
Total number of type mismatches: 2
```

## 🗓️ Upcoming Features
- Data normalization
- Duplicate row detection
- Interactive issue handling
- Pandas integration for data analysis
