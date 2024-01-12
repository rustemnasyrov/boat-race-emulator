from http.server import HTTPServer
import sys
import socket
import threading
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit
from http_responser import MyHandler
import http_responser
from main_window_base import MainWindowBase
from main_send_thread import DataSendingThread
from datetime import datetime

from racer_ui import RacerModel, RacerWidget

class MainWindow(MainWindowBase):
    start_time = datetime.now() # Сохраняем время открытия окна
    http_server_address = ('127.0.0.1', 8000)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Эмулятор отправки информации о тренажёрах")  
        
         # Создаем таймер и подключаем его к слоту
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_func)
        
        self.http_server_thread = threading.Thread(target=self.start_http_server)
        self.http_server_thread.start()
         
    def start_http_server(self):
        http_responser.response_data = self._info.to_dict()
        self.httpd_server = HTTPServer(self.http_server_address, MyHandler)
        print('Starting http server on {}:{}...'.format(*self.http_server_address))
        self.httpd_server.serve_forever()
        
    def start_server(self):
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
        
    def status_go(self):
        self.race_status_edit.setText('go')
        self.start_time = datetime.now() # Сохраняем время открытия окна
        self.timer.start(100)
    
    def status_finish(self):
        self.race_status_edit.setText('finish')
        self.timer.stop()
        self.send_info()
        
    def send_extra_info(self, info):
        for racerWidget in self.racer_widgets:
            racerWidget.distance = info['distance']
            racerWidget.add_info_to(info)
            
    def closeEvent(self, event):
        self.httpd_server.shutdown()
        self.http_server_thread.join()

        return super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
