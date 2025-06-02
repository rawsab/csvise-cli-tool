DEBUG_MODE = False
VERBOSE_MODE = False

def set_debug_mode(val: bool):
    global DEBUG_MODE
    DEBUG_MODE = val

def set_verbose_mode(val: bool):
    global VERBOSE_MODE
    VERBOSE_MODE = val

def log_debug(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def log_verbose(message, section_break=False):
    if VERBOSE_MODE:
        if section_break:
            print()
        print(f"[VERBOSE] {message}")
