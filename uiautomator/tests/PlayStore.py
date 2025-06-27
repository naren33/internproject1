import os
import sys
import time
import subprocess
import pytest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import logger  # noqa: E402

log = logger.setup_logger()


@pytest.fixture(autouse=True)
def setup_and_teardown(request):
    test_name = request.node.name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = r"C:\Users\DELL\internproject1\uiautomator\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"{test_name}_{timestamp}.log")

    log.info(f"[Precondition] Preparing device for test '{test_name}'")
    yield
    log.info(f"[Postcondition] Test '{test_name}' complete. Log saved at {log_filename}")


def log_and_run(description, cmd):
    log.info(f"[STEP] {description}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip() if result.stdout else ""
    log.info(f"[ADB OUTPUT] {output}")
    return output


class TestPlayStore:

    def test_01_launch_playstore(self):
        log_and_run("Launching Play Store", [
            "adb", "shell", "am", "start", "-n",
            "com.android.vending/com.google.android.finsky.activities.MainActivity"
        ])
        time.sleep(2)

    def test_02_search_on_playstore(self):
        query = input("Enter search term: ")
        self.test_01_launch_playstore()
        log_and_run(f"Opening Play Store search with query '{query}'", [
            "adb", "shell", "am", "start", "-a",
            "android.intent.action.VIEW", "-d", f"market://search?q={query}"
        ])
        time.sleep(4)

    def test_03_list_installed_apps(self):
        output = log_and_run("Listing installed packages", [
            "adb", "shell", "pm", "list", "packages"
        ])
        assert output, "No packages found"

    def test_04_check_playstore_launch_time(self):
        start = time.time()
        self.test_01_launch_playstore()
        end = time.time()
        duration = end - start
        log.info(f"Play Store launch time: {duration:.2f}s")
        assert duration > 0

    def test_05_open_an_app(self):
        package_name = input("Enter package name (e.g., com.google.android.youtube): ")
        log_and_run(f"Opening app {package_name} via monkey", [
            "adb", "shell", "monkey", "-p", package_name,
            "-c", "android.intent.category.LAUNCHER", "1"
        ])
        time.sleep(2)

    def test_06_check_notifications(self):
        output = log_and_run("Dumping notification service", [
            "adb", "shell", "dumpsys", "notification"
        ])
        assert output, "No notification output found"

    def test_07_check_airplane_mode_behavior(self):
        log_and_run("Disabling WiFi", ["adb", "shell", "svc", "wifi", "disable"])
        log_and_run("Disabling Mobile Data", ["adb", "shell", "svc", "data", "disable"])
        log_and_run("Enabling Airplane Mode", ["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"])
        log_and_run("Broadcasting Airplane Mode ON", [
            "adb", "shell", "am", "broadcast",
            "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"
        ])

        self.test_01_launch_playstore()
        time.sleep(4)

        log_and_run("Opening search while in airplane mode", [
            "adb", "shell", "am", "start", "-a",
            "android.intent.action.VIEW", "-d", "market://search?q=example"
        ])
        time.sleep(4)

        log_and_run("Taking screenshot in airplane mode", [
            "adb", "shell", "screencap", "-p", "/sdcard/airplane_mode.png"
        ])

    def test_09_press_home_and_return(self):
        log_and_run("Pressing Home key", ["adb", "shell", "input", "keyevent", "3"])
        time.sleep(1)
        self.test_01_launch_playstore()

    def test_10_check_search_suggestions(self):
        query = input("Enter suggestion query: ")
        log_and_run(f"Triggering Play Store search with '{query}'", [
            "adb", "shell", "am", "start", "-a",
            "android.intent.action.VIEW", "-d", f"market://search?q={query}"
        ])
        time.sleep(2)

    def test_12_uninstall_app(self):
        package_name = input("Enter package name to uninstall: ")
        log_and_run(f"Uninstalling {package_name}", ["adb", "uninstall", package_name])
