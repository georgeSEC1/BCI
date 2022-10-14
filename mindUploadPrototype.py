import serial
import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tensorflow as tf
import numpy as np
from collections import deque
NNvar = 30
graphemeBlock = 0
com = "COM3"
baud = 9600 
option = ""
def train():#fix training
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
        text = f.readlines()
    varX = text[0].count(",")-1
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
                    testA.write(','.join(seg) + "\n")#todo,automatically recognise difficulty/effort per syllable
                    testA.flush()
                    testB.write(input("Label data for segment:") +"\n")#todo,automatically recognise difficulty/effort per syllable
                    testB.flush()
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
def gen(text):
    db = []
    model = keras.models.load_model('my_model')
    with open("uploadedGraphemeData.csv", encoding='ISO-8859-1') as f:
        text = f.readlines()
    for grapheme in text:
        proc = 0
        try:
            proc = text.index(grapheme)
        except:
            proc = 0
        print(proc, grapheme.strip())
        with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
            textB = f.readlines()
        analysis = open("analysis.csv", "a", encoding="utf8")
        analysis.write(textB[proc])
        analysis.flush()
        analysis.close()
        dataset = np.loadtxt('analysis.csv', delimiter=',')
        with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
            text = f.readlines()
        varX = text[0].count(",")-1
        X = dataset[:,0:varX]
        predictions = (model.predict(X) > 0.5).astype(int)
        print('%s => %d' % (X[0].tolist(), predictions[0]))
    return db
while(True):
    option = input("record, train or generate mental structure:[r/t/g]")
    if option == "r":
        record()
    if option == "t":
        train()
    if option == "g":
        gen(input("Enter text:"))