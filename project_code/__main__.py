from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer,Qt
import math
import sys
import os
from multiprocessing import Process, Manager, freeze_support
import controller_api_server
import time
import atexit
import datetime
import subprocess

freeze_support()

class Main(QtWidgets.QMainWindow):

    def __init__(self, widget):
        super().__init__()
        uic.loadUi('./ui/main.ui', self)
        self.widget = widget
        self.label.setPixmap(QPixmap(r"./img/background.png"))
        self.device_allow = False
        self.motion=0
        self.emotiv=0
        self.nao=0
        self.detect=0
        self.nao_motion=0

        self.play.clicked.connect(self._start)
        self.emotiv_connect.clicked.connect(self._device_connect)
        self.motion_connect.clicked.connect(self._motion_start)
        self.nao_connect.clicked.connect(self._nao_connect)
        self.detecting.clicked.connect(self._detect_connect)


    def _start(self):
        current_page = SelectLearning(self)
        self.widget.addWidget(current_page)
        self.widget.setCurrentWidget(current_page)

    def _device_connect(self):
        self.emotiv ^= 1
        self.device_allow = True

        if self.emotiv==1:
            rcv['method'] = 'emotiv_create'

            self.emotiv_connect_line.setText("Working")
        else:
            rcv['method'] = 'emotiv_close'

            self.emotiv_connect_line.setText("Not Working")

    def _motion_start(self):
        if rcv['move_on'] is None:
            rcv['move_on']=False

        rcv['move_on']^=1
        print('chk', rcv['move_on'])
        if rcv['move_on']==1:
            rcv['method'] = 'motion'


            self.motion_line.setText("Working")

        else:
            #self._sp_kill()
            self.motion_line.setText("Not Working")

    def _nao_motion_kill(self):
        self.nao_motion.kill()

    def _nao_connect(self):
        self.nao ^= 1

        if self.nao==1:
            #self.sp = subprocess.Popen(['./module/video.exe'])
            #atexit.register(self._sp_kill)
            self.nao_connect_line.setText("Working")
        else:
            #self._sp_kill()
            self.emotiv_connect_line.setText("Not Working")

    def _detect_connect(self):
        self.detect ^= 1
        if self.detect == 1:
            rcv['method'] = 'motion'
            rcv['camera'] = True
            self.nao_connect_line.setText("Working")
        else:
            rcv['camera']=False
            self.emotiv_connect_line.setText("Not Working")


class SelectLearning(QtWidgets.QMainWindow):

    def __init__(self, main_class):
        super().__init__()
        uic.loadUi('./ui/select_learning.ui', self)
        self.main = main_class

        self.home.clicked.connect(self._home)
        self.original.clicked.connect(lambda: self._original(self.original.text()))
        self.front.clicked.connect(lambda: self._kind_front(self.front.text()))
        self.behind.clicked.connect(lambda: self._behind(self.behind.text()))
        self.armL.clicked.connect(lambda: self._arm(self.armL.text()))
        self.armR.clicked.connect(lambda: self._arm(self.armR.text()))
        self.sit_down.clicked.connect(lambda: self._original(self.sit_down.text()))
        self.stand_up.clicked.connect(lambda: self._original(self.stand_up.text()))

    def _home(self):
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(self.main)

    def _original(self, title):
        self.main.title = title
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)
        if self.main.device_allow == True:

            rcv['method'] = 'record_start'

    def _kind_front(self, title):
        current_page = SelectStep(self.main, title)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)

    def _behind(self, title):
        self.main.title = title
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)
        if self.main.device_allow == True:

            rcv['method'] = 'record_start'

    def _arm(self, title):
        current_page = SelectArm(self.main, title)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)


class SelectStep(QtWidgets.QMainWindow):

    def __init__(self, main_class, title):
        super().__init__()
        uic.loadUi('./ui/select_step.ui', self)
        self.main = main_class
        self.main.title = title
        self.home.clicked.connect(self._home)
        self.front.clicked.connect(lambda: self._front(self.front.text()))
        self.right.clicked.connect(lambda: self._right(self.right.text()))
        self.left.clicked.connect(lambda: self._left(self.left.text()))

    def _home(self):
        self.main.widget.removeself.main.widget(self.main.widget.currentWidget())
        self.main.widget.setCurrentself.main.widget(self.main)

    def _front(self, sec_title):
        self.main.title += ' ' + sec_title
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)
        if self.main.device_allow == True:

            rcv['method'] = 'record_start'

    def _right(self, sec_title):
        self.main.title += ' ' + sec_title
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)
        if self.main.device_allow == True:

            rcv['method'] = 'record_start'

    def _left(self, sec_title):
        self.main.title += ' ' + sec_title
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)
        if self.main.device_allow == True:
            rcv['method'] = 'record_start'


class SelectArm(QtWidgets.QMainWindow):

    def __init__(self, main_class, title):
        super().__init__()
        uic.loadUi('./ui/select_arm.ui', self)
        self.main = main_class
        self.main.title = title
        self.home.clicked.connect(self._home)
        self.raise_hand.clicked.connect(lambda: self._send_question(self.raise_hand.text()))
        self.raise_half_hand.clicked.connect(lambda: self._send_question(self.raise_half_hand.text()))
        self.open_hand.clicked.connect(lambda: self._send_question(self.open_hand.text()))
        self.bent_elbow.clicked.connect(lambda: self._send_question(self.bent_elbow.text()))

    def _home(self):
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(self.main)

    def _send_question(self, sec_title):
        self.main.title += ' ' + sec_title
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)
        if self.main.device_allow == True:
            rcv['method'] = 'record_start'


