import sys
import cv2 as cv
import time
import numpy as np

name = "./team2_60.jpg"

img = cv.imread(name)
b, g, r = cv.split(img); img = cv.merge([r, g, b])
imgC = img.copy()      # img의 복사본을 하나 저장해 둔다.
imgG = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

hist, bins = np.histogram(imgG, 256, [0, 255])

cdf = hist.cumsum()
cdf_normalized = cdf / cdf.max()

mapping = cdf * 255 / cdf[255]
LUT = mapping.astype('uint8')

imgCeq = LUT[imgC]        # 3채널 칼라 영상에 대한 LUT 기반 히스토그램 평활화
imgEG = cv.cvtColor(imgCeq, cv.COLOR_RGB2GRAY)     # 히스토그램 평활화된 영상의 그레이 버전. Equalized Gray

cv.imshow(name[:-4],imgCeq)
cv.waitKey()
cv.imshow(name[:-4],imgEG)
cv.waitKey()
cv.destroyAllWindows()