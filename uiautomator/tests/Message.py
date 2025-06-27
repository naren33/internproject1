import subprocess
import time
import csv
import xml.etree.ElementTree as ET
import re
from datetime import datetime

RESULT_FILE = "result.csv"
LOG_FILE = "sms_log.txt"

def setup_csv():
    with open(RESULT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Test Case ID", "Description", "Phone Number", "Message", "Status", "Output", "Timestamp"])

def log_result(test_id, desc, number, message, status, output):
    with open(RESULT_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            test_id, desc, number, message,
            status, output,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

def run_adb(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip(), result.stderr.strip()

def click_send_button():
    subprocess.run(["adb", "shell", "uiautomator", "dump"], stdout=subprocess.DEVNULL)
    subprocess.run(["adb", "pull", "/sdcard/window_dump.xml"], stdout=subprocess.DEVNULL)
    try:
        tree = ET.parse("window_dump.xml")
        root = tree.getroot()
        for node in root.iter("node"):
            res_id = node.attrib.get("resource-id", "").lower()
            text = node.attrib.get("text", "").lower()
            if "send" in res_id or text == "send":
                bounds = node.attrib.get("bounds")
                coords = re.findall(r"\d+", bounds)
                if len(coords) == 4:
                    x1, y1, x2, y2 = map(int, coords)
                    x = (x1 + x2) // 2
                    y = (y1 + y2) // 2
                    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
                    return True
        return False
    except Exception:
        return False

def is_valid_number(number):
    return re.fullmatch(r"[6-9]\d{9}", number.strip()) is not None

def send_sms(phone_number, message, test_id, desc):
    phone_number = phone_number.strip()
    message = message.strip()

    if not is_valid_number(phone_number):
        log_result(test_id, desc, phone_number, message, "Fail", "Invalid phone number format")
        print(f"[❌] Invalid phone number: {phone_number}")
        return

    if message == "":
        log_result(test_id, desc, phone_number, message, "Fail", "Empty message not allowed")
        print(f"[❌] Cannot send empty message to {phone_number}")
        return
    
    command = [
        "adb", "shell", "am", "start",
        "-a", "android.intent.action.SENDTO",
        "-d", f"sms:{phone_number}",
        "--es", "sms_body", f"'{message}'", 
        "--ez", "exit_on_sent", "true"
    ]
    out, err = run_adb(command)
    time.sleep(5)
    success = click_send_button()

    if not success:
        print("[!] Retrying click on send button...")
        time.sleep(5)
        success = click_send_button()

    status = "Pass" if success else "Fail"
    output_msg = out if out else err
    log_result(test_id, desc, phone_number, message, status, output_msg)
    print(f"[{status}] Message {'sent to ' + phone_number if success else 'not sent'}")

def toggle_network(state):
    if state == "off":
        subprocess.run(["adb", "shell", "settings", "put", "global", "airplane_mode_on", "1"])
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"])
    elif state == "on":
        subprocess.run(["adb", "shell", "settings", "put", "global", "airplane_mode_on", "0"])
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false"])
    time.sleep(2)

def save_logcat():
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        subprocess.run("adb logcat -d", shell=True, stdout=f)
    print("[✔] Logcat saved to sms_log.txt")

def open_messages_and_search(contact):
    print("[📲] Launching Messages app...")
    subprocess.run(["adb", "shell", "am", "start", "-n", "com.google.android.apps.messaging/.ui.ConversationListActivity"])
    time.sleep(2)
    subprocess.run(["adb", "shell", "input", "keyevent", "84"])
    time.sleep(1)
    subprocess.run(["adb", "shell", "input", "text", contact])
    time.sleep(2)
    subprocess.run(["adb", "shell", "input", "keyevent", "66"])
    time.sleep(2)

def scroll_up():
    subprocess.run(["adb", "shell", "input", "swipe", "500", "500", "500", "1600"])

def scroll_down():
    subprocess.run(["adb", "shell", "input", "swipe", "500", "1600", "500", "500"])

def wait_for_device():
    print("[🔄] Waiting for device to be ready...")
    while True:
        result = subprocess.run(["adb", "shell", "getprop", "sys.boot_completed"], capture_output=True, text=True)
        if result.stdout.strip() == "1":
            print("[✅] Device boot completed.")
            break
        time.sleep(2)

# ----------- Test Cases ----------- #

def test_valid_number():
    number = input("Enter valid number: ")
    message = input("Enter message: ")
    send_sms(number, message, "TC01", "Send message to valid number")

def test_invalid_number():
    number = input("Enter invalid number: ")
    message = input("Enter message: ")
    send_sms(number, message, "TC02", "Send message to invalid number")

def test_empty_message():
    number = input("Enter number: ")
    send_sms(number, "", "TC03", "Send empty message")

def test_long_message():
    number = input("Enter number: ")
    message = input("Enter your message: ")
    if len(message) > 480:
        print(f"[❌] Message length = {len(message)}. Limit is 480. Message not sent.")
        log_result("TC04", "Send long message", number, message, "Fail", f"Message too long ({len(message)} characters)")
    else:
        send_sms(number, message, "TC04", "Send long message")

def test_special_characters():
    number = input("Enter number: ")
    message = input("Enter message with special characters: ")
    send_sms(number, message, "TC05", "Send message with special characters")

def test_multiple_recipients():
    numbers = input("Enter comma-separated numbers: ").split(',')
    message = input("Enter message: ")
    for idx, num in enumerate(numbers):
        send_sms(num.strip(), message, f"TC06_{idx+1}", "Send message to multiple recipients")

def test_network_off():
    number = input("Enter number: ")
    message = input("Enter message: ")
    toggle_network("off")
    send_sms(number, message, "TC07", "Send message with network OFF")
    toggle_network("on")

def test_without_wifi():
    number = input("Enter number: ")
    message = input("Enter message: ")
    print("[!] Disabling mobile data and Wi-Fi...")
    subprocess.run(["adb", "shell", "svc", "data", "disable"])
    subprocess.run(["adb", "shell", "svc", "wifi", "disable"])
    time.sleep(3)
    send_sms(number, message, "TC08", "Send SMS without SIM or active network")
    input("[!] Enable data/Wi-Fi manually and press Enter...")

def test_emoji_only():
    number = input("Enter number: ")
    message = "😂❤️🔥🙏✨"
    send_sms(number, message, "TC09", "Send SMS with only emojis")

def test_combo_emoji_text_special():
    number = input("Enter number: ")
    message = input("Enter message (emoji + text + special characters): ")
    send_sms(number, message, "TC10", "Send SMS with emoji, text, and special characters")

def test_after_reboot():
    number = input("Enter number: ")
    message = input("Enter message: ")
    print("[⚠] Rebooting device now...")
    subprocess.run(["adb", "reboot"])
    print("Waiting for device to reboot...")
    wait_for_device()
    time.sleep(10)
    print("[📲] Re-opening Messages app after reboot...")
    subprocess.run(["adb", "shell", "am", "start", "-n", "com.google.android.apps.messaging/.ui.ConversationListActivity"])
    time.sleep(20)
    send_sms(number, message, "TC11", "Send SMS after reboot")

def test_while_heavy_app_running():
    number = input("Enter number: ")
    message = input("Enter message: ")
    print("[📱] Launching YouTube as heavy app...")
    subprocess.run(["adb", "shell", "monkey", "-p", "com.google.android.youtube", "-c", "android.intent.category.LAUNCHER", "1"])
    time.sleep(10)
    send_sms(number, message, "TC12", "Send SMS while heavy app is running")

def test_scroll_older():
    contact = input("Enter contact name or number: ")
    open_messages_and_search(contact)
    print("Scrolling up to older messages...")
    for _ in range(3):
        scroll_up()
        time.sleep(1)

def test_scroll_newer():
    contact = input("Enter contact name or number: ")
    open_messages_and_search(contact)
    print("Scrolling down to newer messages...")
    for _ in range(3):
        scroll_down()
        time.sleep(1)

def test_search_contact():
    contact = input("Enter contact name or number: ")
    open_messages_and_search(contact)


def test_battery_saver_on():
    number = input("Enter number: ")
    message = "Test SMS with Battery Saver mode ON."
    print("[⚡] Enabling battery saver...")
    subprocess.run(["adb", "shell", "settings", "put", "global", "low_power", "1"])
    time.sleep(2)
    send_sms(number, message, "TC17", "Send SMS with Battery Saver mode ON")
    subprocess.run(["adb", "shell", "settings", "put", "global", "low_power", "0"])  # Reset


def test_spam_same_number():
    number = input("Enter number: ")
    message = "Spam message"
    for i in range(5):
        send_sms(number, f"{message} #{i+1}", f"TC39_{i+1}", "Send repeated messages to same number")
        time.sleep(1)

def test_url():
    number = input("Enter number: ")
    url = "https://www.openai.com"
    message = f"Check this out: {url}"
    send_sms(number, message, "TC19", "Send SMS with URL and test auto-link behavior")


def All():
    test_valid_number()
    test_invalid_number()
    test_empty_message()
    test_long_message()
    test_special_characters()
    test_multiple_recipients()
    test_network_off()
    save_logcat()
    test_without_wifi()
    test_emoji_only()
    test_combo_emoji_text_special()
    test_after_reboot()
    test_while_heavy_app_running()
    test_scroll_older()
    test_scroll_newer()
    test_search_contact()
    test_battery_saver_on()
    test_spam_same_number()
    test_url()


# ----------- Main Menu ----------- #

def main():
    setup_csv()
    
    while True:
        print("\n----- Message Module Test Menu -----")
        choice = input("Enter your choice: ")
        print("1. Send message to valid number")
        print("2. Send message to invalid number")
        print("3. Send empty message")
        print("4. Send long message")
        print("5. Send message with special characters")
        print("6. Send message to multiple recipients")
        print("7. Send message on Aeroplane Mode")
        print("8. Save logcat")
        print("9. Send SMS without network")
        print("10. Send SMS with only emojis")
        print("11. Send SMS with emojis + text + special chars")
        print("12. Reboot device and send SMS")
        print("13. Send SMS while heavy app running")
        print("14. Scroll to older messages")
        print("15. Scroll to newer messages")
        print("16. Search & open contact chat")
        print("17. Send Message while battery saver is on")
        print("18. send spam msg")
        print("19. msg with url")
        print("20.Exit..")

        if choice == "1":
            test_valid_number()
        elif choice == "2":
            test_invalid_number()
        elif choice == "3":
            test_empty_message()
        elif choice == "4":
            test_long_message()
        elif choice == "5":
            test_special_characters()
        elif choice == "6":
            test_multiple_recipients()
        elif choice == "7":
            test_network_off()
        elif choice == "8":
            save_logcat()
        elif choice == "9":
            test_without_wifi()
        elif choice == "10":
            test_emoji_only()
        elif choice == "11":
            test_combo_emoji_text_special()
        elif choice == "12":
            test_after_reboot()
        elif choice == "13":
            test_while_heavy_app_running()
        elif choice == "14":
            test_scroll_older()
        elif choice == "15":
            test_scroll_newer()
        elif choice == "16":
            test_search_contact()
        elif choice == "17":
            test_battery_saver_on()
        elif choice == "18":
            test_spam_same_number()
        elif choice == "19":
            test_url()
            
        elif choice == "20":
            print("Exiting test menu.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
