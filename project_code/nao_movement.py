# -*- coding: utf-8 -*-
from naoqi import ALProxy
import numpy as np
import cv2
import struct
from collections import deque
from operator import itemgetter
import yaml
import os
import sys
import json

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

    target=deque()

    for i in indices:
        i = i[0]
        sx, sy, bw, bh = boxes[i]

        target.append([classes[class_ids[i]],sx,sy])

    return frame,target


def top(videoDevice,captureDevice):
    result = videoDevice.getImageRemote(captureDevice);
    if result == None:
        print 'cannot capture.'
        return None
    elif result[6] == None:
        print 'no image data string.'
    else:
        # translate value to mat

        values = struct.unpack('<' + 'B' * len(result[6]), bytes(result[6]))
        # i = 0
        frame = np.array(values, dtype='uint8').reshape(height, width, 3)
        detect_frame = yolo(frame)
        frame= detect_frame[0]
        top_list = detect_frame[1]

        return frame,top_list

def bottom(videoDevice,captureDevice):
    # get image
    result = videoDevice.getImageRemote(captureDevice);

    if result == None:
        print 'bottom cannot capture.'
        return None
    elif result[6] == None:
        print 'no image data string.'
    else:
        # translate value to mat

        values = struct.unpack('<' + 'B' * len(result[6]), bytes(result[6]))
        # i = 0
        frame = np.array(values, dtype='uint8').reshape(height, width, 3)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detect_frame = yolo(frame)
        frame = detect_frame[0]
        bottom_list = detect_frame[1]

        return frame, bottom_list

def stop_nao(message):
    ip_addr, port_num = message['ip_addr'], message['port']
    motion = ALProxy('ALMotion', ip_addr, port_num)
    motion.setWalkTargetVelocity(0.0, 0, 0, 0.3)


def start_nao(message):
    ip_addr, port_num=message['ip_addr'],message['port']

    awarness = ALProxy('ALBasicAwareness', ip_addr, port_num)
    awarness.stopAwareness()
    motion = ALProxy('ALMotion', ip_addr, port_num)


    # get NAOqi mod ule proxy
    videoDevice = ALProxy('ALVideoDevice', ip_addr, port_num)
    tts = ALProxy("ALTextToSpeech", ip_addr, port_num)
    tts.setLanguage('Korean')
    # subscribe top camera

    AL_kTopCamera = 0
    AL_kBottomCamera = 1
    AL_kDepthCamera = 2
    AL_kQVGA = 1            # 320x240
    AL_kBGRColorSpace = 11
    name='a'
    captureDevice = videoDevice.subscribeCamera(
        name, AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    while captureDevice =='':
        name*=2
        captureDevice = videoDevice.subscribeCamera(
            name, AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    captureDevice2 = videoDevice.subscribeCamera(
        name, AL_kBottomCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    while captureDevice2=='':
        name*=2
        captureDevice2 = videoDevice.subscribeCamera(
            name, AL_kBottomCamera, AL_kQVGA, AL_kBGRColorSpace, 10)
        print(captureDevice2)

    # create image

    range={'left':0,'push':180,'right':360}

    user_pos={'left':1,'push':0,'right':-1}

    current_pos=[220,0]
    target=None
    original_target=None

    dic = {'bottle': '병','keyboard':' 키보드','cup':'컵'}

    loop_flag=False
    while True:
        if loop_flag:
            break

        direction = message['rcv']['attribute']
        print(direction,direction=='')

        if direction != 'neutral' and direction != '':
            message['send'] = {'method': 'moveOn', 'attribute': 'clear'}
            while True:
                    names = ['HeadPitch', 'HeadYaw']
                    angles = [17 * 0.01745329238474369, 0]
                    timeList = [1.0, 1.0]
                    motion.angleInterpolation(names, angles, timeList, True)

                    t = top(videoDevice,captureDevice)
                    b = bottom(videoDevice,captureDevice2)

                    top_list = t[1]
                    bottom_list = b[1]

                    if direction == 'left' or direction == 'push':
                        top_list = sorted(top_list, key=itemgetter(1), reverse=False)
                        bottom_list = sorted(bottom_list, key=itemgetter(2), reverse=False)

                    elif direction == 'right':
                        top_list = sorted(top_list, key=itemgetter(1), reverse=True)
                        bottom_list = sorted(bottom_list, key=itemgetter(2), reverse=True)

                    if len(top_list) >= 2:

                        if direction == 'push':
                            if len(top_list) >= 3:
                                target = top_list[1]
                            else:
                                target = top_list[0]
                        else:
                            if original_target is None:
                                original_target = (top_list[0], len(top_list))
                                target = top_list[0]
                            elif original_target[1] < len(top_list):
                                target = original_target[0]

                        if range[direction] - 80 > target[1] < range[direction] + 80:
                            target = top_list[1]

                    if -1 * user_pos[direction] * (range[direction] - current_pos[0]) - 20 < 0:

                        motion.setWalkTargetVelocity(1.0, -1 * user_pos[direction], 0, 0.3)
                        current_pos[0] += (-1 * -1 * user_pos[direction] * 40)
                        current_pos[1] += 15


                    elif -1 * user_pos[direction] * (range[direction] - current_pos[0]) - 20 > 0:

                        motion.setWalkTargetVelocity(1.0, user_pos[direction], 0, 0.3)
                        current_pos[0] += (-1 * user_pos[direction] * 40)
                        current_pos[1] += 15

                    else:
                        motion.setWalkTargetVelocity(1.0, user_pos['push'], 0, 0.3)
                        current_pos[0] += (-1 * user_pos['push'] * 40)
                        current_pos[1] += 15

                    if len(bottom_list) > 0 or current_pos[1]>=50:

                        message['send'] = {'method': 'moveOn', 'attribute': 'finish'}
                        stop_nao(message)

                        if len(bottom_list) == 0:
                            if target is not None:
                                if len(target)!=0:
                                    tts.say("정답은{0}입니다.".format(dic[target[0]]))
                            loop_flag=True
                            break

                        else:
                            if len(bottom_list[0][0]) != 0:
                                tts.say("정답은{0}입니다.".format(dic[bottom_list[0][0]]))
                            loop_flag = True
                            break

                    if len(top_list) == 0 or len(bottom_list)>0:
                        motion.setWalkTargetVelocity(0.0, 0, 0, 0.3)
                    """
                    print(message)
                    print('top', top_list)
                    print('bottom', bottom_list)
                    print('target', target)
                    print('current', current_pos)
                    print('------------------------------')
                    """
        else:
            message['send'] = {'method': 'moveOn', 'attribute': 'fail'}

    videoDevice.unsubscribe(captureDevice2)
