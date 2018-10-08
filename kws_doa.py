import sys
import numpy as np
import collections
from mic_array import MicArray
from pixel_ring import pixel_ring
from snowboydetect import SnowboyDetect
import argparse


RATE = 16000
CHANNELS = 8
KWS_FRAMES = 10     # ms
DOA_FRAMES = 800    # ms


def main(model):
    model = "alexa.umdl" if model is "" else model
    pixel_ring.spin()

    detector = SnowboyDetect('snowboy/resources/common.res', 'snowboy/resources/' + model) #alexa/alexa_02092017.umdl')
    detector.SetAudioGain(1)
    detector.SetSensitivity('0.5')


#def main():
    history = collections.deque(maxlen=int(DOA_FRAMES / KWS_FRAMES))

    try:
        with MicArray(RATE, CHANNELS, RATE * KWS_FRAMES / 1000)  as mic:
            for chunk in mic.read_chunks():
                history.append(chunk)

                # Detect keyword from channel 0
                ans = detector.RunDetection(chunk[0::CHANNELS].tostring())
                if ans > 0:
                    frames = np.concatenate(history)
                    direction = mic.get_direction(frames)
                    pixel_ring.set_direction(direction)
                    if int(direction) > 90 and int(direction) <= 270:
                      direct = "Back side"
                    else:
                      direct = "Front side"
                    print('>> "' + model.split(".")[0].upper() + '" voice is from ' + direct) #'{}\n'.format(int(direction)))

    except KeyboardInterrupt:
        pass

    pixel_ring.off()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',   dest='model', type=str, default='', help='model name')

    args  = parser.parse_args()
    model = args.model + '.pmdl' if args.model else 'alexa.umdl'

    main(model)
