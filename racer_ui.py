import random
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QComboBox
from PyQt5.QtCore import Qt
from regatta import RacerModel, RacerState

   
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
        self._distance = distance #В метрах
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
            self.set_slider_maximum(self._distance)
            self.update_info()
            
    def set_slider_maximum(self, distance_in_meters):
        self.distanceSlider.setMaximum(distance_in_meters * RacerModel.DISTANCE_MULTIPLAYER)
        
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
        self.weightLabel = QLabel('Вес:', self)
        self.weight_edit = QLineEdit()
        self.ageLabel = QLabel('Возраст:', self)
        self.age_edit = QLineEdit()
        self.speedLabel = QLabel('Скорость:', self)
        self.sped_edit = QLineEdit()
        self.stateLabel = QLabel('Статус:', self)
        self.state_dropdown = QComboBox()
        self.state_dropdown.addItems(RacerState.all())
        self.sped_edit.setMaximumHeight(20)
        self.sped_edit.textChanged.connect(self.on_speed_changed)

        # создаем слайдер для выбора значения distance
        self.distanceSlider = QSlider(Qt.Horizontal, self)
        self.distanceSlider.setMinimum(0)
        self.set_slider_maximum(self._distance)
        self.distanceSlider.setValue(0)
        self.distanceSlider.setTickPosition(QSlider.TicksBelow)
        self.distanceSlider.setTickInterval(RacerModel.DISTANCE_MULTIPLAYER * 10)
        self.distanceSlider.valueChanged[int].connect(self.changeDistance)
        
        self.auto_mode = QCheckBox('Гребём', self)
        self.auto_mode.setChecked(False)
        self.auto_mode.stateChanged.connect(self.toggle_auto)

        # создаем метку для отображения значения distance
        self.distanceLabel = QLabel('Distance: 0', self)

        row = QHBoxLayout()
        row.addWidget(self.lineLabel)
        row.addWidget(self.stateLabel)
        row.addWidget(self.state_dropdown)
        row.addWidget(self.nameLabel)
        row.addWidget(self.name_edit)
        row.addWidget(self.weightLabel)
        row.addWidget(self.weight_edit)
        row.addWidget(self.ageLabel)
        row.addWidget(self.age_edit)
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
        self._racer_info.distance = value 
        self.distanceLabel.setText('Пройдено: {:07.2f} м из {} за {} c'.format(self._racer_info.get_distance_meters(), self._distance, self._racer_info.time))

    def toggle_auto(self):
        if self.auto_mode.isChecked() and not self.racer_info.speed:
            self.sped_edit.setText(str(round(random.uniform(4.1, 5.6),1)))
        
    def update_info_udp(self, distance, speed, time):
        self.racer_info.set_distance_meters(distance)
        self.racer_info.set_speed_meters_sec(speed)
        self.racer_info.set_time_from_seconds(time)
        self.update_info()

    def update_info(self):
        self.name_edit.setText(self._racer_info.racer)
        self.weight_edit.setText(str(self._racer_info.weight))
        self.age_edit.setText(str(self._racer_info.age))
        self.sped_edit.setText(str(self._racer_info.get_speed_meters_sec()))
        self.lineLabel.setText('Линия: {}, {}'.format(self._line, self._racer_info.trainer_id))
        self.distanceSlider.setValue(self._racer_info.distance )
        self.state_dropdown.setCurrentText(self._racer_info.state)
        
    def on_speed_changed(self):
        if self.auto_mode.isChecked(): 
            self.read_speed_from_ui()
        
    def tick(self, elapsed_time):
        if self.auto_mode.isChecked():
            if self.is_finished():
                self._racer_info.state = RacerState.finish
                self.state_dropdown.setCurrentText(RacerState.finish)
            else:
                if elapsed_time > 0:
                    dt = elapsed_time - self._racer_info.time
                    self._racer_info.time = elapsed_time
                    self._racer_info.state = RacerState.go
                    s = self._racer_info.distance + self._racer_info.speed * (dt/1000)
                    self.distanceSlider.setValue(int(s))
            
    def reset(self):
        self._racer_info.time = 0
        self._racer_info.speed = 0
        self._racer_info.state = RacerState.ready
        self.sped_edit.setText('0')
        self.distanceSlider.setValue(0)
        self.auto_mode.setChecked(False)
        
    def is_finished(self):
        return self._racer_info.get_distance_meters() >= self._distance 
                            
    def send_info(self):
        self._racer_info.racer = self.name_edit.text()
        self._racer_info.weight = int(self.weight_edit.text() or '60')
        self.read_speed_from_ui()
        self._racer_info.distance = self.distanceSlider.value()
        self._racer_info.set_state(self.state_dropdown.currentText())

    def read_speed_from_ui(self):
        try:
            if self.sped_edit is not None:
                text = self.sped_edit.text() or '0'
                self._racer_info.set_speed_meters_sec(float(text))
        except ValueError:
            # Handle the case where the text cannot be converted to a float
            # For example, display an error message or set a default value.
            pass


    def add_info_to(self, dict):
        dict[self.line] =  self.racer_info.as_dict()

if __name__ == '__main__':
    app = QApplication([])
    widget = RacerWidget(RacerModel("Иванов", 0, 0, 0))
    widget.show()
    app.exec_()
