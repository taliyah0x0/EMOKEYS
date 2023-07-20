
# EMOKEYS by Taliyah
# Run this code immediately after plugging in EMOKEYS to your laptop

import serial
import time
import os
s = serial.Serial(port='/dev/cu.usbmodemHIDPC1', baudrate=115200, timeout=0.1) # Check that the port name matches

emojis = os.listdir(f'allEmojiUnicodes')
customs = os.listdir(f'allCustomIDs')
emoji_type = 0 # emoji (0) or discord emote (1)
num_icons = len(emojis)

bitmap_prefix = 'allEmojiBitmaps'
code_prefix = 'allEmojiUnicodes'

# Run on loop until stopped with CTRL + C on Terminal
while True:
    found = -1
    signal = s.readline()
    if signal != b'':
        found = int(signal)
        print(signal)

    if found > -1: # Received cue to send bitmap array
        for sect in range(3): # Send 3 icons per row
            if found * 3 + sect < num_icons: 
                file = open(f'{bitmap_prefix}/{found * 3 + sect}.txt', 'r')
                lines = file.readlines()

                for line in lines:
                    s.write(bytes(line.strip() + '\n', 'utf-8'))
                    time.sleep(0.000032)
                
                # Also send the corresponding unicode/ID to be used in printing
                file = open(f'{code_prefix}/{found * 3 + sect}.txt', 'r')
                lines = file.readlines()

                s.write(bytes('u' + lines[0].strip() + '\n', 'utf-8'))

            else: # No file found, send a blank of all black
                for x in range(2304):
                    s.write(bytes('0\n', 'utf-8'))
                    time.sleep(0.000032)
                
                # Unicode/ID will also be blank
                s.write(bytes('u' + '' + '\n', 'utf-8'))
                
    elif found == -2: # Received cue to toggle between emojis and discord emotes
        if emoji_type == 0:
            emoji_type = 1
            num_icons = len(customs)
            bitmap_prefix = 'allCustomBitmaps'
            code_prefix = 'allCustomIDs'
            s.write(bytes('a', 'utf-8')) # Cue Arduino to load all displays to discord emotes
        else:
            emoji_type = 0
            num_icons = len(emojis)
            bitmap_prefix = 'allEmojiBitmaps'
            code_prefix = 'allEmojiUnicodes'
            s.write(bytes('a', 'utf-8')) # Cue Arduino to load all displays to emojis
