import json

from boat_status import BoatStatus, BoatTrainerRaceState, TrackInfo

#Пакет о состоянии тренажера для визуализации  
class TrackInfo(BoatTrainerRaceState):
    def __init__(self):
        super().__init__()
        self.racer = "" #Имя спортсмена

class RaceInfo:
     # информация о соревнованиях в формате JSON
    def __init__(self) :
        self.regatta = 'Чемпионат РФ'
        self.race = 'Мужчины 35+, 400 м, квалификация 1'
        self.race_id = 76788,
        self.distance = 400
        self.status = BoatStatus.READY #ready, countdown, go, finish
        self.tracks_qty = 4 # количество дорожек
        self.tracks = [
            TrackInfo(),
            TrackInfo()
        ]
        
    def to_json(self):
        track_list = []
        for track in self.tracks:
            track_list.append(track.to_json())
            
        result = self.__dict__.copy()
        result['tracks'] = track_list
        
        return result
    
    @classmethod
    def from_json(cls, json_data):
        result = cls()
        track_list = []
        if 'tracks' in json_data:
            for track in json_data['tracks']:
                track_list.append(TrackInfo.from_json(track))
                
        result.__dict__ = json_data
        result.tracks = track_list
        return result
    
if (__name__ == "__main__"):
    paddle1 = RaceInfo()
    print(json.dumps(paddle1.to_json()))
    
    js1 = paddle1.to_json()
    paddle2 = RaceInfo.from_json(js1)
    print(json.dumps(paddle2.to_json()))

