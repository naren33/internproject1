import subprocess
import os
import csv
import time
from datetime import datetime

# Directories and output files
log_dir = 'camera_logs'
adb_log_dir = 'adb_logs_camera'
report_file = 'camera_test_report.csv'

os.makedirs(log_dir, exist_ok=True)
os.makedirs(adb_log_dir, exist_ok=True)

# Clear logcat before each test
def clear_logcat():
    subprocess.run(["adb", "logcat", "-c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Capture adb logcat after test
def capture_adb_log(tc_id):
    log_path = os.path.join(adb_log_dir, f"{tc_id}_adb.txt")
    with open(log_path, 'w') as f:
        subprocess.run(["adb", "logcat", "-d"], stdout=f)

# Run adb command and record results
def run_command(tc_id, cmd, writer):
    log_path = os.path.join(log_dir, f"{tc_id}.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clear_logcat()
    with open(log_path, 'w') as f:
        f.write(f"Test Case: {tc_id}\nCommand: {' '.join(cmd)}\nTimestamp: {timestamp}\n")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            f.write("Status: PASS\nOutput:\n" + result.stdout)
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "PASS", timestamp])
            return True
        except subprocess.CalledProcessError as e:
            f.write("Status: FAIL\nError Output:\n" + e.stderr)
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "FAIL", timestamp])
            return False

# List of all test cases
def get_test_cases():
    return [
        ("TC_CAM_001", ["adb", "shell", "am", "start", "-a", "android.media.action.IMAGE_CAPTURE"]),
        ("TC_CAM_002", ["adb", "shell", "am", "start", "-a", "android.media.action.IMAGE_CAPTURE", "--ei", "android.intent.extras.CAMERA_FACING", "1"]),
        ("TC_CAM_003", ["adb", "shell", "am", "start", "-a", "android.media.action.VIDEO_CAPTURE"]),
        ("TC_CAM_004", ["adb", "shell", "input", "keyevent", "27"]),
        ("TC_CAM_005", ["adb", "shell", "input", "swipe", "1000", "1000", "100", "100"]),
        ("TC_CAM_006", ["adb", "shell", "input", "swipe", "500", "800", "500", "400"]),
        ("TC_CAM_007", ["adb", "shell", "input", "swipe", "500", "400", "500", "800"]),
        ("TC_CAM_008", ["adb", "shell", "input", "keyevent", "27"]),
        ("TC_CAM_009", ["adb", "shell", "input", "keyevent", "27"]),
        ("TC_CAM_010", ["adb", "shell", "input", "tap", "100", "1800"]),
        ("TC_CAM_011", ["adb", "shell", "input", "tap", "250", "1800"]),
        ("TC_CAM_012", ["adb", "shell", "input", "tap", "900", "100"]),
        ("TC_CAM_013", ["adb", "shell", "input", "tap", "800", "100"]),
        ("TC_CAM_014", ["adb", "shell", "input", "tap", "1000", "300"]),
        ("TC_CAM_015", ["adb", "shell", "input", "tap", "1000", "400"]),
        ("TC_CAM_016", ["adb", "shell", "input", "tap", "700", "1800"]),
        ("TC_CAM_017", ["adb", "shell", "input", "tap", "600", "1000"]),
        ("TC_CAM_018", ["adb", "shell", "sendevent", "/dev/input/event1", "1", "330", "1"]),
        ("TC_CAM_019", ["adb", "shell", "input", "tap", "350", "1800"]),
        ("TC_CAM_020", ["adb", "shell", "input", "tap", "450", "1800"]),
        ("TC_CAM_021", ["adb", "shell", "input", "tap", "1000", "100"]),
        ("TC_CAM_022", ["adb", "shell", "am", "force-stop", "com.sec.android.app.camera"]),
        ("TC_CAM_023", ["adb", "shell", "pm", "clear", "com.sec.android.app.camera"]),
        ("TC_CAM_024", ["adb", "shell", "monkey", "-p", "com.sec.android.app.camera", "-c", "android.intent.category.LAUNCHER", "1"]),
        ("TC_CAM_025", ["adb", "shell", "dumpsys", "media.camera"]),
    ]

# Main executor
def run_camera_executor():
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Test Case ID", "Result", "Timestamp"])

        for tc_id, cmd in get_test_cases():
            print(f"\n▶ Running {tc_id} ...")
            run_command(tc_id, cmd, writer)
            print("⏳ Waiting 15 seconds before next test...\n")
            time.sleep(15)

if __name__ == "__main__":
    run_camera_executor()
