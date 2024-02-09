from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox
import socket

class IpPortDialog(QDialog):
    
    def __init__(self, ip='', port=''):
        super().__init__()
        
        self.ip = ip
        self.port = str(port)
        
        self.initUI()
        
    def initUI(self):
        
        # Создаем подписи для полей ввода
        ip_label = QLabel('IP:', self)
        port_label = QLabel('Port:', self)
        
        # Создаем поля ввода IP и порта и устанавливаем начальные значения
        self.ip_edit = QLineEdit(self)
        self.ip_edit.setText(self.ip)
        
        self.port_edit = QLineEdit(self)
        self.port_edit.setText(self.port)
        
        # Создаем кнопки OK и Cancel
        ok_btn = QPushButton('OK', self)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton('Cancel', self)
        cancel_btn.clicked.connect(self.reject)
        
        # Создаем горизонтальный контейнер для полей ввода и подписей
        ip_hbox = QHBoxLayout()
        ip_hbox.addWidget(ip_label)
        ip_hbox.addWidget(self.ip_edit)
        
        port_hbox = QHBoxLayout()
        port_hbox.addWidget(port_label)
        port_hbox.addWidget(self.port_edit)
        
        # Создаем вертикальный контейнер для всех элементов
        vbox = QVBoxLayout()
        vbox.addLayout(ip_hbox)
        vbox.addLayout(port_hbox)
        vbox.addWidget(ok_btn)
        vbox.addWidget(cancel_btn)
        
        # Устанавливаем главный контейнер для окна
        self.setLayout(vbox)
        
        self.setWindowTitle('IP and Port')
        
    def getValues(self):
        # Возвращает значения IP и порта, введенные пользователем в диалоге
        return (self.ip, self.port)
    
    def validate_ip_port(self):
        ip = self.ip_edit.text()
        port = self.port_edit.text()

        # Проверяем, что ip является валидным адресом или localhost
        if ip != 'localhost' and not self.is_valid_ip(ip):
            QMessageBox.warning(self, 'Ошибка', 'Некорректный IP-адрес')
            return False

        # Проверяем, что порт является целым числом отличным от нуля
        try:
            port = int(port)
            if port <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Некорректный порт')
            return False

        return True

    def is_valid_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
        
    def accept(self):
        if self.validate_ip_port():
            self.ip = self.ip_edit.text()
            self.port = int(self.port_edit.text())
            super().accept()

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        
        # Создаем кнопку Reconnect
        self.reconnect_btn = QPushButton('Reconnect', self)
        self.reconnect_btn.clicked.connect(self.showDialog)
        
        # Устанавливаем главный контейнер для окна
        vbox = QVBoxLayout()
        vbox.addWidget(self.reconnect_btn)
        self.setLayout(vbox)
        
        self.setGeometry(300, 300, 300, 100)
        self.setWindowTitle('IP and Port')
        self.show()
        
    def showDialog(self):
        # Создаем диалоговое окно и отображаем его
        dialog = IpPortDialog('localhost', '5555')
        if dialog.exec_() == QDialog.Accepted:
            # Если пользователь нажал OK, устанавливаем значения IP и порта
            ip, port = dialog.getValues()
            print('IP:', ip)
            print('Port:', port)

if __name__ == '__main__':
    app = QApplication([])
    ex = Example()
    app.exec_()
