from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog,
    QCheckBox, QSpinBox, QMessageBox
)
from version import __version__

class MainWindow(QWidget):
    def __init__(self, config, on_save=None):
        super().__init__()
        self.config = config
        self.on_save = on_save
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"vMix Utility Manager v{__version__}")
        self.resize(600, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("<b>vMix Utility Manager</b>"))
        layout.addWidget(QLabel(f"Version {__version__}"))

        # Source folder
        self.src_edit = QLineEdit(self.config["backup"]["source"])
        self.src_edit.setReadOnly(True)
        src_btn = QPushButton("Browse")
        src_btn.clicked.connect(self.select_source)

        src_row = QHBoxLayout()
        src_row.addWidget(QLabel("Source"))
        src_row.addWidget(self.src_edit)
        src_row.addWidget(src_btn)

        # Target folder
        self.dst_edit = QLineEdit(self.config["backup"]["target"])
        self.dst_edit.setReadOnly(True)
        dst_btn = QPushButton("Browse")
        dst_btn.clicked.connect(self.select_target)

        dst_row = QHBoxLayout()
        dst_row.addWidget(QLabel("Target"))
        dst_row.addWidget(self.dst_edit)
        dst_row.addWidget(dst_btn)

        # Purge Backups After
        self.age_spin = QSpinBox()
        self.age_spin.setRange(1, 3650)  # up to 10 years
        self.age_spin.setValue(
            self.config["backup"].get("max_age_days", 183)
            )
        
        age_row = QHBoxLayout()
        age_row.addWidget(QLabel("Delete backups older than (days)"))
        age_row.addWidget(self.age_spin)


        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_clicked)

        layout.addLayout(src_row)
        layout.addLayout(dst_row)
        layout.addLayout(age_row)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def select_source(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            self.src_edit.setText(path)

    def select_target(self):
        path = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if path:
            self.dst_edit.setText(path)

    def save_clicked(self):
        self.config["backup"]["source"] = self.src_edit.text()
        self.config["backup"]["target"] = self.dst_edit.text()
        self.config["backup"]["max_age_days"] = self.age_spin.value()


        if self.on_save:
            self.on_save(self.config)

        QMessageBox.information(self, "Saved", "Configuration saved")
