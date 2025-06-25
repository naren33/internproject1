import subprocess
import time
import os

def adb(cmd):
    return subprocess.run(["adb", "shell"] + cmd.split(), stdout=subprocess.PIPE, text=True).stdout.strip()

def log_to_logcat(tag, message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    full_message = f"{timestamp} - {message}"
    subprocess.run(["adb", "shell", "log", "-t", tag, full_message])
    print(f"[{tag}] {full_message}")

def get_latest_camera_file():
    return subprocess.run(
        ["adb", "shell", "ls", "-t", "/sdcard/DCIM/Camera/"],
        stdout=subprocess.PIPE, text=True
    ).stdout.strip().split('\n')[0]

def get_thermal_readings():
    return adb("dumpsys thermalservice")

def dump_logcat(tag):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"logcat_{tag}_{timestamp}.txt"
    with open(filename, "w") as f:
        subprocess.run(["adb", "logcat", "-d", "-v", "time"], stdout=f, text=True)
    print(f"📝 Saved {filename}")

def clear_logcat():
    subprocess.run(["adb", "logcat", "-c"])

# -------- Camera Launch and Capture --------
clear_logcat()
tag = "CameraTest"
log_to_logcat(tag, "Launching Camera App...")
adb("monkey -p com.android.camera -c android.intent.category.LAUNCHER 1")
time.sleep(2)

log_to_logcat(tag, "Triggering camera capture...")
adb("input keyevent 27")
time.sleep(2)

latest_file = get_latest_camera_file()
log_to_logcat(tag, f"Latest captured file: {latest_file}")
dump_logcat(tag)

# -------- Screen Rotation Stability --------
clear_logcat()
tag = "RotationTest"
log_to_logcat(tag, "Starting screen rotation test...")
adb("settings put system user_rotation 0")
time.sleep(2)
adb("settings put system user_rotation 1")
time.sleep(2)
adb("settings put system user_rotation 0")
time.sleep(2)
log_to_logcat(tag, "Completed screen rotation test.")
dump_logcat(tag)

# -------- Heating During Heavy Usage --------
clear_logcat()
tag = "HeatTest"
log_to_logcat(tag, "Launching Camera and starting screen recording...")
adb("monkey -p com.android.camera -c android.intent.category.LAUNCHER 1")
time.sleep(2)

rec_proc = subprocess.Popen(["adb", "shell", "screenrecord", "/sdcard/test.mp4"])
log_to_logcat(tag, "Monitoring thermal readings every 30s for 5 minutes...")

for i in range(10):
    thermal = get_thermal_readings()
    log_to_logcat(tag, f"[{i*30}s] Thermal Info:\n{thermal}")
    time.sleep(30)

rec_proc.terminate()
log_to_logcat(tag, "Stopped screen recording.")
dump_logcat(tag)

# -------- Volume Down Shutter Stress --------
clear_logcat()
tag = "VolumeShutterTest"
total_shots = 50
log_to_logcat(tag, f"Starting Volume Down Shutter Stress Test: {total_shots} shots")

for i in range(total_shots):
    adb("input keyevent 25")
    log_to_logcat(tag, f"📸 Shot {i+1}")
    time.sleep(1)

log_to_logcat(tag, "Completed Volume Down Shutter Test.")
dump_logcat(tag)

# -------- HDR Image Capture and Pull --------
clear_logcat()
tag = "HDRTest"
log_to_logcat(tag, "Launching camera for HDR test (ensure HDR enabled)...")
adb("monkey -p com.android.camera -c android.intent.category.LAUNCHER 1")
time.sleep(2)

adb("input keyevent 27")
time.sleep(3)

hdr_file = get_latest_camera_file()
log_to_logcat(tag, f"Captured HDR image: {hdr_file}")
subprocess.run(["adb", "pull", f"/sdcard/DCIM/Camera/{hdr_file}"])
log_to_logcat(tag, "✅ HDR Image pulled to local system.")
dump_logcat(tag)

# -------- Flash Toggle Stress --------
clear_logcat()
tag = "FlashStressTest"
log_to_logcat(tag, "Launching Camera for Flash Toggle Stress Test...")
adb("monkey -p com.android.camera -c android.intent.category.LAUNCHER 1")
time.sleep(2)

log_to_logcat(tag, "Ensure flash is ON in camera UI before test begins.")
time.sleep(5)

for i in range(30):
    adb("input keyevent 27")
    log_to_logcat(tag, f"Capture {i+1}/30")
    time.sleep(2)

thermal_after_flash = get_thermal_readings()
with open("flash_thermal_log.txt", "w") as f:
    f.write("=== Thermal Info ===\n" + thermal_after_flash)

adb("am force-stop com.android.camera")
log_to_logcat(tag, "✅ Flash Toggle Stress Test Completed.")
dump_logcat(tag)

# -------- Final Message --------
print("✅ All tests completed. Individual logcat files saved.")

