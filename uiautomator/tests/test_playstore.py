import subprocess
import time
import csv
from datetime import datetime

class PlayStoreTester:
    def __init__(self, adb_path="adb"):
        self.adb = adb_path
        self.results = []

    def log_result(self, test_name, status, message=""):
        self.results.append({
            "Test Case": test_name,
            "Status": status,
            "Message": message,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"{test_name} - {status}: {message}")

    def export_results(self, filename="test_results.csv"):
        if self.results:
            with open(filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)
            print(f"Results saved to {filename}")
        else:
            print("No test results to export.")

    def test_1_launch_playstore(self):
        test = "1. Launch Play Store"
        try:
            subprocess.run([self.adb, "shell", "am", "start", "-n",
                            "com.android.vending/com.google.android.finsky.activities.MainActivity"])
            time.sleep(2)
            self.log_result(test, "Passed")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def open_search_bar(self, query=""):
        try:
            subprocess.run([self.adb, "shell", "am", "start", "-a",
                            "android.intent.action.VIEW", "-d", f"market://search?q={query}"])
            time.sleep(4)
        except Exception as e:
            print("Error opening search bar:", e)

    def test_2_search_on_playstore(self):
        test = "2. Search on Play Store"
        query = input("Enter search term: ")
        try:
            self.test_1_launch_playstore()
            self.open_search_bar(query)
            self.log_result(test, "Passed")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def test_3_list_installed_apps(self):
        test = "3. List Installed Apps"
        try:
            result = subprocess.run([self.adb, "shell", "pm", "list", "packages"], capture_output=True, text=True)
            app_list = result.stdout.strip().splitlines()
            self.log_result(test, "Passed", f"Packages:\n" + "\n".join(app_list))
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def test_4_check_playstore_launch_time(self):
        test = "4. Check Play Store Launch Time"
        try:
            start = time.time()
            self.test_1_launch_playstore()
            end = time.time()
            self.log_result(test, "Passed", f"Launch time: {end - start:.2f}s")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def test_5_open_app(self):
        test = "5. Open an App"
        package_name = input("Enter package name (e.g., com.google.android.youtube): ")
        try:
            subprocess.run([self.adb, "shell", "monkey", "-p", package_name, "-c",
                            "android.intent.category.LAUNCHER", "1"])
            time.sleep(2)
            self.log_result(test, "Passed", f"Opened app {package_name} via monkey")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def test_6_check_notifications(self):
        test = "6. Check Notifications"
        try:
            result = subprocess.run([self.adb, "shell", "dumpsys", "notification"], capture_output=True)
            output = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
            self.log_result(test, "Passed", f"{len(output.splitlines())} lines")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def test_7_check_airplane_mode_behavior(self):
        test = "7. Check Airplane Mode Behavior"
        try:
            subprocess.run([self.adb, "shell", "svc", "wifi", "disable"])
            subprocess.run([self.adb, "shell", "svc", "data", "disable"])
            subprocess.run([self.adb, "shell", "settings", "put", "global", "airplane_mode_on", "1"])
            subprocess.run([self.adb, "shell", "am", "broadcast",
                            "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"])
            self.test_1_launch_playstore()
            time.sleep(4)
            self.open_search_bar("example")
            time.sleep(4)
            subprocess.run([self.adb, "shell", "screencap", "-p", "/sdcard/airplane_mode.png"])
            self.log_result(test, "Passed", "Airplane mode search and screenshot captured")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    # def test_8_tap_tabs_and_check_activity(self):
    #     test = "8. Tap Tabs and Check Activity"
    #     try:
    #         subprocess.run([self.adb, "shell", "am", "start", "-n",
    #                         "com.android.vending/com.google.android.finsky.activities.MainActivity"])
    #         time.sleep(2)
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "61"])
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "61"])
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "66"])
    #         time.sleep(2)
    #         self.log_result(test, "Passed", "Used keyevents to switch and confirm tab navigation")
    #     except Exception as e:
    #         self.log_result(test, "Failed", str(e))

    def test_9_press_home_and_return(self):
        test = "9. Press Home and Return to Play Store"
        try:
            subprocess.run([self.adb, "shell", "input", "keyevent", "3"])
            time.sleep(1)
            self.test_1_launch_playstore()
            self.log_result(test, "Passed")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    def test_10_check_search_suggestions(self):
        test = "10. Pop-up Suggestions While Searching"
        query = input("Enter suggestion query: ")
        try:
            self.open_search_bar(query)
            time.sleep(2)
            self.log_result(test, "Passed", "Opened search bar for suggestions (verify manually)")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

    # def test_11_install_app(self):
    #     test = "11. Install App from Play Store"
    #     query = input("Enter app name to install: ")
    #     try:
    #         self.open_search_bar(query)
    #         time.sleep(6)
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "66"])
    #         time.sleep(5)
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "61"])
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "61"])
    #         subprocess.run([self.adb, "shell", "input", "keyevent", "66"])
    #         self.log_result(test, "Passed", f"Triggered install flow for {query} via key navigation")
    #     except Exception as e:
    #         self.log_result(test, "Failed", str(e))

    def test_12_uninstall_app(self):
        test = "12. Uninstall an App"
        package_name = input("Enter package name to uninstall: ")
        try:
            subprocess.run([self.adb, "uninstall", package_name])
            self.log_result(test, "Passed", f"Uninstalled {package_name}")
        except Exception as e:
            self.log_result(test, "Failed", str(e))

if __name__ == "__main__":
    tester = PlayStoreTester()

    while True:
        print("\nSelect a test to run:")
        print("1. Launch Play Store")
        print("2. Search on Play Store")
        print("3. List Installed Apps")
        print("4. Check Play Store Launch Time")
        print("5. Open an App")
        print("6. Check Notifications")
        print("7. Check Airplane Mode Behavior")
        # print("8. Tap Tabs and Check Activity")
        print("9. Press Home and Return to Play Store")
        print("10. Pop-up Suggestions While Searching")
        # print("11. Install an App")
        print("12. Uninstall an App")
        print("0. Export results and exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            tester.test_1_launch_playstore()
        elif choice == "2":
            tester.test_2_search_on_playstore()
        elif choice == "3":
            tester.test_3_list_installed_apps()
        elif choice == "4":
            tester.test_4_check_playstore_launch_time()
        elif choice == "5":
            tester.test_5_open_app()
        elif choice == "6":
            tester.test_6_check_notifications()
        elif choice == "7":
            tester.test_7_check_airplane_mode_behavior()
        # elif choice == "8":
        #     tester.test_8_tap_tabs_and_check_activity()
        elif choice == "9":
            tester.test_9_press_home_and_return()
        elif choice == "10":
            tester.test_10_check_search_suggestions()
        # elif choice == "11":
        #     tester.test_11_install_app()
        elif choice == "12":
            tester.test_12_uninstall_app()
        elif choice == "0":
            tester.export_results()
            break
        else:
            print("Invalid choice. Please enter a number from 0 to 12.")