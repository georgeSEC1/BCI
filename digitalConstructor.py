with open("uploadedData.csv", encoding='ISO-8859-1') as f:
    text = f.read()
proc = text.split("\n")
#spiking signal analysis
for line in proc:
    db = []
    word = ""
    procB = line.split(",")
    n = 0
    j = 0
    for node in procB: 
        word = procB[len(procB)-1]
        if len(word) > 0 and len(procB) > 0:            
            var = len(word)/len(procB)
            check = []
            for i in range(len(word)):
                check.append(var)#establish syllable lengths
                var+=var 
            if node.isnumeric() == True:
                if j < len(check):
                    if int(node) > 100 and n < check[j]:#detect effort/difficulty
                        db.append(True)
                        n+=1
                    if int(node) < 100 and n < check[j]:#detect effort/difficulty
                        db.append(False)
                        n+=1
                    print(word, check[j],word[j], db[0])
                    j+=1
option = input("analysis done, press enter")
