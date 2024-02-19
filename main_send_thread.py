import socket
import json
import regatta
import time
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QMutex, QMutexLocker

class DataSendingThread(QThread):
    send_signal = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    _socket = None

    def __init__(self, data):
        super().__init__(parent=data)
        self.data = data
        print("thread started")
        
    def update_status(self, status):
        self.status_changed.emit(status)
        print(status)
        
    def socket(self):
        if not self._socket:
            try:
                self.update_status("Устанавливаем соединение с клиентом {} порт {} ...".format(*self.data.server_address))
                # Создание сокета и установка соединения
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('localhost', 5555) # адрес и порт сервера
                sock.connect(self.data.server_address)
                
                self._socket = sock
                self.update_status('Соединение установлено с {} порт {}'.format(*self.data.server_address))
            except:
                self._socket = None
                
        return self._socket
                

    def run(self):
        while True:
            try:
                info = self.data.get_info()
                if self.socket() and info:
                    data = json.dumps(info).encode('utf-8') # преобразование данных в байты в формате JSON
                    self.socket().sendall(data) # отправка данных
                    time.sleep(0.001) # задержка в 1 секунду перед отправкой следующих данных
            except :
                self.update_status("Соединение потеряно. Переподключаемся...")
                self._socket = None
        
    
    def cleanup(self):
        self.update_status("Закрываем соединение...")
            
        if self._socket:
            self._socket.close()  # закрываем сокет при остановке потока
            self._socket = None
