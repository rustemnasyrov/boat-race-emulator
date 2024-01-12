
import random


#---   Это формат итогового пакета, который генерирется классами ниже
#----------------------------------------------------------------
info_dict = { 
    'regatta' : 'Кубок', #Наименование турнира
    'race' : "Мужчины", #Наименование заезда
    'race status' : 'ready', #ready - стоим на страте, готовы; go - выполнение заезда; finish - заезд окончен 
    'distance' : 300, #дистанция заезда
    'timer' : 0, #время в 10 долях секунд от начала старта. может время будет статусом?
    'tracks' : { 1 :  { #ключ - номер дорожки, заначение - информация о лодке и спротсмене
                    'racer': "Иванов", #ФИО гонщика
                    's': 0,  #расстояние в метрах от старта (может сделать миллиметры и гонять int?)
                    'v': 0,  #моментальная скорость в метрах в секунду (float или сделать миллиметры в секунду и гонять int?)
                    't': 0}, #время от начала старта в миллисекндах на которое получены v и s (int) фактическилокальное время тренажёра
                } 
}

#----------------------------------------------------------------

names = ["Агафонова И.",
         "Нерманова А.",
         "Сергеева Н.",
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
    def __init__(self, racer, v, s, t):
        self.racer = racer
        self.v = v
        self.s = s
        self.t = t
        
    def as_dict(self):
        return {'racer': self.racer, 'v': self.v, 's': self.s, 't': self.t}
    
    def from_dict(self, dict):
        self.racer = dict['racer']
        self.v = dict['v']
        self.s = dict['s']
        self.t = dict['t']
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
        self.distance = distance
        self.race_status = 'ready'
        self.timer = 0
        self.tracks = {}
        self.init_tracks()
        
    def init_tracks(self):
        for i in range(1, 10):
            self.tracks[i] = RacerModel(names[i], round(random.uniform(4.1, 5.6),1), 0, 0)

    def add_track(self, line, dict):
        if line in self.tracks:
            self.tracks[line].from_dict(dict)
        else:
            racer = RacerModel('Иванов', round(random.uniform(4.1, 5.6),1), 0, 0)
            self.tracks[line] = racer.from_dict(dict)

    def to_dict(self):
        tracks_dict = {}
        for i, track in self.tracks.items():
            tracks_dict[i] = track.as_dict()
        
        return {
            self.REGATTA_NAME_KEY: self.regatta_name,
            self.RACE_NAME_KEY: self.race_name,
            self.DISTANCE_KEY: self.distance,
            self.RACE_STATUS_KEY: self.race_status,
            self.TIMER_KEY: self.timer,
            self.TRACKS_KEY: tracks_dict
        }
        
    def __json__(self):
        return self.to_dict()

    @classmethod
    def default(cls):
        return RegattaRaceModel('Кубок', 'Мужчины', 300)

    def from_dict(self, race_dict):
        self.regatta_name = race_dict[self.REGATTA_NAME_KEY]
        self.race_name = race_dict[self.RACE_NAME_KEY]
        self.distance = race_dict[self.DISTANCE_KEY]
        self.race_status = race_dict[self.RACE_STATUS_KEY]
        self.timer = race_dict[self.TIMER_KEY]
        for i, track in race_dict[self.TRACKS_KEY].items():
            self.add_track(int(i), track)
        
        return self

#---   Это формат итогового пакета, котоыф генерирется классами ниже
#----------------------------------------------------------------
info_old = { 
    'regatta' : 'Кубок', #Наименование турнира
    'race' : "Мужчины", #Наименование заезда
    'race status' : 'ready', #ready - стоим на страте, готовы; go - выполнение заезда; finish - заезд окончен 
    'distance' : 300, #дистанция заезда
    'timer' : 0, #время в 10 долях секунд от начала старта. может время будет статусом?
    'tracks' : { 1 :  { #ключ - номер дорожки, заначение - информация о лодке и спротсмене
                    'racer': "Иванов", #ФИО гонщика
                    's': 0,  #расстояние в метрах от старта (может сделать миллиметры и гонять int?)
                    'v': 0,  #моментальная скорость в метрах в секунду (float или сделать миллиметры в секунду и гонять int?)
                    't': 0}, #время от начала старта в миллисекндах на которое получены v и s (int) фактическилокальное время тренажёра
                } 
}

#----------------------------------------------------------------

