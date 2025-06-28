import os
import time
import logging
import subprocess
import pytest
from time import sleep

# --------------------------------------
# Logger Setup
# --------------------------------------
def setup_logger(name="audio_test", log_file="audio_test.log", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler always works
    f_handler = logging.FileHandler(log_file)
    f_handler.setLevel(logging.DEBUG)
    
    # Console handler with error handling
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    return logger

log = setup_logger()

# --------------------------------------
# ADB Utility Functions with improvements
# --------------------------------------
def run_adb_command(command, timeout=15):
    """Run ADB command with better error handling and timeout"""
    try:
        # Ensure adb is in the command
        full_cmd = ["adb"] + command if command[0] != "adb" else command
        result = subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr.strip() else "Unknown error"
            return f"ERROR: {error_msg}"
        return result.stdout.strip() if result.stdout.strip() else "SUCCESS"
    except subprocess.TimeoutExpired:
        return "ERROR: ADB command timed out"
    except Exception as e:
        return f"ERROR: {str(e)}"

def clear_logcat():
    run_adb_command(["logcat", "-c"])

def capture_logcat(test_name):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{test_name}_logcat_{timestamp}.txt"
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", filename)
    with open(log_path, "w", encoding="utf-8") as f:
        subprocess.run(["adb", "logcat", "-d"], stdout=f, text=True)
    return log_path

def log_and_run(description, command, expected=None, retries=2, timeout=15):
    """Run command with logging and optional retries"""
    for attempt in range(retries + 1):
        try:
            log.info(f"\n[STEP] {description}")
            log.info(f"[COMMAND] {' '.join(command)}")
            
            output = run_adb_command(command, timeout=timeout)
            log.info(f"[OUTPUT] {output}")
            
            if output.startswith("ERROR"):
                if attempt < retries:
                    sleep(2)  # Wait before retry
                    continue
                pytest.fail(output)
            
            if expected and expected not in output:
                pytest.fail(f"Expected '{expected}' not found in output")
                
            return output
            
        except Exception as e:
            if attempt == retries:
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
    log_path = capture_logcat(request.node.name)
    log.info(f"Logcat saved to: {log_path}")
    log.info(f"[TEST END] {request.node.name}\n")

# --------------------------------------
# Test Class with improved test cases
# --------------------------------------
class TestAudioModule:
    @pytest.mark.skip(reason="Requires INJECT_EVENTS permission - needs root")
    def test_adjust_volume_buttons(self):
        """Test volume buttons - requires special permissions"""
        log_and_run("Increase volume", ["shell", "input", "keyevent", "KEYCODE_VOLUME_UP"])
        log_and_run("Decrease volume", ["shell", "input", "keyevent", "KEYCODE_VOLUME_DOWN"])

    def test_pause_on_incoming_call(self):
        """Test media pause during call"""
        # First check if we have CALL_PHONE permission
        perm_check = log_and_run("Check CALL_PHONE permission", 
                               ["shell", "dumpsys", "package", "com.android.shell"], 
                               expected="android.permission.CALL_PHONE: granted=true")
        
        if "granted=true" not in perm_check:
            pytest.skip("CALL_PHONE permission not granted to shell")
            
        log_and_run("Play media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/sample.mp3", "-t", "audio/*"
        ])
        sleep(2)
        log_and_run("Simulate call", [
            "shell", "am", "start", "-a", "android.intent.action.CALL",
            "-d", "tel:1234567890"
        ])

    def test_audio_routing_headset_unplug(self):
        """Test audio routing information"""
        output = log_and_run("Check audio route", ["shell", "dumpsys", "audio"])
        assert "Devices:" in output, "Audio devices information not found"

    def test_bluetooth_audio_routing(self):
        """Test Bluetooth audio routing"""
        # First check if Bluetooth is supported
        bt_check = log_and_run("Check Bluetooth support", ["shell", "cmd", "bluetooth_manager", "isEnabled"])
        if "true" not in bt_check.lower():
            log_and_run("Enable Bluetooth", ["shell", "svc", "bluetooth", "enable"])
            sleep(3)  # Wait for BT to enable
        
        output = log_and_run("Check BT audio state", ["shell", "dumpsys", "audio"])
        assert "BT" in output or "Bluetooth" in output, "Bluetooth audio info not found"

    @pytest.mark.skip(reason="Requires INJECT_EVENTS permission - needs root")
    def test_playback_screen_off(self):
        """Test playback with screen off"""
        log_and_run("Start media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/sample.mp3", "-t", "audio/*"
        ])
        sleep(2)
        log_and_run("Turn off screen", ["shell", "input", "keyevent", "26"])

    def test_voice_recording_playback(self):
        """Test voice recording (manual verification)"""
        log_and_run("Launch Voice Recorder", [
            "shell", "am", "start", "-a", "android.provider.MediaStore.RECORD_SOUND"
        ])

    def test_notification_over_audio(self):
        """Test notification during playback"""
        log_and_run("Play media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/sample.mp3", "-t", "audio/*"
        ])
        sleep(2)
        # Use standard notification command that should work on most devices
        log_and_run("Trigger notification", [
            "shell", "cmd", "notification", "post", "test_channel", "Test", "This is a test notification"
        ])

    @pytest.mark.skip(reason="Media command not available on all devices")
    def test_mute_functionality(self):
        """Test mute functionality"""
        log_and_run("Mute media", [
            "shell", "media", "volume", "--stream", "3", "--set", "0"
        ])

    def test_audio_focus_conflict(self):
        """Test audio focus between apps"""
        log_and_run("Simulate App A playing media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/app_a.mp3", "-t", "audio/*"
        ])
        sleep(2)
        log_and_run("Simulate App B playing media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/app_b.mp3", "-t", "audio/*"
        ])

    @pytest.mark.skip(reason="Reboot disrupts test sequence - run manually")
    def test_audio_after_reboot(self):
        """Test audio after device reboot"""
        log_and_run("Reboot device", ["reboot"])
        sleep(60)  # Wait for device to reboot
        log_and_run("Check audio service", ["shell", "dumpsys", "audio"])

    def test_check_alarm_in_silent_mode(self):
        """Test alarm in silent mode"""
        # First check if we have WRITE_SECURE_SETTINGS permission
        perm_check = log_and_run("Check WRITE_SECURE_SETTINGS permission", 
                               ["shell", "dumpsys", "package", "com.android.shell"], 
                               expected="android.permission.WRITE_SECURE_SETTINGS: granted=true")
        
        if "granted=true" not in perm_check:
            pytest.skip("WRITE_SECURE_SETTINGS permission not granted to shell")
            
        log_and_run("Enable DND", [
            "shell", "settings", "put", "global", "zen_mode", "1"
        ])
        log_and_run("Set alarm", [
            "shell", "am", "start", "-a", "android.intent.action.SET_ALARM",
            "--ei", "android.intent.extra.alarm.HOUR", "7",
            "--ei", "android.intent.extra.alarm.MINUTES", "30",
            "--ez", "android.intent.extra.alarm.SKIP_UI", "true"
        ])

    def test_check_bt_audio_route(self):
        """Test Bluetooth audio routing details"""
        output = log_and_run("Dump audio state", ["shell", "dumpsys", "audio"])
        assert "A2DP" in output or "Bluetooth" in output, "Bluetooth audio routing info not found"
        log_and_run("Dump BT manager", ["shell", "dumpsys", "bluetooth_manager"])

    def test_media_resume_after_call(self):
        """Test media resume after call ends"""
        # First check if we have CALL_PHONE permission
        perm_check = log_and_run("Check CALL_PHONE permission", 
                               ["shell", "dumpsys", "package", "com.android.shell"], 
                               expected="android.permission.CALL_PHONE: granted=true")
        
        if "granted=true" not in perm_check:
            pytest.skip("CALL_PHONE permission not granted to shell")
            
        log_and_run("Play media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/sample.mp3", "-t", "audio/*"
        ])
        sleep(2)
        log_and_run("Simulate call", [
            "shell", "am", "start", "-a", "android.intent.action.CALL",
            "-d", "tel:12345"
        ])
        sleep(2)
        log_and_run("End call", ["shell", "input", "keyevent", "KEYCODE_ENDCALL"])
        sleep(1)
        output = log_and_run("Check media state", ["shell", "dumpsys", "audio"])
        assert "playing" in output.lower(), "Media did not resume after call"

    def test_media_ducking(self):
        """Test audio ducking during notifications"""
        log_and_run("Play media", [
            "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", "file:///sdcard/Music/sample.mp3", "-t", "audio/*"
        ])
        sleep(2)
        # Use standard notification command that should work on most devices
        log_and_run("Trigger notification", [
            "shell", "cmd", "notification", "post", "test_channel", "Test", "This is a test notification"
        ])

    @pytest.mark.skip(reason="Requires INJECT_EVENTS permission - needs root")
    def test_media_resume_screen_on(self):
        """Test media resume when screen turns on"""
        log_and_run("Turn off screen", ["shell", "input", "keyevent", "26"])
        sleep(2)
        log_and_run("Turn on screen", ["shell", "input", "keyevent", "26"])
        sleep(1)
        output = log_and_run("Check media state", ["shell", "dumpsys", "audio"])
        assert "playing" in output.lower(), "Media did not resume after screen on"

# --------------------------------------
# Entry Point for CLI run
# --------------------------------------
if __name__ == "__main__":
    import sys
    pytest.main(["-v", sys.argv[0]])