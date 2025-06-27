import os
import time
import logging
import subprocess
import pytest

# --------------------------------------
# Logger Setup
# --------------------------------------
def setup_logger(name="uiautomator", log_file="uiautomator.log", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        return logger

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)

    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

log = setup_logger()

# --------------------------------------
# ADB Utility Functions
# --------------------------------------
def run_adb_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"
        return result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: ADB command timed out"
    except Exception as e:
        return f"ERROR: {str(e)}"

def clear_logcat():
    run_adb_command(["adb", "logcat", "-c"])

def capture_logcat(test_name):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{test_name}_logcat_{timestamp}.txt"
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", filename), "w", encoding="utf-8") as f:
        subprocess.run(["adb", "logcat", "-d"], stdout=f, text=True)

def log_and_run(description, command):
    try:
        log.info(f"\n[STEP] {description}")
        log.info(f"[COMMAND] {' '.join(command)}")
        output = run_adb_command(command)
        log.info(f"[OUTPUT] {output}")
        if output.startswith("ERROR"):
            pytest.fail(output)
        return output
    except Exception as e:
        log.error(f"[EXCEPTION] {str(e)}")
        pytest.fail(f"Exception occurred during: {description} -> {e}")

# --------------------------------------
# Pytest Hooks
# --------------------------------------
@pytest.fixture(autouse=True)
def setup_and_teardown(request):
    log.info(f"\n[TEST START] {request.node.name}")
    clear_logcat()
    yield
    capture_logcat(request.node.name)
    log.info(f"[TEST END] {request.node.name}\n")

