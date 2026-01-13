from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import sys

load_dotenv()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())