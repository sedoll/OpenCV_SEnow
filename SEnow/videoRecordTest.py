import cv2
import datetime
import pyaudio

cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 비디오 코덱 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# 비디오 저장 객체 생성
out = None

# 녹음할 파일의 이름과 설정을 합니다.
audio_format = pyaudio.paInt16  # 오디오 포맷 설정
channels = 2 # 스테레오
sample_rate = 44100  # 샘플 레이트 설정
chunk_size = 1024 # 청크 크기
record_seconds = 10
p = pyaudio.PyAudio()
stream = p.open(format=audio_format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk_size)
frames = []

# 녹화중인지 아닌지 여부를 저장할 변수
recording = False

while(True):
    # 웹캠에서 새로운 프레임 읽기
    ret, frame = cap.read()
    
    frame = cv2.flip(frame, 1) # 영상 좌우반전
    
    # 현재시간 표시
    now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    cv2.putText(frame, str(now), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
    
    # 영상 출력
    cv2.imshow('frame',frame)
    
    keycode = cv2.waitKey(1)
    
    # 녹화 시작
    if keycode == ord('v'):
        # 비디오 저장 객체 생성
        out = cv2.VideoWriter(f'{now}.avi',fourcc, 30.0, (width, height))
        data = stream.read(chunk_size)
        frames.append(data)
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