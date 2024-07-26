import pygame
from dialog_ip_port_editor import IpPortDialog
from racer_ui import RacerModel, RacerWidget
import regatta
from main_send_thread import DataSendingThread
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog
from PyQt5.QtCore import QMutex, QMutexLocker
from PyQt5.QtGui import QIntValidator


class MainWindowBase(QWidget):
    _info = regatta.RegattaRaceModel.default()
    _info_lock = QMutex()
    _server_address = ('127.0.0.1', 5555)
    server_thread = None

    def __init__(self):
        super().__init__()
        
        # Загрузка звукового файла
        pygame.init()
        sound_file_start = "horn.wav"  # Укажите путь к вашему звуковому файлу
        sound_file_esatfets = "horn_gong.wav"
        
        pygame.mixer.init
        pygame.mixer.music.load(sound_file_start)
        
        self.estafet_sound = pygame.mixer.Sound(sound_file_esatfets)
        
        self.dict = self._info.to_dict()

        self.int_ui()
        self.update_info()
        
        self.start_server()
        
     
    def int_ui(self):
        self.regatta_label = QLabel('Наименование турнира:')
        self.regatta_edit = QLineEdit()
        self.race_label = QLabel('Наименование заезда:')
        self.race_edit = QLineEdit()
        self.race_status_label = QLabel('Статус заезда:')
        self.race_status_edit = QLineEdit()
        self.distance_label = QLabel('Дистанция заезда:')
        self.distance_edit = QLineEdit()
        self.distance_edit.setValidator(QIntValidator())
        self.timer_label = QLabel('Время заезда:')
        self.timer_edit = QLineEdit()
        self.timer_edit.setValidator(QIntValidator())
        self.status_label = QLabel('Статус:')
        self.setup_button = QPushButton('Настроить')
        self.setup_button.clicked.connect(self.setup_server_address)

        layout = QVBoxLayout()
        self.main_layout = layout
        row_1 = QHBoxLayout()
        row_1.addWidget(self.regatta_label)
        row_1.addWidget(self.regatta_edit)
        row_1.addWidget(self.race_label)
        row_1.addWidget(self.race_edit)
        row_1.addWidget(self.distance_label)
        row_1.addWidget(self.distance_edit)
        layout.addLayout(row_1, 1)

        row_2 = QHBoxLayout()
        row_2.addWidget(self.race_status_label)
        row_2.addWidget(self.race_status_edit)
        row_2.addWidget(self.timer_label)
        row_2.addWidget(self.timer_edit)
        layout.addLayout(row_2)
        
        row_3 = QHBoxLayout()
        row_3.addWidget(self.setup_button)
        row_3.addWidget(self.status_label)
        row_3.setStretchFactor(self.setup_button, 1)
        row_3.setStretchFactor(self.status_label, 5)
        layout.addLayout(row_3)

        self.add_buttons(layout)
        self.add_racers(layout)

        self.setLayout(layout)
        
        #self.connect_notifications()
        
    def setup_server_address(self):
        # Создаем диалоговое окно и отображаем его
        dialog = IpPortDialog(self._server_address[0], self._server_address[1])
        if dialog.exec_() == QDialog.Accepted:
            # Если пользователь нажал OK, устанавливаем значения IP и порта
            ip, port = dialog.getValues()
            self._server_address = (ip, int(port))
            self.restart_server()
            
    @property
    def server_address(self):
        return self._server_address
    
    def restart_server(self):
        pass
            
    def add_racers(self, lyout):
        vbox = QVBoxLayout()
        self.racer_widgets = []
        for i, racer in self._info.tracks.items():
            self.racer_widgets.append(RacerWidget(racer, distance=self._info.distance, line = i))
            vbox.addWidget(self.racer_widgets[-1])
        lyout.addLayout(vbox)
        
    def delete_racers(self):
        for racer_widget in self.racer_widgets:
            self.main_layout.removeWidget(racer_widget)
        self.racer_widgets = []

    def connect_notifications(self):
        controls = ['regatta_edit', 'race_edit', 'distance_edit', 'timer_edit', 'race_status_edit']
        for control in controls:
            getattr(self, control).textChanged.connect(self.send_info)

    def play_horn(self):
        # Воспроизведение звука
        pygame.mixer.music.play()
        
    def add_buttons(self, layout):
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_info)
        layout.addWidget(self.send_button)
        
    def set_info(self, info):
        with QMutexLocker(self._info_lock):
           self._info.from_dict(info)
           self.update_info()
        
    def get_info(self):
        with QMutexLocker(self._info_lock):
            return self._info.to_dict()

    def get_info_without_mutes(self):
        return self._info
    def get_tracks_info(self):
        with QMutexLocker(self._info_lock):
            return self._info.tracks_dict(False)

    def update_info(self):
        self.regatta_edit.setText(self._info.regatta_name)
        self.race_edit.setText(self._info.race_name)
        self.race_status_edit.setText(self._info.race_status)
        self.distance_edit.setText(str(self._info.get_distance_meters()))
        self.timer_edit.setText(str(self._info.timer))
        for racerWidget in self.racer_widgets:
            racerWidget.distance = self._info.get_distance_meters()
            racerWidget.update_info()
                          
    def update_status(self, status):
        self.status_label.setText(status)

    def send_info(self):
        with QMutexLocker(self._info_lock):
            self.send_info_safe()

    def send_info_safe(self):
        self._info.regatta_name = self.regatta_edit.text()
        self._info.race_name = self.race_edit.text()
        self._info.race_status = self.race_status_edit.text()
        self._info.set_distance_meters(int(self.distance_edit.text() or '200'))
        self._info.timer = int(self.timer_edit.text() or '0') 
        for racer_widget in self.racer_widgets:
            racer_widget.distance = self._info.get_distance_meters()
            racer_widget.send_info()
                
    def start_server(self):
        pass
    
    def stop_server(self):
        if self.server_thread is None:
            return
        
        
        self.server_thread.cleanup()
        self.server_thread.terminate()
        self.server_thread.wait()
        
    def restart_server(self):
        self.stop_server()
        self.start_server()
                
    def closeEvent(self, event):
        self.stop_server()
   



