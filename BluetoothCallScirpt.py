import subprocess
import time

def call_python_script():
    try:
        while True:
            subprocess.run(["python", r" "]) # Put the file path to BluetoothDataLogging.py
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Restarting the script...")
        time.sleep(1)
        call_python_script()

call_python_script()