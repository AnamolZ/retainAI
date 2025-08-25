"""
Python Script Process Manager
Lists all running Python scripts and allows the user to optionally terminate a selected process.
"""

import psutil
import logging

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Helper Functions
def list_python_processes():
    """
    Returns a list of running Python script processes.

    Returns:
        List of tuples: [(pid, script_file_name), ...]
    """
    python_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'] or ''
            cmdline = proc.info['cmdline'] or []

            if 'python' in name.lower() and any(cmd.endswith('.py') for cmd in cmdline):
                py_files = [cmd for cmd in cmdline if cmd.endswith('.py')]
                file_name = py_files[0] if py_files else '(unknown)'
                python_procs.append((proc.pid, file_name))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return python_procs


def kill_process_by_index(python_procs, index):
    """
    Kill a Python process given its index in the list.

    Args:
        python_procs (list): List of Python processes.
        index (int): Index of process to kill.
    """
    try:
        pid = python_procs[index][0]
        psutil.Process(pid).kill()
        logging.info(f"Killed Python process PID {pid} ({python_procs[index][1]})")
    except Exception as e:
        logging.error(f"Failed to kill PID {pid}: {e}")

# Main Execution
if __name__ == "__main__":
    python_procs = list_python_processes()

    if not python_procs:
        logging.info("No Python scripts are currently running.")
    else:
        # Display all running Python scripts
        for idx, (_, file_name) in enumerate(python_procs):
            print(f"[{idx}] {file_name}")

        # Prompt user for action
        choice = input("Enter index of process to kill (or press Enter to skip): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(python_procs):
                kill_process_by_index(python_procs, idx)
            else:
                logging.warning("Invalid index selected. No process killed.")
        else:
            logging.info("No process killed.")