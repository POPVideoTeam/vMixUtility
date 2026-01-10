import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore


import os
import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui


# ---- TEST MODE ----
TEST_SUNDAY_MODE = False  # True = force Sunday confirm behavior on any day






def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CountdownDialog(QtWidgets.QDialog):
    def __init__(self, file_path, seconds, on_settings=None, require_confirm=False):

        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.file_path = file_path
        self.remaining = seconds
        self.on_settings = on_settings
        
        self.require_confirm = require_confirm


        self.setWindowTitle("vMix Scheduler")
        self.setFixedSize(360, 300)

        # ---------- MAIN LAYOUT ----------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(12)

        # ---------- TOP BAR (Settings button) ----------
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addStretch()

        settings_btn = QtWidgets.QPushButton("Settings…")
        settings_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(settings_btn)

        logo_label = QtWidgets.QLabel()
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        
        pixmap = QtGui.QPixmap(resource_path("assets/vmix_logo.png"))
        pixmap = pixmap.scaled(
            200,   # width
            60,    # height
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        
        logo_label.setPixmap(pixmap)
        main_layout.addWidget(logo_label)     

        main_layout.addLayout(top_bar)

        # ---------- MAIN LABEL ----------
        preset_name = os.path.splitext(os.path.basename(file_path))[0]
        
        if self.require_confirm:
            label = QtWidgets.QLabel(
                f"Suggested vMix preset:\n\n<b><br>{preset_name}</b><br><br>\n\n"
                "⚠️ <b>Before Starting vMix, confirm:<br><br></b>\n"
                "• AUDIO BOARD ➜ ON <br>"
                "• MASTER POWER SWITCH ➜ ON<br><br>"
                "\n\n"
                "<b>Click 'Start' once confirmed.</b>"
            )
            label.setStyleSheet("padding-left: 8px; padding-right: 8px;")
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            
        else:
            label = QtWidgets.QLabel(
                f"vMix preset will start automatically:\n\n<b>{preset_name}</b>"
            )
            label.setStyleSheet("padding-left: 8px; padding-right: 8px;")
            label.setAlignment(QtCore.Qt.AlignCenter)
            
        
        label.setTextFormat(QtCore.Qt.RichText)
        main_layout.addWidget(label)

        main_layout.addStretch()

        # ---------- BUTTON ROW (Start / Cancel) ----------
        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch()

        start_btn = QtWidgets.QPushButton("Start Now")
        start_btn.clicked.connect(self.start_now)
        start_btn.setDefault(True)

        self.cancel_btn = QtWidgets.QPushButton("")
        self.cancel_btn.clicked.connect(self.cancel_launch)

        button_row.addWidget(start_btn)
        button_row.addWidget(self.cancel_btn)

        main_layout.addLayout(button_row)

        # ---------- TIMER ----------
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

        self.update_cancel_button()

    # ---------- COUNTDOWN ----------
    def update_cancel_button(self):
        self.cancel_btn.setText(f"Cancel ({self.remaining})")

    def tick(self):
        if self.remaining > 0:
            self.remaining -= 1
            self.update_cancel_button()
        else:
            self.timer.stop()
    
            if self.require_confirm:
                # Sunday behavior: stop and WAIT for the user
                self.cancel_btn.setText("Cancel")
                return
    
            # Normal behavior: auto-start
            self.accept()

    # ---------- ACTIONS ----------
    def start_now(self):
        print("Start Now clicked")
        self.timer.stop()
        self.accept()

    def cancel_launch(self):
        self.timer.stop()
        self.reject()
        QtWidgets.QApplication.quit()

    def open_settings(self):
        self.timer.stop()
        if self.on_settings:
            self.on_settings()
        self.reject()
        
    def showEvent(self, event):
        print(">>> Dialog showEvent")
        super().showEvent(event)

    def closeEvent(self, event):
        print(">>> Dialog closeEvent")
        super().closeEvent(event)
    
    def reject(self):
        print(">>> Dialog reject() CALLED")
        super().reject()


def run_scheduler(config, launch_callback, open_settings_callback):
    today = datetime.today()
    day = today.strftime("%A")
    
    require_confirm = (today.weekday() == 6)  # real Sunday
    if TEST_SUNDAY_MODE:
        require_confirm = True


    schedule = config.get("schedule", {})

    if not schedule or day not in schedule or not schedule[day]:
        return "noop"

    file_path = schedule[day]
    countdown = config.get("app", {}).get("countdown", 5)

    dlg = CountdownDialog(
        file_path,
        countdown,
        on_settings=open_settings_callback,
        require_confirm=require_confirm
    )

    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    print("About to exec dialog. countdown=", countdown, "require_confirm=", require_confirm)

    result = dlg.exec_()
    print("Dialog exec_() returned:", result)
    
    if result == QtWidgets.QDialog.Accepted:
        print("Dialog accepted — calling launch_callback")
        launch_callback(file_path)
        return "launched"
    
    print("Dialog rejected")
    return "canceled"



