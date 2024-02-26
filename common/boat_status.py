import json
from boat_json_injection import BoatJsonInjection

#Константы для статуса дорожки
class BoatStatus:
    READY = 'ready'
    COUNTDOWN = 'countdown'
    GO = 'go'
    FINISH = 'finish'

#Пакет который будет приходит от Fast API к тренажеру
class BoatTrainerParams(BoatJsonInjection):
    def __init__(self):
        self.id = 0 #Уникальный идентификатор тренажера
        self.group = 0 #номер группы дорожек 
        self.track = 0 #номер дорожки в группе
        self.race_distance = 0 #400 - Заданная дистанция гонки - м (float),
        self.racer_weight = 0 #90 - Заданный вес гребца - кг, (int)
        self.racer_age = 0 #45 - Заданный возраст гребца - лет (int)]
        self.race_number = 0 #'456' сартовый номер спортсмена           
        self.status = BoatStatus.READY #статус тренажера
        
#Пакет о состоянии тренажера
class BoatTrainerRaceState(BoatJsonInjection):
    def __init__(self):
        self.id = 0 #Уникальный идентификатор тренажера
        self.time = 0 # Время от начала старта - мс (int) когдда  на финише, тут время заезда конкретного тренажера
        self.acc = 0  #Ускорение на момент time - м/c2 (float)
        self.speed =  0 #Скорость на момент time - м/c (float)
        self.distance = 0  #Дистанция на момент time - м (float)
        self.stroke_rate = 0  #темп гребли на моент time - гр/мин (float)
        self.stroke_qty = 0  #Число гребков на момент time - шт (int)
        self.heart_rate = 0  #ЧСС на момент time - уд/мин (int)
      
#Пакет о состоянии тренажера для Fast API от тренажера
class BoatTrainerInfo(BoatJsonInjection): 
    def __init__(self):
        self.id = 0 #Уникальный идентификатор тренажера
        self.params = BoatTrainerParams()
        self.race_state = BoatTrainerRaceState()

    def to_dict(self):
        return {
            'id': self.id,
            'params': self.params.to_dict(),
            'race_state': self.race_state.to_dict()
        }
        
    @classmethod
    def from_dict(cls, data):
        result = cls()
        result.id = data['id']
        result.params = BoatTrainerParams.from_dict(data['params'])
        result.race_state = BoatTrainerRaceState.from_dict(data['race_state'])
    
if (__name__ == "__main__"):
    paddle1 = BoatTrainerInfo()
    paddle1.distance = 0
    p1_json = paddle1.to_json()
    #delete from dictionary
    del p1_json["group"]
    paddle2 = BoatTrainerInfo()
    paddle2.group = 3435
    paddle2.from_json(p1_json)
    
    print(json.dumps(paddle2.to_json()))