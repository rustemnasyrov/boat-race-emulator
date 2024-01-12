import sys
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from main_window_base import MainWindowBase
from recieve_test_thread import RecieveThread
import json
    
class MainWindowRecieve(MainWindowBase):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Клиент для проверки получения пакетов")  
        

    def start_server(self):
        self.server_thread = RecieveThread(self)
        self.server_thread.message_received.connect(self.message_recieved)
        self.server_thread.status_changed.connect(self.update_status)
        self.server_thread.start()
         
    def message_recieved(self, message):
        try:
          data = json.loads(message) 
          self.set_info(data)
        except Exception as e:
            print(e)
    
    def add_buttons(self, layout):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindowRecieve()
    window.show()

    sys.exit(app.exec_())