class Question(QtWidgets.QMainWindow):
    motion = {'원상태': 'original.gif', '앞으로 정방향': 'walking_forward.gif', '앞으로 좌방향': 'rotate_left.gif',
              '앞으로 우방향': 'rotate_right.gif',
              '뒤로': 'walking_backward.gif', '왼팔 앞으로 들기': 'raise_half_handL.gif', '오른팔 앞으로 들기': 'raise_half_handR.gif',
              '왼팔 위로 들기': 'raise_handL.gif', '오른팔 위로 들기': 'raise_handR.gif',
              '왼팔 옆 펴기': 'open_armL.gif', '오른팔 옆 펴기': 'open_armR.gif',
              '왼팔 팔꿈치 접기': 'bent_armL.gif', '오른팔 팔꿈치 접기': 'bent_armR.gif','앉기':'sit_down.gif','일어서기':'stand_up.gif'}

    default_learning_loop = 5
    default_learning_qtime = 8
    default_rest_time = 8

    def __init__(self, main_class):
        super().__init__()
        uic.loadUi('./ui/question.ui', self)
        self.rest_time = self.default_rest_time
        self.learning_loop = self.default_learning_loop
        self.learning_qtime = self.default_learning_qtime
        self.main = main_class
        self._timer_start()

    def _timer_start(self):
        rcv['action'] = Question.motion[self.main.title][:-4]
        self.Question_title.setText(f'')
        self.next_qtimer = QTimer(self)
        self.next_qtimer.setInterval(1000)
        self.next_qtimer.timeout.connect(self._rest_timer_count)
        self.next_qtimer.start()

    def _rest_timer_count(self):
        if self.main.device_allow == True and self.rest_time==self.default_rest_time:
            rcv['marker'] = 1

        self.gif_image.setHidden(True)
        self._setting_gif_cond()

        self.Question_title.setText(f'{self.rest_time}초 후에 시작 됩니다.')
        self.rest_time -= 1
        if self.rest_time <= 0:
            self.next_qtimer.timeout.connect(self._learning_timer_count)
            self.next_qtimer.timeout.disconnect(self._rest_timer_count)
            self.rest_time = self.default_rest_time


    def _setting_gif_cond(self):
        self.movie = QMovie(f"./img/{self.motion[self.main.title]}")
        self.gif_image.setMovie(self.movie)
        self.movie.start()

    def _learning_timer_count(self):

        if self.main.device_allow == True and self.learning_qtime==self.default_learning_qtime:
            rcv['marker'] = 2

        self.Question_title.setText(f'{self.main.title}')
        self.gif_image.setHidden(False)
        self.learning_qtime -= 1
        if self.learning_qtime <= 0:
            self.next_qtimer.timeout.connect(self._rest_timer_count)
            self.next_qtimer.timeout.disconnect(self._learning_timer_count)
            self.learning_loop -= 1
            self.learning_qtime = self.default_learning_qtime

        if self.learning_loop <= 0:
            self.next_qtimer.stop()
            current_page = Finish(self.main)
            self.main.widget.addWidget(current_page)
            self.main.widget.removeWidget(self.main.widget.currentWidget())
            self.main.widget.setCurrentWidget(current_page)


class Finish(QtWidgets.QMainWindow):

    def __init__(self, main_class):
        super().__init__()
        uic.loadUi('./ui/finish.ui', self)
        self.main = main_class
        self.home.clicked.connect(self._home)
        self.restart.clicked.connect(self._restart)
        tm = datetime.datetime.fromtimestamp(time.time()).second
        while datetime.datetime.fromtimestamp(time.time()).second == tm:
            pass
        if self.main.device_allow == True:
            rcv['method'] = 'record_stop'

    def _home(self):
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(self.main)

    def _restart(self):
        if self.main.device_allow == True:
            #self.main.wb.send_request('record_start')
            rcv['method'] = 'record_start'
        current_page = Question(self.main)
        self.main.widget.addWidget(current_page)
        self.main.widget.removeWidget(self.main.widget.currentWidget())
        self.main.widget.setCurrentWidget(current_page)


class Overlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.resize(200,200)
        self.move(self.width()*4, self.height()*2)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(14):
            if (self.counter / 5) % 14 == i:
                painter.setBrush(QBrush(QColor(127 + (self.counter % 5) * 32, 0, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width() / 2 + 50 * math.cos(2 * math.pi * i / 14.0) - 5,
                self.height() / 2 + 50 * math.sin(2 * math.pi * i / 14.0) - 10,
                10, 10)
        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(30)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()

        if rcv['loading_chk']:
            rcv['loading_chk']=False
            self.killTimer(self.timer)
            self.hide()

def program_exit(process:list):
    for p in process:
        p.kill()

if __name__ == '__main__':
    try:
        os.chdir(sys._MEIPASS)
        print(sys._MEIPASS)
    except:
        os.chdir(os.getcwd())

    try:
        os.makedirs(f'/eeg_record/')
    except FileExistsError:
        pass

    manager=Manager()

    rcv = manager.dict()
    rcv['method'] = None
    rcv['marker'] = 0
    rcv['emotiv_connect'] = False
    rcv['move_on'] =False
    rcv['camera']=Non

    p = Process(target=controller_api_server.nao_controller, args=(rcv,))
    p2 = Process(target=controller_api_server.emotiv_controller, args=(rcv,))
    p.start()
    p2.start()
    atexit.register(program_exit, [p,p2])

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(Main(widget))
    widget.showMaximized()
    app.exec_()








