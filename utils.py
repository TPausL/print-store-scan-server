import cv2
import numpy as np
from typing import Tuple
import os

def hex_to_hsv(hex_code):
    rgb_tuple = tuple(int(hex_code[i+1:i+3], 16) for i in (0, 2, 4))
    hsv_tuple = cv2.cvtColor(np.uint8([[rgb_tuple]]), cv2.COLOR_RGB2HSV)[0][0]
    return hsv_tuple

def get_hsv_threshold(hsv_col: Tuple[int,int,int]):
    factor = float(os.getenv("FACTOR_THRES_GEN", 10))/100
    h,s,v = hsv_col
    h_pro = factor * h
    s_pro = factor * s
    v_pro = factor * v
    return np.array([[max(0,int(h-h_pro)),max(0,int(s-s_pro)),max(0,int(v-v_pro))], [min(180,int(h+h_pro)),min(255,int(s+s_pro)),min(255,int(v+v_pro))]])
    

