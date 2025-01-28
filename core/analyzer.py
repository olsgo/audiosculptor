import loristrck as lt
import numpy as np
import soundfile as sf

class SpectralAnalyzer:
    def __init__(self):
        self.partials = None
        self.sr = 44100
        self.signal = None

    def analyze_file(self, path, **params):
        """Main analysis entry point"""
        # Use soundfile instead of lt.sndread
        sig, self.sr = sf.read(path)
        # Convert to mono if stereo
        if len(sig.shape) > 1:
            sig = sig.mean(axis=1)
        self.signal = sig
        self.analyze_signal(sig, **params)

    def analyze_signal(self, sig, win_size=4096, hop=512,
                  threshold=-90, min_dur=0.02):
        """Perform partial tracking analysis"""
        # Pass all arguments as positional arguments in the correct order
        self.partials = lt.analyze(sig,          # input signal
                                 self.sr,         # sample rate
                                 win_size,        # window size
                                 hop,             # hop size
                                 threshold,       # threshold in dB
                                 min_dur)         # minimum duration in seconds

    def get_analysis_data(self):
        """Return structured numpy array of partials"""
        if self.partials is None:
            return np.array([], dtype=[('time', 'f4'),
                                     ('freq', 'f4'),
                                     ('amp', 'f4'),
                                     ('phase', 'f4')])
        
        # Reshape and extract the data from loristrck's output
        # loristrck returns shape (n_frames, 1, 5) where the last dimension contains:
        # [time, frequency, amplitude, phase, ???]
        partials_data = np.squeeze(self.partials)  # Remove the middle singleton dimension
        return np.array([(t, f, a, p) for t, f, a, p, _ in partials_data],
                       dtype=[('time', 'f4'),
                             ('freq', 'f4'),
                             ('amp', 'f4'),
                             ('phase', 'f4')])