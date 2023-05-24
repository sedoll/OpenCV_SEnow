# OpenCV_SEnow

## OpenCV로 만든 카메라 필터, 스노우
---

[Test Video](https://youtu.be/sYYX3Na88J "My Youtube")<br>

[Blog](https://blog.naver.com/tmvmffpsej/222795649596 "My Blog")<br>

[Reference](https://youtu.be/XK3eU9egll8)<br><br>

## 사용한 라이브러리
---

[mediapipe](https://pypi.org/project/mediapipe)<br>

[OpenCV](https://pypi.org/project/opencv-python)<br>

[pyaudio](https://pypi.org/project/PyAudio)<br>

[moviepy](https://pypi.org/project/moviepy)<br>

[numpy](https://pypi.org/project/numpy)<br><br>

### 녹화 한 파일에서 음성이 안 들릴경우

---

<p><strong>마이크가 음소거 되어 있는지 확인</strong></p><br>

### 사용한 이미지 크기

---

<p>귀: 50x50</p>
<p>입: 100x100</p><br>

### Release Note

---
<strong>22.07.01</strong>

<p>완성</p><br>

<strong>23.02.21</strong>

<p>p를 누를 경우 png 형태로 이미지 저장기능 추가, 정말로 필터 카메라 처럼 만듬</p><br>

<strong>23.03.02</strong>

<p>pimageList 를 기존 2차원 리스트 형태에서 딕셔너리 형태로 변경하여 좀 더 직관적으로 사용하도록 변경</p><br>

<strong>23.03.08</strong>

<p>사용되는 동물 이미지를 얼굴 비율에 맞춰 크기를 동적으로 변환 될 수 있도록 수정</p><br>

<strong>23.03.15</strong>

<p>사용되는 동물 이미지를 얼굴 위치에 맞게 동적으로 커졌다, 작아졌다 될 수 있도록 수정</p><br>

<strong>23.03.30</strong>

<p>영상과 음성 녹화 성공, 이제 만들어진 영상과 음성을 하나로 합치면 됨</p><br>

<strong>23.04.05</strong>

<p>moviepy를 이용해서 영상 합치기 성공, avi(video) + wav(audio) = mp4(video + audio)</p><br>

<strong>23.05.24</strong>

<p>표정 인식을 이용한 필터 추가</p>

[표정 인식에 대한 상세 설명은 내 블로그에 기재](https://blog.naver.com/tmvmffpsej/223104743267)<br>