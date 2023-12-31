import sys
import cv2 as cv
import time
import numpy as np

# 이름과 경로
path = "../data/"
name = "matrix.mp4"
fullname = path + name
winname = name[0:-4]

# 영상 불러오기
cap1 = cv.VideoCapture(fullname)
cap2 = cv.VideoCapture(fullname)
ret1, frame1 = cap1.read()
ret2, frame2 = cap2.read()

# 프레임 관련 변수
tot_frame = int(cap1.get(cv.CAP_PROP_FRAME_COUNT))
fps = int(cap1.get(cv.CAP_PROP_FPS))
delay = int(1000 / fps) - 15
count = 0

# 저장을 위한 변수
frame_width = int(cap1.get(3))
frame_height = int(cap1.get(4))
queue = []
fourcc = cv.VideoWriter_fourcc(*'XVID')
merged_frame = cv.hconcat([frame1, frame2])
out = cv.VideoWriter('team2.avi', fourcc, fps, (merged_frame.shape[1], merged_frame.shape[0]))

# 화면에 텍스트를 표시하기 위한 변수
text_pos = (20, 40)  # 텍스트가 추가될 좌표 (x, y)
font = cv.FONT_HERSHEY_SIMPLEX  # 폰트 선택
font_scale = 1  # 폰트 크기
font_color = (0, 0, 254)  # 폰트 색상 (BGR 형식)
font_thickness = 2  # 폰트 두께

# 트랙바 플레그 or 변수
brightness = 10.0
heflag = 0
frame_pos = 0
sigma = 0
un_sigma = 0

class sq:
    def __init__(self):
        self.sqonx = 0
        self.sqony = 1
        self.sqoffx = 488
        self.sqoffy = 208

    def setminx(self, x):
        self.sqonx = x
    def setmaxx(self, x):
        self.sqoffx = x
    def setminy(self, y):
        self.sqony = y
    def setmaxy(self, y):
        self.sqoffy = y
    def getminx(self):
        return self.sqonx if self.sqonx < self.sqoffx else self.sqoffx
    def getmaxx(self):
        return self.sqonx if self.sqonx > self.sqoffx else self.sqoffx
    def getminy(self):
        return self.sqony if self.sqony < self.sqoffy else self.sqoffy
    def getmaxy(self):
        return self.sqony if self.sqony > self.sqoffy else self.sqoffy

mousesq = sq()

def callback_brightness(x):
    global brightness
    if x >= 10:
        brightness = 4 ** (x / 10.0) - 3
    elif x < 10:
        brightness = x / 10.0

def callback_he(x):
    global heflag
    heflag = x

def callback_playbar(x):
    global frame_pos
    frame_pos = x

def callback_unsharp(x):
    global un_sigma
    un_sigma = x

def callback_gaussian(x):
    global sigma
    sigma = x

def callback_mouse(event, x, y, flags, param):
    global mousesq
    if event == cv.EVENT_LBUTTONDOWN:
        print(x - 488, y)
        mousesq.setminx(x - 488)  # 오른쪽 영상의 x좌표이므로 왼쪽 영상의 넓이 488을 빼준다.
        mousesq.setminy(y)
        print(mousesq.getminx(), mousesq.getminy(), mousesq.getmaxx(), mousesq.getmaxy())
    elif event == cv.EVENT_MOUSEMOVE:
        if flags & cv.EVENT_FLAG_LBUTTON:
            mousesq.setmaxx(x - 488)
            mousesq.setmaxy(y)
    elif event == cv.EVENT_LBUTTONUP:
        mousesq.setmaxx(x - 488)
        mousesq.setmaxy(y)
        print(mousesq.getminx(), mousesq.getminy(), mousesq.getmaxx(), mousesq.getmaxy())

