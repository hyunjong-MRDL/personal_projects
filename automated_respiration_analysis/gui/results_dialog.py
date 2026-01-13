import numpy as np
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QDesktopWidget
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ResultsDialog(QDialog):
    def __init__(self, summary_data, parent=None):
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.setWindowTitle("Analysis Results Summary")
        self.summary_data = summary_data
        self.setMinimumSize(800, 600)
        self.center()
        self.initUI()
        self.plot_results()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Matplotlib canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)
        
    def plot_results(self):
        ax = self.figure.add_subplot(111)
        ax.set_title(f"Summary for {self.summary_data['data_type']} Data ({self.summary_data['total_patients']} patients)")
        
        reproducibility = self.summary_data['reproducibility']
        stability = self.summary_data['stability']
        
        if reproducibility and stability:
            x = np.arange(len(reproducibility))
            width = 0.35
            
            bar1 = ax.bar(x - width/2, reproducibility, width, label='Reproducibility', color='#1f77b4')
            bar2 = ax.bar(x + width/2, stability, width, label='Stability', color='#ff7f0e')
            
            ax.set_ylabel('Metric Value')
            ax.set_xlabel('Patient')
            ax.set_xticks(x)
            ax.set_xticklabels([f"P{i+1}" for i in x], rotation=45, ha="right")
            ax.legend()
            self.figure.tight_layout()
            self.canvas.draw()
        else:
            ax.text(0.5, 0.5, "No data to display.",
                    ha='center', va='center', transform=ax.transAxes, fontsize=12)
            self.canvas.draw()