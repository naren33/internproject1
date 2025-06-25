import subprocess
import os
import csv
import time
from datetime import datetime

# === Directory and file setup ===
log_dir = 'display_logs'
adb_log_dir = 'adb_logs'
report_file = 'display_test_report.csv'

os.makedirs(log_dir, exist_ok=True)
os.makedirs(adb_log_dir, exist_ok=True)

# === Utility Functions ===

def clear_logcat():
    subprocess.run(["adb", "logcat", "-c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def capture_adb_log(tc_id):
    log_path = os.path.join(adb_log_dir, f"{tc_id}_adb.txt")
    with open(log_path, 'w') as f:
        subprocess.run(["adb", "logcat", "-d"], stdout=f)

def run_command(tc_id, cmd, writer):
    log_path = os.path.join(log_dir, f"{tc_id}.txt")
    timestamp = datetime.now()
    clear_logcat()
    with open(log_path, 'w') as f:
        f.write(f"Test Case: {tc_id}\n")
        f.write(f"Command: {' '.join(cmd)}\n")
        f.write(f"Timestamp: {timestamp}\n")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            f.write("Status: PASS\n")
            f.write(f"Output:\n{result.stdout}")
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "PASS", timestamp])
        except subprocess.CalledProcessError as e:
            f.write("Status: FAIL\n")
            f.write(f"Error Output:\n{e.stderr}")
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "FAIL", timestamp])

def run_multiple_commands(tc_id, cmds, writer):
    log_path = os.path.join(log_dir, f"{tc_id}.txt")
    timestamp = datetime.now()
    clear_logcat()
    with open(log_path, 'w') as f:
        f.write(f"Test Case: {tc_id}\n")
        f.write(f"Timestamp: {timestamp}\n")
        try:
            for cmd in cmds:
                f.write(f"Command: {' '.join(cmd)}\n")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                f.write(f"Output:\n{result.stdout}\n")
            f.write("Status: PASS\n")
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "PASS", timestamp])
        except subprocess.CalledProcessError as e:
            f.write("Status: FAIL\n")
            f.write(f"Error Output:\n{e.stderr}")
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "FAIL", timestamp])

# === Test Case Functions ===

