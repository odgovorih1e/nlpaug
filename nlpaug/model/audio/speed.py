import librosa
import numpy as np

from nlpaug.model.audio import Audio

"""
    Reference: https://www.kaggle.com/CVxTz/audio-data-augmentation
    A wrapper of librosa.effects.time_stretch
"""


class Speed(Audio):
    def __init__(self, speed_factor):
        """
        :param speed_factor: Factor for time stretch. Audio will be slowing down if value is between 0 and 1.
            Audio will be speed up if value is larger than 1.
        """
        super(Speed, self).__init__()

        # if speed_factor < 0:
        #     raise ValueError(
        #         'speed_factor should be positive number while {} is passed.'.format(speed_factor))
        self.speed_factor = speed_factor

    def manipulate(self, data):
        speeds = [round(i, 1) for i in np.arange(self.speed_factor[0], self.speed_factor[1], 0.1)]
        speed = speeds[np.random.randint(len(speeds))]

        return librosa.effects.time_stretch(data, speed)
