import subprocess
import csv
import os
import time
from datetime import datetime

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

class GraphicsTest:
    def run_adb_command(self, command, tc_id=None):
        try:
            print(f"[ADB CMD] {command}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout.strip()
            print("[OUTPUT]", output)
            if tc_id:
                collect_script_log(tc_id, command, result=output, status="PASS")
            time.sleep(3)
            return output
        except subprocess.CalledProcessError as e:
            error = e.stderr.strip()
            print("[ERROR]", error)
            if tc_id:
                collect_script_log(tc_id, command, error=error, status="FAIL")
            time.sleep(3)
            return None

    def check_screen_resolution(self, tc_id): return self.run_adb_command("adb shell wm size", tc_id)
    def check_screen_density(self, tc_id): return self.run_adb_command("adb shell wm density", tc_id)
    def capture_screenshot(self, tc_id): return self.run_adb_command("adb shell screencap /sdcard/screen.png && adb pull /sdcard/screen.png", tc_id)
    def record_screen(self, tc_id): return self.run_adb_command("adb shell screenrecord --time-limit 5 /sdcard/demo.mp4 && adb pull /sdcard/demo.mp4", tc_id)
    def check_gpu_renderer(self, tc_id): return self.run_adb_command("adb shell dumpsys SurfaceFlinger", tc_id)
    def check_refresh_rate(self, tc_id): return self.run_adb_command("adb shell dumpsys display", tc_id)
    def enable_gpu_profiling(self, tc_id): return self.run_adb_command("adb shell setprop debug.hwui.profile visual_bars", tc_id)
    def verify_frame_latency(self, tc_id): return self.run_adb_command("adb shell dumpsys gfxinfo com.sec.android.app.camera", tc_id)
    def enable_hw_overlay(self, tc_id): return self.run_adb_command("adb shell service call SurfaceFlinger 1008 i32 1", tc_id)
    def disable_hw_overlay(self, tc_id): return self.run_adb_command("adb shell service call SurfaceFlinger 1008 i32 0", tc_id)
    def hide_navigation_bar(self, tc_id): return self.run_adb_command("adb shell settings put global policy_control immersive.full=*", tc_id)
    def navigation_bar(self, tc_id): return self.run_adb_command("adb shell settings put global policy_control null", tc_id)
    def check_vsync_info(self, tc_id): return self.run_adb_command("adb shell dumpsys SurfaceFlinger --latency", tc_id)
    def dump_surfaceflinger_layers(self, tc_id): return self.run_adb_command("adb shell dumpsys SurfaceFlinger --list", tc_id)
    def stress_test_brightness(self, tc_id): return self.run_adb_command("adb shell cmd statusbar expand-settings && adb shell input swipe 300 1600 800 1600 && timeout /t 2 >nul && adb shell input swipe 100 760 560 760 && adb shell input keyevent KEYCODE_BACK", tc_id)
    def validate_rotation(self, tc_id): return self.run_adb_command("adb shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1", tc_id)
    def simulate_app_cutout_handling(self, tc_id): return self.run_adb_command("adb shell am start -n com.sec.android.app.camera/com.sec.android.app.camera.Camera", tc_id)
    def check_ion_memory(self, tc_id): return self.run_adb_command("adb shell cat /d/ion/heaps/system", tc_id)
    def capture_framebuffer(self, tc_id): return self.run_adb_command("adb shell su -c 'cat /dev/graphics/fb0 > /sdcard/fb0.raw' && adb pull /sdcard/fb0.raw", tc_id)
    def screen_off(self, tc_id): return self.run_adb_command("adb shell input keyevent 26", tc_id)
    def screen_on_unlock(self, tc_id): return self.run_adb_command("adb shell input keyevent 26 && adb shell input swipe 300 1000 300 500", tc_id)
    def launch_ps(self , tc_id): return self.run_adb_command("adb shell monkey -p com.android.vending -v 1", tc_id)
    def gfx_info_ps(self, tc_id): return self.run_adb_command("adb shell dumpsys gfxinfo com.android.vending", tc_id)
    def thermal_service(self, tc_id): return self.run_adb_command("adb shell dumpsys thermalservice", tc_id)
    def bs_gaming(self, tc_id): return self.run_adb_command("adb shell dumpsys SurfaceFlinger --latency"+str('\\')+"SurfaceView[com.bubbleshooter.popbubbles.collectcards/org.cocos2dx.cpp.AppActivity]@0"+str("\\"))
    def wake_screen(self, tc_id): return self.run_adb_command("adb shell input keyevent 224", tc_id)
    #def toggle_screen_fast(self, tc_id): return self.run_adb_command("for /l %i in (1,1,5) do (adb shell input keyevent 26 && timeout /t 1 && adb shell input keyevent 26 && timeout /t 1)", tc_id)
    def toggle_screen_fast(self, tc_id): return self.run_adb_command("for /l %i in (1,1,5) do (adb shell input keyevent 26 && timeout /t 1 && adb shell input keyevent 26 && timeout /t 1)", tc_id)
    def sf_list(self, tc_id): return self.run_adb_command("adb shell dumpsys SurfaceFlinger --list", tc_id)
def collect_logcat(test_case_id):
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{test_case_id}_logcat.log", "w") as f:
        subprocess.run("adb logcat -d", shell=True, stdout=f)
    subprocess.run("adb logcat -c", shell=True)


def collect_script_log(tc_id, command, result=None, error=None, status="PASS"):
    log_path = os.path.join(log_dir, f"{tc_id}.txt")
    with open(log_path, 'a') as f:
        f.write(f"\n---\nTest Case: {tc_id}\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Command: {command}\n")
        f.write(f"Status: {status}\n")
        if result:
            f.write(f"Output:\n{result}\n")
        if error:
            f.write(f"Error Output:\n{error}\n")


def log_result(test_case_id, description, result):
    csv_file = "results.csv"
    row = [test_case_id, description, "PASS" if result else "FAIL"]
    header = ["Test Case ID", "Description", "Result"]
    write_header = not os.path.exists(csv_file)

    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)