# --------------------------------------
# Test Class
# --------------------------------------
class TestDisplayModule:

    def test_set_screen_brightness_to_max(self):
        log_and_run("Set screen brightness to max", ["adb", "shell", "settings", "put", "system", "screen_brightness", "255"])

    def test_enable_auto_brightness(self):
        log_and_run("Enable auto brightness", ["adb", "shell", "settings", "put", "system", "screen_brightness_mode", "1"])

    def test_set_screen_timeout(self):
        log_and_run("Set screen timeout to 60 seconds", ["adb", "shell", "settings", "put", "system", "screen_off_timeout", "60000"])

    def test_set_resolution(self):
        log_and_run("Set resolution to 1080x2340", ["adb", "shell", "wm", "size", "1080x2340"])

    def test_set_density(self):
        log_and_run("Set density to 320", ["adb", "shell", "wm", "density", "320"])

    def test_enable_night_light(self):
        log_and_run("Enable night light", ["adb", "shell", "settings", "put", "secure", "display_night_light_activated", "1"])

    def test_enable_always_on_display(self):
        log_and_run("Enable always-on display", ["adb", "shell", "settings", "put", "secure", "doze_always_on", "1"])

    def test_user_rotation(self):
        log_and_run("Set user rotation to 90° (code 1)", ["adb", "shell", "settings", "put", "system", "user_rotation", "1"])

    def test_disable_auto_rotation(self):
        log_and_run("Disable auto rotation", ["adb", "shell", "settings", "put", "system", "accelerometer_rotation", "0"])

    def test_keep_screen_on_charging(self):
        log_and_run("Keep screen on while charging", ["adb", "shell", "settings", "put", "global", "stay_on_while_plugged_in", "3"])

    def test_take_and_pull_screenshot(self):
        log_and_run("Take screenshot", ["adb", "shell", "screencap", "-p", "/sdcard/disp_test.png"])
        output = run_adb_command(["adb", "pull", "/sdcard/disp_test.png", "."])
        log.info(f"ADB Pull Output: {output}")
        if "file pulled" in output.lower() or "bytes" in output.lower():
            log.info(" Screenshot pulled successfully.")
        else:
            pytest.fail(f"ERROR during pull: {output}")
        # Optional cleanup
        run_adb_command(["adb", "shell", "rm", "/sdcard/disp_test.png"])
        if os.path.exists("disp_test.png"):
            os.remove("disp_test.png")

    def test_send_factory_broadcast(self):
        log_and_run("Broadcast factory test intent", ["adb", "shell", "am", "broadcast", "-a", "android.intent.action.FACTORY_TEST"])

    def test_power_key_press(self):
        log_and_run("Simulate power key press", ["adb", "shell", "input", "keyevent", "26"])

    def test_enable_magnification(self):
        log_and_run("Enable magnification", ["adb", "shell", "settings", "put", "secure", "accessibility_display_magnification_enabled", "1"])

    def test_get_font_scale(self):
        log_and_run("Get font scale", ["adb", "shell", "settings", "get", "system", "font_scale"])

    def test_enable_3_button_nav(self):
        log_and_run("Enable 3-button nav", ["adb", "shell", "cmd", "overlay", "enable", "com.android.internal.systemui.navbar.threebutton"])

    def test_enable_gestural_nav(self):
        log_and_run("Enable gestural nav", ["adb", "shell", "cmd", "overlay", "enable", "com.android.internal.systemui.navbar.gestural"])

    def test_get_screensaver_components(self):
        log_and_run("Get screensaver components", ["adb", "shell", "settings", "get", "secure", "screensaver_components"])

    def test_enable_screensaver(self):
        log_and_run("Enable screensaver", ["adb", "shell", "settings", "put", "secure", "screensaver_enabled", "1"])

    def test_disable_screensaver(self):
        log_and_run("Disable screensaver", ["adb", "shell", "settings", "put", "secure", "screensaver_enabled", "0"])

    def test_enable_color_correction(self):
        log_and_run("Enable color correction", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer_enabled", "1"])

    def test_disable_color_correction(self):
        log_and_run("Disable color correction", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer_enabled", "0"])

    def test_set_color_filter_11(self):
        log_and_run("Set color filter to 11", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer", "11"])

    def test_set_color_filter_12(self):
        log_and_run("Set color filter to 12", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer", "12"])

    def test_set_color_filter_13(self):
        log_and_run("Set color filter to 13", ["adb", "shell", "settings", "put", "secure", "accessibility_display_daltonizer", "13"])

    def test_get_color_filter(self):
        log_and_run("Get current color filter", ["adb", "shell", "settings", "get", "secure", "accessibility_display_daltonizer"])

    def test_set_refresh_rate(self):
        log_and_run("Set refresh rate to 60Hz", ["adb", "shell", "settings", "put", "system", "refresh_rate", "60.0"])

    def test_get_refresh_rate(self):
        log_and_run("Get current refresh rate", ["adb", "shell", "settings", "get", "system", "refresh_rate"])

    def test_window_anim_scale(self):
        log_and_run("Set window animation scale to 0.5", ["adb", "shell", "settings", "put", "global", "window_animation_scale", "0.5"])

    def test_transition_anim_scale(self):
        log_and_run("Set transition animation scale to 0.5", ["adb", "shell", "settings", "put", "global", "transition_animation_scale", "0.5"])

    def test_animator_duration_scale(self):
        log_and_run("Set animator duration scale to 0.5", ["adb", "shell", "settings", "put", "global", "animator_duration_scale", "0.5"])

    def test_00_test_all_conditions(self):
        """Run all display tests sequentially in one method."""
        self.test_set_screen_brightness_to_max()
        self.test_enable_auto_brightness()
        self.test_set_screen_timeout()
        self.test_set_resolution()
        self.test_set_density()
        self.test_enable_night_light()
        self.test_enable_always_on_display()
        self.test_user_rotation()
        self.test_disable_auto_rotation()
        self.test_keep_screen_on_charging()
        self.test_take_and_pull_screenshot()
        self.test_send_factory_broadcast()
        self.test_power_key_press()
        self.test_enable_magnification()
        self.test_get_font_scale()
        self.test_enable_3_button_nav()
        self.test_enable_gestural_nav()
        self.test_get_screensaver_components()
        self.test_enable_screensaver()
        self.test_disable_screensaver()
        self.test_enable_color_correction()
        self.test_disable_color_correction()
        self.test_set_color_filter_11()
        self.test_set_color_filter_12()
        self.test_set_color_filter_13()
        self.test_get_color_filter()
        self.test_set_refresh_rate()
        self.test_get_refresh_rate()
        self.test_window_anim_scale()
        self.test_transition_anim_scale()
        self.test_animator_duration_scale()
        log.info("[RESULT] All Display ADB testcases executed successfully.")

# --------------------------------------
# Entry Point for CLI run
# --------------------------------------
if __name__ == "__main__":
    import sys
    pytest.main(["-v", sys.argv[0]])
