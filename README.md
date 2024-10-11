# 🛠️ CSV Tools

## 💻 Setup
Download `csvtools.py` (recommended to add to project directory) and run commands in terminal.

## 💡 Features
Run the following command, replacing `<filename.csv>` with path to target file and add flags for the following functionalities:
```
python3 csvtools.py <filename.csv> [-display] [-debug] [-v] [-dl delimiter]
```
- `-display` : Displays a formatted table output of the CSV data
- `-debug` : Enables debug output for troubleshooting purposes, including information on incomplete data and type mismatches.
- `-v` : Activates verbose mode, provides detailed logs about script operations
- `-dl delimiter` : Sets a custom delimiter for splitting fields in target CSV file

### Custom Delimiter Example:
```
python3 csvtools.py data.csv -display -dl X
```
Displays a formatted table output of `data.csv` where the fields in raw data are separated by "X".

## 🗓️ Upcoming Features
- Data normalization
- Duplicate row detection
- Interactive issue handling
- Pandas integration for data analysis
