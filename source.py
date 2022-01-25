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
import pydirectinput

mon = {'left': 860, 'top': 960, 'width': 220, 'height': 320}
mon2 = {'left': 700, 'top': 400, 'width': 1200, 'height': 600}


def press_key(key):
    pydirectinput.keyDown(key)
    time.sleep(0.1)
    pydirectinput.keyUp(key)

with mss() as sct:
    counter = 0
    precise_position_counter = 0
    mass_center=(0,0)
    on_position = 0
    precise_position = 0
    while True:
        screenShot = sct.grab(mon)
        img = Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.rgb, 
        )
        src = np.array(img)

        screenShot = sct.grab(mon2)
        img = Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.rgb, 
        )
        screen_center = np.array(img)

        ret, thresh1 = cv2.threshold(src, 180, 255, cv2.THRESH_BINARY)
        gray = cv2.cvtColor(thresh1, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                    param1=70, param2=20,
                                    minRadius=37, maxRadius=43)


        orange_lower=np.array([120,120,0],np.uint8) #bgr 
        orange_upper=np.array([245,255,12],np.uint8)
        orange=cv2.inRange(screen_center,orange_lower,orange_upper)
        try:
            orange_mass_center = ndimage.measurements.center_of_mass(orange)
            orange_mass_center = (int(orange_mass_center[1]),int(orange_mass_center[0]))
            cv2.circle(screen_center, orange_mass_center, 10, (255, 0, 255), 2)
        except:
            pass

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
                    if on_position == 0: 
                        #print(orange_mass_center)
                        if mass_center[0]<35:
                            press_key('b')
                            print("right")
                        if mass_center[0]>45:
                            press_key('k')
                            print("left")
                        if mass_center[1]<35:
                            press_key('i')
                            print("up")
                        if mass_center[1]>35:
                            press_key('p')
                            print("down")
                        if 45>mass_center[0]>35 and 45>mass_center[1]>35:
                            on_position = 1
                            print("Precise targeting")

        if on_position == 1 and precise_position == 0:
            precise_position_counter = precise_position_counter + 1
            if orange_mass_center[0]<634:
                press_key('a')
                print("left")
                precise_position_counter = 0
            if orange_mass_center[0]>704:
                press_key('d')
                print("right")
                precise_position_counter = 0
            if orange_mass_center[1]<274:
                press_key('i')
                print("up")
                precise_position_counter = 0
            if orange_mass_center[1]>377:
                press_key('p')
                print("down")
                precise_position_counter = 0
            if precise_position_counter == 50:
                precise_position = 1
                print("throttle up")
                press_key('6')
                press_key('j')
                
                



        try:
            cv2.imshow('radar', np.array(radar))
            cv2.imshow('detect radar', np.array(src))
            cv2.imshow('center', np.array(screen_center))

            if cv2.waitKey(33) & 0xFF in (
                ord('q'), 
                27, 
            ):
                break
        except:
            cv2.imshow('Srodek', np.array(screen_center))

            if cv2.waitKey(33) & 0xFF in (
                ord('q'), 
                27, 
            ):
                break

