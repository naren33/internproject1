import sys
import os
import traceback
import io
import contextlib
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QTextEdit, QCheckBox, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont

from utils.mongo_helper import fetch_modules
from utils.test_parser import fetch_testcases
from utils import logger

log = logger.setup_logger()


class ReportWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, module_name, test_case_name, method, email, notify):
        super().__init__()
        self.module_name = module_name
        self.test_case_name = test_case_name
        self.method = method
        self.email = email
        self.notify = notify

    @pyqtSlot()
    def run(self):
        buffer = io.StringIO()
        stream_handler = logging.StreamHandler(buffer)
        stream_handler.setFormatter(logging.Formatter('%(message)s'))
        log.addHandler(stream_handler)

        try:
            try:
                mod = __import__(f"tests.{self.module_name}", fromlist=[""])
            except ImportError:
                raise ImportError(f"Module 'tests.{self.module_name}' not found.")

            test_func = None
            if hasattr(mod, self.test_case_name):
                test_func = getattr(mod, self.test_case_name)
            else:
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if isinstance(attr, type) and hasattr(attr, self.test_case_name):
                        instance = attr()
                        test_func = getattr(instance, self.test_case_name)
                        break

            if test_func is None or not callable(test_func):
                raise AttributeError(f"Test case '{self.test_case_name}' not found in module '{self.module_name}'.")

            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                test_func()

            output = buffer.getvalue()
            result = f"""
[Module]        {self.module_name}
[Test Case]     {self.test_case_name}
[Method]        {self.method}
[Email]         {self.email}
[Notify]        {', '.join(self.notify) if self.notify else 'None'}

✅ Output:
{output.strip()}
            """
        except Exception:
            result = f"""
[Module]        {self.module_name}
[Test Case]     {self.test_case_name}
❌ Error:
{traceback.format_exc()}
            """
        finally:
            log.removeHandler(stream_handler)
            buffer.close()

        self.finished.emit(result.strip())


class StunningUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stunning UI Automator")
        self.setMinimumSize(1400, 800)
        self.dark_mode = False
        self.applyLightTheme()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(15)

        logo = QLabel("✨ ThunderSoft")
        logo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo.setStyleSheet("color: #1d4ed8; padding: 30px; letter-spacing: 2px;")
        sidebar_layout.addWidget(logo)

        sidebar_layout.addStretch()
        theme_btn = QPushButton("🌗 Toggle Theme")
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.clicked.connect(self.toggleTheme)
        theme_btn.setStyleSheet("padding: 12px; border-radius: 8px; font-weight: bold;")
        sidebar_layout.addWidget(theme_btn)

        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("SidebarFrame")
        sidebar_frame.setLayout(sidebar_layout)
        sidebar_frame.setFixedWidth(450)

        config_report_layout = QHBoxLayout()
        config_widget = QWidget()
        config_layout = QFormLayout()
        config_layout.setSpacing(20)
        font = QFont("Segoe UI", 14)

        self.module = QComboBox()
        self.module.setEditable(False)
        self.module.setFont(font)
        modules = fetch_modules()
        self.module.addItems(modules if modules else ["No modules found"])

        self.testcase = QComboBox()
        self.testcase.setEditable(False)
        self.testcase.setFont(font)
        self.module.currentTextChanged.connect(self.update_testcases)
        self.update_testcases(self.module.currentText())
        self.testcase.setFixedWidth(400)

        self.method = QComboBox()
        self.method.setEditable(False)
        self.method.addItems(["Default", "Randomized"])
        self.method.setFont(font)
        self.method.setCurrentIndex(0)
        self.method.model().item(1).setEnabled(False)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Enter your email")
        self.email.setFont(font)

        self.pre = QCheckBox("Notify PRE")
        self.post = QCheckBox("Notify POST")
        self.pre.setFont(font)
        self.post.setFont(font)

        notif_layout = QHBoxLayout()
        notif_layout.addWidget(self.pre)
        notif_layout.addWidget(self.post)

        self.btn = QPushButton("🚀 Launch Test")
        self.btn.clicked.connect(self.generateReport)
        self.btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn.setFixedHeight(40)

        label_font = QFont("Segoe UI", 14, QFont.Bold)

        config_layout.addRow(self.makeLabel("Module:", label_font), self.module)
        config_layout.addRow(self.makeLabel("Test Case:", label_font), self.testcase)
        config_layout.addRow(self.makeLabel("Method:", label_font), self.method)
        config_layout.addRow(self.makeLabel("Email:", label_font), self.email)
        config_layout.addRow(self.makeLabel("Job Trigger Notifications:", label_font), notif_layout)
        config_layout.addRow("", self.btn)

        config_widget.setLayout(config_layout)

        report_widget = QWidget()
        report_layout = QVBoxLayout()
        self.report_output = QTextEdit()
        self.report_output.setPlaceholderText("📝 Report console will appear here...")
        self.report_output.setFont(QFont("Fira Code", 11))
        report_layout.addWidget(self.report_output)
        report_widget.setLayout(report_layout)

        config_report_layout.addWidget(config_widget)
        config_report_layout.addWidget(report_widget)

        main_layout.addWidget(sidebar_frame)
        main_layout.addLayout(config_report_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def makeLabel(self, text, font):
        label = QLabel(text)
        label.setFont(font)
        label.setStyleSheet("background-color: transparent;")
        return label

    def update_testcases(self, module_name):
        self.testcase.clear()
        cases = fetch_testcases(module_name)
        if cases:
            self.testcase.addItems(cases)
            for i, case in enumerate(cases):
                self.testcase.setItemData(i, case, Qt.ToolTipRole)
        else:
            self.testcase.addItem("No test cases found")

    def toggleTheme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.applyDarkTheme()
        else:
            self.applyLightTheme()

    def applyDarkTheme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            #SidebarFrame { background-color: #1e293b; }
            QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit {
                color: #ffffff; background-color: #1e293b;
            }
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #374151; border-radius: 6px; padding: 6px;
            }
            QPushButton {
                background-color: #2563eb; color: white; border-radius: 6px; padding: 10px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

    def applyLightTheme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            #SidebarFrame { background-color: #bfdbfe; }
            QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit {
                color: #0f172a; background-color: #f3f4f6;
            }
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px;
            }
            QPushButton {
                background-color: #3b82f6; color: white; border-radius: 6px; padding: 10px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)

    def generateReport(self):
        # Disable the button to prevent rapid multiple clicks
        self.btn.setEnabled(False)
        self.report_output.setText("⏳ Launching test... please wait.")

        notify = []
        if self.pre.isChecked():
          notify.append("PRE")
        if self.post.isChecked():
          notify.append("POST")

        module_name = self.module.currentText()
        test_case_name = self.testcase.currentText()
        method = self.method.currentText()
        email = self.email.text()

        self.thread = QThread()
        self.worker = ReportWorker(module_name, test_case_name, method, email, notify)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.report_output.setText)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # ✅ Define inside the method
        def enable_button_after_finish():
           self.btn.setEnabled(True)

        self.thread.finished.connect(enable_button_after_finish)
        # ✅ Also inside
        self.thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StunningUI()
    window.show()
    sys.exit(app.exec_())