from http.server import HTTPServer
import json
import sys
import socket
import threading
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit
from http_responser import MyHandler
import http_responser
from main_send_ws import WebsocketSender
from main_window_base import MainWindowBase
from main_send_thread import DataSendingThread
from datetime import datetime

from racer_ui import RacerModel, RacerWidget
from recieve_udp import receive_udp_from_trainer
from send_udp import send_udp_to_trainer, PAUSE_COMMAND, START_COMMAND, FINISH_COMMAND

class MainWindow(MainWindowBase):
    start_time = datetime.now() # Сохраняем время открытия окна
    http_server_address = ('127.0.0.1', 8888)
    httpd_server = None
    
    def __init__(self):
        super().__init__()

        self.udp_recieve_thread = None
        self.setWindowTitle("Эмулятор отправки информации о тренажёрах")  
        
         # Создаем таймер и подключаем его к слоту
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)
    
         
    def start_http_server(self):
        self.stop_httpd_server()
        http_responser.response_data = self._info.to_dict()
        self.httpd_server = HTTPServer(self.http_server_address, MyHandler)
        print('Starting http server on {}:{}...'.format(*self.http_server_address))
        self.httpd_server.serve_forever()

    def recieve_udp_packets(self):
        receive_udp_from_trainer(self.process_udp_packet)

    def process_udp_packet(self, lane, boat_id, state, distance, time, speed):
        #print(f"id:{boat_id}, state: {state}, distance: {distance}, lane: {lane}")

        if boat_id == 1054351936:
            self.racer_widgets[1].update_info_udp(distance, speed, time)
        else:
            self.racer_widgets[2].update_info_udp(distance, speed, time)
        
    def start_server(self):
        self.udp_recieve_thread = threading.Thread(target=self.recieve_udp_packets)
        self.udp_recieve_thread.start()


        self.http_server_thread = threading.Thread(target=self.start_http_server)
        self.http_server_thread.start()
        
        #self.ws_sender= WebsocketSender('ws://31.129.102.190:8000/simulators', self.get_tracks_info)
        #self.ws_sender.start()
        
        self.start_server_thread()
        
    def start_server_thread(self):
        self.server_thread = DataSendingThread(self)
        self.server_thread.status_changed.connect(self.update_status)
        self.server_thread.start()
        
    def send_info_safe(self):
        super().send_info_safe()
        http_responser.response_data = self._info.to_dict()
        
    def update_func(self):
        current_time = datetime.now()
        elapsed_time = int((current_time - self.start_time).total_seconds() * 1000)
        self.tick(elapsed_time)
        self.send_info()
        is_all_finished = all(racerWidget.is_finished() for racerWidget in self.racer_widgets)
        if is_all_finished:
            self.status_finish()
        
    def tick(self, elapsed_time):
        self.timer_edit.setText(str(elapsed_time)) # Отображаем время в момент обновления 
        
        if self._info.is_status_countdown and elapsed_time >= 3000:
            self.race_status_edit.setText('go')
            self.start_time = datetime.now()
        
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
        
        
    def reconnect(self):
        pass
        
    def status_ready(self):
       # send_udp_to_trainer(PAUSE_COMMAND, self._info)
        self.race_status_edit.setText('ready')
        self.timer.stop() 
        self.timer_edit.setText('0')
        for racerWidget in self.racer_widgets:
            racerWidget.reset()
        self.send_info()
        
    def status_go(self):
        #send_udp_to_trainer(START_COMMAND, self._info)
        self.race_status_edit.setText('countdown')
        self.start_time = datetime.now() # Сохраняем время открытия окна
        self.timer.start(10)
    
    def status_finish(self):
        #send_udp_to_trainer(FINISH_COMMAND, self._info)
        self.race_status_edit.setText('finish')
        self.timer.stop()
        self.send_info()
        
    def send_extra_info(self, info):
        for racerWidget in self.racer_widgets:
            racerWidget.distance = info['distance']
            racerWidget.add_info_to(info)
            
    def closeEvent(self, event):
        #self.ws_sender.stop()
        
        self.stop_httpd_server()
        self.http_server_thread.join()

        return super().closeEvent(event)

    def stop_httpd_server(self):
        if self.httpd_server is not None:
            self.httpd_server.shutdown()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
