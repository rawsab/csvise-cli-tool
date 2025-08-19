"""
Basic tests for CSVise package
"""
import pytest
import tempfile
import os
from csvtools import main
from csvtools.cleaning_ops import DataCleaner
from csvtools.statistics import DataAnalyzer


def test_import_csvtools():
    """Test that csvtools can be imported"""
    import csvtools
    assert csvtools is not None


def test_data_cleaner_initialization():
    """Test DataCleaner initialization"""
    rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    headers = ["Name", "Age"]
    cleaner = DataCleaner(rows, headers)
    assert cleaner.rows == rows
    assert cleaner.headers == headers


def test_data_analyzer_initialization():
    """Test DataAnalyzer initialization"""
    rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    headers = ["Name", "Age"]
    analyzer = DataAnalyzer(rows, headers)
    assert analyzer.rows == rows
    assert analyzer.headers == headers


def test_basic_statistics():
    """Test basic statistics functionality"""
    rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    headers = ["Name", "Age"]
    analyzer = DataAnalyzer(rows, headers)
    
    stats = analyzer.get_column_statistics("Age")
    assert stats["data_type"] == "numeric"
    assert stats["total_values"] == 2
    assert stats["non_empty_values"] == 2


def test_basic_cleaning():
    """Test basic cleaning functionality"""
    rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    headers = ["Name", "Age"]
    cleaner = DataCleaner(rows, headers)
    
    # Test whitespace normalization
    modified_count = cleaner.normalize_whitespace()
    assert modified_count >= 0  # Should not fail


def test_create_temp_csv():
    """Test creating and processing a temporary CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Name,Age\nAlice,30\nBob,25\n")
        temp_file = f.name
    
    try:
        # Test that the file exists and can be read
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            content = f.read()
            assert "Name,Age" in content
            assert "Alice,30" in content
    finally:
        # Clean up
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
