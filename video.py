# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cv2
import struct
from naoqi import ALProxy
import yaml
import os
import sys

# create image
width = 320
height = 240

try:
    os.chdir(sys._MEIPASS)
    print(sys._MEIPASS)
except:
    os.chdir(os.getcwd())

def yolo(frame):
    # 모델 & 설정 파
    model = './yolo_v3/yolov3.weights'
    config = './yolo_v3/yolov3.cfg'
    class_labels = './yolo_v3/coco.names'
    confThreshold = 0.5
    nmsThreshold = 0.4

    # 클래스 이름 불러오기
    try:
        with open(class_labels, 'rt') as f:
            classes = f.read().rstrip('\n').split('\n')
    except:
        classes=['person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'sofa', 'pottedplant', 'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # 네트워크 생성
    net = cv2.dnn.readNet(model, config)
    # 출력 레이어 이름 받아오기
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    # output_layers = ['yolo_82', 'yolo_94', 'yolo_106']

    # 블롭 생성 & 추론
    blob = cv2.dnn.blobFromImage(frame, 1 / 255., (320, 320), swapRB=True)
    net.setInput(blob)
    outs = net.forward(output_layers)

    h, w = frame.shape[:2]

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            # detection: 4(bounding box) + 1(objectness_score) + 80(class confidence)
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confThreshold:
                # 바운딩 박스 중심 좌표 & 박스 크기
                cx = int(detection[0] * w)
                cy = int(detection[1] * h)
                bw = int(detection[2] * w)
                bh = int(detection[3] * h)

                # 바운딩 박스 좌상단 좌표
                sx = int(cx - bw / 2)
                sy = int(cy - bh / 2)

                boxes.append([sx, sy, bw, bh])
                confidences.append(float(confidence))
                class_ids.append(int(class_id))

    # 비최대 억제
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)

    for i in indices:
        i = i[0]
        sx, sy, bw, bh = boxes[i]
        label = '{0}: {1:.2}'.format(classes[class_ids[i]], confidences[i])
        color = colors[class_ids[i]]
        cv2.rectangle(frame, (sx, sy, bw, bh), color, 2)
        cv2.putText(frame, label, (sx, sy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 255), 1, cv2.LINE_AA)
    return frame

def top(videoDevice,captureDevice,detect):
    result = videoDevice.getImageRemote(captureDevice);

    if result == None:
        print('cannot capture.')
    elif result[6] == None:
        print('no image data string.')
    else:
        # translate value to mat

        values = struct.unpack('<' + 'B' * len(result[6]), bytes(result[6]))
        # i = 0
        frame = np.array(values, dtype='uint8').reshape(height, width, 3)

        if detect ==False:
            return plt.imshow(frame, animated=True)
        else:
            return plt.imshow(yolo(frame), animated=True)

def bottom(videoDevice,captureDevice,detect):
    # get image
    result = videoDevice.getImageRemote(captureDevice);

    if result == None:
        print('bottom cannot capture.')
    elif result[6] == None:
        print('no image data string.')
    else:
        # translate value to matt

        values = struct.unpack('<' + 'B' * len(result[6]), bytes(result[6]))
        # i = 0
        frame = np.array(values, dtype='uint8').reshape(height, width, 3)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if detect == False:
            return plt.imshow(frame, animated=True)
        else:
            return plt.imshow(yolo(frame), animated=True)


def start_video():
    with open('C:/eeg_record/user.yaml') as f:
        user = yaml.load(f, Loader=yaml.FullLoader)

    ip_addr = user['nao']['ip']
    port_num = user['nao']['port']

    # get NAOqi module proxy
    videoDevice = ALProxy('ALVideoDevice', ip_addr, port_num)

    # subscribe top camera
    AL_kTopCamera = 0
    AL_kBottomCamera = 1
    AL_kDepthCamera = 2
    AL_kQVGA = 1            # 320x240
    AL_kBGRColorSpace = 11


    captureDevice = videoDevice.subscribeCamera(
        "test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    captureDevice2 = videoDevice.subscribeCamera(
        "test", AL_kBottomCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    def ani(i):
        T = top(videoDevice,captureDevice, True)

        while T is None:
            pass
        return T,

    fig = plt.figure()
    anime = animation.FuncAnimation(fig, ani, interval=1, blit=True)
    plt.show()
    videoDevice.unsubscribe(captureDevice)
    videoDevice.unsubscribe(captureDevice2)
