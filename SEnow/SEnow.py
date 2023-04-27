import cv2 # opencv, 영상처리
import mediapipe as mp # mediopipe, 얼굴 인식 라이브러리 사용
import os # 파일 생성을 위해 사용
import datetime # 파일 이름을 지정하기 위해 그리고 최대 녹화시간을 카운트 하기 위해 사용
import pyaudio # 오디오 녹화
import wave # 오디오 녹화
import numpy as np # 오디오 연산
from moviepy.editor import * # 비디오, 오디오 합성
import time # 음성 파일이 생성 될 때 까지 delay 발생시키기 위해 사용
import threading # 쓰레드, 두 가지 이상의 일을 하기 위해 사용 (opencv를 이용한 영상처리, moviepy를 이용한 영상, 음성 합성 동시 처리)

# mediapipe library 중에서 얼굴 인식 설정
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# 동물 이미지 기본 주소
animal_path = 'C:/SEnowImage/'

# 이미지, 영상 저장 기본 주소
save_path = 'C:/senow/'

# 웹캠 객체
cap = cv2.VideoCapture(0)

# 창 크기 출력
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(width, height) # 640, 480
SCREEN_REGION = (0, 0, width, height)

# 텍스트
org = (width-100, 30) # 위치
font = cv2.FONT_HERSHEY_SIMPLEX # 폰트
scale = 1 # 크기
color = (255, 0, 0) # 색상
thickness = 2 # 굵기

# 영상
fourcc = cv2.VideoWriter_fourcc(*'XVID') # 영상 코덱 설정
out = None # 영상 저장 객체 초기화
fps = 22.0 # 영상 프레임

# 음성
chunk = 1024 # 청크 크기
format = pyaudio.paInt16 # 오디오 포맷 설정
channels = 2 # 스테레오 (2), 모노(1)
rate = 22050 # 샘플 레이트 설정, 44100으로하면 2배속으로 되서 22050 으로 했더니 정배속으로 됨
duration = 10 # 녹음 최대 시간
audio_frames = []
audio = pyaudio.PyAudio() # 음성 객체 초기화
stream = None 

# 녹화중인지 아닌지 여부를 저장할 변수
recording = False

# 파일 이름 저장 변수 (현재 시간을 이름으로 지정)
fileName = ""


#region 녹화 종료 클래스
class record():
    
    def __init__(self):
        pass
    
    def exit(out, stream, audio, audio_frames):
        global recording
        out.release()
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        waveFile = wave.open(save_path + f"{fileName}.wav", 'wb')
        waveFile.setnchannels(channels)
        waveFile.setsampwidth(audio.get_sample_size(format))
        waveFile.setframerate(rate)
        waveFile.writeframes(b''.join(audio_frames))
        waveFile.close()
        audio_frames = []
        recording = False
        print('녹화종료')
#endregion

#region 영상, 소리 합성, 저장 함수
def videoCapture():
    print('영상, 소리 합성중')
    # 음성 파일은 녹화가 끝나고 만들어 지므로 살짝 지연
    time.sleep(2)
    
    # 합성할 비디오, 오디오 객체 생성
    videoclip = VideoFileClip(save_path + f"{fileName}.avi")
    audioclip = AudioFileClip(save_path + f"{fileName}.wav")

    # 비디오에 오디오 삽입후 파일 생성
    videoclip.audio = audioclip
    video = f"{fileName}.mp4"
    videoclip.write_videofile(save_path + video)
    print(f'영상, 소리 합성 완료, {video} 생성 완료')
#endregion

#region 이미지 저장 함수
def displayCapture(image):
    
    # 저장 폴더, 없는 경우 생성
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    try:
        # 현재 시간을 파일 이름으로 지정하여 png 파일로 저장
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_name = f"{save_path}/{current_time}.png"
        cv2.imwrite(file_name, image) # 이미지 저장
        print(f"{file_name} 저장 완료") # 출력
    except:
        print("에러 발생")
#endregion 

#region 필터 이미지 적용 함수
def filter_images(name):
    global image_right_eye, image_left_eye, image_nose_tip, imageList
    image_right_eye = imageList[name][0]
    image_left_eye = imageList[name][1]
    image_nose_tip = imageList[name][2]
#endregion

