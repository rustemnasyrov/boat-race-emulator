from PyQt5.QtCore import QThread, pyqtSignal
import socket
import time

class RecieveThread(QThread):
    message_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    data = None
    connection = None

    def __init__(self, parent):
        super().__init__(parent)
        self.data = parent
        self.socket = None  # добавляем атрибут для хранения сокета

    def update_status(self, status):
        self.status_changed.emit(status)
        print(status)

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # сохраняем сокет в атрибут
        with self.socket as s:
            print("try bind {}".format(self.data.server_address))
            s.bind(self.data.server_address)
            s.listen()
            self.update_status("Клиент запущен и прослушивает порт {}:{}".format(*self.data.server_address))

            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        self.connection = conn
                        self.update_status(f"Подключение от {addr}")
                        while True:
                            data = conn.recv(5024)
                            if not data:
                                break
                            message = data.decode('utf-8')
                            #print(f"Получены данные: {message}")
                            self.message_received.emit(message)
                except ConnectionResetError:
                    self.update_status("Соединение потеряно, ожидание восстановления...")
                    time.sleep(0.1)  # задержка в 0.1 секунду

    def cleanup(self):
        self.update_status("Закрываем соединение...")
        
        if self.connection:
            self.update_status("Закрываем Коннекцию...")
            self.connection.close()
            
        if self.socket:
            self.socket.close()  # закрываем сокет при остановке потока
            self.socket = None
