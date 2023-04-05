import cv2 # opencv
import datetime # 파일이름
import pyaudio # 오디오 녹화
import wave # 오디오 녹화
import numpy as np # 오디오 녹화
from moviepy.editor import * # 비디오 오디오 합성
import time # 지연
import threading

# 웹캠 객체 지정 및 사이즈 적용
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

# 녹화 종료 클래스
class record():
    
    def __init__(self):
        pass
        
    def exit(out, stream, audio, audio_frames):
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

def clip():
    # 음성 파일은 녹화가 끝나고 만들어 지므로 살짝 지연
    time.sleep(2)
    
    # 합성할 비디오, 오디오 객체 생성
    videoclip = VideoFileClip(path + f"{fileName}.avi")
    audioclip = AudioFileClip(path + f"{fileName}.wav")

    # 비디오에 오디오 삽입후 파일 생성
    videoclip.audio = audioclip
    videoclip.write_videofile(path + f"{fileName}.mp4")

# 비디오와 오디오를 합칠때 thread를 쓰지 않으면 opencv가 끊기므로 thread 적용
record_save = threading.Thread(target=clip)

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
        record.exit(out, stream, audio, audio_frames)
        record_save.start()
    
    # 녹화 중이면
    if recording:
        
        # 프레임 녹화
        out.write(frame)
        
        # 음원 녹화
        audio_frames.append(np.frombuffer(stream.read(chunk), dtype=np.int16))
        
        # 녹음 시간이 duration 을 넘으면 녹화 종료
        if (datetime.datetime.now() - start_time).seconds >= duration:
            # 녹화 종료
            record.exit(out, stream, audio, audio_frames)
            
            recording = False
            record_save.start()
    
    # 종료 esc
    if keycode == 27:
        break

if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()