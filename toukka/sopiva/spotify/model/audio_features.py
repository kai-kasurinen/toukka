#

import enum


class AudioPitch:
    pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, int_pitch):
        self.pitch = int_pitch

    def __repr__(self):
        return self.pitches[self.pitch]

    def __str__(self):
        return self.pitches[self.pitch]


class AudioMode(enum.Enum):
    minor = 0
    major = 1

# END
