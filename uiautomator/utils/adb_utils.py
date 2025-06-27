# utils/adb_utils.py
import subprocess

def run_adb_command(cmd_list):
    try:
        full_cmd = ['adb'] + cmd_list
        result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
        if result.stderr:
            print(f"ADB Error: {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"ADB Command Failed: {e}")
        return ""
