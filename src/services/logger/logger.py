"""
Threaded Logger Utility
Provides asynchronous logging with support for color-coded levels,
text styling (bold, italic), and console clearing.
"""

import threading
import queue
import time
from datetime import datetime
import os

# Logger Class
class Logger:
    """
    Asynchronous logger that prints color-coded messages to the console.
    Supports bold and italic formatting and queue-based logging.
    """

    LEVEL_COLORS = {
        "info": "\033[36m",     # Cyan
        "warn": "\033[33m",     # Yellow
        "error": "\033[31m",    # Red
        "success": "\033[32m",  # Green
    }

    def __init__(self):
        self.log_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self._start_worker()

    # Public Methods
    def log(self, message: str, level: str = "info", bold: bool = False, italic: bool = False):
        """
        Add a message to the logging queue.

        Args:
            message (str): Message text.
            level (str): Logging level: info, warn, error, success.
            bold (bool): Apply bold formatting.
            italic (bool): Apply italic formatting.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put({
            "text": f"[{timestamp}] {message}",
            "level": level.lower(),
            "bold": bold,
            "italic": italic
        })

    def clear(self):
        """
        Clear the console screen.
        """
        self.command_queue.put("CLEAR")

    # Internal Methods
    def _start_worker(self):
        """
        Starts a background daemon thread that continuously processes log and command queues.
        """
        def worker():
            while True:
                # Process commands (e.g., clear console)
                while not self.command_queue.empty():
                    cmd = self.command_queue.get()
                    if cmd == "CLEAR":
                        os.system('cls' if os.name == 'nt' else 'clear')

                # Process log messages
                while not self.log_queue.empty():
                    entry = self.log_queue.get()
                    style = ""
                    if entry["bold"] and entry["italic"]:
                        style = "\033[1m\033[3m"
                    elif entry["bold"]:
                        style = "\033[1m"
                    elif entry["italic"]:
                        style = "\033[3m"

                    color = self.LEVEL_COLORS.get(entry["level"], "\033[37m")
                    reset = "\033[0m"

                    print(f"{style}{color}{entry['text']}{reset}")

                time.sleep(0.1)

        threading.Thread(target=worker, daemon=True).start()

# Global Logger Instance
logger = Logger()

if __name__ == "__main__":
    logger.log("This is an info message")
    logger.log("This is a warning!", level="warn", bold=True)
    logger.log("Error occurred!", level="error", italic=True)
    logger.log("Operation successful!", level="success", bold=True, italic=True)
    time.sleep(1)  # Allow time for logs to appear
    logger.clear()