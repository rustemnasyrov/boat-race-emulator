import threading

from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout
from WebSocketReciever import WebSocketReciever
from get_reponser import GetResponser

from main_send_ws import WebsocketSender
from main_window_base import MainWindowBase
import sys
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

from recieve_udp import receive_udp_from_trainer
from send_udp import send_udp_to_trainer, PAUSE_COMMAND, START_COMMAND, FINISH_COMMAND
from datetime import datetime, time

class HostWindow(MainWindowBase):
    id_to_ind = []
    status_str_to_int = {'go': 0, 'three': 1, 'finish': 2, 'ready': 1}

    ws_address = 'ws://82.97.247.48:8000/ws/'
    udp_address = ("0.0.0.0", 62222)
    udp_send_address = ("192.168.0.255", 61111)
    ws_send_addr = ''
    tick_period = 10

    def __init__(self):
        super().__init__()
        self.receive_udp_packets = None

        self.ws_send_addr = self.ws_address + 'simulators'
        self.ws_recv_addr = self.ws_address + 'commands'

        # Создаем таймер и подключаем его к слоту
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_func)

    def update_func(self):
        current_time = datetime.now()
        elapsed_time = int((current_time - self.start_time).total_seconds() * 1000)
        self.tick(elapsed_time)
        if self._info.is_status_running:
            self._info.timer = elapsed_time
       # self.update_tracks()
       # self.send_info()
       # is_all_finished = all(racerWidget.is_finished() for racerWidget in self.racer_widgets)

        #if is_all_finished:
         #   self.status_finish()
        
    def tick(self, elapsed_time):
        self.timer_edit.setText(str(elapsed_time)) # Отображаем время в момент обновления 
        
        if self._info.is_status_countdown and elapsed_time >= 2900:
           # self.race_status_edit.setText('go')
           # self._info.race_status = 'go'
            self.start_time = datetime.now()
            self.play_horn()
            send_udp_to_trainer(self._info, self.udp_send_address)
        
        if self._info.is_status_running:
            for racerWidget in self.racer_widgets:
                racerWidget.tick(elapsed_time)


    def add_buttons(self, layout):
        self.ready_button = QPushButton('Ready - на старт')
        self.ready_button.clicked.connect(self.status_ready)

        self.go_button = QPushButton('Go - гонка')
        self.go_button.clicked.connect(self.status_go)

        self.finish_button = QPushButton('Finish - завершить гонку')
        self.finish_button.clicked.connect(self.status_finish)

        row = QHBoxLayout()
        row.addWidget(self.ready_button)
        row.addWidget(self.go_button)
        row.addWidget(self.finish_button)
        layout.addLayout(row)



    def receive_udp_packets(self):
        receive_udp_from_trainer(self.process_udp_packet, self.udp_address)

    def process_udp_packet(self, lane, boat_id, state, distance, time, speed):
        # print(f"id:{boat_id}, state: {state}, distance: {distance}, lane: {lane}")
        if lane + 1 in self._info.tracks:
            track = self._info.tracks[lane + 1]
            track.trainer_id = boat_id
            track.set_distance_meters(distance)
            track.time = time
            track.set_speed_meters_sec(speed)

        self.update_info()

    def start_server(self):
        self.udp_receive_thread = threading.Thread(target=self.receive_udp_packets)
        self.udp_receive_thread.start()

        self.ws_sender= WebsocketSender('ws://192.168.0.104:8000/ws/simulators', self.info_to_send)
        self.ws_sender.start_send()
        
        self.thread = WebSocketReciever('ws://82.97.247.48:8000/ws/commands')
        self.thread.data_received.connect(self.receive_info)
        self.thread.start()
        
        self.get_responser = GetResponser.start_thread()
        self.get_responser.set_data(self._info.to_dict())

    def send_info_safe(self):
        super().send_info_safe()
        self.get_responser.set_data(self._info.to_dict())
        
    def update_label(self, data):
        print(data)
        
    def receive_info(self, data):
        if not data:
            return
        print(data)
        race = data['active_race']
        #status = self.status_str_to_int[race['status']]
        distance = race['distance']
        self._info.set_distance_meters(distance)
        self._info.regatta_name = race['tournament_title']
        self._info.race_name = str(race['discipline_title'])
        self._info.race_status = race['status']

        for idx, value in data['simulators'].items():
            if int(idx) in self._info.tracks:
                track = self._info.tracks[int(idx)]
                track.racer = value['fio']
                track.weight = value['weight']
                track.age = value['age']

        send_udp_to_trainer(self._info, self.udp_send_address)

        self.update_info()
        
        if self._info.race_status == 'go':
            self.status_go()
        elif self._info.race_status == 'finish':
            self.status_finish()
        elif self._info.race_status == 'countdown':
            self.status_countdown()
        elif self._info.race_status == 'ready':
            self.status_ready()
            
    def status_countdown(self):
        self.start_timer()        
    
    def status_finish(self):
        self.race_status_edit.setText('finish')
        self.timer.stop()
        send_udp_to_trainer(self.get_info_without_mutes(), self.udp_send_address)

    def status_ready(self):
        self.timer_edit.setText('0')
        for racerWidget in self.racer_widgets:
            racerWidget.reset()

    def status_go(self):
        self.timer.stop()
        self.play_horn()
        self.start_timer() 

    def start_timer(self):
        self.start_time = datetime.now() # Сохраняем время открытия окна
        self.timer.start(self.tick_period)      
    
    def info_to_send(self):
        data = dict()
        for i in range(0, len(self.racer_widgets)):
            data[str(i+1)] = self.racer_widgets[i].racer_info.as_dict(False)
        return data
    
    def closeEvent(self, event):
        
        self.get_responser.stop()
        
        return super().closeEvent(event)    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HostWindow()
    window.show()
    sys.exit(app.exec_())