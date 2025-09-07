import psutil

python_procs = []

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        name = proc.info['name'] or ''
        cmdline = proc.info['cmdline'] or []

        if 'python' in name.lower() and any(cmd.endswith('.py') for cmd in cmdline):
            py_files = [cmd for cmd in cmdline if cmd.endswith('.py')]
            file_name = py_files[0] if py_files else '(unknown)'
            print(f"[{len(python_procs)}] PID: {proc.pid} | File: {file_name}")
            python_procs.append((proc.pid, file_name))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

if not python_procs:
    print("No Python scripts running.")
else:
    choice = input("Enter index to kill (or press Enter to skip): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(python_procs):
            pid = python_procs[idx][0]
            try:
                psutil.Process(pid).kill()
                print(f"Killed PID {pid}")
            except Exception as e:
                print(f"Failed to kill PID {pid}: {e}")
        else:
            print("Invalid index.")
    else:
        print("No process killed.")
