# Here's a plan for the partial editor:

# 1. **Partial Data Handling**

#    - Store partials as structured numpy arrays for efficient manipulation
#    - Implement partial selection/grouping using boolean masks
#    - Use numba for performance-critical numpy operations

# 2. **Interactive Visualization**

#    - Matplotlib with QT aggregation for fast updates
#    - Implement click-and-drag partial manipulation
#    - Shared time axis across all views with synchronized zoom/scroll

# 3. **Custom Rule System**

#    - Create a Python code editor widget with syntax highlighting
#    - Use AST parsing for safe evaluation of user-defined functions
#    - Provide template transformations as starting points

# 4. **Musical Scaling System**
#    - Implement scale database using music21 or custom definitions
#    - Create frequency mapping functions for common temperaments
#    - Add MIDI note number ↔ frequency conversion utilities

import numpy as np
import numpy.typing as npt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numba import jit
import music21
from typing import List, Dict, Optional, Tuple

class PartialData:
    def __init__(self):
        # Align with analyzer.py dtype
        self.dtype = np.dtype([
            ('time', 'f4'),
            ('frequency', 'f4'),
            ('amplitude', 'f4'),
            ('phase', 'f4'),
            ('selected', np.bool_)
        ])
        self.partials = np.array([], dtype=self.dtype)
    
    @jit(nopython=True)
    def select_partials(self, mask: npt.NDArray[np.bool_]) -> None:
        """Select partials using a boolean mask"""
        self.partials['selected'] = mask

class PartialVisualization(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6))
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.partial_data = None
        self._setup_interactions()
    
    def _setup_interactions(self):
        self.fig.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.fig.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self._selection_start = None
        self._selection_rect = None
    
    def _on_mouse_press(self, event):
        if event.inaxes:
            self._selection_start = (event.xdata, event.ydata)
            self._selection_rect = plt.Rectangle(
                self._selection_start, 0, 0, 
                fill=False, edgecolor='r'
            )
            self.axes.add_patch(self._selection_rect)
    
    def _on_mouse_move(self, event):
        if event.inaxes and self._selection_start:
            x0, y0 = self._selection_start
            width = event.xdata - x0
            height = event.ydata - y0
            self._selection_rect.set_width(width)
            self._selection_rect.set_height(height)
            self.draw()
    
    def _on_mouse_release(self, event):
        if event.inaxes and self._selection_start:
            x0, y0 = self._selection_start
            x1, y1 = event.xdata, event.ydata
            xmin, xmax = min(x0, x1), max(x0, x1)
            ymin, ymax = min(y0, y1), max(y0, y1)
            
            # Select partials in rectangle
            mask = (
                (self.partial_data.partials['time'] >= xmin) &
                (self.partial_data.partials['time'] <= xmax) &
                (self.partial_data.partials['frequency'] >= ymin) &
                (self.partial_data.partials['frequency'] <= ymax)
            )
            self.partial_data.select_partials(mask)
            
            # Cleanup
            self._selection_rect.remove()
            self._selection_rect = None
            self._selection_start = None
            self.update_plot(self.partial_data)

    def update_plot(self, partial_data: PartialData):
        self.axes.clear()
        self.partial_data = partial_data
        self.axes.scatter(
            partial_data.partials['time'],
            partial_data.partials['frequency'],
            c=partial_data.partials['amplitude'],
            alpha=0.6
        )
        self.draw()

from .synthesizer import RealTimeSynthesizer

class PartialEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.partial_data = PartialData()
        self.synthesizer = None
        self.setup_ui()
    
    def play_selected(self):
        """Play only selected partials"""
        if self.synthesizer:
            self.synthesizer.stop_playback()
        
        selected_mask = self.partial_data.partials['selected']
        if selected_mask.any():
            selected_data = self.partial_data.partials[selected_mask]
            self.synthesizer = RealTimeSynthesizer(selected_data)
            self.synthesizer.start_playback()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Visualization area
        self.visualization = PartialVisualization(self)
        splitter.addWidget(self.visualization)
        
        # Rule editor area (placeholder for now)
        self.rule_editor = QWidget()
        splitter.addWidget(self.rule_editor)
        
        layout.addWidget(splitter)
    
    def load_partials(self, time: np.ndarray, freq: np.ndarray, 
                     amp: np.ndarray, phase: np.ndarray):
        """Load partial data into the editor"""
        n_partials = len(time)
        self.partial_data.partials = np.zeros(n_partials, dtype=self.partial_data.dtype)
        self.partial_data.partials['time'] = time
        self.partial_data.partials['frequency'] = freq
        self.partial_data.partials['amplitude'] = amp
        self.partial_data.partials['phase'] = phase
        self.visualization.update_plot(self.partial_data)
    
    def load_from_analyzer(self, analyzer):
        """Load partial data from SpectralAnalyzer instance"""
        analysis_data = analyzer.get_analysis_data()
        self.partial_data.partials = np.zeros(len(analysis_data), dtype=self.partial_data.dtype)
        self.partial_data.partials['time'] = analysis_data['time']
        self.partial_data.partials['frequency'] = analysis_data['freq']
        self.partial_data.partials['amplitude'] = analysis_data['amp']
        self.partial_data.partials['phase'] = analysis_data['phase']
        self.partial_data.partials['selected'] = False
        self.visualization.update_plot(self.partial_data)

# Musical scaling utilities
def midi_to_freq(midi_note: float) -> float:
    """Convert MIDI note number to frequency"""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def freq_to_midi(frequency: float) -> float:
    """Convert frequency to MIDI note number"""
    return 69 + 12 * np.log2(frequency / 440.0)