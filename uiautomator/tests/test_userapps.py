import subprocess
import datetime
import os

log_process = None  # global handle for adb logcat process
LOG_DIR = r"C:\Users\user\project1\logs"

def start_adb_log():
    global log_process
    # If already logging, stop previous
    if log_process and log_process.poll() is None:
        log_process.terminate()
        log_process.wait()

    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = os.path.join(LOG_DIR, f"adb_log_{timestamp}.txt")

    # Open file for writing adb logs
    log_file = open(log_file_path, "w", encoding="utf-8")

    # Start adb logcat process, redirect output to file
    log_process = subprocess.Popen(
        ["adb", "logcat"],
        stdout=log_file,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    print(f"📥 Started adb logging to {log_file_path}")

def stop_adb_log():
    global log_process
    if log_process and log_process.poll() is None:
        log_process.terminate()
        log_process.wait()
        log_process = None
        print("📴 Stopped adb logging.")

def launch_app(package_name, main_activity):
    try:
        full_activity = f"{package_name}/{main_activity}"
        result = subprocess.run(
            ["adb", "shell", "am", "start", "-n", full_activity],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if "Error" in result.stderr or "Exception" in result.stderr:
            print(f"❌ Failed to launch app: {result.stderr.strip()}")
        else:
            print(f"✅ App launched successfully: {package_name}")
            print(result.stdout.strip())
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def is_app_installed(package_name):
    try:
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages", package_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return package_name in result.stdout
    except Exception as e:
        print(f"❌ Error checking package: {e}")
        return False

def uninstall_app(package_name):
    try:
        result = subprocess.run(
            ["adb", "uninstall", package_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if "Success" in result.stdout:
            print(f"✅ App '{package_name}' uninstalled successfully.")
        else:
            print(f"❌ Failed to uninstall app: {result.stdout.strip()} {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Exception while uninstalling: {e}")

def grant_permission(package_name, permission):
    try:
        if not is_app_installed(package_name):
            print(f"❌ App '{package_name}' is not installed on the device.")
            return

        grant_result = subprocess.run(
            ["adb", "shell", "pm", "grant", package_name, permission],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if grant_result.stderr.strip():
            print(f"❌ Failed to grant permission: {grant_result.stderr.strip()}")
        else:
            print(f"✅ Permission '{permission}' granted to '{package_name}'.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def get_battery_info():
    try:
        result = subprocess.run(
            ["adb", "shell", "dumpsys", "battery"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stderr:
            print(f"❌ Error retrieving battery info: {result.stderr.strip()}")
            return

        battery_data = result.stdout.strip().splitlines()
        info = {}

        for line in battery_data:
            line = line.strip()
            if line.startswith("level:"):
                info["Level"] = line.split(":")[-1].strip()
            elif line.startswith("status:"):
                info["Status"] = line.split(":")[-1].strip()
            elif line.startswith("AC powered:"):
                info["AC Powered"] = line.split(":")[-1].strip()
            elif line.startswith("USB powered:"):
                info["USB Powered"] = line.split(":")[-1].strip()
            elif line.startswith("Wireless powered:"):
                info["Wireless Powered"] = line.split(":")[-1].strip()
            elif line.startswith("temperature:"):
                info["Temperature (°C)"] = str(int(line.split(":")[-1].strip()) / 10)

        print("🔋 Battery Information:")
        for key, value in info.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def call_notification_service():
    try:
        result = subprocess.run(
            ["adb", "shell", "service", "call", "notification", "1"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stderr.strip():
            print(f"❌ Error calling notification service: {result.stderr.strip()}")
        else:
            print(f"📡 Notification service call result:\n{result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def force_stop_app(package_name):
    try:
        if not is_app_installed(package_name):
            print(f"❌ App '{package_name}' is not installed on the device.")
            return

        stop_result = subprocess.run(
            ["adb", "shell", "am", "force-stop", package_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if stop_result.stderr.strip():
            print(f"❌ Error force-stopping app: {stop_result.stderr.strip()}")
        else:
            print(f"✅ App '{package_name}' force-stopped successfully.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def get_storage_info():
    try:
        result = subprocess.run(
            ["adb", "shell", "df", "-h"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stderr.strip():
            print(f"❌ Error fetching storage info: {result.stderr.strip()}")
            return
        print("📦 Device Storage Usage (df -h):\n")
        print(result.stdout)
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def list_installed_packages():
    try:
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stderr.strip():
            print(f"❌ Error listing packages: {result.stderr.strip()}")
            return
        packages = [line.replace("package:", "").strip() for line in result.stdout.splitlines()]
        print("📱 Installed App Packages:")
        for pkg in packages:
            print(f"- {pkg}")
        print(f"\n🔢 Total Packages: {len(packages)}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def send_enter_key():
    try:
        result = subprocess.run(
            ["adb", "shell", "input", "keyevent", "66"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stderr.strip():
            print(f"❌ Error sending keyevent: {result.stderr.strip()}")
        else:
            print("✅ ENTER keyevent (KEYCODE 66) sent successfully.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

def main():
    while True:
        print("\nADB Control Script - Choose an option:")
        print("1. Launch App")
        print("2. Check if App Installed")
        print("3. Uninstall App")
        print("4. Grant Permission")
        print("5. Get Battery Info")
        print("6. Call Notification Service")
        print("7. Force Stop App")
        print("8. Get Storage Info")
        print("9. List Installed Packages")
        print("10. Send ENTER Key")
        print("11. Stop adb log capture")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            start_adb_log()  # start adb logging when launching app
            pkg = input("Enter package name (e.g. com.whatsapp): ").strip()
            act = input("Enter main activity (e.g. com.whatsapp.Main): ").strip()
            launch_app(pkg, act)
            stop_adb_log()
        elif choice == "2":
            start_adb_log()  # start adb logging when launching app
            pkg = input("Enter package name: ").strip()
            installed = is_app_installed(pkg)
            print(f"App '{pkg}' installed: {installed}")
            stop_adb_log()
        elif choice == "3":
            start_adb_log()  # start adb logging when launching app
            pkg = input("Enter package name to uninstall: ").strip()
            uninstall_app(pkg)
            stop_adb_log()
        elif choice == "4":
            start_adb_log()  # start adb logging when launching app
            pkg = input("Enter package name: ").strip()
            perm = input("Enter permission (e.g. android.permission.CAMERA): ").strip()
            grant_permission(pkg, perm)
            stop_adb_log()
        elif choice == "5":
            start_adb_log()  # start adb logging when launching app
            get_battery_info()
            stop_adb_log()
        elif choice == "6":
            start_adb_log()  # start adb logging when launching app
            call_notification_service()
            stop_adb_log()
        elif choice == "7":
            start_adb_log()  # start adb logging when launching app
            pkg = input("Enter package name to force stop: ").strip()
            force_stop_app(pkg)
            stop_adb_log()
        elif choice == "8":
            start_adb_log()  # start adb logging when launching app
            get_storage_info()
            stop_adb_log()
        elif choice == "9":
            start_adb_log()  # start adb logging when launching app
            list_installed_packages()
            stop_adb_log()
        elif choice == "10":
            start_adb_log()  # start adb logging when launching app
            send_enter_key()
            stop_adb_log()
        elif choice == "11":
            stop_adb_log()
        elif choice == "0":
            print("Exiting.")
            stop_adb_log()
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":1
main()
