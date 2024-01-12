from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt
from regatta import RacerModel

   
class RacerWidget(QWidget):
    _line = 1
    _distance = 300
    _racer_info = RacerModel("Иванов", 0, 0, 0)
    
    auto_mode = False
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.update_info()
        
    def __init__(self, racer_info, distance=200, line=1):
        super().__init__()
        self._racer_info = racer_info
        self._distance = distance
        self._line = line
        self.initUI()
        self.update_info()
    
    #make property for all attributes
    @property
    def racer_info(self):
        return self._racer_info
    
    @racer_info.setter
    def racer_info(self, value):
        self._racer_info = value
        self.update_info()
        
    @property
    def distance(self):
        return self._distance
    
    @distance.setter
    def distance(self, value):
        if value != self._distance:
            self._distance = value
            self.distanceSlider.setValue(0)
            self.distanceSlider.setMaximum(self._distance)
            self.update_info()
        
    @property
    def line(self):
        return self._line
    
    @line.setter
    def line(self, value):
        self._line = value
        self.update_info()
    

    def initUI(self):
        # создаем метки для отображения имени гонщика и значения скорости
        self.lineLabel = QLabel('Линия: ', self)
        self.nameLabel = QLabel('ФИО:', self)
        self.name_edit = QLineEdit()
        self.name_edit.setMaximumHeight(20)
        self.speedLabel = QLabel('Скорость:', self)
        self.sped_edit = QLineEdit()
        self.sped_edit.setMaximumHeight(20)

        # создаем слайдер для выбора значения distance
        self.distanceSlider = QSlider(Qt.Horizontal, self)
        self.distanceSlider.setMinimum(0)
        self.distanceSlider.setMaximum(self._distance)
        self.distanceSlider.setValue(0)
        self.distanceSlider.setTickPosition(QSlider.TicksBelow)
        self.distanceSlider.setTickInterval(10)
        self.distanceSlider.valueChanged[int].connect(self.changeDistance)
        
        self.auto_mode = QCheckBox('Авто', self)
        self.auto_mode.setChecked(True)

        # создаем метку для отображения значения distance
        self.distanceLabel = QLabel('Distance: 0', self)

        row = QHBoxLayout()
        row.addWidget(self.lineLabel)
        row.addWidget(self.nameLabel)
        row.addWidget(self.name_edit)
        row.addWidget(self.speedLabel)
        row.addWidget(self.sped_edit)
        row.addWidget(self.auto_mode)
        row.addStretch(1)
        row.addWidget(self.distanceLabel)
        # создаем вертикальный layout и добавляем все элементы на виджет
        vbox = QVBoxLayout()
        vbox.addLayout(row)
        vbox.addWidget(self.distanceSlider)
        vbox.addStretch(1)
        self.setLayout(vbox)

    def changeDistance(self, value):
        self._racer_info.s = value
        self.distanceLabel.setText('Пройдено: {} из {} за {} c'.format(self._racer_info.s, self._distance, self._racer_info.t))
        
    def update_info(self):
        self.name_edit.setText(self._racer_info.racer)
        self.sped_edit.setText(str(self._racer_info.v))
        self.lineLabel.setText('Линия: {}'.format(self._line))
        self.distanceSlider.setValue(self._racer_info.s)
        
    def tick(self, elapsed_time):
        if self.auto_mode.isChecked() and not self.is_finished():
            self._racer_info.t = elapsed_time
            self.distanceSlider.setValue(self._racer_info.v * (elapsed_time/1000))
            
    def reset(self):
        self._racer_info.t = 0
        self.distanceSlider.setValue(0)
        
    def is_finished(self):
        return self.distanceSlider.value() >= self._distance
                        
    def send_info(self):
        self._racer_info.racer = self.name_edit.text()
        try:
            if self.sped_edit is not None:
                text = self.sped_edit.text() or '0'
                self._racer_info.v = float(text)
        except ValueError:
            # Handle the case where the text cannot be converted to a float
            # For example, display an error message or set a default value.
            pass
        self._racer_info.s = self.distanceSlider.value()


    def add_info_to(self, dict):
        dict[self.line] =  self.racer_info.as_dict()

if __name__ == '__main__':
    app = QApplication([])
    widget = RacerWidget(RacerModel("Иванов", 0, 0, 0))
    widget.show()
    app.exec_()
