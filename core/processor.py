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