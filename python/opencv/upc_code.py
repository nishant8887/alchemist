import math
import numpy as np
import Image, cv2

def get_pixel(x):
    if x < 150:
        return 1
    return 0

def get_resized_barcode_row(image):
    scale_value = 95.0 * 2 / float(r_index - f_index)

    rows, cols = image.shape[:2]
    image = cv2.resize(image, (int(cols * scale_value), int(rows * scale_value)))

    rows, cols = image.shape[:2]
    m = image[rows/2:rows/2+1, 0:cols][0]

    l = []
    for x in m:
        l.append(get_pixel(x))

    return l

def hamming_distance(l, m, complement=False):
    distance = 0
    for index in range(0, len(l)):
        dd = (l[index] != m[index])
        if (dd and not complement) or (not dd and complement):
            distance+=1
    return distance

def left_rotate(l):
    k = l[0]
    l = l[1:]
    l.append(k)
    return l

def compare_se(l):
    d = hamming_distance(l, [1, 1, 0, 0, 1, 1])
    if d < 3:
        return True
    return False

def compare_mid(l):
    d = hamming_distance(l, [0, 0, 1, 1, 0, 0, 1, 1, 0, 0])
    if d < 4:
        return True
    return False

def compare_digit(l, d_map, complement, reverse=False):
    digit = None
    min_d = 7
    for k, v in d_map.items():
        c = v
        if reverse:
            c = v[::-1]
        d = hamming_distance(l, c, complement)
        if d < min_d:
            min_d = d
            digit = k
    return digit, min_d

def read_ean13_code(l):
    upca_digit_map = {
        0: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
        1: [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
        2: [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        3: [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
        4: [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        5: [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
        6: [0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        7: [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
        8: [0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
        9: [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1],
    }
    digits = []

    start = l[0:6]
    is_start = compare_se(start)

    if not is_start:
        return None

    i = 6
    while i < 90:
        w = l[i:i+14]
        while w[0] == 1:
            w = left_rotate(w)

        d_a, min_d_a = compare_digit(w, upca_digit_map, False)
        d_b, min_d_b = compare_digit(w, upca_digit_map, True, True)

        if min_d_a < min_d_b:
            digits.append([d_a, None])
        elif min_d_a > min_d_b:
            digits.append([None, d_b])
        else:
            digits.append([d_a, d_b])
        i = i + 14

    mid = l[90:100]
    is_mid = compare_mid(mid)
    if not is_mid:
        return None

    i = 100
    while i < 184:
        w = l[i:i+14]
        while w[0] == 0:
            w = left_rotate(w)
        d, _ = compare_digit(w, upca_digit_map, True)
        digits.append(d)
        i = i + 14

    end = l[i:]
    is_end = compare_se(end)
    if not is_end:
        return None

    # Validate the digits (check sum)
    return digits



image = cv2.imread('ean_13.png')
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

rows, cols = image.shape[:2]
m = image[rows/2:rows/2+1, 0:cols][0]

f_index = -1
r_index = -1
n = len(m)
for index in range(0, int(n/2)):
    c = get_pixel(m[index])
    cr = get_pixel(m[len(m) - 1 - index])
    if c == 1 and f_index == -1:
        f_index = index

    if cr == 1 and r_index == -1:
        r_index = len(m) - index

image = image[:rows, f_index:r_index]

l = get_resized_barcode_row(image)

v = read_ean13_code(l)
print v

# cv2.imshow('frame', image)
# cv2.waitKey(0)
