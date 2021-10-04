import time
import yaml
import video
import nao_movement
import websocket
import json
from multiprocessing import Process, Manager, freeze_support
import socket
freeze_support()

#warnings.filterwarnings(action='ignore')
with open('C:/eeg_record/user.yaml') as f:
    user = yaml.load(f, Loader=yaml.FullLoader)

def server(ws):
    before_rcv_message = {'method':'','attribute':''}
    before_send_message = json.dumps({'method':'','attribute':''})

    rcv = manager.dict()
    rcv['ip_addr'] = user['nao']['ip']
    rcv['port'] = user['nao']['port']

    rcv['rcv']={'method':'','attribute':''}
    rcv['send']=json.dumps({'method':'','attribute':''})

    p = None
    p2 = None

    while True:

        try:
            rcv_json=ws.recv()

        except socket.error:
            rcv_json=''
        message = json.loads(rcv_json) if rcv_json != '' else {'method': '','attribute':''}
        rcv['rcv'] = message

        if before_rcv_message!=message['method']:

            if message['method']=='videoOn':
                ws.send(json.dumps({'method': 'videoOn','attribute':'clear'}))
                p = Process(target=video.start_video)
                p.start()

            elif message['method']=='videoOff':
                ws.send(json.dumps({'method': 'videoOff','attribute':'clear'}))
                if p is not None:
                    p.terminate()

            elif message['method'] == 'moveOn':

                ws.send(json.dumps({'method': 'moveOn','attribute':'clear'}))
                p2 = Process(target=nao_movement.start_nao, args=(rcv,))
                p2.start()

            elif message['method']=='moveOff':

                ws.send(json.dumps({'method': 'moveOff','attribute':'clear'}))

                if p2 is not None:
                    if p2.is_alive():
                        nao_movement.stop_nao(rcv)
                        if p2 is not None:
                            print("finish")
                            p2.terminate()

        if before_send_message!=rcv['send']:
            ws.send(json.dumps(rcv['send']))

        else:
            try:
                ws.send(json.dumps({'method': '{0}'.format(rcv['rcv']['method']), 'attribute': 'fail'}))
            except socket.error:
                pass

        before_rcv_message=message['method']
        before_send_message = rcv['send']
        time.sleep(0.1)

if __name__=='__main__':
    url = 'ws://localhost:3000'
    ws = websocket.create_connection(url)

    manager=Manager()

    server(ws)

