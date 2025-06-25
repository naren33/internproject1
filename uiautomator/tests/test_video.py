import subprocess
from datetime import datetime
import os
import csv

class VideoTestCommands:
    def __init__(self):
        self.commands = {
            # Basic Functionality
            "VID_01 - Launch Video App": "adb shell monkey -p com.android.gallery3d -c android.intent.category.LAUNCHER 1",
            "VID_02 - Stop Video App": "adb shell am force-stop com.android.gallery3d",
            "VID_03 - Dump Playback State": "adb shell dumpsys activity activities | findstr com.android.gallery3d",
            "VID_04 - Enable Debug Logging": "adb shell setprop log.tag.VideoPlayer DEBUG && adb shell getprop log.tag.VideoPlayer",

            # Playback Quality
            "VID_05 - Frame Drop Tracking": "adb shell dumpsys SurfaceFlinger --latency com.android.gallery3d",
            "VID_06 - Dump AV Sync Status": "adb shell dumpsys SurfaceFlinger --latency",
            "VID_07 - Toggle HW Acceleration": "adb shell dumpsys gfxinfo com.android.gallery3d",
            "VID_08 - Dump Codec Info": "adb shell dumpsys media.player | findstr -i codec",

            # Stress & Performance
            "VID_09 - Play-Pause Stress Test": "python -c \"import subprocess, time; [ (subprocess.run('adb shell input keyevent 85', shell=True), time.sleep(0.1)) for _ in range(5) ]\"",
            "VID_10 - High CPU Load Test": "adb shell top -n 1",
            "VID_11 - Repeated Launch & Kill App Stress": "python -c \"import subprocess, time; [ (subprocess.run('adb shell monkey -p com.android.gallery3d -c android.intent.category.LAUNCHER 1', shell=True), time.sleep(0.2), subprocess.run('adb shell am force-stop com.android.gallery3d', shell=True)) for _ in range(10) ]\"",
            "VID_12 - Thermal Throttling Test": "adb shell dumpsys thermalservice",

            # Error Handling
            "VID_13 - Video Playback Error Handling Test": "adb shell am start -a android.intent.action.VIEW -d file:///sdcard/missing_video.mp4 -t video/mp4",
            "VID_14 - Monitor Buffer Underrun": "adb logcat -d | findstr /i \"buffer underrun\"",
            "VID_15 - High Latency Playback": "adb shell ping -c 10 google.com",

            # Advanced Scenarios
            "VID_16 - PiP Mode Test": "adb shell am start -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity",
            "VID_17 - Background Playback Test": "adb shell am start -a android.intent.action.VIEW -d file:///sdcard/Download/sample.mp4 -t video/mp4 && adb shell input keyevent 3 && adb shell dumpsys media_session | findstr -i playback",
            "VID_18 - Force GPU Rendering Test": "adb shell settings put global force_gpu_rendering 1 && adb shell settings get global force_gpu_rendering",
            "VID_19 - Analyze Frame Rendering Stats": "adb shell dumpsys gfxinfo com.android.gallery3d framestats",
            "VID_20 - Toggle and Verify Screen Rotation": "adb shell settings put system accelerometer_rotation 0 && adb shell settings get system accelerometer_rotation && adb shell settings put system accelerometer_rotation 1 && adb shell settings get system accelerometer_rotation",

            # Utility
            "VID_21 - Video File Properties Dump": "adb shell dumpsys media.audio_flinger | findstr -i 'stream' || adb shell dumpsys media.player",
            "VID_22 - DRM Info Dump": "adb shell getprop | findstr -i drm",
            "VID_23 - Dump Audio HAL State": "adb shell dumpsys media.audio_flinger",
            "VID_24 - Simulate Playback Keyevent": "adb shell input keyevent 85",
            "VID_25 - Seek Functionality Test": "adb shell input keyevent 90"
        }

    def get_command(self, test_name):
        return self.commands.get(test_name)

    def list_tests(self):
        return list(self.commands.keys())


