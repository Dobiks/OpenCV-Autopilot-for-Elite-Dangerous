from PIL import ImageGrab
from numpy.core.fromnumeric import mean
from numpy.lib.type_check import imag
import time
from pynput import keyboard
import cv2 
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from mss import mss
from scipy import ndimage
import statistics

mon = {'left': 860, 'top': 960, 'width': 220, 'height': 320}

with mss() as sct:
    counter = 0
    mass_center=(0,0)
    while True:
        screenShot = sct.grab(mon)
        img = Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.rgb, 
        )
        
        src = np.array(img)

        ret, thresh1 = cv2.threshold(src, 180, 255, cv2.THRESH_BINARY)
        gray = cv2.cvtColor(thresh1, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                    param1=70, param2=20,
                                    minRadius=37, maxRadius=43)


        if circles is not None:
            counter = counter + 1
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                # circle center
                cv2.circle(src, center, 1, (0, 100, 100), 2)
                # circle outline
                radius = i[2]
                cv2.circle(src, center, radius, (255, 0, 255), 2)
                ax1=center[0]-40
                ay1=center[1]-40
                ax2=center[0]+40
                ay2=center[1]+40
                #print(radius)
                radar = gray[ay1:ay2,ax1:ax2]
                ret, radar = cv2.threshold(radar, 180, 255, cv2.THRESH_BINARY)
                try:
                    mass_center = ndimage.measurements.center_of_mass(radar)
                    mass_center = (int(mass_center[1]),int(mass_center[0]))
                    cv2.circle(radar, mass_center, 1, (255, 0, 255), 1)
                    radar = cv2.resize(radar, (200,200), interpolation = cv2.INTER_AREA)
                except:
                    pass
                if counter%10==0:
                    print(mass_center)


        try:
            cv2.imshow('radar', np.array(radar))
            cv2.imshow('test', np.array(src))
            if cv2.waitKey(33) & 0xFF in (
                ord('q'), 
                27, 
            ):
                break
        except:
            pass



