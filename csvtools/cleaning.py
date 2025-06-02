import re
from .config import CONFIG
from .utils import log_verbose

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

def apply_string_case(value, case_type):
    if case_type == "upper":
        return value.upper()
    elif case_type == "lower":
        return value.lower()
    return value
