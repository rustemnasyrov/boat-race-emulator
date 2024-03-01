Эмуляция работы тренажёров во время соревнования

[Файле regatta.py](regatta.py)

Тут содержится описание структуры пакета
    
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


[Файл main_ui.py](main_ui.py)

Основной файл эмулятора

- Отправляет пакеты TCP/IP по умолчанию на порт localhost:5555
- Отвечает json на POST-запрос по адресу localhost:8000 
- Запуск python main_ui.py

[Файл recieve_test_ui.py](recieve_test_ui.py)

Тестовый клиент получающий данные по TCP/IP порт localhost:5555

[Как подключить к мобильному хотспоту больше 8 устройств]

First press Win+R key on your keyboard, then type ''regedit'' and press enter. It will open windows registry editor.
Copy line below and paste it in the textbox then press enter:
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\icssvc\Settings

Right click on an empty space in the right side and choose New/ DWORD (32bit) Value
Name the value ''WifiMaxPeers''
Double click on it and choose decimal, then put the value whatever you want to.
At last press ok and restart your pc.
Well done!