from http.server import HTTPServer
import json
import logging
import sys
import socket
import threading
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit
import pygame
from extropolation import BoatParameters
from http_responser import MyHandler, get_current_boat_parameters, get_now_boat_parameters, set_current_boat_parameters
import http_responser
from logger import log_info
from main_send_ws import WebsocketSender
from main_window_base import MainWindowBase
from main_send_thread import DataSendingThread
from datetime import datetime

from racer_ui import RacerModel, RacerWidget
from recieve_udp import receive_udp_from_trainer, stop_udp_recieve
from send_udp import send_udp_to_trainer, PAUSE_COMMAND, START_COMMAND, FINISH_COMMAND


class MainWindow(MainWindowBase):
    start_time = datetime.now() # Сохраняем время открытия окна
    http_server_address = ('127.0.0.1', 8888)
    udp_address = ("192.168.137.1", 62222)
    udp_send_address = ("192.168.137.255", 61111)
    httpd_server = None
    tick_period = 10
    is_fresh_data = [False, False, False, False, False, False, False, False]
    
    def __init__(self):
        super().__init__()

        self.udp_recieve_thread = None
        self.setWindowTitle("Эмулятор отправки информации о тренажёрах")  
        
         # Создаем таймер и подключаем его к слоту
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)

        self.create_logger()


    def create_logger(self):
        # Создаем объект логгера
        self.logger = logging.getLogger(__name__)

        # Устанавливаем уровень логирования
        self.logger.setLevel(logging.INFO)

        # Создаем обработчик для записи в файл
        file_handler = logging.FileHandler('my_log_file.log')

        # Устанавливаем уровень логирования для обработчика
        file_handler.setLevel(logging.INFO)

        # Создаем форматтер для сообщений лога
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Устанавливаем форматтер для обработчика
        file_handler.setFormatter(formatter)

        # Добавляем обработчик к логгеру
        self.logger.addHandler(file_handler)

        self.logger.info('Application started')
        http_responser.logger = self.logger

    
         
    def start_http_server(self):
        self.stop_httpd_server()
        http_responser.response_data = self._info.to_dict()
        self.httpd_server = HTTPServer(self.http_server_address, MyHandler)
        print('Starting http server on {}:{}...'.format(*self.http_server_address))
        self.httpd_server.serve_forever()

    def recieve_udp_packets(self):
        receive_udp_from_trainer(self.process_udp_packet, self.udp_address)

    def process_udp_packet(self, lane, boat_id, state, distance, time, speed,  acceleration, boatTime):
      
        if lane in self._info.tracks:
            track = self._info.tracks[lane]
            track.trainer_id = boat_id
            
            if self._info.is_status_running:
                track.set_distance_meters(distance)
                #self.logger.info('udp_distance: ' + str(distance))
                track.time = int(boatTime * 1000)
                track.set_speed_meters_sec(speed)
                
                self.is_fresh_data[lane] = True

            if self._info.is_status_running:
                self.racer_widgets[lane-1].update_info()
            

            
        #http_responser.response_data = self._info.to_dict()
        
        
    def start_server(self):
        self.udp_recieve_thread = threading.Thread(target=self.recieve_udp_packets)
        self.udp_recieve_thread.start()


        self.http_server_thread = threading.Thread(target=self.start_http_server)
        self.http_server_thread.start()
        
        #self.ws_sender= WebsocketSender('ws://31.129.102.190:8000/simulators', self.get_tracks_info)
        #self.ws_sender.start()
        
        #self.start_server_thread()
        
    def start_server_thread(self):
        self.server_thread = DataSendingThread(self)
        self.server_thread.status_changed.connect(self.update_status)
        self.server_thread.start()
        
    def send_info_safe(self):
        super().send_info_safe()
        if not self._info.is_status_running:
            http_responser.response_data = self._info.to_dict()


    def update_track_param(self, track_num):  
        #log_info('--->> update_track_param')  
        comment = ''
        track = self._info.tracks[track_num]    
        if self.is_fresh_data[track_num]:
            #log_info('fresh:')  
            self._current_boat_parameters[track_num] = BoatParameters(track.time, track.speed, track.distance, self._current_boat_parameters[track_num])
            self.is_fresh_data[track_num] = False
            comment = f'udp: for time {self._current_boat_parameters[track_num].timestamp}'
            #log_info(f'{comment}')
        else:
            #log_info(f">> extrpol started << for: {self._current_boat_parameters[track_num].timestamp}")
            if self._current_boat_parameters[track_num]:
                params = self._current_boat_parameters[track_num].get_next_for_now()
                #log_info(f'extrpol: for time {self._current_boat_parameters[track_num].timestamp}')
                if params:
                    track.time = params.time
                    track.distance = params.distance 
                    track.speed = params.speed
                    comment = f'Extrp: for time {params.timestamp}'
        
        self.update_info()
        http_responser.response_data = self._info.to_dict()
        log_info(f'update: track - {track_num} {int(track.time)} {track.speed} {track.distance} {comment}')
        #log_info('---------------------------------------------------------------------------------------->>')  

    def update_tracks(self):
        if not self._info.is_status_running:
            return 
        for i in range(1,3):
            self.update_track_param(i)

    def update_func(self):
        current_time = datetime.now()
        elapsed_time = int((current_time - self.start_time).total_seconds() * 1000)
        self.tick(elapsed_time)
        if self._info.is_status_running:
            self._info.timer = elapsed_time
        self.update_tracks()
        #self.send_info()
        is_all_finished = all(racerWidget.is_finished() for racerWidget in self.racer_widgets)

        if is_all_finished:
            self.status_finish()
        
    def tick(self, elapsed_time):
        self.timer_edit.setText(str(elapsed_time)) # Отображаем время в момент обновления 
        
        if self._info.is_status_countdown and elapsed_time >= 2900:
            self.race_status_edit.setText('go')
            self._info.race_status = 'go'
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
        
    def reconnect(self):
        pass
        
    def status_ready(self):
        self.race_status_edit.setText('ready')
        self.timer.stop() 
        self.timer_edit.setText('0')
        for racerWidget in self.racer_widgets:
            racerWidget.reset()
        self.send_info()
        send_udp_to_trainer(self._info, self.udp_send_address)

    def status_go(self):
        self.race_status_edit.setText('countdown')
        self.start_time = datetime.now() # Сохраняем время открытия окна
        self.timer.start(self.tick_period)
        self.send_info()
        send_udp_to_trainer(self._info, self.udp_send_address)
    
    def status_finish(self):
        self.race_status_edit.setText('finish')
        self.timer.stop()
        self.send_info()
        send_udp_to_trainer(self._info, self.udp_send_address)

    def send_extra_info(self, info):
        for racerWidget in self.racer_widgets:
            racerWidget.distance = info['distance']
            racerWidget.add_info_to(info)
            
    def closeEvent(self, event):
        stop_udp_recieve()

        #self.ws_sender.stop()
        
        self.stop_httpd_server()
        self.http_server_thread.join()

        return super().closeEvent(event)

    def stop_httpd_server(self):
        if self.httpd_server is not None:
            self.httpd_server.shutdown()

    _current_boat_parameters = [None,None,None,None]

    def get_now_boat_parameters(self):
        if self._current_boat_parameters:
            self._current_boat_parameters =  self._current_boat_parameters.get_next_for_now()

        return self._current_boat_parameters

    def set_current_boat_parameters(self, new_boat_parameters):
        if not new_boat_parameters:
            return
        self._current_boat_parameters = new_boat_parameters


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
