import openpyxl
import requests

class Racer:
    def __init__(self, number, name, year,discipline, class_, coach, organization, weight, weight2, zaezd):
        self.number = number
        self.fio = name
        self.discipline = discipline
        self.year = year
        self.class_ = class_
        self.coach = coach
        self.organization = organization
        self.weight1 = weight
        self.weight2 = weight2 
        self.zaezd_number = zaezd
    
    @property
    def zaezd(self):
        return f'Заезд {self.zaezd_number}'
    
    @property
    def first_name(self):
        #Первый элмент до пробела из self.fio очищенный от ведущих и закрывающих пробелов
        return self.fio.split()[1]
    
    @property
    def last_name(self):
        return self.fio.split()[0].strip()
    
    @property
    def weight(self):
        if self.weight2:
            res=  self.weight2
        res = self.weight1
        return int(res)
    
    @property
    def age(self):
        return 2024 - int(self.year)

def read_excel():
    wb = openpyxl.load_workbook('sandbox/kt_race.xlsx')
    ws = wb['sheet1']
    racers = {}
    count = 0
    zaezd_count = 0
    for i in range(1,300):
        racer = Racer(
            ws.cell(row=i, column=1).value,
            ws.cell(row=i, column=2).value,
            ws.cell(row=i, column=3).value,
            ws.cell(row=i, column=4).value,
            ws.cell(row=i, column=5).value,
            ws.cell(row=i, column=6).value,
            ws.cell(row=i, column=7).value,
            ws.cell(row=i, column=8).value,
            ws.cell(row=i, column=9).value,
            ws.cell(row=i, column=10).value
        )

        if racer.coach:
            count += 1
            if racer.discipline not in racers:
                racers[racer.discipline] = {}
            
            if racer.zaezd not in racers[racer.discipline]:
                racers[racer.discipline][racer.zaezd] = []
                zaezd_count += 1
            
            racers[racer.discipline][racer.zaezd].append(racer)
            print(racer.first_name)

    #напечатаем все имена из массива racers
    print(f'Считано {count} участников. Дисциплин {len(racers)}. Заездов {zaezd_count}')
    for item in racers:
        print(item)
        for zaezd in racers[item]:
            z_racers = racers[item][zaezd]
            print(f'-{zaezd}: {len(z_racers)}')
            for i in range(0, len(z_racers)):
                print(f'\t {i+1} {z_racers[i].number}  {z_racers[i].last_name} {z_racers[i].first_name} \t\t{z_racers[i].weight} \t{z_racers[i].age}')
    
    return racers            
#подключаемся и авторизуемся на сервере fastapi
    
if __name__ == '__main__':

    read_excel()