# Updated to pass tc_id to each method
TEST_CASES = [
    #("TC_GFX_001", "check_screen_resolution", "Check screen resolution"),
    #("TC_GFX_002", "check_screen_density", "Check screen density"),
    #("TC_GFX_003", "capture_screenshot", "Capture screenshot"),
    #("TC_GFX_004", "record_screen", "Record screen for 5 seconds"),
    #("TC_GFX_005", "check_gpu_renderer", "Check GPU renderer"),
    #("TC_GFX_006", "check_refresh_rate", "Check active refresh rate"),
    #("TC_GFX_007", "enable_gpu_profiling", "Enable GPU rendering profiling"),
   # ("TC_GFX_008", "verify_frame_latency", "Verify frame latency"),
    #("TC_GFX_009", "enable_hw_overlay", "Enable hardware overlays"),
 #   ("TC_GFX_010", "disable_hw_overlay", "Disable hardware overlays"),
  #  ("TC_GFX_011", "hide_navigation_bar", "To hide navigation bar"),
   # ("TC_GFX_012", "navigation_bar", "To unhide navigation bar"),
    #("TC_GFX_013", "check_vsync_info", "Check vsync info"),
    #("TC_GFX_014", "dump_surfaceflinger_layers", "Dump SurfaceFlinger layers"),
#    ("TC_GFX_015", "validate_rotation", "Validate display rotation"),
 #   ("TC_GFX_016", "simulate_app_cutout_handling", "Simulate app display cutout handling"),
  #  ("TC_GFX_017", "check_ion_memory", "Check ION memory usage"),
   # ("TC_GFX_018", "capture_framebuffer", "Capture framebuffer"),
    #("TC_GFX_019", "screen_off", "Turn screen off"),
#    ("TC_GFX_020", "screen_on_unlock", "Turn screen on & unlock"),
 #   ("TC_GFX_021", "launch_ps", "To launch Play store"),
  #  ("TC_GFX_022", "gfx_info_ps", "Gfx info of Playstore"),
   # ("TC_GFX_023", "thermal_service", "Monitor thermal throttling while gaming"),
   # ("TC_GFX_024", "bs_gaming", "Log dropped frames while gaming")
    #("TC_GFX_025", "wake_screen", "Trigger ambient screen wake and validate response time"),
    ("TC_GFX_026", "toggle_screen_fast", "Run fast screen on/off loop to test render pipeline resilience"),
    #("TC_GFX_027", "sf_list", "Current composition layers"),
]


def run_all_tests():
    gfx = GraphicsTest()
    for tc_id, method_name, description in TEST_CASES:
        print(f"\n=== Running {tc_id}: {description} ===")
        method = getattr(gfx, method_name, None)
        result = None
        if method:
            result = method(tc_id)
            time.sleep(1)
        collect_logcat(tc_id)
        log_result(tc_id, description, result is not None)
        print(f"Logged result for {tc_id}")


if __name__ == "__main__":
    run_all_tests()
