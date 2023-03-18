import cv2
import numpy as np
import datetime

cap = cv2.VideoCapture(0)

# 비디오 코덱 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# 비디오 저장 객체 생성
out = None

# 녹화중인지 아닌지 여부를 저장할 변수
recording = False

while(True):
    # 웹캠에서 새로운 프레임 읽기
    ret, frame = cap.read()
    
    # 현재시간 표시
    now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    cv2.putText(frame, str(now), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # 영상 출력
    cv2.imshow('frame',frame)
    
    keycode = cv2.waitKey(1)
    
    # 녹화 시작
    if keycode == ord('v'):
        # 비디오 저장 객체 생성
        out = cv2.VideoWriter(f'{now}.avi',fourcc, 30.0, (640,480))
        
        # 녹화 시작
        recording = True
        
    # 녹화 종료
    if keycode == ord('b'):
        # 녹화 중이면
        if recording:
            # 녹화 종료
            out.release()
            recording = False
            
    # 녹화 중이면
    if recording:
        # 프레임 녹화
        out.write(frame)
    
    # 종료 esc
    if keycode == 27:
        break

# 객체 해제
cap.release()
cv2.destroyAllWindows()