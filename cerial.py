import serial
import time
import os
s = serial.Serial(port='/dev/cu.usbmodemHIDPC1', baudrate=115200, timeout=0.1)

emojis = os.listdir(f'allEmojiUnicodes')
customs = os.listdir(f'allCustomIDs')
emoji_type = 0
num_icons = len(emojis)

bitmap_prefix = 'allEmojiBitmaps'
code_prefix = 'allEmojiUnicodes'

while True:
    found = -1
    signal = s.readline()
    if signal != b'':
        print(signal)
        found = int(signal)

    if found > -1:
        for sect in range(3): # Send 3 icons per row
            if found * 3 + sect < num_icons: 
                file = open(f'{bitmap_prefix}/{found * 3 + sect}.txt', 'r')
                lines = file.readlines()

                for line in lines:
                    s.write(bytes(line.strip() + '\n', 'utf-8'))
                    time.sleep(0.00003)
                
                file = open(f'{code_prefix}/{found * 3 + sect}.txt', 'r')
                lines = file.readlines()

                s.write(bytes('u' + lines[0].strip() + '\n', 'utf-8'))
            else: # No file found, send a blank
                for x in range(2304):
                    s.write(bytes('0\n', 'utf-8'))
                    time.sleep(0.00003)
                
                s.write(bytes('u' + '' + '\n', 'utf-8'))
                
    elif found == -2:
        if emoji_type == 0:
            emoji_type = 1
            num_icons = len(customs)
            bitmap_prefix = 'allCustomBitmaps'
            code_prefix = 'allCustomIDs'
            s.write(bytes('a', 'utf-8'))
        else:
            emoji_type = 0
            num_icons = len(emojis)
            bitmap_prefix = 'allEmojiBitmaps'
            code_prefix = 'allEmojiUnicodes'
            s.write(bytes('a', 'utf-8'))
