import subprocess
import os
import csv
import time
from datetime import datetime

# Directories and report file
log_dir = 'clock_logs'
adb_log_dir = 'adb_logs'
report_file = 'clock_test_report.csv'

os.makedirs(log_dir, exist_ok=True)
os.makedirs(adb_log_dir, exist_ok=True)

# Clear logcat logs
def clear_logcat():
    subprocess.run(["adb", "logcat", "-c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Capture ADB log output
def capture_adb_log(tc_id):
    log_path = os.path.join(adb_log_dir, f"{tc_id}_adb.txt")
    with open(log_path, 'w') as f:
        subprocess.run(["adb", "logcat", "-d"], stdout=f)

# Run a command and log the result
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
            return True
        except subprocess.CalledProcessError as e:
            f.write("Status: FAIL\n")
            f.write(f"Error Output:\n{e.stderr}")
            capture_adb_log(tc_id)
            writer.writerow([tc_id, "FAIL", timestamp])
            return False

# All test case definitions
def TC_CLK_001(writer): return run_command("TC_CLK_001", ["adb", "shell", "am", "start", "-a", "android.intent.action.SET_ALARM", "--ei", "android.intent.extra.alarm.HOUR", "6", "--ei", "android.intent.extra.alarm.MINUTES", "30", "--ez", "android.intent.extra.alarm.SKIP_UI", "true"], writer)
def TC_CLK_002(writer): return run_command("TC_CLK_002", ["adb", "shell", "am", "start", "-a", "android.intent.action.SET_TIMER", "--ei", "android.intent.extra.alarm.LENGTH", "120", "--ez", "android.intent.extra.alarm.SKIP_UI", "true"], writer)
def TC_CLK_003(writer): return run_command("TC_CLK_003", ["adb", "shell", "settings", "put", "global", "zen_mode", "1"], writer)
def TC_CLK_004(writer): return run_command("TC_CLK_004", ["adb", "shell", "settings", "put", "global", "zen_mode", "0"], writer)
def TC_CLK_005(writer): return run_command("TC_CLK_005", ["adb", "shell", "dumpsys", "alarm"], writer)
def TC_CLK_006(writer): return run_command("TC_CLK_006", ["adb", "shell", "input", "keyevent", "26"], writer)
def TC_CLK_007(writer): return run_command("TC_CLK_007", ["adb", "shell", "settings", "put", "global", "time_zone", "Asia/Kolkata"], writer)
def TC_CLK_008(writer): return run_command("TC_CLK_008", ["adb", "shell", "input", "tap", "400", "1300"], writer)
def TC_CLK_009(writer): return run_command("TC_CLK_009", ["adb", "shell", "pm", "clear", "com.sec.android.app.clockpackage"], writer)
def TC_CLK_010(writer): return run_command("TC_CLK_010", ["adb", "shell", "input", "tap", "700", "850"], writer)
def TC_CLK_011(writer): return run_command("TC_CLK_011", ["adb", "shell", "settings", "put", "system", "alarm_volume", "7"], writer)
def TC_CLK_012(writer): return run_command("TC_CLK_012", ["adb", "shell", "settings", "put", "system", "vibrate_when_ringing", "1"], writer)
def TC_CLK_013(writer): return run_command("TC_CLK_013", ["adb", "shell", "am", "start", "-n", "com.sec.android.app.clockpackage/.ClockPackage"], writer)
def TC_CLK_014(writer): return run_command("TC_CLK_014", ["adb", "shell", "am", "force-stop", "com.sec.android.app.clockpackage"], writer)
def TC_CLK_015(writer): return run_command("TC_CLK_015", ["adb", "reboot"], writer)
def TC_CLK_016(writer): return run_command("TC_CLK_016", ["adb", "shell", "settings", "get", "system", "time_12_24"], writer)
def TC_CLK_017(writer): return run_command("TC_CLK_017", ["adb", "shell", "settings", "get", "global", "time_zone"], writer)
def TC_CLK_018(writer): return run_command("TC_CLK_018", ["adb", "shell", "svc", "power", "stayon", "true"], writer)
def TC_CLK_019(writer): return run_command("TC_CLK_019", ["adb", "shell", "am", "start", "-n", "com.android.settings/.Settings$DateTimeSettingsActivity"], writer)
def TC_CLK_020(writer): run_command("TC_CLK_020_KEY", ["adb", "shell", "input", "keyevent", "224"], writer); return run_command("TC_CLK_020_SWIPE", ["adb", "shell", "input", "swipe", "500", "1500", "500", "500"], writer)
def TC_CLK_021(writer): return run_command("TC_CLK_021", ["adb", "shell", "monkey", "-p", "com.sec.android.app.clockpackage", "-v", "10"], writer)
def TC_CLK_022(writer): return run_command("TC_CLK_022", ["adb", "shell", "dumpsys", "jobscheduler"], writer)
def TC_CLK_023(writer): return run_command("TC_CLK_023", ["adb", "shell", "am", "start", "-a", "android.intent.action.SHOW_ALARMS"], writer)
def TC_CLK_024(writer): return run_command("TC_CLK_024", ["adb", "shell", "content", "query", "--uri", "content://com.android.deskclock/alarm"], writer)
def TC_CLK_025(writer): return run_command("TC_CLK_025", ["adb", "shell", "dumpsys", "alarm"], writer)

# Test case executor
def run_clock_executor():
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Test Case ID", "Result", "Timestamp"])

        test_cases = [
            ("TC_CLK_001", TC_CLK_001), ("TC_CLK_002", TC_CLK_002), ("TC_CLK_003", TC_CLK_003),
            ("TC_CLK_004", TC_CLK_004), ("TC_CLK_005", TC_CLK_005), ("TC_CLK_006", TC_CLK_006),
            ("TC_CLK_007", TC_CLK_007), ("TC_CLK_008", TC_CLK_008), ("TC_CLK_009", TC_CLK_009),
            ("TC_CLK_010", TC_CLK_010), ("TC_CLK_011", TC_CLK_011), ("TC_CLK_012", TC_CLK_012),
            ("TC_CLK_013", TC_CLK_013), ("TC_CLK_014", TC_CLK_014), ("TC_CLK_015", TC_CLK_015),
            ("TC_CLK_016", TC_CLK_016), ("TC_CLK_017", TC_CLK_017), ("TC_CLK_018", TC_CLK_018),
            ("TC_CLK_019", TC_CLK_019), ("TC_CLK_020", TC_CLK_020), ("TC_CLK_021", TC_CLK_021),
            ("TC_CLK_022", TC_CLK_022), ("TC_CLK_023", TC_CLK_023), ("TC_CLK_024", TC_CLK_024),
            ("TC_CLK_025", TC_CLK_025)
        ]

        for tc_id, test_func in test_cases:
            print(f" Running {tc_id} ...")
            test_func(writer)
            print(" Waiting 15 seconds before next test...\n")
            time.sleep(15)

if __name__ == "__main__":
    run_clock_executor()
