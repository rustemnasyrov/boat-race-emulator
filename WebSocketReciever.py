import websocket
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel
import sys
import time
import json


class WebSocketReciever(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.ws = websocket.WebSocketApp(self.url, on_message=self.on_message, on_close=self.on_close)
        self.should_stop = False

    def on_message(self, ws, message):
        # Здесь ваш код для обработки полученного сообщения из веб-сокета
        data = json.loads(message)
        self.data_received.emit(data)

    def on_close(self, ws):
        self.reconnect()

    def run(self):
        while not self.should_stop:
            try:
                self.ws.run_forever()
            except websocket.WebSocketConnectionClosedException:
                pass  # Скрываем сообщение об ошибке
            except Exception as e:
                print(f"WebSocket connection lost. Retrying in 1 seconds... {e}")
                time.sleep(1)
                self.reconnect()

    def reconnect(self):
        self.ws = websocket.WebSocketApp(self.url, on_message=self.on_message, on_close=self.on_close)

    def send_message(self, message):
        try:
            self.ws.send(json.dumps(message))
        except Exception as e:
            print(e)

    def stop(self):
        self.should_stop = True
        self.ws.close()
        
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