def TC_DISP_001(writer): return run_command("TC_DISP_001", ["adb", "shell", "settings", "put", "system", "screen_brightness", "255"], writer)
def TC_DISP_002(writer): return run_command("TC_DISP_002", ["adb", "shell", "settings", "put", "system", "screen_brightness_mode", "1"], writer)
def TC_DISP_003(writer): return run_command("TC_DISP_003", ["adb", "shell", "settings", "put", "system", "screen_off_timeout", "60000"], writer)
def TC_DISP_004(writer): return run_command("TC_DISP_004", ["adb", "shell", "wm", "size", "1080x2340"], writer)
def TC_DISP_005(writer): return run_command("TC_DISP_005", ["adb", "shell", "wm", "density", "320"], writer)
def TC_DISP_006(writer): return run_command("TC_DISP_006", ["adb", "shell", "settings", "put", "secure", "display_night_light_activated", "1"], writer)
def TC_DISP_007(writer): return run_command("TC_DISP_007", ["adb", "shell", "settings", "put", "secure", "doze_always_on", "1"], writer)
def TC_DISP_008(writer): return run_command("TC_DISP_008", ["adb", "shell", "settings", "put", "system", "user_rotation", "1"], writer)
def TC_DISP_009(writer): return run_command("TC_DISP_009", ["adb", "shell", "settings", "put", "system", "accelerometer_rotation", "0"], writer)
def TC_DISP_010(writer): return run_command("TC_DISP_010", ["adb", "shell", "settings", "put", "global", "stay_on_while_plugged_in", "3"], writer)
def TC_DISP_011(writer): return run_multiple_commands("TC_DISP_011", [["adb", "shell", "screencap", "-p", "/sdcard/disp_test.png"], ["adb", "pull", "/sdcard/disp_test.png"]], writer)
def TC_DISP_012(writer): return run_command("TC_DISP_012", ["adb", "shell", "am", "broadcast", "-a", "android.intent.action.FACTORY_TEST"], writer)
def TC_DISP_013(writer): return run_command("TC_DISP_013", ["adb", "shell", "input", "keyevent", "26"], writer)
def TC_DISP_014(writer): return run_command("TC_DISP_014", ["adb", "shell", "settings", "put", "secure", "accessibility_display_magnification_enabled", "1"], writer)
def TC_DISP_015(writer): return run_command("TC_DISP_015", ["adb", "shell", "settings", "get", "system", "font_scale"], writer)
def TC_DISP_016(writer): return run_command("TC_DISP_016", ["adb", "shell", "cmd", "overlay", "enable", "com.android.internal.systemui.navbar.threebutton"], writer)
def TC_DISP_017(writer): return run_command("TC_DISP_017", ["adb", "shell", "cmd", "overlay", "enable", "com.android.internal.systemui.navbar.gestural"], writer)
def TC_DISP_018(writer): return run_command("TC_DISP_018", ["adb", "shell", "settings", "get", "secure", "screensaver_components"], writer)
def TC_DISP_019(writer): return run_command("TC_DISP_019", ["adb", "shell", "settings", "put", "secure", "screensaver_enabled", "1"], writer)
def TC_DISP_020(writer): return run_command("TC_DISP_020", ["adb", "shell", "settings", "put", "secure", "screensaver_enabled", "0"], writer)
def TC_DISP_021(writer): return run_command("TC_DISP_021", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer_enabled", "1"], writer)
def TC_DISP_022(writer): return run_command("TC_DISP_022", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer_enabled", "0"], writer)
def TC_DISP_023(writer): return run_command("TC_DISP_023", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer", "11"], writer)
def TC_DISP_024(writer): return run_command("TC_DISP_024", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer", "12"], writer)
def TC_DISP_025(writer): return run_command("TC_DISP_025", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer", "13"], writer)
def TC_DISP_026(writer): return run_command("TC_DISP_026", ["adb", "shell", "settings", "get", "secure", "accessibility_display_daltonizer"], writer)
def TC_DISP_027(writer): return run_command("TC_DISP_027", ["adb", "shell", "settings", "put", "system", "refresh_rate", "60.0"], writer)
def TC_DISP_028(writer): return run_command("TC_DISP_028", ["adb", "shell", "settings", "get", "system", "refresh_rate"], writer)
def TC_DISP_029(writer): return run_command("TC_DISP_029", ["adb", "shell", "settings", "put", "global", "window_animation_scale", "0.5"], writer)
def TC_DISP_030(writer): return run_command("TC_DISP_030", ["adb", "shell", "settings", "put", "global", "transition_animation_scale", "0.5"], writer)
def TC_DISP_031(writer): return run_command("TC_DISP_031", ["adb", "shell", "settings", "put", "global", "animator_duration_scale", "0.5"], writer)

# === Test Case Runner ===

def run_display_executor():
    test_cases = [
        ("TC_DISP_001", TC_DISP_001), ("TC_DISP_002", TC_DISP_002), ("TC_DISP_003", TC_DISP_003),
        ("TC_DISP_004", TC_DISP_004), ("TC_DISP_005", TC_DISP_005), ("TC_DISP_006", TC_DISP_006),
        ("TC_DISP_007", TC_DISP_007), ("TC_DISP_008", TC_DISP_008), ("TC_DISP_009", TC_DISP_009),
        ("TC_DISP_010", TC_DISP_010), ("TC_DISP_011", TC_DISP_011), ("TC_DISP_012", TC_DISP_012),
        ("TC_DISP_013", TC_DISP_013), ("TC_DISP_014", TC_DISP_014), ("TC_DISP_015", TC_DISP_015),
        ("TC_DISP_016", TC_DISP_016), ("TC_DISP_017", TC_DISP_017), ("TC_DISP_018", TC_DISP_018),
        ("TC_DISP_019", TC_DISP_019), ("TC_DISP_020", TC_DISP_020), ("TC_DISP_021", TC_DISP_021),
        ("TC_DISP_022", TC_DISP_022), ("TC_DISP_023", TC_DISP_023), ("TC_DISP_024", TC_DISP_024),
        ("TC_DISP_025", TC_DISP_025), ("TC_DISP_026", TC_DISP_026), ("TC_DISP_027", TC_DISP_027),
        ("TC_DISP_028", TC_DISP_028), ("TC_DISP_029", TC_DISP_029), ("TC_DISP_030", TC_DISP_030),
        ("TC_DISP_031", TC_DISP_031)
    ]

    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Test Case ID", "Result", "Timestamp"])

        for tc_id, test_func in test_cases:
            print(f"Running {tc_id}...")
            test_func(writer)
            print("Waiting 15 seconds before next test...\n")
            time.sleep(15)

if __name__ == "__main__":
    run_display_executor()
