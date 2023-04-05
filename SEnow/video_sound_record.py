import cv2
import datetime
import pyaudio
import wave
import numpy as np

cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 녹화 파일 저장 위치
path = './record/'

# 영상
fourcc = cv2.VideoWriter_fourcc(*'XVID') # 영상 코덱 설정
out = None # 영상 저장 객체 초기화
fps = 20.0

# 음성
chunk = 1024 # 청크 크기
format = pyaudio.paInt16 # 오디오 포맷 설정
channels = 2 # 스테레오 (2), 모노(1)
rate = 22050 # 샘플 레이트 설정, 44100으로하면 2배속으로 되서 22050 으로 했더니 정배속으로 됨
duration = 10 # 녹음 최대 시간
audio_frames = []
audio = pyaudio.PyAudio()
stream = None

# 녹화중인지 아닌지 여부를 저장할 변수
recording = False

fileName = ""

class record():
    
    def __init__(self):
        pass
        
    def run(out, stream, audio, audio_frames):
        global recording
        out.release()
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        waveFile = wave.open(path + f"{fileName}.wav", 'wb')
        waveFile.setnchannels(channels)
        waveFile.setsampwidth(audio.get_sample_size(format))
        waveFile.setframerate(rate)
        waveFile.writeframes(b''.join(audio_frames))
        waveFile.close()
        audio_frames = []
        recording = False

while(True):
    # 웹캠에서 새로운 프레임 읽기
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame = cv2.flip(frame, 1) # 영상 좌우반전
    
    # 현재시간 표시
    now = datetime.datetime.now().strftime("%H-%M-%S")
    cv2.putText(frame, str(now), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
    
    # 영상 출력
    cv2.imshow('frame',frame)
    
    keycode = cv2.waitKey(25)
    
    # 녹화 시작
    if keycode == ord('v'):
        # 오디오 생성
        stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        
        # 비디오 저장 객체 생성
        fileName = datetime.datetime.now().strftime("%H-%M-%S")
        out = cv2.VideoWriter(path + f'{fileName}.avi',fourcc, fps, (width, height))

        # 녹화 시작
        recording = True
        start_time = datetime.datetime.now()
    
    # 녹음 시간이 duration 을 넘으면 녹화 종료
    if keycode == ord('b') and recording:
        # 녹화 종료
        record.run(out, stream, audio, audio_frames)
    
    # 녹화 중이면
    if recording:
        
        # 프레임 녹화
        out.write(frame)
        
        # 음원 녹화
        audio_frames.append(np.frombuffer(stream.read(chunk), dtype=np.int16))
        
        # 녹음 시간이 duration 을 넘으면 녹화 종료
        if (datetime.datetime.now() - start_time).seconds >= duration:
            # 녹화 종료
            record.run(out, stream, audio, audio_frames)
    
    # 종료 esc
    if keycode == 27:
        break

if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()