import math
import numpy as np
import cv2
import sudoku_solver as ss

from PIL import Image, ImageFilter, ImageEnhance

import pytesseract
from pytesseract import image_to_string

def get_digit(image):

    oh, ow = image.shape[:2]
    area_limit = oh * ow

    contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    cs = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in cs:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 0.05 * area_limit and w * h < 0.8 * area_limit:
            image = image[y:y+h,x:x+w]
            break

    # cv2.imshow('image', image)
    # cv2.waitKey(0)

    pil_img = Image.fromarray(image)
    cstr = image_to_string(pil_img, config='-psm 10')
    if cstr in digits and cstr != '':
        return int(cstr)
    return None

image = cv2.imread('sudoku_03.png')
height, width = image.shape[:2]
image = cv2.resize(image, (2*width, 2*height), interpolation=cv2.INTER_CUBIC)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
r_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 2)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 18))
v_image = cv2.erode(r_image, kernel, iterations = 2)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 18))
v_image = cv2.dilate(v_image, kernel, iterations = 3)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 1))
h_image = cv2.erode(r_image, kernel, iterations = 2)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 2))
h_image = cv2.dilate(h_image, kernel, iterations = 3)

r_image = cv2.add(v_image, h_image)

contours, hierarchy = cv2.findContours(r_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

selected_imgs = []
for c in contours:
    area = cv2.contourArea(c)
    if area > 400 and area < 8000:
        x, y, w, h = cv2.boundingRect(c)
        if abs(w - h) < 10:
            img = image[y:y+h,x:x+w]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            selected_imgs.append((x, y, img))
            cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

cv2.imshow('image', image)
cv2.waitKey(0)

selected_imgs.sort(key=lambda x: x[0])

digits = '123456789'
smatrix = []

su = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]

if len(selected_imgs) == 81:
    for i in range(0, 9):
        l = selected_imgs[9*i:9*i+9]
        l.sort(key=lambda x: x[1])
        smatrix.append(l)

    for i in range(0, 9):
        for j in range(0, 9):
            img = smatrix[j][i][2]

            h, w = img.shape[:2]
            img = cv2.resize(img, (3*w, 3*h), interpolation=cv2.INTER_CUBIC)

            ret, img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)

            digit = get_digit(img)
            if digit is not None:
                su[i][j] = digit

print "Sudoku is:"
ss.show(su)
sol = ss.solve_sudoku(su)
print "Solution is:"
ss.show(sol)

# cv2.imshow('image', image)
# cv2.waitKey(0)
