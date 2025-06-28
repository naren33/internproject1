# utils/device_connector.py

import subprocess

def get_connected_devices():
    """
    Returns a list of connected device IDs via adb.
    """
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()

        # Skip first line "List of devices attached"
        devices = [line.split()[0] for line in lines[1:] if 'device' in line]
        return devices
    except Exception as e:
        print(f"[Device Check Error] {e}")
        return []

def is_device_connected():
    """
    Checks if at least one device is connected.
    """
    devices = get_connected_devices()
    return len(devices) > 0

def wait_for_device(timeout=30):
    """
    Wait for a device to be connected within a timeout period.
    """
    import time
    start = time.time()
    while time.time() - start < timeout:
        if is_device_connected():
            print("[Device Connected]")
            return True
        print("Waiting for device...")
        time.sleep(2)
    print("[Timeout] No device detected.")
    return False
