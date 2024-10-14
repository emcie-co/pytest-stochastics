import sys
from typing import Any, TextIO

class Logger:
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARN": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
    }
    RESET = "\033[0m"

    def __init__(self, file: TextIO = sys.stderr, prefix:str=""):
        self.file = file
        self.prefix = prefix

    def _log(self, level: str, *values: Any, sep: str = " ", end: str = "\n") -> None:
        color = self.COLORS.get(level, "")
        prefix = f"{self.prefix}{level:<5}"  # This will pad the level to 5 characters
        try:
            message = sep.join(str(value) for value in values)
            colored_message = f"{color}{prefix}: {message}{self.RESET}"
            print(colored_message, end=end, file=self.file)
        except Exception:
            # If coloring fails, fall back to non-colored output
            print(f"*{prefix}: {sep.join(str(value) for value in values)}", end=end, file=sys.stderr)

    def debug(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("DEBUG", *values, sep=sep, end=end)

    def info(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("INFO", *values, sep=sep, end=end)

    def warning(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("WARN", *values, sep=sep, end=end)

    def error(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("ERROR", *values, sep=sep, end=end)
