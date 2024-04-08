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
        #проверит является ли res строкой
        if isinstance(res, str):
            res = res.split(',')[0].split('.')[0]
        return int(res)
    
    @property
    def age(self):
        return 2024 - int(self.year)
    
    def check(self):
        check_fileds = ['number', 'fio', 'year', 'discipline', 'weight1']   
        #проверить, что все поля класса заполнены
        for key in check_fileds:
            if getattr(self, key) is None:
                raise Exception(f'Не заполнено поле {key}')
        return True
        

def read_excel(filename, page_name = 'sheet1', rows = (1,300), reset_zaezd = False):
    wb = openpyxl.load_workbook(filename)
    ws = wb[page_name]
    racers = {}
    count = 0
    zaezd_count = 0
    for i in range(rows[0],rows[1]):
        racer = Racer(
            ws.cell(row=i, column=1).value, #номер
            ws.cell(row=i, column=2).value, #имя
            ws.cell(row=i, column=3).value, #год
            ws.cell(row=i, column=4).value, #дисциплина
            ws.cell(row=i, column=5).value, #класс
            ws.cell(row=i, column=6).value, #тренер
            ws.cell(row=i, column=7).value, #организация
            ws.cell(row=i, column=8).value, #вес
            ws.cell(row=i, column=9).value, #вес 2
            ws.cell(row=i, column=10).value #заезд
        )

        if racer.fio:
            count += 1
            if racer.discipline not in racers:
                racers[racer.discipline] = {}
            
            if reset_zaezd:
                racer.zaezd = None
                
            if racer.zaezd not in racers[racer.discipline]:
                racers[racer.discipline][racer.zaezd] = []
                zaezd_count += 1
            
            racers[racer.discipline][racer.zaezd].append(racer)
            
            try:
                racer.check()
            except Exception as e:
                raise Exception(f'Ошибка в записи участника строка: {i} -  {e}')
            
            print(racer.first_name)

    #напечатаем все имена из массива racers
    print(f'Считано {count} участников. Дисциплин {len(racers)}. Заездов {zaezd_count}')
    print('Дисциплины:')
    total = 0
    for item in racers.keys():
        cnt = 0
        for zaezd in racers[item].values():
            cnt = cnt + len(zaezd)
        print(f'{item} участников {cnt}')
        total += cnt
    print(f'== Всего участников {total}')
    
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
    
    read_excel('sandbox/002_volochek.xlsx', 'Лист1', (8,200))