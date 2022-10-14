#Mind uploading technology 
#Copyright (C) 2022 George Wagenkencht
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
import serial
import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tensorflow as tf
import numpy as np
from collections import deque
import time
NNvar = 25
graphemeBlock = 0
com = "COM3"
baud = 9600 
option = ""
def train():#Adversarial training between easy and difficult n-grams... Then simulation...
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
        text = f.readlines()
    varX = text[0].count(",")
    dataset = np.loadtxt("uploadedSignalData.csv", delimiter=',',usecols = range(varX+1))
    X = dataset[:,0:varX]
    y = dataset[:,varX]
    model = Sequential()
    model.add(Dense(120, input_shape=(X.shape[-1],), activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y, epochs=150, batch_size=10, verbose=1)
    model.save('my_model')
def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out
def record():
    ser = serial.Serial(com, baud, timeout = 0.1) 
    record = ""
    i = 0
    testA = open("uploadedSignalData.csv", "a", encoding="utf8")
    testB = open("uploadedGraphemeData.csv", "a", encoding="utf8")
    while ser.isOpen():
        var = ser.readline().decode('utf-8')
        if len(var) > 0:
            record += var.strip() + ","
            print(var.strip())
            if i == NNvar:
                word = input("Label word for signal data:")
                graphemeBlock = len(word)
                data = chunkIt(record,graphemeBlock)
                count = 0
                procX = 0
                for seg in data:
                    seg = list(filter(None, seg.split(",")))
                    if procX == 0:
                        procX = len(seg)-1
                        print(procX)
                    seg = seg[:procX]
                    print(seg, "=", count)
                    testB.write(input("Label data for segment:") +"\n")#todo,automatically recognise difficulty/effort per syllable
                    testB.flush()
                    testA.write(','.join(seg) + "," + input("Stress detected? [1 or 0](WIP):")+ "\n")#todo,automatically recognise difficulty/effort per syllable
                    testA.flush()
                    count+=1
                i = 0
                break
            i+=1
    testA.close()
    testB.close()
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:#post processing
        text = f.read().replace(",\n","\n").replace("\n,","\n")
    proc = open("uploadedSignalData.csv", "w", encoding="utf8")
    proc.write(text)
    proc.flush()
    proc.close()
    return record
def gen(text):#refactor into construction using gen() input rather than record() input
    db = []
    model = keras.models.load_model('my_model')
    with open("uploadedGraphemeData.csv", encoding='ISO-8859-1') as f:
        text = f.readlines()
    analysis = open("analysis.csv", "a", encoding="utf8")
    for grapheme in text:
        proc = 0
        try:
            proc = text.index(grapheme)
        except:
            proc = 0
        with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
            textB = f.readlines()
        analysis.write(textB[proc])
        analysis.flush()
    analysis.close()
    dataset = np.loadtxt('analysis.csv', delimiter=',')
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
        text = f.readlines()
    varX = text[0].count(",")
    X = dataset[:,0:varX]
    predictions = (model.predict(X) > 0.5).astype(int)
    for i in range(len(X)):
        if predictions[i] == 0:
            db.append(False)
        if predictions[i] == 1:
            db.append(True)
        print('%s => %d' % (X[i].tolist(), predictions[i]))
    return db
while(True):
    option = input("record, train or generate mental structure? [r/t/g]:")
    if option == "r":
        record()
    if option == "t":
        train()
    if option == "g":
        db = gen(input("Enter text:"))
        print(db)