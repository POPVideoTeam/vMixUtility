
"""
Compiled with auto-py-to-exe
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

from config import load_config, save_config
from main_window import MainWindow
from scheduler import run_scheduler
from backup import run_backup
from version import __version__

def launch_vmix(file_path):
    print(f"Launching vMix preset: {file_path}")
    os.startfile(file_path)

def main():
    print("=== vMixUtility START ===")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    print("Qt app created")

    config = load_config()
    print("Config loaded:", config)

    window = MainWindow(config, save_config)
    print("MainWindow constructed")

    def open_settings():
        print("Opening settings window")
        window.show()
        window.raise_()
        window.activateWindow()

    # --- STARTUP BACKUP ---
    print("About to run startup backup")
    try:
        run_backup(config)
        print("Startup backup COMPLETED")
    except Exception as e:
        print("Startup backup FAILED:", e)

    # --- SCHEDULER ---
    print("About to run scheduler")
    run_scheduler(
        config=config,
        launch_callback=launch_vmix,
        open_settings_callback=open_settings
    )
    print("Scheduler returned")

    print("Entering Qt event loop")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