# 비디오와 오디오를 합칠때 thread를 쓰지 않으면 opencv가 끊기므로 thread 적용
video_save = threading.Thread(target=videoCapture)

#region 동물 이미지 불러오기
# cv2.IMREAD_UNCHANGED, 이미지파일을 alpha channel(누끼)까지 포함하여 읽는다.
# 이미지를 쉽게 보기 위해 dictionary 를 사용
imageList = {
    'panda' : [cv2.imread(animal_path+'panda/right_eye_cutout.png', cv2.IMREAD_UNCHANGED), cv2.imread(animal_path+'panda/left_eye_cutout.png', cv2.IMREAD_UNCHANGED),
            cv2.imread(animal_path+'panda/nose_tip_cutout.png', cv2.IMREAD_UNCHANGED)],
    'cat' : [cv2.imread(animal_path+'cat/right_eye2.png', cv2.IMREAD_UNCHANGED), cv2.imread(animal_path+'cat/left_eye2.png', cv2.IMREAD_UNCHANGED),
            cv2.imread(animal_path+'cat/nose_tip2.png', cv2.IMREAD_UNCHANGED)],
    'dog' : [cv2.imread(animal_path+'dog/right_eye3.png', cv2.IMREAD_UNCHANGED), cv2.imread(animal_path+'dog/left_eye3.png', cv2.IMREAD_UNCHANGED),
            cv2.imread(animal_path+'dog/nose_tip3.png', cv2.IMREAD_UNCHANGED)]
}
#endregion

# 처음 이미지 기본값, 판다 적용
image_right_eye = imageList['panda'][0]
image_left_eye = imageList['panda'][1]
image_nose_tip = imageList['panda'][2]

#region mideapipe 얼굴인식 기본 코드
IMAGE_FILES = []
with mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5) as face_detection:
    for idx, file in enumerate(IMAGE_FILES):
        image = cv2.imread(file)
        # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
        results = face_detection.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Draw face detections of each face.
        if not results.detections:
            continue
        annotated_image = image.copy()
        for detection in results.detections:
            print('Nose tip:')
            print(mp_face_detection.get_key_point(
                detection, mp_face_detection.FaceKeyPoint.NOSE_TIP))
            mp_drawing.draw_detection(annotated_image, detection)
        cv2.imwrite('/tmp/annotated_image' +
                    str(idx) + '.png', annotated_image)
#endregion

#region 캠에 이미지 덮어 씌우는 함수
def overlay(image, x, y, w, h, overlay_image): # 대상 이미지, x, y 좌표, width, height, 덮어씌울 이미지
    alpha = overlay_image[:, :, 3] #BGRA, A값을 가져옴
    mask_image = alpha / 255 # 0~255 ->255로 나누면 0~1의 값을 가짐, 1: 불투명, 0: 투명
    # print(x, y, w, h)
    
    # 얼굴이 창 크기를 벗어나면 오류가 생기므로 예외처리
    try:
        for c in range(0, 3): #BGR 처리
             image[y-h: y+h, x-w: x+w, c] = (overlay_image[:, :, c] * mask_image) + (image[y-h: y+h, x-w: x+w, c] * (1-mask_image))
    except Exception as e:
        print(e)
        pass
#endregion

