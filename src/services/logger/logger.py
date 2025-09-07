import threading
import queue
import time
from datetime import datetime
import os

class Logger:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self._start_worker()

    def log(self, message, level="info", bold=False, italic=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put({
            "text": f"[{timestamp}] {message}",
            "level": level.lower(),
            "bold": bold,
            "italic": italic
        })

    def clear(self):
        self.command_queue.put("CLEAR")

    def _start_worker(self):
        def run():
            while True:
                while not self.command_queue.empty():
                    cmd = self.command_queue.get()
                    if cmd == "CLEAR":
                        os.system('cls' if os.name == 'nt' else 'clear')
                while not self.log_queue.empty():
                    entry = self.log_queue.get()
                    style = ""
                    if entry["bold"] and entry["italic"]:
                        style = "\033[1m\033[3m"
                    elif entry["bold"]:
                        style = "\033[1m"
                    elif entry["italic"]:
                        style = "\033[3m"

                    color = {
                        "info": "\033[36m",
                        "warn": "\033[33m",
                        "error": "\033[31m",
                        "success": "\033[32m"
                    }.get(entry["level"], "\033[37m")

                    reset = "\033[0m"
                    print(f"{style}{color}{entry['text']}{reset}")
                time.sleep(0.1)

        threading.Thread(target=run, daemon=True).start()

logger = Logger()