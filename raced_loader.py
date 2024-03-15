import requests
import json

from racers_export import read_excel

class APICommand:
    def __init__(self, api, path):
        self.api = api
        self.path = path
       
    def post(self, path, data):
        return self.api.post(path, data)
    
    def add_raw(self, **kwargs):
        return self.post(path=self.path, data=kwargs)
    
    def get(self, path):
        return self.api.get(path)
        
    def list(self):
        return self.get(self.path)['items']
        
    def get_by_id(self, id):
        return self.get(path=f'{self.path}/{id}')
    
    def find(self, title):
        items = self.list()
        for item in items:
            if item['title'] == title:
                return item
        return None
class ApiClient:

    def __init__(self, server_address):
        self.server_address = server_address
        self.auth_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMDUyMzA2NX0.mfIMfMIP5e5ac3H-7sw-JRQbAIf4VvcIkMolKZA5RKM'
        

    def post(self, path, data):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        url = f'{self.server_address}/{path}/'
        data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'There was a problem with your request {url}. Status code:', response.status_code)

    def get(self, path):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        url = f'{self.server_address}/{path}/'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'There was a problem with your request {url}. Status code:', response.status_code)
        
    def get_command(self, path):
        return APICommand(self, path)

class TournamentsCommand (APICommand):
    def __init__(self, api):
        super().__init__(api, 'tournament')

    def add(self, title, start_date, end_date, is_archive = 0, find_before = False):
        
        if find_before:
            item = self.find(title)
            if item is not None:
                return item
            
        data = {
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'is_archive': is_archive
        }
        return self.post(path=self.path, data=data)

    
class DisciplineCommand (APICommand):
    def __init__(self, api):
        super().__init__(api, 'discipline')

    def add(self, title, tournament_id, distance, steps, find_before = False):
        if find_before:
            item = self.find(title)
            if item is not None:
                return item
            
        data = {
            'title': title,
            'tournament_id': tournament_id,
            'distance': distance,
            'steps': steps
        }
        return self.post(path=self.path, data=data)

class RacesCommand (APICommand):
    def __init__(self, api):
        super().__init__(api, 'race')

    def add(self, title, discipline_id, place, start_time, status, tracks, find_before = False):
        if find_before:
            item = self.find(title)
            if item is not None:
                return item

        data = {
            'title': title,
            'discipline_id': discipline_id,
            'place': place,
            'start_time': start_time, #"2024-03-14T06:31:00.392Z"
            'status': status,
            'tracks': tracks #["1", "2", "3", "4", "5"]
        }
        return self.post(path=self.path, data=data)

class SportsmenCommand (APICommand):
    def __init__(self, api):
        super().__init__(api, 'sportsmen')

    def add(self, first_name, last_name, weight, age, tournaments):
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'weight': weight,
            'age': age,
            'tournaments': tournaments
        }
        return self.post(path=self.path, data=data)
       
class NovaRaceServer (ApiClient):

    def __init__(self, server_address):
        super().__init__(server_address)
        self.tournament = TournamentsCommand(self)
        self.discipline = DisciplineCommand(self)
        self.race = RacesCommand(self)
        self.sportsmen = SportsmenCommand(self)

remote_api_client = NovaRaceServer('http://82.97.247.48:8000')

local_api_client = NovaRaceServer('http://localhost:8000')
local_api_client.auth_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxMDYzNTk2M30.v9Nw8MzEumOI2fSKmFr4Y-oPoriJilYwpLsTKIu5xJM'

def create_tournament(api):
    discipline_names = {
        'Девочки до 13 лет',
        'Мальчики до 13 лет',
        'Юноши до 15 лет',
        'Девушки до 15 лет',
        'Юноши до 17 лет',
        'Девушки до 17 лет',
        'Юниоры до 19 лет',
        'Юниорки до 19 лет',
        'Юниоры до 24 лет',
        'Юниорки до 24 лет',
    }

    tournament_title = 'Контрольная Тренировка'

    tour = api.tournament.add(title=tournament_title, start_date='2024-03-15', end_date='2024-03-15', is_archive=0, find_before = True)
    tour_id = tour['id']
    tournaments = [{"id": tour_id, "title": tournament_title}]

    for name in discipline_names:
        api.discipline.add(name, tour_id, 200, 8, find_before = True)

    sportsmans = [
        {'first_name': 'Иван', 'last_name': 'Иванов', 'weight': 70, 'age': 12, 'tournaments': tournaments},
        {'first_name': 'Петр', 'last_name': 'Петров', 'weight': 80, 'age': 11, 'tournaments': tournaments},
        {'first_name': 'Василий', 'last_name': 'Васильев', 'weight': 90, 'age': 10, 'tournaments': tournaments},
        {'first_name': 'Сергей', 'last_name': 'Сергеев', 'weight': 100, 'age': 9, 'tournaments': tournaments},
        {'first_name': 'Алексей', 'last_name': 'Алексеев', 'weight': 110, 'age': 8, 'tournaments': tournaments},
        {'first_name': 'Виктор', 'last_name': 'Викторов', 'weight': 120, 'age': 7, 'tournaments': tournaments},
        {'first_name': 'Виктор1', 'last_name': 'Викторов', 'weight': 120, 'age': 7, 'tournaments': tournaments},
        {'first_name': 'Виктор2', 'last_name': 'Викторов', 'weight': 120, 'age': 7, 'tournaments': tournaments},
        {'first_name': 'Виктор3', 'last_name': 'Викторов', 'weight': 120, 'age': 7, 'tournaments': tournaments}
    ]

    sportman_in_base = []
    tracks = []
    for i in range(len(sportsmans)): 
        sportman = sportsmans[i]
        added_sp = api.sportsmen.add(sportman['first_name'], sportman['last_name'], sportman['weight'], sportman['age'], sportman['tournaments'])
        track = {"number": i+1,"sportsman_id": added_sp['id']}
        tracks.append(track)

#    def add(self, title, discipline_id, place, start_time, status, tracks, find_before = False):
    dsicipline_id = api.discipline.find('Девочки до 13 лет')['id']
    api.race.add('Заезд 1', dsicipline_id, 'СПб', '2024-03-15T06:31:00.392Z', 0, tracks)

def load_tournaments(api):
    racers = read_excel()

    tournament_title = 'КТ от НОВА 2'

    tour = api.tournament.add(title=tournament_title, start_date='2024-03-15', end_date='2024-03-15', is_archive=0, find_before = True)
    tour_id = tour['id']
    tournaments = [{"id": tour_id, "title": tournament_title}]

    for item in racers:
        discipline = api.discipline.add(item, tour_id, 200, 8, find_before = True)
        for zaezd in racers[item]:
            z_racers = racers[item][zaezd]
            print(f'-{zaezd}: {len(z_racers)}')
            tracks = []
            for i in range(0, len(z_racers)):
                sportman = z_racers[i]
                added_sp = api.sportsmen.add(sportman.first_name, sportman.last_name, sportman.weight, sportman.age, tournaments)
                track = {"number": i+1,"sportsman_id": added_sp['id']}
                tracks.append(track)

            #    def add(self, title, discipline_id, place, start_time, status, tracks, find_before = False):
            api.race.add(zaezd, discipline['id'], 'СПб', '2024-03-15T06:31:00.392Z', 0, tracks)

    return racers            


if __name__ == '__main__':
    load_tournaments(remote_api_client)



