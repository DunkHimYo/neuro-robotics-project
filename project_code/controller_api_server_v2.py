import os
from cortex2.emotiv_cortex2_client import EmotivCortex2Client
import time
import yaml
from emotiv_frame import frame_calculator
import websockets
import websockets.legacy.server
import asyncio
from collections import deque
import numpy as np
import json
import warnings
from preprocessing import preprocessing
from tensorflow.keras.models import load_model
from collections import Counter

warnings.filterwarnings(action='ignore')

with open('C:/eeg_record/user.yaml') as f:
    user = yaml.load(f, Loader=yaml.FullLoader)

def emotiv_controller(message):
    before_message = None
    url = "wss://localhost:6868"
    while True:
        message_method = message['method']
        if before_message!=message_method:
            if message_method=='emotiv_create':
                client = EmotivCortex2Client(url,
                                             client_id=user['emotiv']['id'],
                                             client_secret=user['emotiv']['secret'],
                                             check_response=True,
                                             authenticate=True,
                                             debug=True, data_deque_size=1, license=user['emotiv']['license'],
                                             debit=10)
                client.query_headsets()
                client.connect_headset(0)
                client.request_access()
                client.create_activated_session(0)
                sub = ["eeg"]
                rcv['eeg_frame'] = frame_calculator(client, sub)

                eeg_buffer = deque()
                message['emotiv_connect'] = True

                while True:
                    if message['method']!='record_start' and message['motion_chk']==1:
                        rcv = client.receive_data()
                        if rcv!= None and 'eeg' in list(rcv.keys()):
                            eeg_buffer.append(rcv['eeg'])
                            #print(datetime.datetime.fromtimestamp(rcv['time']))
                        if len(eeg_buffer) >= 128 * 8:
                            message['eeg'] = eeg_buffer
                            eeg_buffer.popleft()

                    elif message['method']=='emotiv_close':
                        message['emotiv_connect'] = False
                        break

                    elif message['method'] == 'record_start':
                        if sub[0]!='eeg':
                            client.unsubscribe(sub)
                            sub = ['eeg']
                            client.subscribe(streams=sub)

                        tm = list()
                        marker = list()

                        while True:
                            if message['method'] == 'record_stop':
                                file_len = 0
                                try:
                                    os.makedirs(f'/eeg_record/{message["action"]}/{file_len}')
                                except FileExistsError:
                                    file_len = len(os.listdir(f'/eeg_record/{message["action"]}'))
                                    os.makedirs(f'/eeg_record/{message["action"]}/{file_len}')

                                frame = rcv['eeg_frame'].requests_to_data_frame(eeg_buffer, tm)
                                frame['MARKER_HARDWARE'] = marker
                                frame.loc[frame.MARKER_HARDWARE == 1, 'MARKERS'] = 'rest'
                                frame.loc[frame.MARKER_HARDWARE == 2, 'MARKERS'] = message['action']
                                frame.loc[frame.MARKER_HARDWARE == 0, 'MARKERS'] = ''
                                frame.to_csv(rf'\eeg_record\{message["action"]}\{file_len}\{message["action"]}.csv')
                                eeg_buffer=deque()
                                break

                            rcv = client.receive_data()

                            if rcv != None:
                                eeg_buffer.append(rcv[sub[0]])
                                tm.append(rcv['time'])
                                mark = message['marker']
                                marker.append(mark)
                                if mark != 0:
                                    message['marker'] = 0

                    else:
                        message['eeg'] = None
                        eeg_buffer = deque()
                        client.request_access()

            before_message = message_method


def nao_controller(message):
    before_message = None

    while True:
        message_method=message['method']
        if before_message!=message_method:

            if message_method=='emotiv_close':
                message['emotiv_connect'] = False
                break

            if message_method == 'motion':
                message['com']=None

                async def accept(websocket, path):
                    channel = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
                    category = ['neutral', 'left', 'right', 'front']
                    while True:

                        if message['eeg'] != None and message['move_on']==True:

                            await websocket.send(json.dumps({f'method': 'moveOn','attribute':''}))
                            rcv_message = json.loads(await websocket.recv())['attribute']
                            print(rcv_message)
                            if rcv_message=='clear':
                                vot = deque()
                                while True:
                                    if len(vot) >= 25:
                                        for i in range(5):
                                            vot.popleft()

                                    frame = rcv['eeg_frame'].requests_to_data_frame(message['eeg'])[channel]

                                    x = np.array(preprocessing(frame.T, sfreq=128))
                                    x = x.reshape(*x.shape,1)

                                    answer = load_model(f'./model/mod0.h5').predict(x)[0]
                                    vot.append(np.where(answer == max(answer))[0][0])

                                    answer = load_model(f'./model/mod1.h5').predict(x)[0]
                                    vot.append(np.where(answer == max(answer))[0][0])

                                    answer = load_model(f'./model/mod2.h5').predict(x)[0]
                                    vot.append(np.where(answer == max(answer))[0][0])

                                    answer = load_model(f'./model/mod3.h5').predict(x)[0]
                                    vot.append(np.where(answer == max(answer))[0][0])

                                    answer = load_model(f'./model/mod4.h5').predict(x)[0]
                                    vot.append(np.where(answer == max(answer))[0][0])
                                    vot_idx=Counter(vot).keys()[0]

                                    if len(vot)==25 and category[vot_idx]!='neutral':
                                        await websocket.send(json.dumps({f'method': 'moveOn','attribute':k}))
                                        rcv = json.loads(await websocket.recv())

                                        if rcv['attribute']=='finish':
                                            await websocket.send(json.dumps({f'method': 'moveOn','attribute':'break'}))
                                            rcv = json.loads(await websocket.recv())
                                            message['move_on'] = False

                                        if message['move_on']==False:
                                            break

                                    elif message['emotiv_connect'] == False:
                                        break


                        elif message['move_on']==False:
                            await websocket.send(json.dumps({f'method': 'moveOff','attribute':''}))
                            rcv = await websocket.recv()
                            message['move_on'] = None

                        if message['camera']==True:
                            await websocket.send(json.dumps({f'method': 'videoOn','attribute':''}))
                            rcv = await websocket.recv()
                            message['camera']=None

                        elif message['camera']==False:
                            await websocket.send(json.dumps({f'method': 'videoOff','attribute':''}))
                            rcv = await websocket.recv()
                            message['camera']=None

                websoc_svr = websockets.serve(accept, 'localhost', 3000, ping_interval=None)
                event_loop = asyncio.get_event_loop()
                event_loop.run_until_complete(websoc_svr)
                event_loop.run_forever()

        before_message=message_method
        time.sleep(0.1)

