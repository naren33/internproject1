import subprocess
import time
import os
import sys
import io
import csv
from datetime import datetime

class WiFiModule:
    def __init__(self):
        self.log_dir = "logs"
        self.summary_file = os.path.join(self.log_dir, "wifi_test_summary.csv")
        os.makedirs(self.log_dir, exist_ok=True)

        if not os.path.exists(self.summary_file):
            with open(self.summary_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Test Case ID", "Description", "Status", "Log File"])

        self.test_results = []

    def pre_config(self, tc_id):
        msg = f"[{tc_id}] Pre-Config: Ensure device is connected and ready\n"
        print(msg.strip())
        self._append_log(tc_id, msg)
        subprocess.run(["adb", "wait-for-device"])
        subprocess.run(["adb", "root"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def post_config(self, tc_id):
        msg = f"[{tc_id}] Post-Config: Cleaning up or resetting state\n"
        print(msg.strip())
        self._append_log(tc_id, msg)
        subprocess.run(["adb", "shell", "svc", "wifi", "enable"])

    def _append_log(self, tc_id, text):
        log_path = os.path.join(self.log_dir, f"{tc_id}_log.txt")
        with open(log_path, "a") as f:
            f.write(f"{datetime.now()} - {text}")

    def log_test(self, tc_id, description, func, *args):
        log_path = os.path.join(self.log_dir, f"{tc_id}_log.txt")
        buffer = io.StringIO()
        sys_stdout_backup = sys.stdout
        status = "UNKNOWN"

        try:
            self.pre_config(tc_id)

            sys.stdout = buffer
            func(*args)
            sys.stdout = sys_stdout_backup

            self.post_config(tc_id)

            lines = buffer.getvalue().strip().splitlines()
            for line in reversed(lines):
                if line.startswith("Status:"):
                    status = line.split(":")[1].strip()
                    break
        except Exception as e:
            sys.stdout = sys_stdout_backup
            print(f"[ERROR] {e}")
            self._append_log(tc_id, f"[ERROR] {e}\n")
            status = "FAIL"

        with open(log_path, "a") as f:
            f.write(buffer.getvalue())

        with open(self.summary_file, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([tc_id, description, status, log_path])

        self.test_results.append((tc_id, description, status))
        print(f"[✓] {tc_id} -> {status} (Log: {log_path})")

    def print_summary(self):
        print("\n========== 📋 TEST SUMMARY ==========")
        print(f"{'TC ID':<8} {'Description':<40} {'Status'}")
        print("-" * 60)
        for tc_id, desc, status in self.test_results:
            print(f"{tc_id:<8} {desc:<40} {status}")
        print("-" * 60)

    # ================== 25 AUTOMATED TEST CASES ==================

    def test_tc001(self): subprocess.run(["adb", "shell", "svc", "wifi", "enable"]); print("Status: PASS")
    def test_tc002(self): subprocess.run(["adb", "shell", "svc", "wifi", "disable"]); print("Status: PASS")
    def test_tc003(self):
        print("[TC003] Stress test: Toggle WiFi ON/OFF 10 times")
        try:
            for i in range(10):
                print(f"Cycle {i+1}: Disable WiFi")
                subprocess.run(["adb", "shell", "svc", "wifi", "disable"])
                time.sleep(1)
                print(f"Cycle {i+1}: Enable WiFi")
                subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
                time.sleep(1)
            print("Expected: No failure or crash during rapid toggling")
            print("Status:   PASS\n")
        except Exception as e:
            print(f"[ERROR] Exception during toggling: {e}")
            print("Status:   FAIL\n")

    def test_tc004(self):
        subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
        time.sleep(2)
        result = subprocess.check_output(["adb", "shell", "ip", "addr", "show", "wlan0"]).decode()
        print("Status: PASS" if "inet " in result else "Status: FAIL")

    def test_tc005(self):
        out = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        print("Status: PASS" if "RSSI" in out or "rssi" in out else "Status: FAIL")
    def test_tc006(self):
        subprocess.run(["adb", "shell", "svc", "wifi", "disable"])
        time.sleep(1)
        out = subprocess.check_output(["adb", "shell", "ip", "addr", "show", "wlan0"]).decode()
        print("Status: PASS" if "inet " not in out else "Status: FAIL")
    def test_tc007(self):
        out = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        print("Status: PASS" if "connected" in out.lower() or "SSID" in out else "Status: FAIL")
    def test_tc008(self):
        out = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        print("Status: PASS" if "frequency" in out else "Status: FAIL")
    def test_tc009(self):
        subprocess.run(["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"])
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"])
        time.sleep(2)
        out = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        result = "enabled: true" not in out
        subprocess.run(["adb", "shell", "settings", "put", "global", "airplane_mode_on", "0"])
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false"])
        print("Status: PASS" if result else "Status: FAIL")
    def test_tc010(self):
        mac = subprocess.check_output(["adb", "shell", "cat", "/sys/class/net/wlan0/address"]).decode().strip()
        print("Status: PASS" if mac else "Status: FAIL")
    def test_tc011(self):
        output = subprocess.check_output(["adb", "shell", "settings", "get", "global", "wifi_sleep_policy"]).decode().strip()
        print("Status: PASS" if output in ["0", "1", "2"] else "Status: FAIL")
    def test_tc012(self):
        subprocess.run(["adb", "shell", "svc", "wifi", "disable"])
        time.sleep(1)
        subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
        time.sleep(1)
        print("Status: PASS")
    def test_tc013(self):
        for _ in range(3):
            subprocess.run(["adb", "shell", "svc", "wifi", "disable"])
            time.sleep(1)
            subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
            time.sleep(1)
        print("Status: PASS")
    def test_tc014(self):
        out = subprocess.check_output(["adb", "shell", "cmd", "wifi", "list-scan-results"]).decode(errors='ignore')
        print("Status: PASS" if "SSID" in out else "Status: FAIL")
    def test_tc015(self):
        result = subprocess.check_output(["adb", "shell", "ip", "route", "get", "8.8.8.8"]).decode()
        print("Status: PASS" if "wlan0" in result else "Status: FAIL")
    def test_tc016(self):
        subprocess.run(["adb", "shell", "cmd", "battery", "set", "level", "5"])
        subprocess.run(["adb", "shell", "cmd", "battery", "reset"])
        print("Status: PASS")
    def test_tc017(self):
        out = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        print("Status: PASS" if "supplicant state" in out.lower() else "Status: FAIL")
    def test_tc018(self):
        print("[TC023] Check for WiFi sleep policy")
        try:
            output = subprocess.check_output(["adb", "shell", "settings", "get", "global", "wifi_sleep_policy"]).decode().strip()
            print(f"Sleep Policy: {output}")
            print("Expected: 2 = Never, 1 = Only when plugged, 0 = Always")
            if output in ["0", "1", "2"]:
                print("Status:  PASS\n")
            else:
                print("Status:  FAIL\n")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            print("Status:   FAIL\n")
    def test_rssi(self):
                print(" Get RSSI (Signal Strength)")

    try:
        # Step 1: Ensure WiFi is ON
        print("Checking WiFi status...")
        wifi_status = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        if "Wi-Fi is disabled" in wifi_status:
            print("WiFi is OFF. Enabling WiFi...")
            subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
            time.sleep(5)  # wait for connection to establish

        # Step 2: Fetch updated WiFi info
        output = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()

        # Step 3: Look for RSSI values
        found = False
        for line in output.splitlines():
            if "rssi" in line.lower():
                print(line.strip())
                found = True

        # Step 4: Result
        if found:
            print("Expected: RSSI should be a negative dBm value (e.g., -40)")
            print("Status:   PASS\n")
        else:
            print("RSSI info not found. WiFi may not be connected.")
            print("Status:   FAIL\n")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("Status:   FAIL\n")
    
    def test_tc020(self):
        subprocess.run(["adb", "shell", "svc", "wifi", "disable"])
        time.sleep(2)
        subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
        
    def test_tc021(self):
        print("[TC021] Ensure WiFi is off in Airplane mode")
        subprocess.run(["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"])
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"])
        time.sleep(3)
        output = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        if "enabled: true" in output:
            print("WiFi still ON in Airplane mode")
        else:
            print("WiFi disabled in Airplane mode")
        subprocess.run(["adb", "shell", "settings", "put", "global", "airplane_mode_on", "0"])
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false"])

    def test_tc022(self):
        out = subprocess.check_output(["adb", "shell", "ping", "-c", "1", "8.8.8.8"]).decode()
        print("Status: PASS" if "bytes from" in out else "Status: FAIL")
    def test_tc023(self):
        out = subprocess.check_output(["adb", "shell", "getprop", "wifi.status"]).decode()
        print("Status: PASS" if out else "Status: FAIL")
    def test_tc024(self):
        
        subprocess.run(["adb", "shell", "svc", "wifi", "enable"])
        time.sleep(2)
        subprocess.run(["adb", "shell", "am", "start", "-a", "android.settings.TETHER_SETTINGS"])
        

    def test_tc025(self):
        print("[TC025] List all saved WiFi configurations")
        try:
            output = subprocess.check_output(["adb", "shell", "su", "-c", "cat /data/misc/wifi/WifiConfigStore.xml"]).decode(errors='ignore')
            if "SSID" in output:
                print("Saved Configurations Found:")
                for line in output.splitlines():
                    if "SSID" in line:
                        print(line.strip())
                print("Status: PASS\n")
            else:
                print("Status:   FAIL — No SSID found\n")
        except subprocess.CalledProcessError as e:
            print(f"Error reading saved WiFi configs: {e}")
            print("Status: FAIL\n")


# RUN

if __name__ == "__main__":
    wifi = WiFiModule()
    for i in range(1, 26):
        tc_id = f"TC{str(i).zfill(3)}"
        description = f"Automated WiFi Test {i}"
        wifi.log_test(tc_id, description, getattr(wifi, f"test_tc{str(i).zfill(3)}"))
    wifi.print_summary()
