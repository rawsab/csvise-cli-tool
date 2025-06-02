import re
from .config import CONFIG
from .utils import log_verbose

def detect_delimiter(sample_row, custom_delimiter=None):
    if custom_delimiter:
        log_verbose(f"Using custom delimiter: {custom_delimiter}\n", section_break=True)
        return custom_delimiter
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
