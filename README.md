| 영상 시청을 원할시 클릭 |
| ------ |
|[![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/prject_img.png)](https://youtu.be/SbXY6q6RwJo)|

# BCI 기반 뉴로 로보틱스 시스템

- 최근 로보틱스 시장이 증가하면서 뉴로 로보틱스 시장도 함께 성장하고 있다. 이런 추세에 따라 실시간으로 에이전트가 사용자의 생각을 읽고 필요한 명령을 수행 하는 기술이 필요하다. 해당 논문에서는 일반인을 대상으로 MI(Motor Imagery)에 따른 에이전트의 명령 수행을 위한 BCI(Brain- Computer Interface)연구로 사용자의 MI-EEG 수집, 분석 및 모델을 제작하였다. 모델은 MI기반으로 8초간 128Hz 샘플링 주파수로 수집된 14채널 EEG의 Frequency Bands를 구하여 Sliding Window 알고리즘으로 Segmentation한 후  C-LSTM으로 학습한다. 학습 결과 94%성능을 보여주었으며 이 연구를 통해 사용자는 원하는 방향을 생각하였을 때 생성된 EEG를 이용하여 에이전트를 원격 조종하는 것이 성공적으로 사용될 수 있음을 보여준다.

## 장비 소개

| 장비 소개 |
| ------ |
![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/equipment.jpg)

## 프로그램 소개
- GUI화면 실행, 실시간 영상 처리 및 EEG 처리 등 백그라운드로 처리해야 하는 작업이 많이 있기 때문에 Parallel 프로그래밍 적용
- Nao의 경우 Python 2.7을 지원해 SubProcess 방법으로 따로 제작하여 GUI프로그램과 Local API 형식으로 통신하여 연동

| 프로그램 소개 |
| ------ |
![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/gui.png)


## 학습 방법

| 방법 |
| ------ |
|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/learning_method.jpg)|
|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/data_collection.jpg)|

## 객체 인식 방법
- CoCo데이터셋으로 학습시킨 Yolo 모델을 적용하여 실시간으로 이미지를 처리해 객체 인식 및 좌표 추출

| 방법 |
| ------ |
|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/yolo_model.jpg)|

## 뇌파 학습 방법
- 초 단위로 Conv연산이 진행된 데이터를 lstm을 이용하여 시계열 학습을 시킴
- Conv-Lstm기반으로 neutral, left, right, front 총 4개의 label을 각각 255개를 수집하여 학습
- 오버피팅을 방지하기 위해 DropOut 적용 및 일반화 성능을 높이기 위해 L1_L2 regularization 적용

| 방법 | 결과 |
| ------ | ------ |
|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/model.jpg)|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/learning.jpg)|
