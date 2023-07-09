import serial
import time
import os
s = serial.Serial(port='/dev/cu.usbmodemHIDPC1', baudrate=115200, timeout=0.1)

emojis = os.listdir(f'allEmojiUnicodes')
num_emojis = len(emojis)

while True:
    found = -1
    signal = s.readline()
    if signal != b'':
        print(signal)
        if str(signal)[2] == 'u':
            if int(str(signal)[3:-1]) < num_emojis:
                file = open(f'allEmojiUnicodes/{int(str(signal)[3:-1])}.txt', 'r')
                lines = file.readlines()

                s.write(bytes(lines[0].strip(), 'utf-8'))
            else:
                s.write(bytes('', 'utf-8'))
        else:
            found = int(signal)

    if found > -1:
        for sect in range(3):
            if found * 3 + sect < num_emojis:
                file = open(f'allEmojiBitmaps/{found * 3 + sect}.txt', 'r')
                lines = file.readlines()

                for line in lines:
                    s.write(bytes(line.strip() + '\n', 'utf-8'))
                    time.sleep(0.000028)
                
                file = open(f'allEmojiUnicodes/{found * 3 + sect}.txt', 'r')
                lines = file.readlines()

                s.write(bytes('u' + lines[0].strip() + '\n', 'utf-8'))
            else:
                for x in range(2304):
                    s.write(bytes('0\n', 'utf-8'))
                    time.sleep(0.000025)
