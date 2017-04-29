import numpy as np
import cv2

MARGIN = 10
HEIGHT = 480
WIDTH = 640

def detect_barcode(image):
    # load the image and convert it to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction
    gradX = cv2.Sobel(gray, ddepth = cv2.cv.CV_32F, dx = 1, dy = 0, ksize = -1)
    gradY = cv2.Sobel(gray, ddepth = cv2.cv.CV_32F, dx = 0, dy = 1, ksize = -1)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)

    # blur and threshold the image
    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)

    # construct a closing kernel and apply it to the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations = 4)
    closed = cv2.dilate(closed, None, iterations = 4)

    # find the contours in the thresholded image, then sort the contours
    # by their area, keeping only the largest one
    (cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cs = sorted(cnts, key = cv2.contourArea, reverse = True)

    b_image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)

    if len(cs) > 0:
        c = cs[0]
        area = cv2.contourArea(c)

        if area > (WIDTH * HEIGHT / 20):
            # compute the rotated bounding box of the largest contour
            rect = cv2.minAreaRect(c)

            box_points = cv2.cv.BoxPoints(rect)
            box = np.int0(box_points)

            # draw a bounding box arounded the detected barcode and display the image
            cv2.drawContours(image, [box], -1, (0, 255, 0), 2)    

            max_x = max(box_points[0][0], box_points[1][0], box_points[2][0], box_points[3][0])
            min_x = min(box_points[0][0], box_points[1][0], box_points[2][0], box_points[3][0])

            max_y = max(box_points[0][1], box_points[1][1], box_points[2][1], box_points[3][1])
            min_y = min(box_points[0][1], box_points[1][1], box_points[2][1], box_points[3][1])

            r_image = image[min_y-MARGIN:max_y+MARGIN, min_x-MARGIN:max_x+MARGIN]

            rows, cols = r_image.shape[:2]
            dim = max(rows, cols)
            rm = cv2.getRotationMatrix2D((cols/2, rows/2), rect[2], 1)
            r_image = cv2.warpAffine(r_image, rm, (dim, dim))

            r, g, b = cv2.split(r_image)
            (_, thresh) = cv2.threshold(g, 250, 255, cv2.THRESH_BINARY)

            (cntsl, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            csl = sorted(cntsl, key = cv2.contourArea, reverse = True)

            if len(csl) > 0:
                cr = csl[0]
                fx, fy, fw, fh = cv2.boundingRect(cr)
                r_image = r[fy:fy+fh, fx:fx+fw]

                r_width = WIDTH / fw
                r_height = HEIGHT / fh

                new_w = WIDTH
                new_h = r_width * fh

                if r_width > r_height:
                    new_h = HEIGHT
                    new_w = r_height * fw

                r_image = cv2.resize(r_image, (new_w, new_h))

            b_image = r_image

    return image, b_image

vcapture = cv2.VideoCapture(0)

while True:
    try:
        # Capture frame-by-frame
        ret, frame = vcapture.read()

        # Our operations on the frame come here
        bc_image, b_image = detect_barcode(frame)

        # Display the resulting frame
        cv2.imshow('frame', bc_image)
        cv2.imshow('barcode', b_image)
    except:
        print 'Some error'
        pass

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
vcapture.release()
cv2.destroyAllWindows()