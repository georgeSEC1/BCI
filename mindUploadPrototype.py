#BCI - brain computer interface technology. 
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
import random
NNvar = 50#work on continually adequate samples throughout short ngrams and long n-grams alike
partition = 10
sampleSize = 2
graphemeBlock = 0
com = "COM3"
baud = 9600 
option = ""
targetSize = 8
def delay(ngram):
    print()
    print(ngram)
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    time.sleep(1)
    return
def returnNgrams(data,length, mode):
    if mode == "sequential":
        ngram = ""
        pos = random.randint(1,len(data))
        n = 0
        while(n < length and pos+length < len(data)-1):
            if pos+n < len(data)-2 and pos+n > 0:
                ngram += data[pos+n] + " "
            n+=1
        delay(ngram)
        return ngram
    if mode == "random":
        ngram = ""
        pos = random.randint(1,len(data))
        n = 0
        while(n < length and pos+length < len(data)-1):
            pos = random.randint(1,len(data))
            if pos+n < len(data)-2 and pos+n > 0:
                ngram += data[pos+n] + " "
            n+=1
        delay(ngram)
        return ngram
def train(dataFile,modelName):
    with open(dataFile, encoding='ISO-8859-1') as f:
        text = f.readlines()
    varX = text[0].count(",")
    dataset = np.loadtxt(dataFile, delimiter=',',usecols = range(varX+1))
    X = dataset[:,0:varX]
    y = dataset[:,varX]
    model = Sequential()
    model.add(Dense(120, input_shape=(X.shape[-1],), activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y, epochs=150, batch_size=10, verbose=1)
    model.save(modelName)
def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out
def recordData(ngram,stress,dataFile):#Adversarial training between easy and difficult n-grams, full 2d grapheme differentiation...
    ser = serial.Serial(com, baud, timeout = 0.1) 
    record = ""
    i = 0
    outputA = ""
    outputB = ""
    graphemeBlock = round(NNvar/partition)
    while ser.isOpen():
        var = ser.readline().decode('utf-8')
        if len(var) > 0:
            record += var.strip() + ","
            print(var.strip())
            if i == NNvar:
                word = ngram
                data = chunkIt(record,graphemeBlock)
                count = 0
                procX = 0
                for seg in data:
                    seg = list(filter(None, seg.split(",")))
                    print(seg, "=", count)
                    outputA += ','.join(seg) + "," + str(stress) + "\n"
                    outputB += ngram[count]
                    count+=1
                i = 0
                break
            i+=1
    testX = open(dataFile, "a", encoding="utf8")
    testX.write(outputA)
    testX.close()
    with open(dataFile, encoding='ISO-8859-1') as f:#post processing
        text = f.read()
    total = ""
    text = text.split("\n")
    for line in text:
        line = line.split(",")
        line = line[-partition:]
        total += ','.join(line)+"\n"
    total = total.replace("\n\n","\n")
    proc = open(dataFile, "w", encoding="utf8")
    proc.write(total)
    proc.flush()
    proc.close()
    return dataFile
def predict(inputFile,model):#refactor into construction using gen() input rather than record() input
    db = []
    model = keras.models.load_model(model)
    dataset = np.loadtxt(inputFile, delimiter=',')
    with open(inputFile, encoding='ISO-8859-1') as f:
        textC = f.readlines()
    varX = textC[0].count(",")
    X = dataset[:,0:varX]
    predictions = (model.predict(X)).astype(int)
    for i in range(len(predictions)):
        if predictions[i] == 0:
            db.append(str(0))
        if predictions[i] == 1:
            db.append(str(1))
        print('%s => %d' % (X[i].tolist(), predictions[i]))
    return db
while(True):
    with open("xaa", encoding='ISO-8859-1') as f:
        data = f.read().split(" ")
    option = input("train or initialise? [t/i]:")
    if option == "t":
        for i in range(sampleSize):
            train(recordData(returnNgrams(data,targetSize,"random"),1, "SignalData.csv"),"stress_model")#mode,stress,outputFile,saved model
        for i in range(sampleSize):
            train(recordData(returnNgrams(data,targetSize,"sequential"),0, "SignalData.csv"),"relax_model")#mode,stress,outputFile,saved model
    if option == "i":
        predict(recordData(returnNgrams(data,targetSize,"sequential"),0,"SignalInitData.csv"),"stress_model")