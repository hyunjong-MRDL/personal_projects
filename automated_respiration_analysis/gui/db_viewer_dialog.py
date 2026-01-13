from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject
from app.database_manager import DatabaseManager

class DbViewerWorker(QRunnable):
    class Signals(QObject):
        finished = pyqtSignal(list)
        error = pyqtSignal(str)

    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        try:
            db_manager = DatabaseManager(self.db_config)
            if db_manager.connect():
                data = db_manager.fetch_all_results()
                db_manager.close()
                self.signals.finished.emit(data)
            else:
                self.signals.error.emit("Failed to connect to the database. Please check your credentials.")
        except Exception as e:
            self.signals.error.emit(f"An unexpected error occurred while fetching data: {e}")

class DbViewerDialog(QDialog):
    """
    A dialog to display database contents in a table.
    """
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.setWindowTitle("Database Results")
        self.setMinimumSize(800, 600)
        self.threadpool = QThreadPool()
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Patient ID", "Data Type", "Reproducibility", "LVL Mean", "LVL STD", "Stability", "Error Mean", "Error STD"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.loading_label = QLabel("Fetching data from the database...")
        self.loading_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.loading_label)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        self.loading_label.show()
        self.table.hide()

        worker = DbViewerWorker(self.db_config)
        worker.signals.finished.connect(self.populate_table)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def populate_table(self, data):
        self.loading_label.hide()
        self.table.show()
        
        self.table.setRowCount(len(data))
        for row, record in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(record.get('patient_id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(record.get('data_type', ''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(record.get('reproducibility', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(record.get('lvl_mean', ''))))
            self.table.setItem(row, 4, QTableWidgetItem(str(record.get('lvl_std', ''))))
            self.table.setItem(row, 5, QTableWidgetItem(str(record.get('stability', ''))))
            self.table.setItem(row, 6, QTableWidgetItem(str(record.get('error_mean', ''))))
            self.table.setItem(row, 7, QTableWidgetItem(str(record.get('error_std', ''))))
            
    def handle_error(self, message):
        self.loading_label.hide()
        self.table.hide()
        QMessageBox.warning(self, "Database Error", message)