#region 메인 실행 코드
with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5) as face_detection:
    
    animal = 'panda'
    while cap.isOpened():
        ret, image = cap.read()
        
        if not ret:
            break
        
        # 영상 좌우반전
        # 스마트폰의 전면 카메라 처럼 카메라 적용
        image = cv2.flip(image, 1)
        
        # 현재시간 표시
        now = datetime.datetime.now().strftime("%H-%M-%S")
        time_org = (10, 30)
        # cv2.putText(image, str(now), time_org, font, scale, color, thickness)
        
        # 현재 적용된 동물 필터 텍스트 출력
        cv2.putText(image, animal, org, font, scale, color, thickness)
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)

        # Draw the face detection annotations on the image. 
        # mediapipe의 얼굴을 rectagle로 나타내고 세부 위치에 dot로 그리는 함수 부분
        # dot와 rectagle을 그리는 대신 점의 좌표를 이용해 동물 이미지를 추가하도록 수정
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.detections:
            for detection in results.detections:
                # mp_drawing.draw_detection(image, detection) # 얼굴 크기에 맞게 박스를 생성
                # print(detection) # detection의 값을 보기위해 사용
                
                # dot의 특정 위치 가져오기
                keypoints = detection.location_data.relative_keypoints
                right_eye = keypoints[0] # 오른쪽 눈
                left_eye = keypoints[1] # 왼쪽 눈
                nose_tip = keypoints[2] # 코 끝 부분
                
                # 이미지 적용
                # 이미지의 크기를 동적으로 하기위해 얼굴의 크기 값을 연산하는 부분을 이용
                box_wh = detection.location_data.relative_bounding_box
                box_w = int(round(box_wh.width, 2) * 100)
                box_h = int(round(box_wh.height, 2) * 100)

                # 이미지 위치 지정, 얼굴크기에 맞게 위치를 동적으로 지정 함
                w, h = width, height
                right_eye = (int(right_eye.x * w)-box_w, int(right_eye.y * h)-(box_h*3))
                left_eye = (int(left_eye.x * w)+box_w, int(left_eye.y * h)-(box_h*3)) 
                nose_tip = (int(nose_tip.x * w), int(nose_tip.y * h)+box_h)
                
                #region 이미지 대입
                # operands could not be broadcast together with shapes을 방지하기 위해 기존 이미지를 변형 한 후 사용
                # 해당 에러는 현재 입히는 이미지의 크기와 opencv 상에서 적용되는 이미지의 해상도가 달라 생기는 것으로
                # 둘의 이미지를 같아지게 하도록 cv2.resize()를 적용
                
                # 오른쪽 귀
                overlay_right_eye = cv2.resize(image_right_eye, (box_w*2, box_h*2))
                overlay(image, *right_eye, box_w, box_h, overlay_right_eye)
                
                # 왼쪽 귀
                overlay_left_eye = cv2.resize(image_left_eye, (box_w*2, box_h*2))
                overlay(image, *left_eye, box_w, box_h, overlay_left_eye)
                
                # 코, 입
                overlay_nose_tip = cv2.resize(image_nose_tip, (box_w*4, box_h*4))
                overlay(image, *nose_tip, box_w*2, box_h*2, overlay_nose_tip)
                #endregion

        # 영상 출력
        cv2.imshow('SEnow Camera', cv2.resize(image, None, fx=1.5, fy=1.5))

        # 키보드 입력
        keycode = cv2.waitKey(25)
        
        #esc 를 누르면 종료
        if keycode == 27:
            break
        
        #region 이미지 변환
        if keycode == ord('a'):
            animal = 'panda'
            filter_images(animal)
            print('판다')

        if keycode == ord('s'):
            animal = 'cat'
            filter_images(animal)
            print('고양이')

        if keycode == ord('d'):
            animal = 'dog'
            filter_images(animal)
            print('개')
        #endregion
        
        # opencv 사진 저장
        if keycode == ord('p'):
            # 이미지라서 args를 튜플 형식이 아닌 리스트 형식으로 값을 넣어줘야 된다.
            img_save = threading.Thread(target=displayCapture, args=[image])
            img_save.start()
        
        #region 녹화 시작
        if keycode == ord('v') and recording == False:
            print('녹화 시작')
            # 오디오 생성
            stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
            
            # 비디오 저장 객체 생성
            fileName = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            out = cv2.VideoWriter(save_path + f'{fileName}.avi',fourcc, fps, (width, height))

            # 녹화 시작
            recording = True
            start_time = datetime.datetime.now()
        #endregion
        
        # 녹음 시간이 duration 을 넘으면 녹화 종료
        if keycode == ord('b') and recording:
            # 녹화 종료
            record.exit(out, stream, audio, audio_frames)
            video_save.start()
        
        #region 녹화 중이면
        if recording:
            
            # 프레임 녹화
            out.write(image)
            
            # 음원 녹화
            audio_frames.append(np.frombuffer(stream.read(chunk), dtype=np.int16))
            
            # 녹음 시간이 duration 을 넘으면 녹화 종료
            if (datetime.datetime.now() - start_time).seconds >= duration:
                # 녹화 종료
                record.exit(out, stream, audio, audio_frames)
                video_save.start()
        #endregion
#endregion

if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()