import os
import sys
import time
import pytest
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import adb_utils, logger  # noqa: E402

log = logger.setup_logger()


@pytest.fixture(autouse=True)
def setup_and_teardown(request):
    test_name = request.node.name
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    log_dir = r"C:\Users\DELL\internproject1\uiautomator\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"{test_name}_{timestamp}.log")

    try:
        log.info(f"[Precondition] Ensuring Bluetooth is OFF for {test_name}")
        adb_utils.run_adb_command(['shell', 'svc', 'bluetooth', 'disable'])
        adb_utils.run_adb_command(['shell', 'logcat', '-c'])
    except Exception as e:
        log.error(f"Precondition failed: {e}")
        log.error(traceback.format_exc())

    yield

    try:
        logcat_output = adb_utils.run_adb_command(['shell', 'logcat', '-d'])
        with open(log_filename, "w", encoding="utf-8") as log_file:
            log_file.write(logcat_output)

        log.info(f"[Postcondition] Bluetooth OFF. Log saved: {log_filename}")
        adb_utils.run_adb_command(['shell', 'svc', 'bluetooth', 'disable'])
    except Exception as e:
        log.error(f"Postcondition failed: {e}")
        log.error(traceback.format_exc())


def log_and_run(description, cmd):
    try:
        log.info(f"[TEST STEP] {description}")
        output = adb_utils.run_adb_command(cmd)
        log.info(f"[ADB OUTPUT] {output}")
        return output
    except Exception as e:
        log.error(f"[ERROR] {description} failed with: {e}")
        log.error(traceback.format_exc())
        pytest.fail(f"Step failed: {description}")


