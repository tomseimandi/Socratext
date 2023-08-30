import cv2
import numpy as np
import math


def get_skew_angles(img, kernel_size=5, low_threshold=50, high_threshold=150):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 50  # minimum number of pixels making up a line
    max_line_gap = 20  # maximum gap in pixels between connectable line segments

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)

    angles = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            angle = math.atan((y1 - y2) / (x2 - x1))
            angles.append(angle)

    return angles


def get_angle(img, units="degrees"):
    angles = get_skew_angles(img=img)
    filtered_angles = [angle for angle in angles if abs(angle) < 0.25]
    skew_angle = sum(filtered_angles) / len(filtered_angles)
    skew_angle_in_degrees = skew_angle * 180 / math.pi
    return skew_angle_in_degrees if units == "degrees" else skew_angle


def rotate_image(image, angle: float):
    new_image = image.copy()
    (h, w) = new_image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    new_image = cv2.warpAffine(new_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return new_image


def crop_ticket_image(image_path: str, save_path: str):
    # Read image
    img = cv2.imread(image_path)
    hh, ww = img.shape[:2]

    # Get edges
    canny = cv2.Canny(img, 50, 200)

    # Get contours
    contours = cv2.findContours(
        canny,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    contours = contours[0] if len(contours) == 2 else contours[1]

    # Filter out small regions
    cimg = np.zeros_like(canny)
    for cntr in contours:
        area = cv2.contourArea(cntr)
        if area > 20:
            cv2.drawContours(cimg, [cntr], 0, 255, 1)

    # Get convex hull and draw on input
    points = np.column_stack(np.where(cimg.transpose() > 0))
    hull = cv2.convexHull(points)
    himg = img.copy()
    cv2.polylines(himg, [hull], True, (0, 0, 255), 1)

    # Draw convex hull as filled mask
    mask = np.zeros_like(cimg, dtype=np.uint8)
    cv2.fillPoly(mask, [hull], 255)

    # blacken out input using mask
    mimg = img.copy()
    mimg = cv2.bitwise_and(mimg, mimg, mask=mask)

    # get rotate rectangle
    rotrect = cv2.minAreaRect(hull)
    (center), (width, height), angle = rotrect
    box = cv2.boxPoints(rotrect)
    boxpts = np.int0(box)

    # draw rotated rectangle on copy of input
    rimg = img.copy()
    cv2.drawContours(rimg, [boxpts], 0, (0, 0, 255), 1)

    # from https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle tends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    if angle < -45:
        angle = -(90 + angle)

    # otherwise, check width vs height
    else:
        if width > height:
            angle = -(90 + angle)
        else:
            angle = -angle

    # negate the angle to unrotate
    neg_angle = -angle
    print('unrotation angle:', neg_angle)
    print('')

    # Get rotation matrix
    # center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, neg_angle, scale=1.0)

    # unrotate to rectify
    result = cv2.warpAffine(
        mimg,
        M,
        (ww, hh),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0)
    )

    # save results
    cv2.imwrite(save_path, result)
