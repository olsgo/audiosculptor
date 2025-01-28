I'll help you design an architecture for this audio analysis and resynthesis tool. Here's a technical blueprint:

### 1. System Architecture

```python
AudioSculptor/
├── core/
│   ├── analyzer.py       # Loristrck analysis wrapper
│   ├── processor.py      # Numpy-based transformations
│   ├── synthesizer.py    # Resynthesis engine
│   └── utilities.py      # File I/O, format conversion
├── gui/
│   ├── main_window.py    # Primary interface
│   ├── canvas.py         # Visualization system
│   ├── partial_editor.py # Partial manipulation UI
│   └── widgets.py        # Custom controls
└── presets/              # Transformation templates
```

### 2. Core Analysis Implementation (analyzer.py)

```python
import loristrck as lt
import numpy as np

class SpectralAnalyzer:
    def __init__(self):
        self.partials = None
        self.sr = 44100

    def analyze_file(self, path, **params):
        """Main analysis entry point"""
        self.sr, sig = lt.sndread(path)
        self.analyze_signal(sig, **params)

    def analyze_signal(self, sig, win_size=4096, hop=512,
                      threshold=-90, min_dur=0.02):
        """Perform partial tracking analysis"""
        self.partials = lt.analyze(sig, self.sr,
                                 resolution=win_size,
                                 hopsize=hop,
                                 threshold=threshold,
                                 minduration=min_dur)

    def get_analysis_data(self):
        """Return structured numpy array of partials"""
        return np.array(self.partials,
                      dtype=[('time', 'f4'),
                             ('freq', 'f4'),
                             ('amp', 'f4'),
                             ('phase', 'f4')])
```

### 3. Spectral Processing Engine (processor.py)

```python
class PartialProcessor:
    def __init__(self, partials):
        self.partials = partials.copy()

    def apply_transformation(self, func):
        """Apply numpy-based transformation function"""
        # Func signature: (times, freqs, amps, phases) -> modified
        fields = ['time', 'freq', 'amp', 'phase']
        t, f, a, p = [self.partials[field] for field in fields]
        new_f, new_a, new_p = func(t, f, a, p)
        self.partials['freq'] = new_f
        self.partials['amp'] = new_a
        self.partials['phase'] = new_p

    def time_stretch(self, factor):
        self.partials['time'] *= factor

    def frequency_shift(self, shift_fn):
        """shift_fn can be constant value or function(freq)->new_freq"""
        if callable(shift_fn):
            self.partials['freq'] = np.vectorize(shift_fn)(self.partials['freq'])
        else:
            self.partials['freq'] += shift_fn

    # Add more transformation methods as needed
```

### 4. GUI Main Window Structure (main_window.py)

```python
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Central widget with horizontal layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left panel: Analysis parameters and controls
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # File loading section
        self.file_selector = QLineEdit()
        self.browse_btn = QPushButton("Browse...")

        # Analysis parameters
        self.win_size = QSpinBox()
        self.hop_size = QSpinBox()
        self.threshold = QDoubleSpinBox()

        # Visualization controls
        self.waveform_btn = QRadioButton("Waveform")
        self.spectrogram_btn = QRadioButton("Spectrogram")
        self.partials_btn = QRadioButton("Partials")

        # Right panel: Visualization canvas
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(control_panel, 1)
        layout.addWidget(self.canvas, 3)

        # Connect signals
        self.browse_btn.clicked.connect(self.load_audio)
        self.win_size.valueChanged.connect(self.update_analysis)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName()
        self.file_selector.setText(path)
        self.analyzer.analyze_file(path)
        self.update_visualization()

    def update_analysis(self):
        # Re-run analysis with new parameters
        pass

    def update_visualization(self):
        # Update canvas based on selected view mode
        pass
```

### 5. Real-Time Synthesis System (synthesizer.py)

```python
import sounddevice as sd

class RealTimeSynthesizer:
    def __init__(self, partials, sr=44100):
        self.partials = partials
        self.sr = sr
        self.stream = None

    def start_playback(self):
        """Stream synthesized audio in real-time"""
        def callback(outdata, frames, time, status):
            # Resynthesis happens here
            synth_sig = lt.synthesize(self.partials, self.sr)
            outdata[:] = synth_sig.reshape(-1, 1)

        self.stream = sd.OutputStream(
            samplerate=self.sr,
            channels=1,
            callback=callback
        )
        self.stream.start()

    def stop_playback(self):
        if self.stream:
            self.stream.stop()
```

### 6. Key Technical Considerations

1. **Partial Data Handling**

   - Store partials as structured numpy arrays for efficient manipulation
   - Implement partial selection/grouping using boolean masks
   - Use numba for performance-critical numpy operations

2. **Interactive Visualization**

   - Matplotlib with QT aggregation for fast updates
   - Implement click-and-drag partial manipulation
   - Shared time axis across all views with synchronized zoom/scroll

3. **Custom Rule System**

   - Create a Python code editor widget with syntax highlighting
   - Use AST parsing for safe evaluation of user-defined functions
   - Provide template transformations as starting points

4. **Musical Scaling System**
   - Implement scale database using music21 or custom definitions
   - Create frequency mapping functions for common temperaments
   - Add MIDI note number ↔ frequency conversion utilities

### 7. Optimization Strategies

- Implement partial data caching for fast parameter tweaking
- Use Dask for out-of-core processing of large audio files
- Employ GPU acceleration for complex numpy operations using CuPy
- Implement level-of-detail rendering for visualization (decimate data at high zoom levels)

### 8. Example Transformation (Frequency Snapping)

```python
def snap_to_scale(scale_degrees, base_freq=440):
    """Create a frequency snapping function for a musical scale"""
    scale_freqs = [base_freq * 2**(d/12) for d in scale_degrees]

    def _snapper(freq):
        nearest = min(scale_freqs, key=lambda x: abs(x - freq))
        return nearest

    return _snapper

# Usage in processor:
scale = [0, 2, 4, 7, 9]  # Major pentatonic intervals
processor.frequency_shift(snap_to_scale(scale))
```
