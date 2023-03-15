import cv2
import mediapipe as mp
import os
import datetime
import numpy as np

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# 동물 이미지 기본 path 주소
animal_path = 'C:/SEnowImage/'

# For webcam input:
cap = cv2.VideoCapture(0)

# 이미지 저장 기본 path 주소
save_path = "C:/senow/"

# 창 크기 출력
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(width, height) # 640, 480
SCREEN_REGION = (0, 0, width, height)

org = (50, 50) # 위치
font = cv2.FONT_HERSHEY_SIMPLEX # 폰트
scale = 1 # 크기
color = (255, 0, 0) # 색상
thickness = 2 # 굵기

# 이미지 불러오기
imageList = {
    'panda' : [cv2.imread(animal_path+'panda/right_eye_cutout.png', cv2.IMREAD_UNCHANGED), cv2.imread(animal_path+'panda/left_eye_cutout.png', cv2.IMREAD_UNCHANGED),
            cv2.imread(animal_path+'panda/nose_tip_cutout.png', cv2.IMREAD_UNCHANGED)],
    'cat' : [cv2.imread(animal_path+'cat/right_eye2.png', cv2.IMREAD_UNCHANGED), cv2.imread(animal_path+'cat/left_eye2.png', cv2.IMREAD_UNCHANGED),
            cv2.imread(animal_path+'cat/nose_tip2.png', cv2.IMREAD_UNCHANGED)],
    'dog' : [cv2.imread(animal_path+'dog/right_eye3.png', cv2.IMREAD_UNCHANGED), cv2.imread(animal_path+'dog/left_eye3.png', cv2.IMREAD_UNCHANGED),
            cv2.imread(animal_path+'dog/nose_tip3.png', cv2.IMREAD_UNCHANGED)]
}

# 이미지 기본값은 판다
image_right_eye = imageList['panda'][0]
image_left_eye = imageList['panda'][1]
image_nose_tip = imageList['panda'][2]

# For static images:
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

# 캠에 이미지 덮어 씌우는 함수
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
    
# 이미지 저장 함수
def displayCapture(screenshot): # screenshot을 통해 opencv 창 정보를 받아옴
    
    # 이미지 저장 폴더, 없는 경우 생성
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    try:
        # 현재 시간을 파일 이름으로 사용하여 png 파일로 저장
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_name = f"{save_path}/{current_time}.png"
        cv2.imwrite(file_name, screenshot) # 이미지 저장
        print(f"Screenshot saved to {file_name}") # 출력
    except:
        print("에러 발생")

# 메인
with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5) as face_detection:
    animal = 'panda'
    while cap.isOpened():
        success, image = cap.read()
        
        if not success:
            break
        
        image = cv2.flip(image, 1) # 영상 좌우반전
        
        # 해당 동물 텍스트 출력
        cv2.putText(image, animal, org, font, scale, color, thickness)
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)

        # Draw the face detection annotations on the image. 점을 그리는 함수
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.detections:
            for detection in results.detections:
                # mp_drawing.draw_detection(image, detection) # 얼굴 크기에 맞게 박스를 생성
                # print(detection) # detection의 값을 보기위해 사용
                
                #특정 위치 가져오기
                keypoints = detection.location_data.relative_keypoints
                right_eye = keypoints[0] # 오른쪽 눈
                left_eye = keypoints[1] # 왼쪽 눈
                nose_tip = keypoints[2] # 코 끝 부분
                
                # 이미지 대입, 크기 지정 / width, height 값을 바꾸면 실행이 안되는 버그가 있음
                box_wh = detection.location_data.relative_bounding_box # 크기를 동적으로 하기위한 코드
                box_w = int(box_wh.width * 100)
                box_h = int(box_wh.height * 100)

                # 이미지 위치 지정
                w, h = width, height
                right_eye = (int(right_eye.x * w)-box_w, int(right_eye.y * h)-(box_h*3))
                left_eye = (int(left_eye.x * w)+box_w, int(left_eye.y * h)-(box_h*3)) 
                nose_tip = (int(nose_tip.x * w), int(nose_tip.y * h)+box_h)
                
                # operands could not be broadcast together with shapes을 방지하기 위해 기존 이미지를 변형 한 후 사용
                overlay_right_eye = cv2.resize(image_right_eye, (box_w*2, box_h*2))
                overlay(image, *right_eye, box_w, box_h, overlay_right_eye)
                
                overlay_left_eye = cv2.resize(image_left_eye, (box_w*2, box_h*2))
                overlay(image, *left_eye, box_w, box_h, overlay_left_eye)
                
                overlay_nose_tip = cv2.resize(image_nose_tip, (box_w*4, box_h*4))
                overlay(image, *nose_tip, box_w*2, box_h*2, overlay_nose_tip)

        # 영상 출력
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('SEnow Camera', cv2.resize(image, None, fx=1.5, fy=1.5))

        # 키보드 입력
        keycode = cv2.waitKey(1) # 입력 값을 이런식으로 변수에 저장해서 사용해야 딜레이가 생기지 않음
        
        #esc 를 누르면 종료
        if keycode == 27:
            break
        
        # 이미지 변환
        if keycode == ord('a'):
            image_right_eye = imageList['panda'][0]
            image_left_eye = imageList['panda'][1]
            image_nose_tip = imageList['panda'][2]
            animal = 'panda'
            print('판다')

        if keycode == ord('s'):
            image_right_eye = imageList['cat'][0]
            image_left_eye = imageList['cat'][1]
            image_nose_tip = imageList['cat'][2]
            animal = 'cat'
            print('고양이')

        if keycode == ord('d'):
            image_right_eye = imageList['dog'][0]
            image_left_eye = imageList['dog'][1]
            image_nose_tip = imageList['dog'][2]
            animal = 'dog'
            print('개')
        
        # 화면 캡처
        if keycode == ord('p'):
            displayCapture(image)

cap.release()
cv2.destroyAllWindows()