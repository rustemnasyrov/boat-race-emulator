from http.client import HTTPResponse
from http.server import HTTPServer
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QCheckBox
from UdpPacket import UDPPacketBufferList
from WebSocketReciever import WebSocketReciever
from get_reponser import GetResponser
from http_responser import MyHandler
from logger import log_info
from main_send_ws import WebsocketSender
from main_window_base import MainWindowBase
import sys
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from recieve_udp import log_update_func, receive_udp_from_trainer
from send_udp import send_udp_to_trainer, PAUSE_COMMAND, START_COMMAND, FINISH_COMMAND
from datetime import datetime, time

class HostWindow(MainWindowBase):
    id_to_ind = []
    status_str_to_int = {'go': 0, 'three': 1, 'finish': 2, 'ready': 1}

    ws_address = 'ws://localhost:8000/ws/tst'
    #ws_address = 'ws://82.97.247.48:8000/ws/tst'

    #udp_address = ("192.168.137.1", 61112)
    #udp_send_address = ("192.168.137.255", 61111)
    udp_address = ("127.0.0.1", 61112)
    udp_send_address = ("127.0.0.255", 61111)
    ws_send_addr = ''
    tick_period = 10
    
    packet_buffer = None

    def __init__(self):

        super().__init__()
        
        self.receive_udp_packets = None
        
        self.packet_buffer = UDPPacketBufferList(15, self.process_udp_packet)

        # Создаем таймер и подключаем его к слоту
        self.race_timer = QTimer()
        self.race_timer.timeout.connect(self.update_race_data)
        
        self.ws_send_timer = QTimer()
        self.ws_send_timer.timeout.connect(self.send_data_to_ws)
        self.ws_send_timer.start(11)
        
    def add_buttons(self, layout):
        self.auto_mode = QCheckBox('Режим эмулятора тренажёров', self)
        self.auto_mode.setChecked(False)
        #self.auto_mode.stateChanged.connect(self.toggle_auto)
        layout.addWidget(self.auto_mode)
    
    @property    
    def is_auto_mode(self):
        return self.auto_mode.isChecked()
    
    def update_race_data(self):
        current_time = datetime.now()
        elapsed_time = int((current_time - self.start_time).total_seconds() * 1000)
        self.tick(elapsed_time)
        if self._info.is_status_running or self._info.is_status_countdown:
            self._info.timer = elapsed_time

        
    def tick(self, elapsed_time):
        self.timer_edit.setText(str(elapsed_time)) 
        
        if self._info.is_status_running and self.is_auto_mode:
            for racerWidget in self.racer_widgets:
                racerWidget.tick(elapsed_time)
                
    def send_data_to_ws(self):
        self.packet_buffer.do_process_packet()
        if self.is_auto_mode:
            self.send_info()
        #log_info(f'Model time {self._info.tracks[1].time}')
        data = self.info_to_send()
        self.thread.send_message(data)
        self.get_responser.set_data(self._info.to_dict())

    def receive_udp_packets(self):
        receive_udp_from_trainer(self.packet_buffer.add_packet_to_buffer, self.udp_address)

    def process_udp_packet(self, udp_packet):
        if udp_packet.lane in self._info.tracks:
            track = self._info.tracks[udp_packet.lane]
            track.trainer_id = udp_packet.id
            track.set_distance_meters(udp_packet.distance)
            track.time = int(udp_packet.boatTime * 1000) 
            track.set_speed_meters_sec(udp_packet.speed)
            track.stroke_rate = int(udp_packet.strokeRate)
            track.set_acceleration_meters_sec2(udp_packet.acceleration)
            track.set_state(str(udp_packet.state))
            
        #self.update_info()

    def start_server(self):
        self.thread = WebSocketReciever(self.ws_address)
        self.thread.data_received.connect(self.receive_server_info)
        self.thread.start()
        
        self.get_responser = GetResponser(self.thread)
        self.get_responser.set_data(self._info.to_dict())
        self.get_responser.start()
        self.get_responser.setPriority(QThread.TimeCriticalPriority)

        self.udp_receive_thread = QThread(self.thread)
        self.udp_receive_thread.run = self.receive_udp_packets
        self.udp_receive_thread.start()
        
    def receive_server_info(self, data):
        if not data:
            return
        print(data)
        race = data['active_race']
        distance = race['distance']
        self._info.set_distance_meters(distance)
        self._info.regatta_name = race['tournament_title']
        self._info.race_name = str(race['discipline_title']) + ', ' + str(race['race_title'])
        self._info.race_status = race['status'] if race['status'] != 'stop' else 'ready'

        if self._info.race_status == 'ready':
            self._info.init_tracks(count = len(data['simulators']))
            self.delete_racers()
            self.add_racers(self.main_layout)

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
        elif self._info.race_status == 'ready' or self._info.race_status == 'stop':
            self.status_ready()
            
    def status_countdown(self):
        self.start_race_timer()        
    
    def status_finish(self):
        self.race_timer.stop()

    def status_ready(self):
        self.race_timer.stop()
        self._info.timer = 0
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
        return self._info.tracks_dict(False)
    
    def closeEvent(self, event):
        self.get_responser.stop()
        
        return super().closeEvent(event)    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HostWindow()
    window.show()
    sys.exit(app.exec_())