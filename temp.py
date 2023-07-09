import serial
import time
import os
s = serial.Serial(port='/dev/cu.usbmodem114301', baudrate=115200, timeout=0.1)

while True:
    s.write(bytes('u' + 'd83edef6' + '\n', 'utf-8'))
    time.sleep(1)