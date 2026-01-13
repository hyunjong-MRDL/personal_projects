import pathlib
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QSizePolicy,
    QProgressBar, QGroupBox, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import QThreadPool

from app.analyze import AnalysisWorker
from gui.progress_dialog import ProgressDialog
from gui.db_viewer_dialog import DbViewerDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Respiratory Analysis GUI")
        self.setGeometry(100, 100, 600, 400)

        # QThreadPool to manage worker threads
        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")
        
        # UI Elements
        self.data_path = ""
        self.db_config = {}

        # Top-level layout
        main_layout = QVBoxLayout()
        main_widget = QWidget()

        # Data Path Selection
        data_group = QGroupBox("1. Select Data Directory")
        data_layout = QHBoxLayout()
        self.data_path_line_edit = QLineEdit()
        self.data_path_line_edit.setPlaceholderText("No directory selected")
        self.data_path_line_edit.setReadOnly(True)
        data_browse_button = QPushButton("Browse")
        data_browse_button.clicked.connect(self.browse_data_path)
        
        data_layout.addWidget(self.data_path_line_edit)
        data_layout.addWidget(data_browse_button)
        data_group.setLayout(data_layout)
        
        # Database Configuration
        db_group = QGroupBox("2. MySQL Database Configuration")
        db_layout = QVBoxLayout()
        
        # Load from environment variables and set as default values
        db_host = os.getenv("DB_HOST", "")
        db_user = os.getenv("DB_USER", "")
        db_password = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "")
        
        self.db_host_input = QLineEdit()
        self.db_host_input.setText(db_host)
        self.db_host_input.setPlaceholderText("DB Host (e.g., localhost)")
        
        self.db_user_input = QLineEdit()
        self.db_user_input.setText(db_user)
        self.db_user_input.setPlaceholderText("Username")
        
        self.db_password_input = QLineEdit()
        self.db_password_input.setText(db_password)
        self.db_password_input.setPlaceholderText("Password")
        self.db_password_input.setEchoMode(QLineEdit.Password)
        
        self.db_name_input = QLineEdit()
        self.db_name_input.setText(db_name)
        self.db_name_input.setPlaceholderText("Database Name (e.g., respiration_db)")
        
        db_layout.addWidget(self.db_host_input)
        db_layout.addWidget(self.db_user_input)
        db_layout.addWidget(self.db_password_input)
        db_layout.addWidget(self.db_name_input)
        db_group.setLayout(db_layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Analysis")
        self.start_button.clicked.connect(self.start_analysis)
        self.start_button.setFixedSize(150, 40)
        self.start_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.view_db_button = QPushButton("View Database")
        self.view_db_button.clicked.connect(self.view_database)
        self.view_db_button.setFixedSize(150, 40)
        self.view_db_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.view_db_button)
        button_layout.addStretch(1)

        # Main Layout Assembly
        main_layout.addWidget(data_group)
        main_layout.addWidget(db_group)
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def browse_data_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if directory:
            self.data_path = pathlib.Path(directory)
            self.data_path_line_edit.setText(str(self.data_path))

    def start_analysis(self):
        # 1. Input validation
        if not self.data_path:
            QMessageBox.warning(self, "Input Error", "Please select a data directory.")
            return

        db_config = {
            'host': self.db_host_input.text().strip(),
            'user': self.db_user_input.text().strip(),
            'password': self.db_password_input.text(),
            'database': self.db_name_input.text().strip()
        }

        # Check if database credentials are provided
        if not all(db_config.values()):
            QMessageBox.warning(self, "Input Error", "Please provide all database credentials.")
            return

        print("Starting analysis with the following settings:")
        print(f"Data Path: {self.data_path}")
        print(f"DB Config: {db_config['user']}@{db_config['host']}/{db_config['database']}")

        # 2. Start analysis in a worker thread
        progress_dialog = ProgressDialog(self)
        
        worker = AnalysisWorker(self.data_path, db_config)
        worker.signals.progress.connect(progress_dialog.update_progress)
        worker.signals.status.connect(progress_dialog.update_status)
        worker.signals.finished.connect(progress_dialog.close)
        worker.signals.error.connect(progress_dialog.show_error)
        worker.signals.results.connect(self.show_results)
        
        self.threadpool.start(worker)
        progress_dialog.exec_()
    
    def view_database(self):
        db_config = {
            'host': self.db_host_input.text().strip(),
            'user': self.db_user_input.text().strip(),
            'password': self.db_password_input.text(),
            'database': self.db_name_input.text().strip()
        }
        
        if not all(db_config.values()):
            QMessageBox.warning(self, "Input Error", "Please provide all database credentials.")
            return

        viewer = DbViewerDialog(db_config)
        viewer.exec_()

    def show_results(self, results):
        print("Analysis finished. Results received.")
        print(f"First 5 rows of data:\n{results.head()}")