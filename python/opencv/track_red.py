import numpy as np
import cv2

vcapture = cv2.VideoCapture(0)

while True:
    ret, frame = vcapture.read()

    b,g,r = cv2.split(frame)

    rb = cv2.subtract(r, b)
    rg = cv2.subtract(r, g)
    gray = cv2.add(rb, rg)

    ret, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

    eroded = cv2.erode(thresh, None, iterations = 1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(eroded, cv2.MORPH_CLOSE, kernel)

    closed = cv2.erode(closed, None, iterations = 4)
    closed = cv2.dilate(closed, None, iterations = 4)

    (cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cs = sorted(cnts, key = cv2.contourArea, reverse = True)

    if len(cs) > 0:
        c = cs[0]
        rect = cv2.minAreaRect(c)
        box = np.int0(cv2.cv.BoxPoints(rect))

        cv2.drawContours(frame, [box], -1, (0, 255, 0), 3)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vcapture.release()
cv2.destroyAllWindows()
