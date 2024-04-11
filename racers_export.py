import os
import openpyxl
import requests

class Racer:
    def __init__(self, number, name, year,discipline, class_, coach, organization, weight, zaezd):
        self.number = number
        self.fio = name
        self.discipline = discipline
        self.year = year
        self.class_ = class_
        self.coach = coach
        self.organization = organization
        self.weight1 = weight
        self.zaezd_number = zaezd
        self.track_number = 0
    
    @property
    def zaezd(self):
        if isinstance(self.zaezd_number, str):
            return self.zaezd_number
        
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
        
class Discipline:

    def __init__(self, name):
        self.name = name
        self.races = {}
        self.racers = []

    def add_racer(self, racer):
        self.racers.append(racer)
        if racer.zaezd not in self.races:
            self.races[racer.zaezd] = []
        
        self.races[racer.zaezd].append(racer)

    def race_names(self):
        return self.races.keys()
    
    def get_race(self, name):
        if name in self.races:
            return self.races[name]
        return []
    
    def values(self):
        return self.races.values()
    
    def arrange_races(self, prefix, start_num, tracks_count = 9):
        rc_qty = len(self.racers)
        zaezd_count = int(rc_qty / tracks_count)
        if zaezd_count * tracks_count < rc_qty:
            zaezd_count += 1
        
        on_track = int(rc_qty / zaezd_count)
        reminder = rc_qty - on_track * zaezd_count 

        self.races = {}
        cur_racer_idx = 0
        for z in range(0, zaezd_count):
            zaezd_name = f'{prefix} {start_num+z}' 
            self.races[zaezd_name] = []
            zaezd_racer_list = self.races[zaezd_name]
            track_num = 1
            for r in range(0, on_track):
                zaezd_racer_list.append(self.racers[cur_racer_idx])
                self.racers[cur_racer_idx].zaezd_number = zaezd_name
                self.racers[cur_racer_idx].track_number = track_num
                cur_racer_idx += 1
                track_num += 1
            if reminder:
                zaezd_racer_list.append(self.racers[cur_racer_idx])
                self.racers[cur_racer_idx].zaezd_number = zaezd_name
                self.racers[cur_racer_idx].track_number = track_num
                cur_racer_idx += 1
                track_num += 1
                reminder -= 1
        
        return zaezd_count
    
    def print(self):
        pass


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
            ws.cell(row=i, column=9).value #заезд
        )

        if racer.number:
            count += 1
            if racer.discipline not in racers:
                racers[racer.discipline] = Discipline(racer.discipline)
            
            if reset_zaezd:
                racer.zaezd_number = None
                
            racers[racer.discipline].add_racer(racer) 

            try:
                racer.check()
            except Exception as e:
                raise Exception(f'Ошибка в записи участника строка: {i} -  {e}')
            
            print(racer.first_name)
    
    zaezd_count = 0
    if reset_zaezd:
        for discipline in racers.values():
            zaezd_count += discipline.arrange_races('Заезд', zaezd_count+1, 9) 

    #напечатаем все имена из массива racers
    print(f'Считано {count} участников. Дисциплин {len(racers)}. Заездов {zaezd_count}')
    print('Дисциплины:')
    total = 0
    for item in racers.keys():
        cnt = len(racers[item].racers)
        print(f'{item} участников {cnt}')
        total += cnt
    print(f'== Всего участников {total}')
    
    for item in racers:
        print(item)
        for zaezd in racers[item].race_names():
            z_racers = racers[item].get_race(zaezd)
            print(f'-{zaezd}: {len(z_racers)}')
            for i in range(0, len(z_racers)):
                print(f'\t {z_racers[i].track_number} {z_racers[i].number}  {z_racers[i].last_name} {z_racers[i].first_name} \t\t{z_racers[i].weight} \t{z_racers[i].age}')
    
    return racers            
#подключаемся и авторизуемся на сервере fastapi

# Выгружаем в Excel результат работы функции read_excel
def write_excel(filename, racers):
    from openpyxl.styles.alignment import Alignment
    from openpyxl.styles.fonts import Font

    #удалть filename если он уже существует
    if os.path.isfile(filename):
        os.remove(filename)

    wb = openpyxl.Workbook()
    ws = wb.active

    

    #объединяем три колонки и печтатаем заголовок "Заезды" крупным шрифтом
    ws.merge_cells('A1:C1')
    ws['A1'] = 'Заезды'
    ws['A1'].font = Font(size=16, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    
    #выравниваем по центру

    
    #ws.append(['Номер', 'ФИО', 'Год рождения', 'Дисциплина', 'вес, кг', 'Тренер', 'Организвция', 'Заезд'])
    #обвечсти ячейки чёрным цветом
    for row in ws.iter_rows():
        for cell in row:
            #обести рамкой, а не залить
            cell.border = openpyxl.styles.Border(
                left=openpyxl.styles.Side(border_style='thin', color='00000000'),
                right=openpyxl.styles.Side(border_style='thin', color='00000000'),
                top=openpyxl.styles.Side(border_style='thin', color='00000000'),
                bottom=openpyxl.styles.Side(border_style='thin', color='00000000')
                #fill=openpyxl.styles.PatternFill(start_color='00000000', end_color='00000000', fill_type='solid')
                #font=openpyxl.styles.Font(color='00000000')
                #alignment=openpyxl.styles.Alignment(horizontal='center', vertical='center')
                #number_format='@'
            )
    
    discp = [
"мужчины 35 лет и старше",
"юноши до 15 лет",
"девушки до 15 лет",
"юноши до 17 лет",
"девушки до 17 лет",
"юниоры до 19 лет",
"мальчики до 13 лет",
"девочки до 13 лет"]
    minutes = 0
    hours = 13
    
    #Задать ширину колонок
    
    for item in racers:
        for zaezd in racers[item].race_names():
            z_racers = racers[item].get_race(zaezd)
            start_time = f'{hours:02d}:{minutes % 60:02d}' 
            minutes += 5
            hours = hours + minutes // 60

            ws.append(['', ''])
            ws.append(['', zaezd, start_time]) 
            #Сделать жирным
            ws[f'B{ws.max_row}'].font = Font(bold=True)
            ws.append(['', item])
            ws[f'B{ws.max_row}'].font = Font(bold=True)            
            ws.append(['Дорожка', 'ФИО', 'Год рождения', 'вес, кг'])
            last_row = ws.max_row
            for i in range(0, len(z_racers)):
                ws.append([z_racers[i].track_number, z_racers[i].fio, z_racers[i].year, z_racers[i].weight])
            #Обвести всё что ниже рамкой
            for row in ws.iter_rows(min_row=last_row, max_row=ws.max_row):
                for cell in row:
                    cell.border = openpyxl.styles.Border(
                        left=openpyxl.styles.Side(border_style='thin', color='00000000'),
                        right=openpyxl.styles.Side(border_style='thin', color='00000000'),
                        top=openpyxl.styles.Side(border_style='thin', color='00000000'),
                        bottom=openpyxl.styles.Side(border_style='thin', color='00000000')
                        #fill=openpyxl.styles.PatternFill(start_color='00000000', end_color='00000000', fill_type='solid')
                        #font=openpyxl.styles.Font(color='00000000')
                        #alignment=openpyxl.styles.Alignment(horizontal='center', vertical='center')
                        #number_format='@'
                    )
    wb.save(filename)
    
if __name__ == '__main__':
    
    racers = read_excel('sandbox/002_volochek_4.xlsx', 'Лист1', (3,400), False)
    write_excel('sandbox/002_volochek_out.xlsx', racers)