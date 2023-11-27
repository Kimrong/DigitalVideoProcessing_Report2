import sys
import cv2 as cv
import time
import numpy as np

#이름과 경로
path="../data/"
name="matrix.mp4"
fullname=path+name
winname=name[0:-4]

queue = []

#영상 불러오기
cap1 = cv.VideoCapture(fullname)
cap2 = cv.VideoCapture(fullname)
ret1, frame1 = cap1.read()
ret2, frame2 = cap2.read()

#프레임 관련 변수
tot_frame = int(cap1.get(cv.CAP_PROP_FRAME_COUNT))
fps=int(cap1.get(cv.CAP_PROP_FPS))
bias=15
delay=int(1000/fps)-bias
count=0
frame_pos=0

#저장을 위한 변수
frame_width = int(cap1.get(3))
frame_height = int(cap1.get(4))

fourcc = cv.VideoWriter_fourcc(*'XVID')
merged_frame = cv.hconcat([frame1, frame2])
out = cv.VideoWriter('team.avi', fourcc, fps, (merged_frame.shape[1], merged_frame.shape[0]))
#화면에 텍스트를 표시하기 위한 변수
text_pos = (20, 40)  # 텍스트가 추가될 좌표 (x, y)
font = cv.FONT_HERSHEY_SIMPLEX  # 폰트 선택
font_scale = 1  # 폰트 크기
font_color = (0, 0, 254)  # 폰트 색상 (BGR 형식)
font_thickness = 2  # 폰트 두께

#밝기 관련 변수
brightness=10.0
onx=0
ony=0
offx=488
offy=208
heflag=0
def callback_brightness(x):
    global brightness
    if x >= 10 :
        brightness=4**(x/10.0)-3
    elif x < 10 :
        brightness=x/10.0

def HE(x):
    global heflag
    if x==1:
        # subframe=cv.equalizeHist(frame2[ony:offy, onx:offx])
        # frame2[ony:offy, onx:offx]=subframe
        heflag=1
    else:
        heflag=0

def callback_playbar(x):
    global frame_pos
    frame_pos=x
    
def mouse(event, x, y, flags, param):
    global onx, ony, offx, offy
    if event==cv.EVENT_LBUTTONDOWN:
        onx=x-488
        ony=y
        print(onx, ony, offx, offy)
    if event==cv.EVENT_MOUSEMOVE:
        if flags&cv.EVENT_FLAG_LBUTTON:
            offx=x-488
            offy=y
    if event==cv.EVENT_LBUTTONUP:
        offx=x-488
        offy=y
        print(onx, ony, offx, offy)
    
        
if cap1.isOpened() and cap2.isOpened():
    s_time=time.time()  #시작시간 기록
    #윈도우와 트랙바 생성
    win=cv.namedWindow(winname)
    cv.createTrackbar("brightness", winname, 10, 20, callback_brightness)
    cv.createTrackbar("playbar", winname, 0, tot_frame, callback_playbar)
    cv.createTrackbar("HE", winname, 0, 1, HE)
    print(onx, ony, offx, offy)
    while ret1 or ret2:
        # 프레임 위치에 따라 재생바의 위치도 변경
        cv.setTrackbarPos("playbar",winname,frame_pos)
        # 2번 프레임에 밝기 변화 추가
        subframe=cv.convertScaleAbs(frame2[ony:offy, onx:offx],alpha=brightness,beta=0)
        #scaled_frame=cv.convertScaleAbs(frame2,alpha=brightness,beta=0)
        frame2[ony:offy, onx:offx]=subframe
        scaled_frame=frame2
        if heflag==1:
            
            yuv_image = cv.cvtColor(subframe, cv.COLOR_BGR2YUV)

            # Y 채널에 대해 히스토그램 평활화 수행
            yuv_image[:,:,0] = cv.equalizeHist(yuv_image[:,:,0])

            # YUV 이미지를 다시 BGR로 변환
            equalized_image = cv.cvtColor(yuv_image, cv.COLOR_YUV2BGR)
            frame2[ony:offy, onx:offx]=equalized_image
            # gray_frame2 = cv.cvtColor(subframe, cv.COLOR_BGR2GRAY)
            # subframe = cv.equalizeHist(gray_frame2)
            # frame2[ony:offy, onx:offx] = cv.cvtColor(subframe, cv.COLOR_GRAY2BGR)
        # 이미지에 텍스트 추가
        
        text_frame1 = cv.putText(frame1, "org_index="+str(int(cap1.get(cv.CAP_PROP_POS_FRAMES))), text_pos, font, font_scale, font_color,
                                  font_thickness)
        text_frame2 = cv.putText(scaled_frame, "this_index="+str(count), text_pos, font, font_scale,
                                  font_color, font_thickness)
        count+=1

        #프레임 합쳐서 윈도우에 띄우기
        merged_frame = cv.hconcat([text_frame1, text_frame2])
        cv.imshow(winname,merged_frame)
        cv.setMouseCallback(winname, mouse, merged_frame)
        queue.append(merged_frame)
        #"esc"로 종료, "space"로 일시정지
        key=cv.waitKey(1)
        if key==27:
            for sf in queue:
                out.write(sf) #프레임 저장
            time.sleep(0.1)
            sys.exit()
        elif key==32:
            while True:
                queue.append(merged_frame)
                key = cv.waitKey(delay)
                if key==32:
                    break
                elif key==115:
                    cv.imwrite('./team_'+str(int(cap1.get(cv.CAP_PROP_POS_FRAMES)))+'.jpg',merged_frame)
                elif key == 27:
                    for sf in queue:
                        out.write(sf) #프레임 저장
                    time.sleep(0.1)
                    sys.exit()
                time.sleep(0.000001)
        elif key==115:
            cv.imwrite('./team_'+str(int(cap1.get(cv.CAP_PROP_POS_FRAMES)))+'.jpg',merged_frame)
        #프레임 받아오기
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        frame_pos+=1
        cap1.set(cv.CAP_PROP_POS_FRAMES, frame_pos)
        cap2.set(cv.CAP_PROP_POS_FRAMES, frame_pos)

    #원래 동영상의 시간과 실제 재생시간의 차이 출력
    print("total playtime = 44sec")
    runtime=time.time()-s_time
    print(f"run time = {runtime}sec")

else:   #비디오를 못찾으면 강제종료
    print("Error : video not found")
    sys.exit()