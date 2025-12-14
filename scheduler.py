import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore


class CountdownDialog(QtWidgets.QDialog):
    def __init__(self, file_path, seconds, on_settings=None):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.file_path = file_path
        self.remaining = seconds
        self.on_settings = on_settings

        self.setWindowTitle("vMix Scheduler")
        self.setFixedSize(360, 260)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        preset_name = os.path.splitext(os.path.basename(file_path))[0]

        label = QtWidgets.QLabel(
            f"vMix preset will start automatically:\n\n<b>{preset_name}</b>"
        )
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(label)

        start_btn = QtWidgets.QPushButton("Start Now")
        start_btn.clicked.connect(self.start_now)
        layout.addWidget(start_btn)

        self.cancel_btn = QtWidgets.QPushButton("")
        self.cancel_btn.clicked.connect(self.cancel_launch)
        layout.addWidget(self.cancel_btn)

        settings_btn = QtWidgets.QPushButton("Settings…")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

        self.update_cancel_button()

    def update_cancel_button(self):
        self.cancel_btn.setText(f"Cancel ({self.remaining})")

    def tick(self):
        if self.remaining > 0:
            self.remaining -= 1
            self.update_cancel_button()
        else:
            self.timer.stop()
            self.accept()

    def start_now(self):
        self.timer.stop()
        self.accept()

    def cancel_launch(self):
        self.timer.stop()
        self.reject()

    def open_settings(self):
        self.timer.stop()
        if self.on_settings:
            self.on_settings()
        self.reject()   # <-- close popup, treat as cancel


def run_scheduler(config, launch_callback, open_settings_callback):
    """
    Called by main app when it's time to evaluate today's schedule.
    """

    day = datetime.today().strftime("%A")
    schedule = config["schedule"]

    if day not in schedule:
        return

    file_path = schedule[day]
    countdown = config["app"].get("countdown", 5)

    dlg = CountdownDialog(
        file_path,
        countdown,
        on_settings=open_settings_callback
    )

    if dlg.exec_() == QtWidgets.QDialog.Accepted:
        if os.path.isfile(file_path):
            launch_callback(file_path)
