# utils/adb_utils.py

import subprocess

def run_adb_command(cmd_list):
    """
    Run an ADB command.
    Args:
        cmd_list (list): ADB command split as list (e.g., ['shell', 'dumpsys', 'audio'])
    Returns:
        str: Output from the command
    """
    try:
        full_cmd = ['adb'] + cmd_list
        result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            print(f"[ADB Error] {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"[ADB Exception] {e}")
        return ""
