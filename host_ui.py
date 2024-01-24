import threading

from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout

from main_send_ws import WebsocketSender
from main_window_base import MainWindowBase
import sys

from recieve_udp import receive_udp_from_trainer
from send_udp import send_udp_to_trainer, PAUSE_COMMAND, START_COMMAND, FINISH_COMMAND

class HostWindow(MainWindowBase):
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

    def status_ready(self):
        self.send_info()
        send_udp_to_trainer(PAUSE_COMMAND, self.get_info_without_mutes())


    def status_go(self):
        send_udp_to_trainer(START_COMMAND, self.get_info_without_mutes())


    def status_finish(self):
        send_udp_to_trainer(FINISH_COMMAND, self.get_info_without_mutes())


    def receive_udp_packets(self):
        receive_udp_from_trainer(self.process_udp_packet)

    def process_udp_packet(self, lane, boat_id, state, distance, time, speed):
        # print(f"id:{boat_id}, state: {state}, distance: {distance}, lane: {lane}")

        if boat_id == 1054351936:
            self.racer_widgets[1].update_info_udp(distance, speed, time)
        else:
            self.racer_widgets[2].update_info_udp(distance, speed, time)

    def start_server(self):
        self.udp_receive_thread = threading.Thread(target=self.receive_udp_packets)
        self.udp_receive_thread.start()

        self.ws_sender= WebsocketSender('ws://31.129.102.190:8000/ws/simulators', self.get_tracks_info)
        self.ws_sender.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HostWindow()
    window.show()
    sys.exit(app.exec_())