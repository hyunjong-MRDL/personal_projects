import pandas as pd
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from app import dataloader, processing
from app.database_manager import DatabaseManager
import os
import traceback

class AnalysisWorker(QRunnable):
    class Signals(QObject):
        finished = pyqtSignal()
        error = pyqtSignal(str)
        progress = pyqtSignal(int)
        status = pyqtSignal(str)
        results = pyqtSignal(pd.DataFrame)

    def __init__(self, data_root, db_config):
        super().__init__()
        self.data_root = data_root
        self.db_config = db_config
        self.signals = self.Signals()

    def run(self):
        try:
            print("Worker thread started.")
            self.signals.status.emit("Starting analysis...")
            
            if not self.data_root.exists() or not self.data_root.is_dir():
                raise FileNotFoundError(f"Data directory not found: {self.data_root}")

            print("Loading patient data...")
            self.signals.status.emit("Loading patient data...")
            total_list = dataloader.patient_listing(self.data_root)
            
            if not total_list:
                self.signals.error.emit("No patient data found in the selected directory.")
                return

            all_results = []
            total_data_types = len(total_list)
            
            for i, data_type in enumerate(total_list):
                patient_list = total_list[data_type]
                
                self.signals.status.emit(f"Processing data type: {data_type}")
                
                total_patients = len(patient_list)
                for j, patient_path in enumerate(patient_list):
                    self.signals.status.emit(f"Analyzing patient {j+1}/{total_patients} in {data_type}...")
                    
                    patient_results = processing.batch_processing([patient_path])
                    
                    for patient_id, fractions in patient_results.items():
                        for fraction, metrics in fractions.items():
                            all_results.append({
                                'patient_id': patient_id.split(os.sep)[-1],
                                'data_type': data_type,
                                'fraction': fraction,
                                'reproducibility': metrics[0],
                                'lvl_mean': metrics[1],
                                'lvl_std': metrics[2],
                                'stability': metrics[3],
                                'error_mean': metrics[4],
                                'error_std': metrics[5]
                            })
                    
                    progress_value = int(((i + 1) / total_data_types) * 100)
                    self.signals.progress.emit(progress_value)
            
            df_results = pd.DataFrame(all_results)
            print("Analysis complete. Attempting to save to database...")
            self.signals.status.emit("Analysis complete. Saving to database...")
            
            db_manager = DatabaseManager(self.db_config)
            db_manager.connect()
            db_manager.insert_dataframe(df_results, 'analysis_results')
            db_manager.close()
            
            print("Data successfully uploaded to the database.")
            self.signals.status.emit("Data successfully uploaded to the database.")
            
            self.signals.results.emit(df_results)
            self.signals.finished.emit()

        except Exception as e:
            error_message = f"An error occurred: {e}\n{traceback.format_exc()}"
            print(error_message)
            self.signals.error.emit(str(e))