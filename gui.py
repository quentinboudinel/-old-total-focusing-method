import os
from random import randint
from tkinter import Tk, Frame, LabelFrame, Label, Entry, Button, Radiobutton
from tkinter import StringVar
from tkinter import BOTH, LEFT, RIGHT, X
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pickle
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

from tfm import Material, Signal, Probes, TotalFocusingMethod

class Gui(Tk):
    def __init__(self):
        super().__init__()

        self.title('Total Focusing Method GUI')
        self.resizable(width=False, height=False)

        """
            COMMON VARs
        """
        self.velocityVar = StringVar()
        self.velocityVar.set("1490")
        self.rateVar = StringVar()
        self.rateVar.set("20")
        self.stepVar = StringVar()
        self.stepVar.set("1")

        """
            FMC FRAME
        """
        self.defectsVar = list()
        self.defectsVar.append((StringVar(), StringVar()))
        self.defectsVar[0][0].set("0")
        self.defectsVar[0][1].set("0")
        self.frequencyVar = StringVar()
        self.frequencyVar.set("10")
        self.periodsVar = StringVar()
        self.periodsVar.set("3")
        self.numberVar = StringVar()
        self.numberVar.set("4")

        fmcFrame = LabelFrame(self, text='Full Matrix Capture Simulation')

        #Material paramters
        materialFrame = LabelFrame(fmcFrame, text='Material')
            #Velocity
        velocityFrame = Frame(materialFrame)
        velocityLabel = Label(velocityFrame, text='Velocity (m/s) =')
        velocityEdit = Entry(velocityFrame, textvariable=self.velocityVar)
        velocityLabel.pack(side=LEFT)
        velocityEdit.pack(side=RIGHT)
            #Defects
        defectsHeadFrame = Frame(materialFrame)
        defectsLabelFmc = Label(defectsHeadFrame, text='Defects (mm, mm):')
        defectsFrame = Frame(materialFrame)
        defectFrames = list()
        defectFrames.append(Frame(defectsFrame))
        defectEditFmcX = Entry(defectFrames[-1], textvariable=self.defectsVar[-1][0])
        defectEditFmcY = Entry(defectFrames[-1], textvariable=self.defectsVar[-1][1])
        defectEditFmcX.pack(side=LEFT)
        defectEditFmcY.pack(side=LEFT)
        defectFrames[-1].pack()

        def delDefect():
            self.defectsVar.pop()
            defectFrames[-1].pack_forget()
            defectFrames.pop()

            if len(self.defectsVar) < 2:
                defectsDelButtonFmc.pack_forget()

        def addDefect():
            self.defectsVar.append((StringVar(), StringVar()))
            self.defectsVar[-1][0].set(randint(-10, 10))
            self.defectsVar[-1][1].set(randint(0, 10))
            defectFrames.append(Frame(defectsFrame))
            defectEditFmcX = Entry(defectFrames[-1], textvariable=self.defectsVar[-1][0])
            defectEditFmcY = Entry(defectFrames[-1], textvariable=self.defectsVar[-1][1])
            defectEditFmcX.pack(side=LEFT)
            defectEditFmcY.pack(side=LEFT)
            defectFrames[-1].pack()

            if len(self.defectsVar) > 1:
                defectsDelButtonFmc.pack(side=LEFT)

        defectsButtonsFrame = Frame(defectsHeadFrame)
        defectsAddButtonFmc = Button(defectsButtonsFrame, text='+', command=addDefect)
        defectsDelButtonFmc = Button(defectsButtonsFrame, text='-', command=delDefect)
        defectsAddButtonFmc.pack(side=LEFT)

        defectsLabelFmc.pack(side=LEFT)
        defectsButtonsFrame.pack(side=LEFT)

        velocityFrame.pack(expand=True, fill=X, padx=100)
        defectsHeadFrame.pack()
        defectsFrame.pack()

        #Signal parameters
        signalFrame = LabelFrame(fmcFrame, text='Signal')
            #Signal frequency
        frequencyFrame = Frame(signalFrame)
        frequencyLabel = Label(frequencyFrame, text='Signal frequency (MHz) =')
        frequencyEdit = Entry(frequencyFrame, textvariable=self.frequencyVar)
        frequencyLabel.pack(side=LEFT)
        frequencyEdit.pack(side=RIGHT)
            #Number of periods
        numberFrame = Frame(signalFrame)
        periodsLabel = Label(numberFrame, text='Number of periods =')
        periodsEdit = Entry(numberFrame, textvariable=self.periodsVar)
        periodsLabel.pack(side=LEFT)
        periodsEdit.pack(side=RIGHT)
            #Sampling sampling
        rateFrame = Frame(signalFrame)
        rateLabel = Label(rateFrame, text='Sampling rate (MHz) =')
        rateEdit = Entry(rateFrame, textvariable=self.rateVar)
        rateLabel.pack(side=LEFT)
        rateEdit.pack(side=RIGHT)

        frequencyFrame.pack(expand=True, fill=X, padx=100)
        numberFrame.pack(expand=True, fill=X, padx=100)
        rateFrame.pack(expand=True, fill=X, padx=100)

        #Probes parameters
        probesFrame = LabelFrame(fmcFrame, text='Probes')
            #Number
        numberFrame = Frame(probesFrame)
        numberLabel = Label(numberFrame, text='Number of probes =')
        numberEdit = Entry(numberFrame, textvariable=self.numberVar)
        numberLabel.pack(side=LEFT)
        numberEdit.pack(side=RIGHT)
            #Step
        stepFrame = Frame(probesFrame)
        stepLabel = Label(stepFrame, text='Step between probes (mm) =')
        stepEdit = Entry(stepFrame, textvariable=self.stepVar)
        stepLabel.pack(side=LEFT)
        stepEdit.pack(side=RIGHT)


        numberFrame.pack(expand=True, fill=X, padx=100)
        stepFrame.pack(expand=True, fill=X, padx=100)

        materialFrame.pack(fill=X, padx=10)
        signalFrame.pack(fill=X, padx=10)
        probesFrame.pack(fill=X, padx=10)

        generateButton = Button(fmcFrame, text='Generate and save data', command=self.generateData)
        generateButton.pack()

        """
            TFM FRAME
        """
        self.pathVar = StringVar()
        self.pathVar.set('')
        self.minX = StringVar()
        self.minX.set('-16')
        self.maxX = StringVar()
        self.maxX.set('16')
        self.minY = StringVar()
        self.minY.set('0')
        self.maxY = StringVar()
        self.maxY.set('25')
        self.pixSizeVar = StringVar()
        self.pixSizeVar.set('0.030')

        tfmFrame = LabelFrame(text='Total Focusing Method')

        #Data frame
        dataFrame = LabelFrame(tfmFrame, text='Select data')
        dataLabel = Label(dataFrame, text='Selected data:')
        dataEntry = Entry(dataFrame, text=self.pathVar)
        dataButton = Button(dataFrame, text='Browse capture data', command=self.browse)

        dataLabel.pack(side=LEFT)
        dataEntry.pack(expand=True, fill=X, side=LEFT, padx=10)
        dataButton.pack(side=LEFT)

        #Parameters frame
        parametersFrame = Frame(tfmFrame)

        velocityFrame = Frame(parametersFrame)
        velocityLabel = Label(velocityFrame, text='Velocity (m/s) =')
        velocityEdit = Entry(velocityFrame, textvariable=self.velocityVar)

        velocityLabel.pack()
        velocityEdit.pack()

        samplingFrame = Frame(parametersFrame)
        samplingLabel = Label(samplingFrame, text='Sampling rate (MHz) =')
        samplingEdit = Entry(samplingFrame, textvariable=self.rateVar)

        samplingLabel.pack()
        samplingEdit.pack()

        stepFrame = Frame(parametersFrame)
        stepLabel = Label(stepFrame, text='Step (mm) =')
        stepEdit = Entry(stepFrame, textvariable=self.stepVar)

        stepLabel.pack()
        stepEdit.pack()

        velocityFrame.pack(side=LEFT, expand=True, fill=BOTH)
        samplingFrame.pack(side=LEFT, expand=True, fill=BOTH)
        stepFrame.pack(side=LEFT, expand=True, fill=BOTH)

        #Imaging frame
        imagingFrame = LabelFrame(tfmFrame, text='Image reconstruction')

        sizeFrame = Frame(imagingFrame)
        widthFrame = LabelFrame(sizeFrame, text='Width')
        minXLabel = Label(widthFrame, text='minX (mm) =')
        minXEdit = Entry(widthFrame, textvariable=self.minX)
        maxXLabel = Label(widthFrame, text='maxX (mm) =')
        maxXEdit = Entry(widthFrame, textvariable=self.maxX)

        minXLabel.pack()
        minXEdit.pack()
        maxXLabel.pack()
        maxXEdit.pack()

        heightFrame = LabelFrame(sizeFrame, text='Height')
        minYLabel = Label(heightFrame, text='minY (mm) =')
        minYEdit = Entry(heightFrame, textvariable=self.minY)
        maxYLabel = Label(heightFrame, text='maxY (mm) =')
        maxYEdit = Entry(heightFrame, textvariable=self.maxY)

        minYLabel.pack()
        minYEdit.pack()
        maxYLabel.pack()
        maxYEdit.pack()

        pixSizeAndButtonFrame = Frame(sizeFrame)
        pixelSizeLabel = Label(pixSizeAndButtonFrame, text='Pixel size (mm) =')
        pixelSizeEdit = Entry(pixSizeAndButtonFrame, textvariable=self.pixSizeVar)
        reconstructButton = Button(pixSizeAndButtonFrame, text='Reconstruct', command=self.reconstruct)

        pixelSizeLabel.pack()
        pixelSizeEdit.pack()
        reconstructButton.pack()

        widthFrame.pack(side=LEFT, expand=True, fill=X)
        heightFrame.pack(side=LEFT, expand=True, fill=X)
        pixSizeAndButtonFrame.pack(side=LEFT, padx=10)

        sizeFrame.pack(fill=X)

        dataFrame.pack(fill=X, padx=10, pady=10)
        parametersFrame.pack(fill=X, padx=10)
        imagingFrame.pack(expand=True, fill=BOTH, padx=10, pady=10)

        fmcFrame.pack(fill=X)
        tfmFrame.pack(fill=X)

    def browse(self):
        initialdir = os.path.dirname(os.path.abspath(__file__)) + '/Data'
        self.pathVar.set(askopenfilename(initialdir=initialdir))

    def getMaterialParameters(self):
        velocity = float(self.velocityVar.get())
        defects = list()
        for defectVar in self.defectsVar:
            x = float(defectVar[0].get()) / 1000
            y = float(defectVar[1].get()) / 1000
            defects.append((x, y))
        return velocity, defects

    def getSignalParameters(self):
        frequency = float(self.frequencyVar.get()) * 10**6
        periods = int(self.periodsVar.get())
        rate = float(self.rateVar.get()) * 10**6
        return frequency, periods, rate

    def getProbesParameters(self):
        number = int(self.numberVar.get())
        step = float(self.stepVar.get()) / 1000
        return number, step

    def generateData(self):
        data = dict()

        velocity, defects = self.getMaterialParameters()
        material = Material(velocity, defects)
        frequency, periods, rate = self.getSignalParameters()
        signal = Signal(frequency=frequency, periods=periods, rate=rate)

        number, step = self.getProbesParameters()
        probes = Probes(number, step, signal)

        matrix = probes.scan(material)
        initialdir = os.path.dirname(os.path.abspath(__file__)) + '/Data'
        path = asksaveasfilename(initialdir=initialdir)
        if not path.endswith('.fmcs'):
            path += '.fmcs'
        with open(path, 'wb') as file:
            pickle.dump(matrix, file)

    def getMatrix(self, path):
        if '.fmcs' in path:
            with open(path, 'rb') as file:
                matrix = pickle.load(file)
        else:
            with open(path, 'rb') as file:
                data = file.read()
                number = int(np.sqrt(np.frombuffer(data[0:4], np.int32)[0]))
                length = np.frombuffer(data[4:8], np.int32)[0]
                matrix = np.frombuffer(data[8:], np.int16).reshape(number, number, length)
        return matrix

    def reconstruct(self):
        path = self.pathVar.get()
        matrix = self.getMatrix(path)

        velocity = float(self.velocityVar.get())
        rate = float(self.rateVar.get()) * 10**6
        step = float(self.stepVar.get()) / 1000

        tfm = TotalFocusingMethod(velocity, rate, step)

        minX = float(self.minX.get()) / 1000
        maxX = float(self.maxX.get()) / 1000
        minY = float(self.minY.get()) / 1000
        maxY = float(self.maxY.get()) / 1000
        pixSize = float(self.pixSizeVar.get()) / 1000

        image = tfm.reconstruct(matrix, minX, maxX, minY, maxY, pixSize)

        fig = plt.imshow(np.transpose(image))
        plt.show()

def main():
    root = Gui()
    root.mainloop()

if __name__=='__main__':
    main()
