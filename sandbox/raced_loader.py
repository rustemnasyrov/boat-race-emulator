import requests
import json

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
        response = requests.post(url, headers=headers, data=json.dumps(data))

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
    
class DisciplineCommand (APICommand):
    def __init__(self, api):
        super().__init__(api, 'discipline')

    def add(self, title, tournament_id, distance, steps,):
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

    def add(self, title, discipline_id, place, start_time, status, tracks):
        data = {
            'title': title,
            'discipline_id': discipline_id,
            'place': place,
            'start_time': start_time, #"2024-03-14T06:31:00.392Z"
            'status': status,
            'tracks': tracks #["1", "2", "3", "4", "5"]
        }
        return self.post(path=self.path, data=data)
       

class NovaRaceServer (ApiClient):

    def __init__(self, server_address):
        super().__init__(server_address)
        self.discipline = DisciplineCommand(self)

    def tournament_list(self):
        return self.get(path='tournament')['items']
        
    def add_tournament(self, title, start_date, end_date, is_archive = 0):
        data = {
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'is_archive': is_archive
        }
        return self.post(path='tournament', data=data)
    
    def get_tournament(self, id):
        return self.get(path=f'tournament/{id}')
    
    def find_tournament(self, title):
        items = self.tournament_list()
        for item in items:
            if item['title'] == title:
                return item
        return None

    

 
api_client = NovaRaceServer('http://82.97.247.48:8000')

tournament_data = {
    'title': 'Девушки до 15 лет',
    'start_date': '2024-03-13',
    'end_date': '2024-03-13',
    'is_archive': 0
}

#print(api_client.post(tournament_data, path='/tournament/'))
tid = api_client.find_tournament('Девушки до 15 лет')
#api_client.add_discipline('Девушки до 15 лет', tid['id'], 200, 20)
#api_client.add_discipline('Юноши до 15 лет', tid['id'], 200, 20)

print(api_client.discipline.find('Юноши до 15 лет'))


