import numpy as np
import pyaudio
from aubio import pitch as aubio_pitch

class PitchDetector:
    def __init__(self):
        # Parameters for the pitch detection
        self.downsample = 1
        self.samplerate = 44100 // self.downsample
        self.win_s = 4096 // self.downsample
        self.hop_s = 512  // self.downsample

        self.tolerance = 0.8
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.samplerate,
                                  input=True,
                                  frames_per_buffer=self.hop_s)

        self.pitch_detector = aubio_pitch("yin", self.win_s, self.hop_s, self.samplerate)
        self.pitch_detector.set_unit("midi")
        self.pitch_detector.set_tolerance(self.tolerance)

    def get_pitch(self):
        audio_chunk = self.stream.read(self.hop_s)
        signal = np.frombuffer(audio_chunk, dtype=np.float32)
        detected_pitch = self.pitch_detector(signal)[0]
        return detected_pitch

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
