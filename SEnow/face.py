# 표정 인식
import cv2
import dlib
import numpy as np
from keras.models import load_model

# 얼굴 인식
face_cascade = cv2.CascadeClassifier('c:/j/haarcascade_frontalface_default.xml')

# 표정 인식을 위한 눈, 코, 입등의 위치 반환
predictor = dlib.shape_predictor('c:/j/shape_predictor_68_face_landmarks.dat')

# 표정 라벨링
expression_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# 표정 가중치 모델
model = load_model('c:/j/emotion_model.hdf5')

# 비디오 실행
cap = cv2.VideoCapture(0)

expression_label = None

lowerb1 = (0, 40, 0)
upperb1 = (20, 180, 255)

exp = 2       # 볼록, 오목 지수 (오목 : 0.1 ~ 1, 볼록 : 1.1~)
scale = 1           # 변환 영역 크기 (0 ~ 1)

prev_faces = []

def lens(exp, scale, frame):
    rows, cols = frame.shape[:2]
    # 매핑 배열 생성 ---②
    mapy, mapx = np.indices((rows, cols),dtype=np.float32)

    # 좌상단 기준좌표에서 -1~1로 정규화된 중심점 기준 좌표로 변경 ---③
    mapx = 2*mapx/(cols-1)-1
    mapy = 2*mapy/(rows-1)-1

    # 직교좌표를 극 좌표로 변환 ---④
    r, theta = cv2.cartToPolar(mapx, mapy)

    # 왜곡 영역만 중심확대/축소 지수 적용 ---⑤
    r[r< scale] = r[r<scale] **exp  

    # 극 좌표를 직교좌표로 변환 ---⑥
    mapx, mapy = cv2.polarToCart(r, theta)

    # 중심점 기준에서 좌상단 기준으로 변경 ---⑦
    mapx = ((mapx + 1)*cols-1)/2
    mapy = ((mapy + 1)*rows-1)/2
    
    return mapx, mapy

while True:
    # ret, frame 반환
    ret, frame = cap.read()
    
    if not ret:
        break
    
    

    # 얼굴인식을 위해 gray 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 얼굴 인식
    # scaleFactor이 1에 가까울수록 표정 인식이 잘 되고 멀 수록 잘 안됨
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    #region 얼굴이 인식되면 표정을 인식
    for (x, y, w, h) in faces:
        # 얼굴 크기에 알맞도록 사각형 그리기
        # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # 얼굴 크기 반환
        face_roi = gray[y:y+h, x:x+w]

        # 표정을 인식하기 위해 표정 dataset과 똑같은 사이즈 변환
        # dataset 이미지와 입력된 얼굴의 크기가 다르면 error 발생
        face_roi = cv2.resize(face_roi, (64, 64))
        face_roi = np.expand_dims(face_roi, axis=-1)
        face_roi = np.expand_dims(face_roi, axis=0)
        face_roi = face_roi / 255.0

        # 모델을 통해 표정 분석
        output = model.predict(face_roi)[0]

        # 해당 표정의 값 반환
        expression_index = np.argmax(output)

        # 표정에 따른 label 값 저장
        expression_label = expression_labels[expression_index]

        # 표정 값 출력
        print(expression_label, end=' ')
        # cv2.putText(frame, expression_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    #endregion
    
    # region 표정에 따른 필터
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if expression_label == 'Surprise':
        # mask = cv2.inRange(hsv, lowerb1, upperb1)
        # frame = mask # 2차원 형태로 얼굴의 형태만 추출
        # frame = cv2.bitwise_and(frame, frame, mask=mask) # 검출된 얼굴의 영역을 원본 이미지에 합성
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
    mapx, mapy = lens(exp, scale, frame)
    if expression_label == 'Happy':
        frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
    #endregion
    
    # 출력
    cv2.imshow('Expression Recognition', frame)

    # esc 누를 경우 종료
    key = cv2.waitKey(25)
    if key == 27:
        break

if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()
