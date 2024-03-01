import websocket
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel
import sys


import json


class WebSocketReciever(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.ws = websocket.WebSocketApp(self.url, on_message=self.on_message)

    def on_message(self, ws, message):
        # Здесь ваш код для обработки полученного сообщения из веб-сокета
        data = json.loads(message)
        self.data_received.emit(data)

    def run(self):
        self.ws.run_forever()

    def send_message(self, message):
        self.ws.send(json.dumps(message))
        
        
#### --- test here -----
class MyApp:
    def __init__(self):
        self.thread = WebSocketReciever('ws://82.97.247.48:8000/ws/commands')
        self.thread.data_received.connect(self.update_label)
        self.thread.start()

    def update_label(self, data):
        print(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())