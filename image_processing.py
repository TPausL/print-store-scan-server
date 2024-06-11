import cv2 as cv
import numpy as np
import argparse
import matplotlib.pyplot as plt
import mpl_toolkits
import time
import random as rng
import os
#from calibrate import get_color_thresholds

""" def read_thresholds(filename):
    with open(filename) as file:
        lines = file.readlines()
        names = []
        thresholds = np.ndarray(shape= (len(lines),2,3))
        for (i,l) in enumerate(lines):
            l = l.split(";")
            thresholds[i][0] = l[1].split(",")
            thresholds[i][1] = l[2].split(",")
            names.append(l[0])
        return thresholds,names """

rng.seed(1234)



def analyze_color(image: cv.typing.MatLike):
    image = cv.resize(image,None, fx=0.3, fy=0.3,interpolation=cv.INTER_LINEAR)
    cv.imwrite("add_color_image.jpeg" , image)

    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    threshold = 80
    _, mask = cv.threshold(image_gray, threshold, threshold, 1 )

    cv.imwrite("add_color_mask.jpeg" , mask)

    mean = cv.mean(image,mask)
    mean_rgb = cv.cvtColor(np.uint8([[mean[0:3]]]), cv.COLOR_BGR2RGB)[0][0]
    hex_str = "#" + "".join([hex(int(i)).split("x")[1] for i in mean_rgb[0:3]])
    return hex_str


    
def classify_color(image: cv.typing.MatLike,thresholds):
    
    image_HSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    possible_colors = []
    min_area_size = (image.size/3)* float(os.getenv("FACTOR_MIN_AREA", 1))/100
    max_area_size = (image.size/3)*float(os.getenv("FACTOR_MAX_AREA", 40))/100

    for i in range(len(thresholds)):
        image_threshold = cv.inRange(image_HSV, thresholds[i][0], thresholds[i][1])

        dilate_size = int(os.getenv("FACTOR_DILATE", 20))
        dilate_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2*dilate_size + 1, 2*dilate_size+1), (dilate_size, dilate_size))
        image_threshold = cv.dilate(image_threshold,dilate_kernel)
        contours, _ = cv.findContours(image_threshold, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if(len(contours) <= 0): 
            continue
        contour = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)[0]
        area = cv.contourArea(contour)
        if area > min_area_size and area < max_area_size:
            possible_colors.append((i,area))

    
    possible_colors  = sorted(possible_colors,key=lambda x: x[1],reverse=True)
    if(len(possible_colors) <= 0):
        return -1
    color = possible_colors[0][0]
    if color == None:
        return -1
    return color

#parser = argparse.ArgumentParser(description='Code for detecting color off the biggest object in image')
#parser.add_argument('--thresholds',"-t", help='Path to file that contains color value thresholds. \n (Format of file: [name;low_h,low_s,low_v;high_h,high_s,high_v])', default="thresholds.csv", type=str)
#parser.add_argument('--input',"-i",required=True, help='File to scan', type=str)
#args = parser.parse_args()



