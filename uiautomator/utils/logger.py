# utils/logger.py
import logging
import os

def setup_logger(log_file="bluetooth_test.log"):
    logger = logging.getLogger("BluetoothTestLogger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:  # Prevent duplicate handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler
        log_path = os.path.join(os.getcwd(), log_file)
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
