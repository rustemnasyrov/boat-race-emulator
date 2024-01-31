import threading
import time
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout

from main_send_ws import WebsocketSender
from main_window_base import MainWindowBase
import sys

from recieve_udp import receive_udp_from_trainer
from send_udp import send_udp_to_trainer, PAUSE_COMMAND, START_COMMAND, FINISH_COMMAND

class HostWindow(MainWindowBase):
    id_to_ind = []
    lanes = []
    status_str_to_int = {'go': 0, 'three': 1, 'finish': 2, 'on_start': 3}
    def __init__(self):
        super().__init__()
        self.receive_udp_packets = None


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
        receive_udp_from_trainer(self.process_udp_packet)
    def send_udp_packets(self):
        send_udp_to_trainer(self._info.race_status, self._info)



    def process_udp_packet(self, lane, boat_id, state, distance, time, speed):
        # print(f"id:{boat_id}, state: {state}, distance: {distance}, lane: {lane}")
        if boat_id not in self.lanes:
            print(str(boat_id) + " " + str(lane))
            self.lanes.append(boat_id)
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

        self.udp_send_thread = threading.Thread(target=self.send_udp_packets)
        self.udp_send_thread.start()

        self.ws_sender= WebsocketSender('ws://31.129.102.190:8000/ws/simulators', self.info_to_send)
        self.ws_sender.start_send()

        self.ws_receiver = WebsocketSender('ws://31.129.102.190:8000/ws/commands', self.receive_info)
        self.ws_receiver.start_receive()

    def receive_info(self, data):
        if not data:
            return
        race = data['active_race']
        status = self.status_str_to_int[race['status']]
        distance = 200
        self._info.set_distance_meters(distance)
        print(distance)
        self._info.regatta_name = race['tournament_name']
        self._info.race_name = str(race['discipline_description'])
        self._info.race_status = race['status']
        for idx, value in data['simulators'].items():
            if int(idx) in self._info.tracks:
                track = self._info.tracks[int(idx)]
                track.racer = value['fio']
                track.weight = value['weight']
                track.age = value['age']

        send_udp_to_trainer(status, self.get_info_without_mutes())

        self.update_info()



    def status_ready(self):
        self._info.race_status = 'three'
        self.update_info()
        send_udp_to_trainer('three', self.get_info_without_mutes())


    def status_go(self):
        self._info.race_status = 'go'
        self.update_info()
        send_udp_to_trainer('go', self.get_info_without_mutes())


    def status_finish(self):
        self._info.race_status = 'finish'
        self.update_info()
        send_udp_to_trainer('finish', self.get_info_without_mutes())
    def info_to_send(self):
        data = dict()
        for i in range(9):
            new_d = dict()
            new_d['time'] = self.racer_widgets[i]._racer_info.time
            new_d['speed'] = self.racer_widgets[i]._racer_info.speed
            new_d['distance'] = self.racer_widgets[i]._racer_info.distance
            new_d['state'] = False
            data[str(i+1)] = new_d
        return data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HostWindow()
    window.show()
    sys.exit(app.exec_())