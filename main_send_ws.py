import websocket
import json
import threading
import time

# Создаем словарь с данными, которые мы хотим отправить
data = {
    "1": {'racer': 'John', 'speed': '50', 'distance': '100', 'time': '0'},
    "2": {'racer': 'Jane', 'speed': '60', 'distance': '200', 'time': '0'},
    "3": {'racer': 'Jack', 'speed': '70', 'distance': '300', 'time': '0'},
    "4": {'racer': 'Jill', 'speed': '80', 'distance': '400', 'time': '0'},
    "5": {'racer': 'Joe', 'speed': '90', 'distance': '500', 'time': '0'},
    "6": {'racer': 'Jen', 'speed': '100', 'distance': '600', 'time': '0'},
    "7": {'racer': 'Jas', 'speed': '110', 'distance': '700', 'time': '0'},
    "8": {'racer': 'Jax', 'speed': '120', 'distance': '800', 'time': '0'},
    "9": {'racer': 'Jay', 'speed': '130', 'distance': '900', 'time': '0'}
    }

#Перепеши то что ниже в класс для работы с вэб-сокетом
class WebsocketSender:
    
    def __init__(self, url, data_function):
        self.url = url
        self.data_function = data_function
        self.do_run = True
        
        
    def start(self):
        self.thread = threading.Thread(target=self.send_data_to_websocket)
        self.thread.start()
        
    def stop(self):
        self.do_run = False
        self.close()
        self.thread.join()
        
    def close(self):
        if self.ws:
            self.ws.close()
            self.ws = None
        
    def send_data_to_websocket(self):
        self.ws = None
        while self.do_run:
            try:
                if not self.ws:
                    self.ws = websocket.WebSocket()
                    self.ws.connect(self.url)
                # Отправляем JSON-данные на вэб-сокет
                data = self.data_function()
                self.ws.send(json.dumps(data))
                time.sleep(0.01)
            except Exception as e:
                print('Websocket send error {}'.format(e))
                time.sleep(5)
                self.ws = None
        
        self.close()

    def receive_data_from_websocket(self):
        while self.do_run:
            try:
                message = self.ws.recv()
                # Обрабатываем полученные данные в json
                json_data = json.loads(message)

                print(message)
            except Exception as e:
                print('Websocket receive error {}'.format(e))
                time.sleep(5)
                self.ws = None


def get_data():
    return data

# Запускаем функцию отправки данных в отдельном потоке
if __name__ == '__main__':
    t = WebsocketSender('ws://31.129.102.190:8000/ws/simulators', get_data)
    t.start()

