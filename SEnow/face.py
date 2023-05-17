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
video_capture = cv2.VideoCapture(0)

prev_faces = []

while True:
    # ret, frame 반환
    ret, frame = video_capture.read()
    
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
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

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
        # print(expression_label, end=' ')
        # 표정 값 출력
        cv2.putText(frame, expression_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    #endregion
    
    # 출력
    cv2.imshow('Expression Recognition', frame)

    # esc 누를 경우 종료
    key = cv2.waitKey(25)
    if key == 27:
        break

if video_capture.isOpened():
    video_capture.release()
cv2.destroyAllWindows()
