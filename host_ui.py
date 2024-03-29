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

    ws_address = 'ws://82.97.247.48:8000/ws/tst'
    udp_address = ("0.0.0.0", 62222)
    udp_send_address = ("192.168.0.255", 61111)
    ws_send_addr = ''
    tick_period = 10

    def __init__(self):

        super().__init__()
        
        self.receive_udp_packets = None

        # Создаем таймер и подключаем его к слоту
        self.race_timer = QTimer()
        self.race_timer.timeout.connect(self.update_race_data)
        
        self.ws_send_timer = QTimer()
        self.ws_send_timer.timeout.connect(self.send_data_to_ws)
        self.ws_send_timer.start(10)

    def update_race_data(self):
        current_time = datetime.now()
        elapsed_time = int((current_time - self.start_time).total_seconds() * 1000)
        self.tick(elapsed_time)
        if self._info.is_status_running:
            self._info.timer = elapsed_time

        
    def tick(self, elapsed_time):
        self.timer_edit.setText(str(elapsed_time)) 
        
        if self._info.is_status_running:
            for racerWidget in self.racer_widgets:
                racerWidget.tick(elapsed_time)
                
    def send_data_to_ws(self):
        data = self.info_to_send()
        self.thread.send_message(data)

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
        
        self.thread = WebSocketReciever(self.ws_address)
        self.thread.data_received.connect(self.receive_server_info)
        self.thread.start()
        
        self.get_responser = GetResponser.start_thread()
        self.get_responser.set_data(self._info.to_dict())
        
    def receive_server_info(self, data):
        if not data:
            return
        print(data)
        race = data['active_race']
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
        elif self._info.race_status == 'finish' or self._info.race_status == 'stop':
            self.status_finish()
        elif self._info.race_status == 'countdown':
            self.status_countdown()
        elif self._info.race_status == 'ready':
            self.status_ready()
            
    def status_countdown(self):
        self.start_race_timer()        
    
    def status_finish(self):
        self.race_status_edit.setText('finish')
        self.race_timer.stop()

    def status_ready(self):
        self.timer_edit.setText('0')
        for racerWidget in self.racer_widgets:
            racerWidget.reset()

    def status_go(self):
        self.race_timer.stop()
        self.play_horn()
        self.start_race_timer() 

    def start_race_timer(self):
        self.start_time = datetime.now() # Сохраняем время открытия окна
        self.race_timer.start(self.tick_period)      
    
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