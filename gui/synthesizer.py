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