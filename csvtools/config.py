import json
from .utils import log_verbose

CONFIG_FILE = 'csvtoolsConfig.json'

CONFIG = {
    "additional_delimiters": [],
    "start_index": 1,
    "num_rows_to_print": None,
    "display_column_lines": False,
    "display_row_lines": False,
    "check_type_mismatches": True,
    "string_case": "default"
}

def load_config():
    global CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            user_config = json.load(f)
            CONFIG.update(user_config)
            log_verbose(f"Loaded configuration: {CONFIG}", section_break=True)
    except FileNotFoundError:
        log_verbose(f"Configuration file {CONFIG_FILE} not found. Using default settings.", section_break=True)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {CONFIG_FILE}. Using default settings.")
    except Exception as e:
        print(f"Error loading configuration: {e}. Using default settings.")
