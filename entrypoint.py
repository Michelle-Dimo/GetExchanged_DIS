import time
import subprocess

print("Waiting for database...")

while True:
    result = subprocess.run(["flask", "init-db"])
    if result.returncode == 0:
        break
    print("Database not ready yet...")
    time.sleep(2)

print("Database initialized")

subprocess.run([
    "flask", "--app", "app",
    "run", "--host=0.0.0.0",
    "--debug"
])