from math import pi, sqrt, sin
import numpy as np

def frange(start, end, step):
    while start < end:
        yield start
        start += step

def dist(A, B):
    a1, a2 = A
    b1, b2 = B
    distance = (b1-a1)**2 + (b2-a2)**2
    distance = sqrt(distance)
    return distance

class Signal(list):
    def __init__(self, signal=None, **kwargs):
        super().__init__()

        self.rate = kwargs['rate']

        if signal is None:
            if 'length' in kwargs:
                for t in range(kwargs['length']):
                    self.append(0.0)
            else:
                frequency = kwargs['frequency']
                periods = kwargs['periods']
                duration = periods / frequency
                for t in frange(0, duration, 1/self.rate):
                    self.append(sin(2 * pi * frequency * t) * \
                    max(1 - abs(2*t/duration-1), 0))

        else:
            for _ in signal:
                self.append(_)

    def concatenate(self, other):
        return Signal(self[:] + other[:], rate=self.rate)

    def __add__(self, other):
        rate = self.rate
        lenSelf, lenOther = len(self), len(other)
        if lenSelf > lenOther:
            sumSignal = Signal(length=lenSelf, rate=self.rate)
            for i in range(lenOther):
                sumSignal[i] = self[i] + other[i]
            for i in range(lenOther, lenSelf):
                sumSignal[i] = self[i]
        else:
            sumSignal = Signal(length=lenOther, rate=self.rate)
            for i in range(lenSelf):
                sumSignal[i] = self[i] + other[i]
            for i in range(lenSelf, lenOther):
                sumSignal[i] = other[i]

        return sumSignal

    def __iadd__(self, other):
        return self + other

    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            return 0

    def delayed(self, delay):
        rate = self.rate
        signal = Signal(signal=[0]*int(rate*delay) + self[:], rate=rate)
        return signal

    def sigSum(signals):
        length = max(len(signal) for signal in signals)
        sumSignal = Signal(length=length, rate=signals[0].rate)
        for signal in signals:
            sumSignal += signal
        return sumSignal

class Material:
    def __init__(self, velocity, defects=[]):
        self.velocity = velocity
        self.defects = defects

    def response(self, signal, transmitter, receiver):
        velocity = self.velocity
        defects = self.defects

        delays = list()
        for defect in defects:
            distance = dist(transmitter, defect) + dist(defect, receiver)
            delay = distance / velocity
            delays.append(delay)

        response = Signal.sigSum([signal.delayed(delay) for delay in delays])
        return response

class Probes(dict):
    def __init__(self, number, step, signal=None):
        self.number = number
        shift = (number - 1) / 2
        for probe in range(number):
            self[probe] = ((probe - shift) * step, 0)
        if signal:
            self.signal = signal

    def scan(self, material):
        number = self.number
        signal = self.signal
        data = [[0 for i in range(number)] for j in range(number)]

        for t, transmitter in self.items():
            for r, receiver in self.items():
                response = material.response(signal, transmitter, receiver)
                data[t][r] = response
        return data

class TotalFocusingMethod:
    def __init__(self, velocity, rate, step):
        self.velocity = velocity
        self.rate = rate
        self.step = step

    def reconstruct(self, matrix, minX, maxX, minY, maxY, pixSize):
        velocity = self.velocity
        rate = self.rate
        if type(matrix) == list:
            number = len(matrix)
        else:
            number = matrix.shape[0]
        step = self.step
        probes = Probes(number, step)

        resolution = 1/pixSize
        width = int((maxX - minX) * resolution)
        height = int((maxY - minY) * resolution)

        image_array = np.zeros((width, height))

        print('Resolution:', resolution)
        print('Image size:', image_array.shape)
        print('Number of pixels:', image_array.size)
        print('Number of iterations:', image_array.size * number**2)

        for x in range(width):
            print(int(x/width*100))
            for y in range(height):
                for t, transmitter in probes.items():
                    for r, receiver in probes.items():
                        pixel = (x / resolution + minX, y / resolution + minY)
                        distance = dist(transmitter, pixel) + dist(pixel, receiver)
                        delay = distance / velocity
                        sample = int(delay * rate)
                        if len(matrix[t][r]) > sample :
                            image_array[x][y] += matrix[t][r][sample]
        return image_array
