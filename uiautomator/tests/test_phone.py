import subprocess
from datetime import datetime
import os

class PhoneTestCommands:
    def __init__(self):
        self.commands = {
            "PHN_01 - Launch Dialer App": "adb shell am start -a android.intent.action.DIAL",
            "PHN_02 - End Call Test": "adb shell input keyevent KEYCODE_ENDCALL",
            "PHN_03 - Dump Call State": "adb shell dumpsys telecom",
            "PHN_04 - Toggle Speaker Mode": "adb shell input keyevent KEYCODE_SPEAKER",
            "PHN_05 - Simulate Incoming Call": "adb shell am start -a android.intent.action.CALL -d tel:1234567890",
            "PHN_06 - Microphone Test": "adb shell am start -n com.android.soundrecorder/.MainActivity",
            "PHN_07 - Call Forwarding Test": "adb shell service call phone 1 s16 '1234567890'",
            "PHN_08 - Dump Network Info": "adb shell dumpsys telephony.registry",
            "PHN_09 - DTMF Test": "adb shell input keyevent KEYCODE_1",
            "PHN_10 - Airplane Mode Test": "adb shell settings put global airplane_mode_on 1",
            "PHN_11 - Voicemail Test": "adb shell am start -a android.intent.action.CALL -d voicemail:",
            "PHN_12 - Call Drop Test": "adb shell svc data disable",
            "PHN_13 - Bluetooth Headset Test": "adb shell am start -a android.bluetooth.adapter.action.REQUEST_ENABLE",
            "PHN_14 - Call Duration Test": "adb shell dumpsys call_log",
            "PHN_15 - Multi-Call Test": "adb shell am start -a android.intent.action.CALL -d tel:9876543210",
            "PHN_16 - Open Call Settings": "adb shell am start -a android.settings.CALL_SETTINGS",
            "PHN_17 - Get Active Network Info": "adb shell dumpsys connectivity",
            "PHN_18 - Enable Do Not Disturb Mode": "adb shell settings put global zen_mode 1",
            "PHN_19 - Disable Do Not Disturb Mode": "adb shell settings put global zen_mode 0",
        }

    def get_command(self, test_name):
        return self.commands.get(test_name)

    def list_tests(self): 
        return list(self.commands.keys())

class PhoneTestExecutor:
    def __init__(self):
        self.commands = PhoneTestCommands()
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.report_lines = [] 
        self.report_file = f"logs/phone_test_report_{self.timestamp}.txt"
        os.makedirs("logs", exist_ok=True)

    def run_tests(self, selected_tests):
        self.report_lines.append(f"Phone Test Report - {self.timestamp}\n{'=' * 60}\n")

        for test_name in selected_tests:
            command = self.commands.get_command(test_name)
            test_id = test_name.split(" - ")[0]
            output_log = f"logs/{test_id}_output.txt"
            logcat_log = f"logs/{test_id}_logcat.txt"

            try:
                result = subprocess.run(command, shell=True, capture_output=True, encoding="utf-8", errors="replace")
                output = result.stdout.strip()
                error_output = result.stderr.strip()

                with open(output_log, 'w', encoding='utf-8') as out_f:
                    out_f.write(f"Test: {test_name}\nCommand: {command}\nOutput:\n{output}\n")
                    if error_output:
                        out_f.write(f"\nErrors:\n{error_output}\n")

                logcat_result = subprocess.run(["adb", "logcat", "-d"], capture_output=True, encoding="utf-8", errors="replace")
                with open(logcat_log, 'w', encoding='utf-8') as log_f:
                    log_f.write(logcat_result.stdout)

                self.report_lines.append(
                    f"Test: {test_name}\nCommand: {command}\nOutput:\n{output}\n{'-' * 60}\n"
                )

                subprocess.run(["adb", "logcat", "-c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            except Exception as e:
                error_msg = f"Test: {test_name} - ERROR: {str(e)}\n{'-' * 60}\n"
                self.report_lines.append(error_msg)
 
                with open(output_log, 'w', encoding='utf-8') as err_f:
                    err_f.write(error_msg)
                with open(logcat_log, 'w', encoding='utf-8') as err_f:
                    err_f.write(error_msg)

        self.save_report()

    def save_report(self):
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.report_lines))

    def prompt_user_selection(self):
        available_tests = self.commands.list_tests()

        print("\nAvailable Phone Test Cases:")
        for idx, test in enumerate(available_tests, 1):
            print(f"{idx}. {test}")

        input_str = input("\nEnter test numbers to run (comma-separated, e.g., 1,3,5): ")
        try:
            indexes = [int(i.strip()) for i in input_str.split(",") if i.strip().isdigit()]
            selected = [available_tests[i - 1] for i in indexes if 0 < i <= len(available_tests)]
            if not selected:
                print("[WARN] No valid test numbers selected. Running all tests.")
                return available_tests
            return selected
        except Exception as e:
            print(f"[ERROR] Invalid input. Running all tests. ({e})")
            return available_tests

if __name__ == "__main__":
    executor = PhoneTestExecutor()
    selected_tests = executor.prompt_user_selection()
    executor.run_tests(selected_tests)
