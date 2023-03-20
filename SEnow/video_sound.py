import cv2
import numpy as np
import pyaudio
import wave

# 웹캠 설정
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 비디오 작성 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# 오디오 작성 설정
audio_format = pyaudio.paInt16 # 오디오 포맷 설정
channels = 1 # 모노
sample_rate = 44100 # 샘플 레이트 설정
chunk = 1024 # 청크 크기
audio_filename = "output.wav"
audio_frames = []

audio_writer = wave.open(audio_filename, 'wb')
audio_writer.setnchannels(channels)
audio_writer.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_format))
audio_writer.setframerate(sample_rate)

# 오디오 스트림 시작
p = pyaudio.PyAudio()
stream = p.open(format=audio_format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk)

while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        break
    
    # 프레임 작성
    out.write(frame)
    
    # 오디오 읽기
    audio_data = stream.read(chunk)
    audio_frames.append(audio_data)
    
    # 화면에 출력
    cv2.imshow('frame', frame)
    
    # 종료
    if cv2.waitKey(1) == 27:
        break

# 작성된 프레임과 오디오 저장
out.release()
stream.stop_stream()
stream.close()
p.terminate()
audio_writer.writeframes(b''.join(audio_frames))
audio_writer.close()

# 윈도우 종료
cv2.destroyAllWindows()
