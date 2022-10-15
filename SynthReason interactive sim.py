# SynthReason - Synthetic Dawn - Intelligent symbolic manipulation
# BSD 2-Clause License
# 
# Copyright (c) 2022, GeorgeSEC1 - George Wagenknecht
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import random
import re
iterations = 3
targetNgramSize = 3
token = " a "
mentalRules = ""
if len(mentalRules) == 0:
   mentalRules = input("Please paste mental rules into the simulation:")
def formatSentences(sync):
    sentences = sync.split(".")
    i = 0
    total = ""
    for sentence in sentences:
        total += sentence + ". " 
    proc = convert(total)
    totalB = ""
    n = 0
    while(n < len(proc)-7):
        if proc[n] != proc[n+1] and proc[n] != proc[n+2] and proc[n] != proc[n+3] and proc[n] != proc[n+4] and proc[n] != proc[n+5] and proc[n] != proc[n+6] :
            totalB += proc[n] + " "   
        n+=1
    return totalB[:-1] + "."
def branch(data,user,mentalRules): 
    words = sorted(user.split(" "))
    total = ""
    for word in words:
        for i in range(len(mentalRules)-1):
            ruleA = mentalRules[i]
            ruleB = mentalRules[i+1]
            try:
                ini = random.randint(1,len(data))
                string = convert(returnWords(data,data.index(word,ini),targetNgramSize))
                for index in string:
                    ini = random.randint(1,len(data))
                    if ruleA[1] == '0' and ruleB[1] == '1':
                        if index.find(ruleA[0]) < index.find(ruleB[0]) :
                            total += index + " "
            except:
                total
        if len(convert(total)) > 100:
            break
    return total
def convert(lst):
    return (lst.split())
def gather(user,file):
    with open(file, encoding='ISO-8859-1') as f:
        text = f.read()
    sentences = text.split(token)
    data = text.split(".")
    output = ""
    i = 0
    j = 0
    words = convert(user)
    while(i < len(sentences)-1):
        if len(sentences[i]) > 0 and i <len(sentences)-2 and i <len(data)-2:
            for word in words:
                try:
                    if sentences[i].find(" " + word + " ") > -1 or sentences[i].find(".",data[j].find(data[j+1])+1) > -1:
                        output += sentences[i] + token
                        j+=1
                except:
                    output
        i+=1
    return output
def returnWords(dataX,pos,length):
    ngram = ""
    n = 0
    while(n < length and pos+length < len(dataX)-1):
        if pos+n < len(dataX)-2 and pos+n > 0:
            ngram += dataX[pos+n] + " "
        n+=1
    return ngram
with open("fileList.conf", encoding='ISO-8859-1') as f:
    files = f.readlines()
    print("SynthReason - Synthetic Dawn")
    with open("questions.conf", encoding='ISO-8859-1') as f:
    	questions = f.readlines()
    filename = "Compendium#" + str(random.randint(0,10000000)) + ".txt"
    random.shuffle(questions)
    mentalRules = mentalRules.split(",")
    while(True):
        print()
        user = re.sub('\W+',' ',input("USER: "))
        random.shuffle(files)
        counter = 0
        for file in files: 
            sync = user
            data = convert(gather(user,file.strip()))
            for index in range(iterations):
               sync = branch(data,sync,mentalRules) + sync
            sync = formatSentences(sync.replace('\'', '').replace('\"', '').replace('//', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').replace('-', '').replace('(', '').replace(')', ''))
            print()
            print("using " , file.strip() ,  " answering: " , user)
            print("AI:" ,sync)
            f = open(filename, "a", encoding="utf8")
            f.write("\n")
            f.write("using " + file.strip() + " answering: " + user)
            f.write("\n")
            f.write(sync)
            f.write("\n")
            f.close()
            if len(convert(sync)) >= 0:
                break
