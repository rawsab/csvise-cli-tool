# CSVise CLI Tools

<div align="center">

**Beautiful CLI tools for CSV analysis, validation, and data cleaning with Rich-powered output**

[![PyPI version](https://badge.fury.io/py/csvise.svg)](https://badge.fury.io/py/csvise)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Installation](#-installation) • [Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation)

<div align="center">
<img width="700" alt="Screenshot" src="https://github.com/user-attachments/assets/8343b73f-2887-48bc-b475-4abe2fa20c11" />
</div>

</div>

---

## 📋 Table of Contents

  - [🚀 Installation](#-installation)
    - [From PyPI (Recommended)](#from-pypi-recommended)
    - [From Source](#from-source)
  - [⚡ Quick Start](#-quick-start)
    - [Display CSV Data](#display-csv-data)
    - [Analyze Data](#analyze-data)
    - [Clean Data](#clean-data)
  - [✨ Features](#-features)
    - [Display \& Validation](#display--validation)
    - [Data Analysis \& Statistics](#data-analysis--statistics)
    - [Data Cleaning Operations](#data-cleaning-operations)
    - [🎨 Rich UI Integration](#-rich-ui-integration)
  - [📖 Documentation](#-documentation)
    - [Command Reference](#command-reference)
      - [Global Options](#global-options)
      - [Custom Delimiter Example](#custom-delimiter-example)
    - [Configuration](#configuration)
    - [Examples](#examples)
      - [Rich UI Examples](#rich-ui-examples)
      - [Classic Mode Examples](#classic-mode-examples)
      - [Data Analysis Examples](#data-analysis-examples)
      - [Data Cleaning Examples](#data-cleaning-examples)
    - [Example Output](#example-output)
  - [🔧 Development](#-development)
    - [Setup Development Environment](#setup-development-environment)
    - [Run Tests](#run-tests)
    - [Code Quality](#code-quality)
    - [Build Package](#build-package)
  - [📄 License](#-license)

---

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install csvise
```

### From Source

```bash
git clone https://github.com/rawsabsaid/csvise-cli-tool.git
cd csvise-cli-tool
pip install -e .
```

---

## ⚡ Quick Start

### Display CSV Data
```bash
# Beautiful table display with Rich formatting
csvise display data.csv

# Classic plain text output
csvise display data.csv --classic
```

### Analyze Data
```bash
# Comprehensive analysis
csvise analyze data.csv

# Detect outliers and correlations
csvise analyze data.csv --outliers --correlations
```

### Clean Data
```bash
# Remove duplicates and normalize whitespace
csvise clean data.csv --remove-duplicates --normalize-whitespace --output cleaned.csv
```

---

## ✨ Features

### Display & Validation

Beautiful CSV display with automatic delimiter detection and data validation:

```bash
csvise display FILENAME [OPTIONS]
```

**Options:**
- `--display` : Display formatted table output
- `--debug` : Enable debug output for troubleshooting
- `-v` : Verbose mode with detailed operation logs
- `-dl, --delimiter DELIMITER` : Set custom delimiter
- `-stf, --save_to_file OUTPUT` : Save output to file
- `--rich` : Use Rich formatting (default)
- `--classic` : Use classic plain text formatting

### Data Analysis & Statistics

Comprehensive data analysis with statistical insights:

```bash
csvise analyze FILENAME [OPTIONS]
```

**Options:**
- `--columns, -c` : Analyze specific columns (comma-separated)
- `--correlations` : Show correlation matrix for numeric columns
- `--outliers` : Detect outliers in numeric columns
- `--distribution` : Show value distribution for categorical columns
- `-v` : Verbose mode
- `--classic` : Use classic plain text formatting

### Data Cleaning Operations

Powerful data cleaning and transformation capabilities:

```bash
csvise clean FILENAME [OPTIONS]
```

**Options:**
- `--remove-duplicates` : Remove duplicate rows
- `--normalize-whitespace` : Normalize whitespace in all columns
- `--standardize-case` : Standardize text case (upper, lower, title, sentence)
- `--fill-missing` : Fill missing values (empty, mode, mean, median, custom)
- `--fill-value` : Custom value for missing data
- `--remove-empty-rows` : Remove rows with high empty cell percentage
- `--output, -o` : Output file for cleaned data
- `-v` : Verbose mode
- `--classic` : Use classic plain text formatting

### 🎨 Rich UI Integration

CSVise features beautiful Rich-powered CLI output:

- **Color-coded Tables**: Data types are color-coded (integers in green, floats in yellow, booleans in magenta)
- **Information Panels**: File statistics and validation issues in styled panels
- **Progress Indicators**: Visual feedback during data processing
- **Enhanced Messages**: Beautiful error and success message formatting
- **Type Highlighting**: Automatic highlighting of data type mismatches

**Modes:**
- **Rich Mode** (`--rich`): Enhanced visual experience with colors and panels **[default]**
- **Classic Mode** (`--classic`): Traditional plain text output for compatibility

---

## 📖 Documentation

### Command Reference

#### Global Options
- `--help` : Show help and documentation
- `--version` : Display current version

#### Custom Delimiter Example
```bash
csvise display data.csv --delimiter ";"
```

### Configuration

Customize default behavior with `csvtoolsConfig.json`:

```json
{
    "additional_delimiters": ["|", ";", "###"],
    "start_index": 1,
    "num_rows_to_print": null,
    "display_column_lines": true,
    "display_row_lines": false,
    "check_type_mismatches": true,
    "string_case": "default"
}
```

### Examples

#### Rich UI Examples
```bash
# Beautiful table with validation
csvise display data.csv --debug

# Analysis with correlations
csvise analyze data.csv --correlations

# Clean data with progress feedback
csvise clean data.csv --remove-duplicates --normalize-whitespace
```

#### Classic Mode Examples
```bash
# Plain text output for scripts
csvise display data.csv --classic --debug

# Classic analysis output
csvise analyze data.csv --classic --outliers
```

#### Data Analysis Examples
```bash
# Comprehensive analysis
csvise analyze data.csv --correlations

# Analyze specific columns
csvise analyze data.csv --columns "Age,Salary,Department"

# Detect outliers
csvise analyze data.csv --outliers

# Show distributions
csvise analyze data.csv --distribution
```

#### Data Cleaning Examples
```bash
# Basic cleaning
csvise clean data.csv --remove-duplicates --normalize-whitespace

# Advanced cleaning pipeline
csvise clean data.csv \
    --remove-duplicates \
    --normalize-whitespace \
    --standardize-case title \
    --fill-missing mode \
    --output cleaned_data.csv

# Remove empty rows
csvise clean data.csv --remove-empty-rows 0.5 --output cleaned.csv
```

### Example Output

```plaintext
[VERBOSE] Detecting delimiter from sample row: Name,Age,Occupation
[VERBOSE] Delimiter detected: ,
[VERBOSE] Detected columns: ['Name', 'Age', 'Occupation']

  | Name      | Age       | Occupation  
--------------+-----------+-------------
1 | Alice     | 30        | Engineer   
2 | Bob       | 25        | Designer   
3 | Charlie   | Manager   |             
4 | Diana     | 28        | 7          
5 | Edward    | 40.5      | Developer  
6 | Frank     | 20        | Student    
7 | George    | 45        | Retired    

ROWS WITH INCORRECT LENGTH:
Row 3 is of length 2, expected 3

ROWS WITH POTENTIAL TYPE MISMATCHES:
Row 3, Column 2: Found str, expected int
Row 4, Column 3: Found int, expected str

Total number of rows with incorrect length: 1
Total number of type mismatches: 2
```

---

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/rawsabsaid/csvise-cli-tool.git
cd csvise-cli-tool
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black csvtools/

# Check linting
flake8 csvtools/

# Type checking
mypy csvtools/
```

### Build Package

```bash
python -m build
twine check dist/*
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by [Rawsab Said](https://github.com/rawsabsaid)**

[GitHub](https://github.com/rawsabsaid/csvise-cli-tool) • [PyPI](https://pypi.org/project/csvise/) • [Issues](https://github.com/rawsabsaid/csvise-cli-tool/issues)

</div>
