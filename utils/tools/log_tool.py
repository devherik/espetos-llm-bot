# Define ANSI escape codes for colors and reset
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

def log_message(message: str, level: str = "INFO") -> None:
    """
    Logs a message with a specific level and color.
        message (str): The message to log.
        level (str): The log level (e.g., "INFO", "SUCCESS", "ERROR", "WARNING", "DEBUG").
    """
    color = {
        "INFO": BLUE,
        "SUCCESS": GREEN,
        "ERROR": RED,
        "WARNING": YELLOW,
        "DEBUG": MAGENTA
    }.get(level, RESET)
    print(f"{color}{level} {RESET}{message}")