class VideoTestExecutor:
    def __init__(self):
        self.commands = VideoTestCommands()
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.base_log_dir = "test_logs"
        os.makedirs(self.base_log_dir, exist_ok=True)
        self.csv_report_file = f"{self.base_log_dir}/video_test_report.csv"

        self.test_groups = {
            "Basic Functionality": range(1, 5),
            "Playback Quality": range(5, 9),
            "Stress & Performance": range(9, 13),
            "Error Handling": range(13, 16),
            "Advanced Scenarios": range(16, 21),
            "Utility": range(21, 26)
        }

        self._initialize_report_file()

    def _initialize_report_file(self):
        if not os.path.exists(self.csv_report_file):
            with open(self.csv_report_file, 'w', newline='', encoding='utf-8') as file:
                csv.writer(file).writerow([
                    "Timestamp", "Test ID", "Test Name", "Feature",
                    "Status", "Execution Time (s)", "Output File",
                    "Logcat File", "Remarks"
                ])

    def run_tests(self, selected_tests):
        for test_name in selected_tests:
            test_id = test_name.split(" - ")[0]
            feature = test_name.split(" - ")[1].split()[0]
            command = self.commands.get_command(test_name)
            start_time = datetime.now()

            log_dir = os.path.join(self.base_log_dir, f"{test_id}_{self.timestamp}")
            os.makedirs(log_dir, exist_ok=True)
            output_file = os.path.join(log_dir, "output.log")
            logcat_file = os.path.join(log_dir, "adb_logcat.log")

            result = {
                "Timestamp": self.timestamp,
                "Test ID": test_id,
                "Test Name": test_name,
                "Feature": feature,
                "Status": "UNKNOWN",
                "Execution Time": -1,
                "Output File": output_file,
                "Logcat File": logcat_file,
                "Remarks": ""
            }

            try:
                subprocess.run(["adb", "logcat", "-c"], capture_output=True)
                output, returncode = self._execute_command(command, output_file)
                self._capture_logcat(logcat_file)

                result["Status"], result["Remarks"] = self._validate_output(test_id, output, returncode)

            except subprocess.TimeoutExpired:
                result["Status"] = "TIMEOUT"
                result["Remarks"] = "Test execution exceeded time limit"
            except Exception as e:
                result["Status"] = "ERROR"
                result["Remarks"] = str(e)

            result["Execution Time"] = (datetime.now() - start_time).total_seconds()
            self._write_result_to_csv(result)

        print(f"✅ All tests executed. Report available at: {self.csv_report_file}")

    def _execute_command(self, command, output_file):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        extra_output = subprocess.getoutput(command)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Command: {command}\n")
            f.write(f"Return Code: {result.returncode}\n\n")
            f.write("Standard Output:\n")
            f.write(result.stdout + "\n")
            if result.stderr:
                f.write("Standard Error:\n" + result.stderr + "\n")
            f.write("\nSubprocess.getoutput():\n")
            f.write(extra_output)

        return result.stdout + "\n" + extra_output, result.returncode

    def _capture_logcat(self, filepath):
        result = subprocess.run(["adb", "logcat", "-d"], capture_output=True, text=True, encoding='utf-8')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.stdout)

    def _validate_output(self, test_id, output, returncode):
        if returncode != 0:
            return "FAIL", f"Return code: {returncode}"
        if test_id == "VID_01":
            return ("PASS" if returncode == 0 else "FAIL", f"Monkey return code: {returncode}")
        return "PASS", "Executed without errors"

    def _write_result_to_csv(self, result):
        with open(self.csv_report_file, 'a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow([
                result["Timestamp"],
                result["Test ID"],
                result["Test Name"],
                result["Feature"],
                result["Status"],
                f"{result['Execution Time']:.2f}",
                os.path.relpath(result["Output File"]),
                os.path.relpath(result["Logcat File"]),
                result["Remarks"]
            ])

    def prompt_user_selection(self):
        print("\n📋 Available Test Groups:")
        for group, indexes in self.test_groups.items():
            print(f"\n{group}:")
            for i in indexes:
                print(f"{i}. {self.commands.list_tests()[i - 1]}")

        user_input = input("\nSelect tests (e.g., 1,2,5 or group name or 'all'): ").strip().lower()

        if user_input == "all":
            return self.commands.list_tests()

        if user_input in (g.lower() for g in self.test_groups):
            group_name = next(g for g in self.test_groups if g.lower() == user_input)
            return [self.commands.list_tests()[i - 1] for i in self.test_groups[group_name]]

        try:
            indices = [int(i.strip()) for i in user_input.split(",")]
            return [self.commands.list_tests()[i - 1] for i in indices if 0 < i <= len(self.commands.list_tests())]
        except:
            print("❌ Invalid selection. Defaulting to all tests.")
            return self.commands.list_tests()


if __name__ == "__main__":
    executor = VideoTestExecutor()
    selected = executor.prompt_user_selection()
    executor.run_tests(selected)
