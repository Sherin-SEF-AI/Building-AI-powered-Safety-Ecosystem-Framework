import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, 
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QTextEdit,
    QProgressBar, QTabWidget, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.ensemble import IsolationForest

class DataProcessingThread(QThread):
    update_progress = pyqtSignal(int)
    processing_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

    def run(self):
        try:
            self.data = pd.read_csv(self.file_path)
            self.update_progress.emit(100)
            self.processing_complete.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

class HealthDataAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health Data Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Initialize the canvas here
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        self.create_tabs()
        self.create_status_bar()

        self.data = None
        self.file_path = None

    def create_tabs(self):
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.create_data_tab()
        self.create_graph_tab()

    def create_data_tab(self):
        data_tab = QWidget()
        self.tab_widget.addTab(data_tab, "Data")
        data_layout = QVBoxLayout()
        data_tab.setLayout(data_layout)
        
        self.upload_button = QPushButton("Upload CSV File")
        self.upload_button.clicked.connect(self.load_csv)
        data_layout.addWidget(self.upload_button)
        
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        data_layout.addWidget(self.debug_text)
    
    def create_graph_tab(self):
        graph_tab = QWidget()
        self.tab_widget.addTab(graph_tab, "Graphs")
        graph_layout = QVBoxLayout()
        graph_tab.setLayout(graph_layout)

        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Select Graph", "Histogram", "Scatter Plot", "Anomaly Detection"])
        self.graph_type_combo.currentIndexChanged.connect(self.plot_graph)
        graph_layout.addWidget(self.graph_type_combo)

        # Add the canvas to the layout
        graph_layout.addWidget(self.canvas)

    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addWidget(self.progress_bar)

    def load_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.file_path = file_name
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            self.data_processing_thread = DataProcessingThread(file_name)
            self.data_processing_thread.update_progress.connect(self.update_progress_bar)
            self.data_processing_thread.processing_complete.connect(self.on_processing_complete)
            self.data_processing_thread.error_occurred.connect(self.on_error_occurred)
            self.data_processing_thread.start()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def on_processing_complete(self):
        self.progress_bar.setVisible(False)
        self.data = pd.read_csv(self.file_path)
        self.debug_text.append(f"Data loaded from {self.file_path}:\n{self.data.head()}\n")
        self.debug_text.append(f"Data types:\n{self.data.dtypes}\n")
        if self.data.empty:
            self.debug_text.append("The loaded CSV file is empty.\n")
        else:
            analysis_results = self.data.describe(include='all')
            self.debug_text.append(f"Analysis results:\n{analysis_results}\n")
        self.plot_graph()

    def on_error_occurred(self, error_message):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Error loading CSV file: {error_message}")

    def plot_graph(self):
        if self.data is None or self.data.empty:
            self.status_bar.showMessage("No data loaded or data is empty.")
            return
        
        graph_type = self.graph_type_combo.currentText()
        self.figure.clf()  # Clear the figure
        self.ax = self.figure.add_subplot(111)  # Add a new subplot
        
        # Filter numerical columns
        numerical_data = self.data.select_dtypes(include=['number'])
        
        if graph_type == "Histogram":
            if not numerical_data.empty:
                numerical_data.hist(ax=self.ax)
                self.ax.set_title('Histogram of Health Data')
            else:
                self.ax.text(0.5, 0.5, "No numerical data available for histogram", ha='center', va='center')
        elif graph_type == "Scatter Plot":
            if numerical_data.shape[1] >= 2:
                self.ax.scatter(numerical_data.iloc[:, 0], numerical_data.iloc[:, 1])
                self.ax.set_title('Scatter Plot of Health Data')
                self.ax.set_xlabel(numerical_data.columns[0])
                self.ax.set_ylabel(numerical_data.columns[1])
            else:
                self.ax.text(0.5, 0.5, "Not enough numerical data for scatter plot", ha='center', va='center')
        elif graph_type == "Anomaly Detection":
            self.anomaly_detection(numerical_data)
        
        self.canvas.draw()

    def anomaly_detection(self, numerical_data):
        if numerical_data.empty or numerical_data.shape[1] < 2:
            self.ax.text(0.5, 0.5, "Not enough numerical data for anomaly detection", ha='center', va='center')
            return
        
        try:
            isolation_forest = IsolationForest(contamination=0.1)
            numerical_data['anomaly'] = isolation_forest.fit_predict(numerical_data)
            
            inliers = numerical_data[numerical_data['anomaly'] == 1]
            outliers = numerical_data[numerical_data['anomaly'] == -1]
            
            self.ax.scatter(inliers.iloc[:, 0], inliers.iloc[:, 1], c='blue', label='Inliers')
            self.ax.scatter(outliers.iloc[:, 0], outliers.iloc[:, 1], c='red', label='Outliers')
            self.ax.set_title('Anomaly Detection using Isolation Forest')
            self.ax.set_xlabel(numerical_data.columns[0])
            self.ax.set_ylabel(numerical_data.columns[1])
            self.ax.legend()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error in anomaly detection: {e}")
            self.ax.text(0.5, 0.5, f"Error in anomaly detection: {e}", ha='center', va='center')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = HealthDataAnalyzer()
    main_window.show()
    sys.exit(app.exec_())

