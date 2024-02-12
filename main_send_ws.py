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
    cnt = 0
    def __init__(self, url, data_function):
        self.url = url
        self.data_function = data_function
        self.do_run = True

        
        
    def start_send(self):
        self.thread = threading.Thread(target=self.send_data_to_websocket)
        self.thread.start()

    def start_receive(self):
        self.thread = threading.Thread(target=self.receive_data_from_websocket)
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
                time.sleep(2)
            except Exception as e:
                print('Websocket send error {}'.format(e))
                time.sleep(5)
                self.ws = None
        
        self.close()

    def receive_data_from_websocket(self):
        self.ws = None
        while self.do_run:
            try:
                if not self.ws:
                    self.ws = websocket.WebSocket()
                    self.ws.connect(self.url)

                message = self.ws.recv()
                # Обрабатываем полученные данные в json
                json_data = json.loads(message)
                self.data_function(json_data)
            except Exception as e:
                print('Websocket receive error {}'.format(e))
                time.sleep(5)
                self.ws = None


def send_data():
    return data

def receive_data(data):
    cur = data['simulators']
    for i in (data['simulators']):
        print(cur[i]['fio'])

# Запускаем функцию отправки данных в отдельном потоке
if __name__ == '__main__':
    t = WebsocketSender('ws://31.129.102.190:8000/ws/simulators', send_data)
    t.start_send()
    t = WebsocketSender('ws://31.129.102.190:8000/ws/commands', receive_data)
    t.start_receive()

