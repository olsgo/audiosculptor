from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from core.analyzer import SpectralAnalyzer
from gui.partial_editor import PartialEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AudioSculptor")
        self.analyzer = SpectralAnalyzer()
        
        # Central widget with horizontal layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left panel: Analysis parameters and controls
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # File loading section
        file_group = QGroupBox("Audio File")
        file_layout = QHBoxLayout()
        self.file_selector = QLineEdit()
        self.browse_btn = QPushButton("Browse...")
        file_layout.addWidget(self.file_selector)
        file_layout.addWidget(self.browse_btn)
        file_group.setLayout(file_layout)
        control_layout.addWidget(file_group)

        # Analysis parameters
        analysis_group = QGroupBox("Analysis Parameters")
        param_layout = QFormLayout()
        
        # Window size (resolution in loristrck)
        self.win_size = QSpinBox()
        self.win_size.setRange(128, 32768)  # Power of 2 values
        self.win_size.setValue(2048)
        self.win_size.setSingleStep(128)
        
        # Hop size
        self.hop_size = QSpinBox()
        self.hop_size.setRange(32, 8192)
        self.hop_size.setValue(256)
        self.hop_size.setSingleStep(32)
        
        # Amplitude threshold
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(-120, 0)
        self.threshold.setValue(-90)
        self.threshold.setSingleStep(1)
        
        # Minimum duration
        self.min_duration = QDoubleSpinBox()
        self.min_duration.setRange(0.001, 10.0)
        self.min_duration.setValue(0.05)
        self.min_duration.setSingleStep(0.01)
        self.min_duration.setSuffix(" s")
        
        # Maximum number of partials
        self.max_partials = QSpinBox()
        self.max_partials.setRange(1, 10000)
        self.max_partials.setValue(100)
        self.max_partials.setSingleStep(10)
        
        param_layout.addRow("Window Size:", self.win_size)
        param_layout.addRow("Hop Size:", self.hop_size)
        param_layout.addRow("Threshold (dB):", self.threshold)
        param_layout.addRow("Min Duration:", self.min_duration)
        param_layout.addRow("Max Partials:", self.max_partials)
        
        analysis_group.setLayout(param_layout)
        control_layout.addWidget(analysis_group)

        # Visualization controls
        view_group = QGroupBox("View Mode")
        view_layout = QVBoxLayout()
        self.waveform_btn = QRadioButton("Waveform")
        self.spectrogram_btn = QRadioButton("Spectrogram")
        self.partials_btn = QRadioButton("Partials")
        self.partials_btn.setChecked(True)
        
        view_layout.addWidget(self.waveform_btn)
        view_layout.addWidget(self.spectrogram_btn)
        view_layout.addWidget(self.partials_btn)
        view_group.setLayout(view_layout)
        control_layout.addWidget(view_group)

        # Add stretch to push everything up
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        
        # Right panel: Visualization and editing
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Visualization canvas
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.axes = self.canvas.figure.add_subplot(111)
        
        # Partial editor
        self.partial_editor = PartialEditor()
        
        right_layout.addWidget(self.canvas)
        right_layout.addWidget(self.partial_editor)
        
        # Add panels to main layout
        layout.addWidget(control_panel, 1)
        layout.addWidget(right_panel, 3)

        # Connect signals
        self.browse_btn.clicked.connect(self.load_audio)
        # Update signal connections
        self.win_size.valueChanged.connect(self.update_analysis)
        self.hop_size.valueChanged.connect(self.update_analysis)
        self.threshold.valueChanged.connect(self.update_analysis)
        self.min_duration.valueChanged.connect(self.update_analysis)
        self.max_partials.valueChanged.connect(self.update_analysis)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.aiff);;All Files (*.*)"
        )
        if path:
            self.file_selector.setText(path)
            self.analyzer.analyze_file(path)
            self.partial_editor.load_from_analyzer(self.analyzer)
            self.update_visualization()

    def update_analysis(self):
        if not self.file_selector.text():
            return
            
        self.analyzer.analyze_signal(
            self.analyzer.signal,  # Current audio signal
            win_size=self.win_size.value(),
            hop=self.hop_size.value(),
            threshold=self.threshold.value(),
            min_dur=self.min_duration.value(),
            max_partials=self.max_partials.value()
        )
        self.partial_editor.load_from_analyzer(self.analyzer)
        self.update_visualization()

    def update_visualization(self):
        self.axes.clear()
        
        if self.waveform_btn.isChecked():
            # TODO: Implement waveform visualization
            pass
        elif self.spectrogram_btn.isChecked():
            # TODO: Implement spectrogram visualization
            pass
        elif self.partials_btn.isChecked():
            # Partial visualization is handled by the partial editor
            pass
            
        self.canvas.draw()