| 영상 시청을 원할시 클릭 |
| ------ |
|[![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/prject_img.png)](https://www.youtube.com/watch?v=Ri9MkI7lXek)|

# BCI 기반 뉴로 로보틱스 시스템

- 코로나로 인해 국가 재난 발생으로 외출 제한이 발생하였으며 경제적 활동을 위해서는 외출이 불가피합니다. 이를 통해 사람과의 접촉을 최소화 할 수 있는 방안이 필요하다고 생각하였으며 BCI기반으로 생각을 통해 에이전트를 제어해 사람과의 접촉을 최소화 및 사람이 접근하기 힘든 구역 사용자가 신체적 여건으로 인해 갈 수 없는 상황도 해결 가능합니다.

## 장비 소개

| 장비 소개 |
| ------ |
![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/equipment.jpg)

## 프로그램 소개
- 파이썬의 특징인 GIL의 효과로 멀티스레딩을 막아 기본적으로 Concurrent 프로그래밍을 지원하는 문제점이 있어 해당 프로젝트의 경우 GUI화면 실행, 실시간 영상 처리 및 EEG 처리 등 백그라운드로 처리해야 하는 특징이 있기 때문에 MultiProcessing으로 Parallel 프로그래밍 적용
- Nao의 경우 Python 2.7을 지원해 SubProcess 방법으로 따로 제작하여 GUI프로그램과 Local API 형식으로 통신하여 

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
- Conv-Lstm기반으로 neutral, left, right, front 총 4개의 label을 각각 255개를 수집하여 학습

| 방법 | 결과 |
| ------ | ------ |
|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/model.jpg)|![waiting](https://github.com/DunkHimYo/neuro-robotics-project/blob/main/project_video/learning.jpg)|
