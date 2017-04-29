import numpy as np
import cv2
import time

vcapture = cv2.VideoCapture(0)
formerframe = None
frametime = time.time()

while True:
    # Capture frame-by-frame
    ret, frame = vcapture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if formerframe is None:
        formerframe = gray
        continue

    if time.time() > frametime + 100000:
        formerframe = gray
        frametime = time.time()
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(formerframe, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 1000:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
vcapture.release()
cv2.destroyAllWindows()