if cap1.isOpened() and cap2.isOpened():
    s_time = time.time()  # 시작시간 기록
    # 윈도우와 트랙바 생성
    win = cv.namedWindow(winname)
    cv.createTrackbar("Brightness", winname, 10, 20, callback_brightness)
    cv.createTrackbar("Playbar", winname, 0, tot_frame, callback_playbar)
    cv.createTrackbar("HE", winname, 0, 1, callback_he)
    cv.createTrackbar("Gaussian", winname, 0, 9, callback_gaussian)
    cv.createTrackbar("Unsharp", winname, 0, 9, callback_unsharp)

    while ret1 or ret2:
        # 프레임 위치에 따라 재생바의 위치도 변경
        cv.setTrackbarPos("Playbar", winname, frame_pos)
        if mousesq.getminy() - mousesq.getmaxy() != 0 and mousesq.getminx() - mousesq.getmaxx() != 0:
            subframe = cv.convertScaleAbs(
                frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()], alpha=brightness,
                beta=0)
            frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()] = subframe

            # 히스토그램 평활화
            if heflag == 1:
                yuv_image = cv.cvtColor(
                    frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()], cv.COLOR_BGR2YUV)

                # Y 채널에 대해 히스토그램 평활화 수행
                yuv_image[:, :, 0] = cv.equalizeHist(yuv_image[:, :, 0])

                # YUV 이미지를 다시 BGR로 변환
                equalized_image = cv.cvtColor(yuv_image, cv.COLOR_YUV2BGR)
                frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()] = equalized_image

            # 가우시안 블러링
            if sigma != 0:
                blur_image = cv.GaussianBlur(
                    frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()], (0, 0), sigma)
                frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()] = blur_image

            # 언샤프 마스킹
            if un_sigma != 0:
                blur = cv.GaussianBlur(frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()],
                                       ksize=(21, 21), sigmaX=un_sigma, borderType=cv.BORDER_REPLICATE)
                UnsharpMaskImg = frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()] - blur
                frame2[mousesq.getminy():mousesq.getmaxy(), mousesq.getminx():mousesq.getmaxx()] += UnsharpMaskImg

        # 이미지에 텍스트 추가
        text_frame1 = cv.putText(frame1, "org_index=" + str(int(cap1.get(cv.CAP_PROP_POS_FRAMES))), text_pos, font,
                                 font_scale, font_color, font_thickness)
        text_frame2 = cv.putText(frame2, "this_index=" + str(count), text_pos, font, font_scale, font_color,
                                 font_thickness)
        count += 1

        # 프레임 합쳐서 윈도우에 띄우기
        merged_frame = cv.hconcat([text_frame1, text_frame2])
        cv.imshow(winname, merged_frame)
        cv.setMouseCallback(winname, callback_mouse, merged_frame)
        queue.append(merged_frame)

        # "esc"로 종료, "space"로 일시정지, 's'로 프레임 저장
        key = cv.waitKey(1)
        if key == 27:
            for sf in queue:
                out.write(sf)  # 영상 저장
            time.sleep(0.1)
            sys.exit()
        elif key == 32:
            while True:
                queue.append(merged_frame)
                key = cv.waitKey(delay)
                if key == 32:
                    break
                elif key == 115:
                    cv.imwrite('./team2_' + str(int(cap1.get(cv.CAP_PROP_POS_FRAMES))) + '.jpg', merged_frame)
                elif key == 27:
                    for sf in queue:
                        out.write(sf)  # 영상 저장
                    time.sleep(0.1)
                    sys.exit()
                time.sleep(0.000001)
        elif key == 115:
            cv.imwrite('./team2_' + str(int(cap1.get(cv.CAP_PROP_POS_FRAMES))) + '.jpg', merged_frame)

        # 프레임 받아오기
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        frame_pos += 1
        cap1.set(cv.CAP_PROP_POS_FRAMES, frame_pos)
        cap2.set(cv.CAP_PROP_POS_FRAMES, frame_pos)

    # 원래 동영상의 시간과 실제 재생시간의 차이 출력
    print("total playtime = 44sec")
    runtime = time.time() - s_time
    print(f"run time = {runtime}sec")

    # 영상 저장
    for sf in queue:
        out.write(sf)

else:  # 비디오를 못찾으면 강제종료
    print("Error : video not found")
    sys.exit()