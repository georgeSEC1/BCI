import serial
duration = 50
com = "COM3"
baud = 9600 
i = 0
option = ""
def record():
    ser = serial.Serial(com, baud, timeout = 0.1) 
    record = ""
    i = 0
    test = open("uploadedData.csv", "a", encoding="utf8")
    while ser.isOpen():
        var = ser.readline().decode('utf-8')
        if len(var) > 0:
            record += var.strip() + ","
            print(var.strip())
            if i == duration:
                record = record[:-1]
                test.write(record + "," + input("Please label data: ") +"\n")
                test.flush()
                i = 0
                break
            i+=1
    test.close()
    return record
while(True):
    option = input("manual record electrical impulses for x duration, press enter to begin")
    record()