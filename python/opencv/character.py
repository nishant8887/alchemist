import math
import numpy as np
import Image, cv2
import pytesseract
from pytesseract import image_to_string

image = cv2.imread('sudoku.jpg')
height, width = image.shape[:2]
image = cv2.resize(image, (2*width, 2*height), interpolation=cv2.INTER_CUBIC)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

edges = cv2.Canny(threshold, 50, 100, apertureSize=3)
edges = cv2.dilate(edges, None, iterations = 2)
edges = cv2.erode(edges, None, iterations = 3)

cv2.imshow('image', edges)
cv2.waitKey(0)

lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
vlines = []
hlines = []
for rho, theta in lines[0]:
    if theta < (np.pi/64): # Vertical line
        vlines.append((rho, theta))

    if ((np.pi/2) - (np.pi/64) < theta and theta < (np.pi/2)): # Horizontal lines
        hlines.append((rho, theta))

vlines.sort(key=lambda tup: tup[0])
hlines.sort(key=lambda tup: tup[0])

lines = [vlines[0], vlines[-1], hlines[0], hlines[-1]]
vlines = [vlines[0], vlines[-1]]
hlines = [hlines[0], hlines[-1]]

va = []
vb = []
for rho, theta in vlines:
    va.append([np.cos(theta), np.sin(theta)])
    vb.append(rho)

ha = []
hb = []
for rho, theta in hlines:
    ha.append([np.cos(theta), np.sin(theta)])
    hb.append(rho)

pts = []
for i in range(0,2):
    for j in range(0,2):
        a = np.array([va[i], ha[j]])
        b = np.array([vb[i], hb[j]])
        x = np.linalg.solve(a, b)
        pts.append([x[0], x[1]])

# for pt in pts:
#     cv2.circle(image, (pt[0], pt[1]), 4, (255,0,0), -1)

# for rho, theta in lines:
#     a = np.cos(theta)
#     b = np.sin(theta)
#     x0 = a*rho
#     y0 = b*rho
#     x1 = int(x0 + 1000*(-b))
#     y1 = int(y0 + 1000*(a))
#     x2 = int(x0 - 1000*(-b))
#     y2 = int(y0 - 1000*(a))
#     cv2.line(image, (x1,y1), (x2,y2), (0,0,255), 2)

pts = np.float32(pts)
pts2 = np.float32([[0,0],[0,500],[500,0],[500,500]])
M = cv2.getPerspectiveTransform(pts,pts2)

dst = cv2.warpPerspective(threshold, M, (500,500))
dst = cv2.erode(dst, None, iterations = 1)
# dst = cv2.dilate(dst, None, iterations = 2)
# dst = cv2.erode(dst, None, iterations = 1)

ret,th1 = cv2.threshold(dst,127,255,cv2.THRESH_BINARY)

(cnts, _) = cv2.findContours(th1.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
cs = sorted(cnts, key = cv2.contourArea, reverse = True)

width, height = th1.shape
approx_sq_size = (width * height / 81)

th1 = cv2.cvtColor(th1,cv2.COLOR_GRAY2RGB)

blocks = []
digits = '123456789'
for c in cs:
    carea = cv2.contourArea(c)
    if carea < approx_sq_size and carea > approx_sq_size * 0.1:
        x,y,w,h = cv2.boundingRect(c)
        # cv2.rectangle(th1,(x,y),(x+w,y+h),(255,0,0),2)
        blockimg = th1[y:y+h, x:x+w].copy()
        blockimg = cv2.cvtColor(blockimg, cv2.COLOR_BGR2GRAY)
        blockimg = cv2.dilate(blockimg, None, iterations = 2)
        blockimg = cv2.erode(blockimg, None, iterations = 1)

        bheight, bwidth = blockimg.shape[:2]
        blockimg = cv2.resize(blockimg, (3*bwidth, 3*bheight), interpolation=cv2.INTER_CUBIC)
        blockimg = cv2.dilate(blockimg, None, iterations = 3)
        blockimg = cv2.erode(blockimg, None, iterations = 2)

        # cv2.imshow('image', blockimg)
        # cv2.waitKey(0)

        pil_img = Image.fromarray(blockimg)
        cstr = image_to_string(pil_img, config='-psm 10')
        if cstr in digits and cstr != '':
            blocks.append((x,y,w,h,cstr))

cv2.imshow('image', image)
cv2.waitKey(0)

# block_dict = {}
blocks = sorted(blocks, key=lambda x: x[1] * 500 + x[0])
for block in blocks:
    x0 = round((block[0] + (block[2] / 2)) / float(500 / 9))
    y0 = round((block[1] + (block[3] / 2)) / float(500 / 9))
    value = block[4]
    print (x0, y0, value)

    # if not block_dict.get(x0, None):
    #     block_dict[x0] = {}

    # block_dict[x0][y0] = value

# print block_dict

# for y in range(0,12):
#     hstr = ''
#     for x in range(0, 12):
#         if block_dict.get(x, None) and block_dict[x].get(y, None):
#             hstr += str(block_dict[x][y])
#         else:
#             hstr += '0'
#     print hstr

# pil_img = Image.fromarray(image)
# print image_to_string(pil_img)