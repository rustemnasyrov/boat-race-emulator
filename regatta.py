
import random


#---   Это формат итогового пакета, который генерирется классами ниже
#----------------------------------------------------------------
info_dict = { 
    'regatta' : 'НОВА РЕГАТТА', #Наименование турнира
    'race' : "Открытый заезд", #Наименование заезда
    'race status' : 'ready', #ready - стоим на страте, готовы; go - выполнение заезда; finish - заезд окончен 
    'distance' : 100, #дистанция заезда в метрах
    'timer' : 0, #время в 10 долях секунд от начала старта. может время будет статусом?
    'tracks' : { 1 :  { #ключ - номер дорожки, заначение - информация о лодке и спротсмене
                    'racer': "Иванов", #ФИО гонщика
                    'distance': 0,  #расстояние в миллиметрах от старта (int диапазон от 0 до 2000 метров в основном, но может быть и больше)
                    'speed': 0,  #моментальная скорость в миллиметрах в секунду (int)
                    'time': 0}, #время от начала старта в миллисекндах на которое получены v и s (int) фактически локальное время тренажёра
                } 
}

#----------------------------------------------------------------

names = ["Агафонова И.",
         "Михайлов А.",
         "Васильев Н.",
         "Алексеева А.",
         "Смирнова Н.",
         "Кузнецова Н.",
         "Павлова Н.",
         "Михайлова Н.",
         "Васильева Н.",
         "Феоктистова Н.",
         "Борисова Н.",
         "Антонова Н.",
         "Тарасова Н.",
         "Александрова Н.",
         "Петрова Н."]

class RacerModel:
    RC_RACER_KEY = 'racer'
    RC_SPEED_KEY = 'speed'
    RC_DISTANCE_KEY = 'distance'
    RC_TIME_KEY = 'time'
    RC_STROKE_RATE_KEY = 'stroke_rate' 
    
    DISTANCE_MULTIPLAYER = 1000
    
    def __init__(self, racer, speed, distance, time=0):
        self.racer = racer
        self.set_speed_meters_sec(speed)
        self.set_distance_meters(distance)
        self.time = time #milis
        self.weight = 60
        self.age = 15
        self.trainer_id = 0
        self.stroke_rate = 220

    def set_time_from_seconds(self, seconds):
        self.time = int(seconds * 1000)
    def set_distance_meters(self, distance):
        self.distance = int(distance * self.DISTANCE_MULTIPLAYER)
        
    def get_distance_meters(self):
        return self.distance / self.DISTANCE_MULTIPLAYER
    
    def set_speed_meters_sec(self, speed):
        self.speed = int(speed * self.DISTANCE_MULTIPLAYER)
    def get_speed_meters_sec(self):
        return self.speed / self.DISTANCE_MULTIPLAYER
        
    def as_dict(self, with_racer=True):
        result = {self.RC_SPEED_KEY: self.speed, self.RC_DISTANCE_KEY: self.distance, self.RC_TIME_KEY: self.time, self.RC_STROKE_RATE_KEY: self.stroke_rate}
        if with_racer:
            result[self.RC_RACER_KEY] = self.racer
        return result
    
    def from_dict(self, dict):
        self.racer = dict[self.RC_RACER_KEY]
        self.speed = int(dict[self.RC_SPEED_KEY])
        self.distance = int(dict[self.RC_DISTANCE_KEY])
        self.time = int(dict[self.RC_TIME_KEY])
        self.stroke_rate = int(dict[self.RC_STROKE_RATE_KEY])
        return self
    
class RegattaRaceModel:
    REGATTA_NAME_KEY = 'regatta'
    RACE_NAME_KEY = 'race'
    DISTANCE_KEY = 'distance'
    RACE_STATUS_KEY = 'status'
    TIMER_KEY = 'timer'
    TRACKS_KEY = 'tracks'
    
    def __init__(self, regatta_name, race_name, distance):
        self.regatta_name = regatta_name
        self.race_name = race_name
        self.set_distance_meters(distance)
        self.race_status = 'ready'
        self.timer = 0
        self.tracks = {}
        self.init_tracks()
        
    @property
    def is_status_countdown(self):
        return self.race_status == 'countdown'
    
    @property
    def is_status_running(self):
        return self.race_status == 'go'
    
    def set_distance_meters(self, distance):
        self.distance = distance * RacerModel.DISTANCE_MULTIPLAYER
        
    def get_distance_meters(self):
        return int(self.distance / RacerModel.DISTANCE_MULTIPLAYER)
        
    def init_tracks(self):
        for i in range(1, 6):
            self.tracks[i] = RacerModel(names[i], 0, 0, 0)

    def add_track(self, line, dict):
        if line in self.tracks:
            self.tracks[line].from_dict(dict)
        else:
            racer = RacerModel('Иванов', round(random.uniform(4.1, 5.6),1), 0, 0)
            self.tracks[line] = racer.from_dict(dict)

    def to_dict(self):
        tracks_dict = self.tracks_dict()
        
        return {
            self.REGATTA_NAME_KEY: self.regatta_name,
            self.RACE_NAME_KEY: self.race_name,
            self.DISTANCE_KEY: self.get_distance_meters(),
            self.RACE_STATUS_KEY: self.race_status,
            self.TIMER_KEY: self.timer,
            self.TRACKS_KEY: tracks_dict
        }

    def tracks_dict(self, with_racer=True):
        tracks_dict = {}
        for i, track in self.tracks.items():
            tracks_dict[i] = track.as_dict(with_racer)
        return tracks_dict
        
    def __json__(self):
        return self.to_dict()

    @classmethod
    def default(cls):
        return RegattaRaceModel('AAA CUP 2024', 'Открытый заезд', 50)

    def from_dict(self, race_dict):
        self.regatta_name = race_dict[self.REGATTA_NAME_KEY]
        self.race_name = race_dict[self.RACE_NAME_KEY]
        self.distance = race_dict[self.DISTANCE_KEY]
        self.race_status = race_dict[self.RACE_STATUS_KEY]
        self.timer = race_dict[self.TIMER_KEY]
        for i, track in race_dict[self.TRACKS_KEY].items():
            self.add_track(int(i), track)
        
        return self
    



