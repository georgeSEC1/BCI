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
import random
NNvar = 50#work on continually adequate samples throughout short ngrams and long n-grams alike
partition = 5
sampleSize = 5
graphemeBlock = 0
com = "COM3"
baud = 9600 
option = ""
targetNgramSize = 3
def returnWords(data,length):
    ngram = ""
    pos = random.randint(1,len(data))
    n = 0
    while(n < length and pos+length < len(data)-1):
        if pos+n < len(data)-2 and pos+n > 0:
            ngram += data[pos+n] + " "
        n+=1
    print()
    print(ngram)
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    time.sleep(1)
    return ngram
def returnRWords(data,length):
    ngram = ""
    pos = random.randint(1,len(data))
    n = 0
    while(n < length and pos+length < len(data)-1):
        pos = random.randint(1,len(data))
        if pos+n < len(data)-2 and pos+n > 0:
            ngram += data[pos+n] + " "
        n+=1
    print()
    print(ngram)
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    time.sleep(1)
    return ngram
def train():
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
def record(ngram,stress):#Adversarial training between easy and difficult n-grams, full 2d grapheme differentiation...
    ser = serial.Serial(com, baud, timeout = 0.1) 
    record = ""
    i = 0
    testX = open("uploadedSignalData.csv", "a", encoding="utf8")
    testY = open("uploadedGraphemeData.csv", "a", encoding="utf8")
    while ser.isOpen():
        var = ser.readline().decode('utf-8')
        if len(var) > 0:
            record += var.strip() + ","
            print(var.strip())
            if i == NNvar:
                word = ngram
                graphemeBlock = round(NNvar/partition)
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
                    testY.write(ngram[count])#todo,automatically recognise difficulty/effort per syllable
                    testY.flush()
                    testX.write(','.join(seg) + "," + str(stress) + "\n")#todo,automatically recognise difficulty/effort per syllable
                    testX.flush()
                    count+=1
                i = 0
                break
            i+=1
    testX.close()
    testY.close()
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:#post processing
        text = f.read().replace(",\n","\n").replace("\n,","\n")
    proc = open("uploadedSignalData.csv", "w", encoding="utf8")
    proc.write(text)
    proc.flush()
    proc.close()
    return record
def gen(inputData):#refactor into construction using gen() input rather than record() input
    db = []
    model = keras.models.load_model('my_model')
    with open("uploadedGraphemeData.csv", encoding='ISO-8859-1') as f:
        text = f.read()
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
        textB = f.readlines()
    analysis = open("analysis.csv", "w", encoding="utf8")
    for grapheme in inputData:
        proc = 0
        proc = text.find(grapheme)
        if proc > -1:
            analysis.write(textB[proc])
            analysis.flush()
    analysis.close()
    dataset = np.loadtxt('analysis.csv', delimiter=',')
    with open("uploadedSignalData.csv", encoding='ISO-8859-1') as f:
        textC = f.readlines()
    varX = textC[0].count(",")
    X = dataset[:,0:varX]
    predictions = (model.predict(X) > 0.5).astype(int)
    with open("uploadedGraphemeData.csv", encoding='ISO-8859-1') as f:
        procData = f.read()
    for i in range(len(X)):
        if predictions[i] == 0:
            db.append(str(inputData[i])+str(0))
        if predictions[i] == 1:
            db.append(str(inputData[i])+str(1))
        print('%s => %d' % (X[i].tolist(), predictions[i]))
    return db
while(True):
    option = input("record, train or generate? [r/t/g]:")
    if option == "r":
        with open("xaa", encoding='ISO-8859-1') as f:
            data = f.read().split(" ")
        for i in range(sampleSize):
            select = random.randint(0,1)
            if select == 0:
                record(returnWords(data,targetNgramSize),0)
            if select == 1:
                record(returnRWords(data,targetNgramSize),1)
    if option == "t":
        train()
    if option == "g":
        db = gen(input("Enter text:"))
        print("Generated rules: ", db)
        GR = open("generatedRules.csv", "w", encoding="utf8")
        GR.write(','.join(db))
        GR.close()
        print("\"generatedRules.csv\" generated, Please paste contents into the simulation script.")        