class TestBluetoothControl:

    def test_01_enable_bluetooth(self):
        log_and_run("Enable Bluetooth", ['shell', 'svc', 'bluetooth', 'enable'])
        output = adb_utils.run_adb_command(['shell', 'dumpsys', 'bluetooth_manager'])
        assert "enabled" in output.lower()

    def test_02_disable_bluetooth(self):
        log_and_run("Enable Bluetooth", ['shell', 'svc', 'bluetooth', 'enable'])
        log_and_run("Disable Bluetooth", ['shell', 'svc', 'bluetooth', 'disable'])
        output = adb_utils.run_adb_command(['shell', 'dumpsys', 'bluetooth_manager'])
        assert "enabled" not in output.lower()

    def test_03_toggle_bluetooth(self):
        log_and_run("Toggle ON", ['shell', 'svc', 'bluetooth', 'enable'])
        log_and_run("Toggle OFF", ['shell', 'svc', 'bluetooth', 'disable'])
        log_and_run("Toggle ON again", ['shell', 'svc', 'bluetooth', 'enable'])
        output = adb_utils.run_adb_command(['shell', 'dumpsys', 'bluetooth_manager'])
        assert "enabled" in output.lower()

    def test_04_check_bluetooth_mac(self):
        mac = log_and_run("Get Bluetooth MAC", ['shell', 'settings', 'get', 'secure', 'bluetooth_address'])
        assert ":" in mac.strip()

    def test_05_check_bt_state_with_dumpsys(self):
        output = log_and_run("Check Bluetooth state", ['shell', 'dumpsys', 'bluetooth_manager'])
        assert any(state in output.lower() for state in ["enabled", "disabled"])

    def test_06_scan_for_devices(self):
        log_and_run("Start Bluetooth", ['shell', 'svc', 'bluetooth', 'enable'])
        output = log_and_run("Start scanning", [
            'shell', 'am', 'broadcast', '-a', 'android.bluetooth.adapter.action.REQUEST_DISCOVERABLE'
        ])
        assert "broadcast completed" in output.lower() or "result=" in output.lower()

    def test_07_check_discoverable_mode(self):
        state = log_and_run("Check discoverable mode", [
            'shell', 'settings', 'get', 'global', 'bluetooth_discoverable_timeout'
        ])
        assert state.strip().isdigit()

    def test_08_make_device_discoverable(self):
        output = log_and_run("Make device discoverable", [
            'shell', 'am', 'start', '-a', 'android.bluetooth.adapter.action.REQUEST_DISCOVERABLE'
        ])
        assert "cmp=" in output.lower() or "starting" in output.lower()

    def test_09_check_paired_devices(self):
        output = log_and_run("Check paired devices", [
            'shell', 'cmd', 'bluetooth_manager', 'getPairedDevices'
        ])
        log.info(f"Paired Devices: {output}")
        assert output and output.strip()

    def test_10_enable_bt_via_settings_put(self):
        log_and_run("Enable BT via settings", [
            'shell', 'settings', 'put', 'global', 'bluetooth_on', '1'
        ])
        output = adb_utils.run_adb_command(['shell', 'dumpsys', 'bluetooth_manager'])
        assert "enabled" in output.lower()

    def test_11_check_bt_stack(self):
        output = log_and_run("Get Bluetooth stack info", ['shell', 'dumpsys', 'bluetooth_manager'])
        assert "bluetoothmanager" in output.lower()

    def test_12_trigger_bt_settings_ui(self):
        output = log_and_run("Trigger Bluetooth UI", [
            'shell', 'am', 'start', '-a', 'android.settings.BLUETOOTH_SETTINGS'
        ])
        assert "cmp=" in output.lower() or "starting" in output.lower()

    def test_13_bt_off_state_check(self):
        log_and_run("Turn off Bluetooth", ['shell', 'svc', 'bluetooth', 'disable'])
        output = log_and_run("Check Bluetooth off state", ['shell', 'dumpsys', 'bluetooth_manager'])
        assert "enabled" not in output.lower()

    def test_14_bt_logcat_filter(self):
        log_and_run("Start Bluetooth", ['shell', 'svc', 'bluetooth', 'enable'])
        output = log_and_run("Capture Bluetooth logs", ['shell', 'logcat', '-d'])
        assert "bluetooth" in output.lower() or len(output.strip()) > 0

    def test_15_restart_bluetooth_adapter(self):
        log_and_run("Disable Bluetooth", ['shell', 'svc', 'bluetooth', 'disable'])
        log_and_run("Enable Bluetooth", ['shell', 'svc', 'bluetooth', 'enable'])
        output = adb_utils.run_adb_command(['shell', 'dumpsys', 'bluetooth_manager'])
        assert "enabled" in output.lower()

    def test_00_test_all_conditions(self):
        failed_tests = []

        test_methods = [
            ("test_01_enable_bluetooth", self.test_01_enable_bluetooth),
            ("test_02_disable_bluetooth", self.test_02_disable_bluetooth),
            ("test_03_toggle_bluetooth", self.test_03_toggle_bluetooth),
            ("test_04_check_bluetooth_mac", self.test_04_check_bluetooth_mac),
            ("test_05_check_bt_state_with_dumpsys", self.test_05_check_bt_state_with_dumpsys),
            ("test_06_scan_for_devices", self.test_06_scan_for_devices),
            ("test_07_check_discoverable_mode", self.test_07_check_discoverable_mode),
            ("test_08_make_device_discoverable", self.test_08_make_device_discoverable),
            ("test_09_check_paired_devices", self.test_09_check_paired_devices),
            ("test_10_enable_bt_via_settings_put", self.test_10_enable_bt_via_settings_put),
            ("test_11_check_bt_stack", self.test_11_check_bt_stack),
            ("test_12_trigger_bt_settings_ui", self.test_12_trigger_bt_settings_ui),
            ("test_13_bt_off_state_check", self.test_13_bt_off_state_check),
            ("test_14_bt_logcat_filter", self.test_14_bt_logcat_filter),
            ("test_15_restart_bluetooth_adapter", self.test_15_restart_bluetooth_adapter),
        ]

        for name, method in test_methods:
            try:
                log.info(f"[RUNNING] {name}")
                method()
                log.info(f"[PASSED] {name}")
            except Exception as e:
                log.error(f"[FAILED] {name} with error: {e}")
                log.error(traceback.format_exc())
                failed_tests.append(name)

        if failed_tests:
            summary = f"{len(failed_tests)} test(s) failed: {', '.join(failed_tests)}"
            log.error(f"[SUMMARY] {summary}")
            raise Exception(f"{len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        else:
            log.info("[SUMMARY] All Bluetooth tests executed successfully.")
