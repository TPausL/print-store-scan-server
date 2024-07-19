import cv2 as cv
import numpy as np
import random as rng
import os


rng.seed(1234)


"""
    Analyses the color of the image by trying to cut the background off and averaging the color of the remaining image.
"""
def analyze_color(image: cv.typing.MatLike):

    cv.imwrite("add_color_image.jpeg" , image)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    threshold = 110
    _, mask = cv.threshold(image_gray, threshold, threshold, 1 )

    cv.imwrite("add_color_mask.jpeg" , mask)

    mean = cv.mean(image,mask)
    mean_rgb = cv.cvtColor(np.uint8([[mean[0:3]]]), cv.COLOR_BGR2RGB)[0][0]
    print(mean_rgb)
    hex_str = '#%02x%02x%02x' % tuple(mean_rgb)
    return hex_str


"""
Try to find which color is a (the best match) for the product in the image, by comparing the image to each color (thresholds) in the DB and within a certain range considering the biggest as a match
"""
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
        cv.imwrite("im_threshold" + str(i)  + ".jpeg" , image_threshold)

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


