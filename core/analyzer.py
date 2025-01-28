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
        sig, self.sr = sf.read(path)
        # Convert to mono if stereo
        if len(sig.shape) > 1:
            sig = sig.mean(axis=1)
        self.signal = sig
        self.analyze_signal(sig, **params)

    def analyze_signal(self, sig, win_size=2048, hop=256,
                      threshold=-90, min_dur=0.05, max_partials=100):
        """Perform partial tracking analysis"""
        # Pass all arguments as positional arguments in the correct order
        self.partials = lt.analyze(sig,          # input signal
                                 self.sr,         # sample rate
                                 win_size,        # window size
                                 hop,             # hop size
                                 threshold,       # threshold in dB
                                 min_dur,         # minimum duration in seconds
                                 max_partials)    # maximum number of partials

    def get_analysis_data(self):
        """Return structured numpy array of partials"""
        if self.partials is None:
            return np.array([], dtype=[('time', 'f4'),
                                     ('freq', 'f4'),
                                     ('amp', 'f4'),
                                     ('phase', 'f4')])
        
        # Reshape and extract the data from loristrck's output
        partials_data = np.squeeze(self.partials)  # Remove singleton dimensions
        return np.array([(t, f, a, p) for t, f, a, p, _ in partials_data],
                       dtype=[('time', 'f4'),
                             ('freq', 'f4'),
                             ('amp', 'f4'),
                             ('phase', 'f4')])

    def get_number_of_partials(self):
        """Return the number of partials analyzed"""
        if self.partials is None:
            return 0
        return len(self.partials)
