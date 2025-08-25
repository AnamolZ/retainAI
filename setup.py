import subprocess

subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "setup.ps1"], check=True)