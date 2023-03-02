import cv2
import mediapipe as mp
import os
import datetime

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# 이미지 불러오기
imageList = {
    'panda' : [cv2.imread('C:/SEnowImage/panda/right_eye_cutout.png', cv2.IMREAD_UNCHANGED), cv2.imread('C:/SEnowImage/panda/left_eye_cutout.png', cv2.IMREAD_UNCHANGED),
            cv2.imread('C:/SEnowImage/panda/nose_tip_cutout.png', cv2.IMREAD_UNCHANGED)],
    'cat' : [cv2.imread('C:/SEnowImage/cat/right_eye2.png', cv2.IMREAD_UNCHANGED), cv2.imread('C:/SEnowImage/cat/left_eye2.png', cv2.IMREAD_UNCHANGED),
            cv2.imread('C:/SEnowImage/cat/nose_tip2.png', cv2.IMREAD_UNCHANGED)],
    'dog' : [cv2.imread('C:/SEnowImage/dog/right_eye3.png', cv2.IMREAD_UNCHANGED), cv2.imread('C:/SEnowImage/dog/left_eye3.png', cv2.IMREAD_UNCHANGED),
            cv2.imread('C:/SEnowImage/dog/nose_tip3.png', cv2.IMREAD_UNCHANGED)]
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

# For webcam input:
cap = cv2.VideoCapture(0)

SAVE_PATH = "C:/senow/"

# 창 크기 출력
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(w, h) # 640, 480
SCREEN_REGION = (0, 0, w, h)

# 캠에 이미지 덮어 씌우는 함수
def overlay(image, x, y, w, h, overlay_image): # 대상 이미지, x, y 좌표, width, height, 덮어씌울 이미지
    alpha = overlay_image[:, :, 3] #BGRA, A값을 가져옴
    mask_image = alpha / 255 # 0~255 ->255로 나누면 0~1의 값을 가짐, 1: 불투명, 0: 투명
    
    # 얼굴이 창 크기를 벗어나면 오류가 생기므로 예외처리
    try:
        for c in range(0, 3): #BGR 처리
            image[y-h: y+h, x-w: x+w, c] = (overlay_image[:, :, c] * mask_image) + (image[y-h: y+h, x-w: x+w, c] * (1-mask_image))
    except:
        pass
    
# 이미지 저장 함수
def displayCapture(screenshot): # screenshot을 통해 opencv 창 정보를 받아옴
    
    # 이미지 저장 폴더, 없는 경우 생성
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    try:
        # 현재 시간을 파일 이름으로 사용하여 png 파일로 저장
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_name = f"{SAVE_PATH}/{current_time}.png"
        cv2.imwrite(file_name, screenshot) # 이미지 저장
        print(f"Screenshot saved to {file_name}") # 출력
    except:
        print("에러 발생")

# 메인
with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
                
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
                # mp_drawing.draw_detection(image, detection)
                
                #특정 위치 가져오기
                keypoints = detection.location_data.relative_keypoints
                right_eye = keypoints[0] # 오른쪽 눈
                left_eye = keypoints[1] # 왼쪽 눈
                nose_tip = keypoints[2] # 코 끝 부분

                # 이미지 위치 지정
                right_eye = (int(right_eye.x * w)-20, int(right_eye.y * h)-100)
                left_eye = (int(left_eye.x * w)+20, int(left_eye.y * h)-100) 
                nose_tip = (int(nose_tip.x * w), int(nose_tip.y * h)+30)

                # 이미지 대입
                overlay(image, *right_eye, 25, 25, image_right_eye)
                overlay(image, *left_eye, 25, 25, image_left_eye)
                overlay(image, *nose_tip, 50, 50, image_nose_tip)

        # 영상 출력
        # Flip the image horizontally for a selfie-view display.
#         cv2.imshow('MediaPipe Face Detection', cv2.flip(image, 1)) # 좌우 반전되어 출력
        cv2.imshow('MediaPipe Face Detection', cv2.resize(cv2.flip(image, 1), None, fx=1.5, fy=1.5))
    
        # 키보드 입력
        keycode = cv2.waitKey(1) # 입력 값을 이런식으로 변수에 저장해서 사용해야 딜레이가 생기지 않음
        
        #q를 누르면 종료
        if keycode == ord('q'):
            break
        
        # 이미지 변환
        if keycode == ord('a'):
            image_right_eye = imageList['panda'][0]
            image_left_eye = imageList['panda'][1]
            image_nose_tip = imageList['panda'][2]
            print('판다')

        if keycode == ord('s'):
            image_right_eye = imageList['cat'][0]
            image_left_eye = imageList['cat'][1]
            image_nose_tip = imageList['cat'][2]
            print('고양이')

        if keycode == ord('d'):
            image_right_eye = imageList['dog'][0]
            image_left_eye = imageList['dog'][1]
            image_nose_tip = imageList['dog'][2]
            print('개')
        
        # 화면 캡처
        if keycode == ord('p'):
            displayCapture(image)

cap.release()
cv2.destroyAllWindows()