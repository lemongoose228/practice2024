# Проектно-технологическая практика 2024

### Выполнили: _Валеев Глеб, Конова Екатерина_
---

### Описание проекта:
Данный проект представляет собой эмулятор передачи данных со спутников. По запросу пользователя проект загружает архивные данные со спутника, после чего они распаковываются и начинается стриминг данныx по временным интервалам

### Функционал:
* Загрузка данных: Сервер каждый день в определённое время загружает и распаковывает файлы RINEX, в которых содержатся данные наблюдений станций.
* Обработка данных: Полученные данные обрабатываются и преобразуются в потоковый формат для дальнейшей публикации.
* Получение топиков: С помощью FAstAPI пользователь вводит в запрос интересующие его станции и ему будут выданы темы по этим станциям
* Публикация данных: Обработанные данные публикуются в брокер по топикам, соответствующим определённым станциям станциям 
* Подписка на данные: Пользователи могут подключаться к брокеру и подписаться на определённые топики, чтобы получать потоковую информацию с выбранных станций

### Установка проекта:
* Перейдите в папку `practice` и склонируйте репозиторий:  `https://github.com/lemongoose228/practice2024.git`
```sh
mkdir practice
cd practice
git clone https://github.com/lemongoose228/practice2024.git

```
* Установите pip и зависимости, которые находятся в файле `requirements.txt`
```sh
sudo apt install python3-pip
pip install -r ./txt/requirements.txt
```
* Необходимо выдать права на исполнение всем файлам, для этого вам нужно будет дать права на исполнение файлу `issueRights` и запустить его
```sh 
chmod +x issueRights
./issueRights
```
* Необходимо задать путь к текущей директории
```sh 
nano ./txt/mainpath.txt
Введите туда путь до текущей директории, например /home/user/practice
```
### Запуск проекта:
* sudo apt install uvicorn
* Запуск сервера FastAPI: `uvicorn main:app --reload --port 8002 --host 0.0.0.0`
* Если вы запускаете проект локально, то откройте браузер и перейдите по адресу `http://127.0.0.1:8002/docs`, если вы запускаете его с виртуальной машины Яндекса, то перейдите по адресу `http://IP_вашей_ВМ:8002/docs`

## Функции FastAPI

``GetDate (/sites)``
Показывает список всех станций и соответствующие им доступные файлы данных.
* Вводные данные: Нет.
* Данные вывода: JSON объект со списком станций.


``Get Date (/sites/start)``
Заускает сиситему
* Вводные данные: дата в формате 2024-01-05
* Данные вывода: сообщение "Система успешно запущена, подождите некоторое время".

``Create Topics (/topics)``
Выводит темы по заданными прёмникам
* Вводные данные: JSON объект со списком станций.
* Данные вывода: JSON объект со списком тем по заданным приёмникам(если такие приёмники существуют).


## Описание файлов

#### Bash скрипты:
`changeRNX`: меняет rnx1 на rnx2 в файле variables.txt 

`create_services`: создает и управляет сервисом, который запускает Python-скрипт publisher.py для обработки файлов .rnx. 
Он делает следующее:
1. Создает сервис: Если сервис не существует, он создает его, настраивает, запускает и включает в автозапуск.
2. Обновляет статус: Если сервис уже существует, он проверяет его активность и обновляет статус в файле pub_statuses.txt.
3. Запускает сервис: Если сервис не активен и время больше или равно 23:00, он запускает сервис.
В целом, этот скрипт автоматизирует процесс запуска и управления сервисом, который обрабатывает файлы .rnx.


`issueRights`: выдаёт права на исполнение нужным файлам


`rmDateData`: Этот скрипт удаляет папку с данными, соответствующую дате, указанной в файле variables.txt. Он считывает дату из файла, вычисляет предыдущий день и удаляет папку с данными за этот день.


`template`: Этот скрипт представляет собой файл конфигурации сервиса systemd, который описывает службу publisher. Этот файл конфигурации создает службу, которая запускает Python-скрипт publisher.py под пользователем user с определенными настройками. Служба будет автоматически перезапускаться при сбоях и будет доступна по умолчанию.


`newDay`: Этот скрипт обновляет дату в файле variables.txt, скачивает данные за новую дату, распаковывает архив, конвертирует файл .crx.gz в .rnx и перемещает его в соответствующую папку, а затем создаёт сервис для обработки файла .rnx.
В целом, скрипт автоматизирует процесс обновления даты, скачивания данных, распаковки архива, обработки файла .crx.gz и создания сервиса для обработки .rnx файла.


`starts`: Этот скрипт обрабатывает файлы.crx.gz из архива за указанную дату. Он:
1. Считывает путь: Получает путь к основному каталогу из файла mainpath.txt.
2. Записывает дату: Дописывает дату (переданную как аргумент) и rnx1 в файл variables.txt.
3. Cкачивание данных и распаковка архива.
4. Обрабатывает файлы: Обходит каждый файл .crx.gz в директории с архивом, распаковывает его, конвертирует в .rnx с помощью CRX2RNX, перемещает в папку rnx1 или rnx2 (в зависимости от настроек в variables.txt) и создает сервис для обработки файла .rnx.


#### Python скрипты:
`main.py`: Этот скрипт представляет собой API, которое предоставляет функции для скачивания данных, запуска системы и получения списка доступных станций.
Основные функции:
1. downloading(date, check): Возвращает True, если загрузка пройдет успешно, и False в противном случае.
2. /sites/list: Возвращает список доступных станций, которые хранятся в папке data. 
3. /sites/start: Запускает систему для указанной даты. 
  - Запускает скрипт starts с помощью subprocess. 
4. /sites/topics: Принимает список receivers и возвращает список доступных тем (топиков) для каждого из них. Проверяет наличие соответствующих файлов в папке data и возвращает информацию о них.


`downloader.py`: Этот скрипт скачивает файл с данными за указанную дату с API simurg.space. 
Он:
1. Получает дату: Считывает дату с аргумента командной строки.
2. Создает имя файла: Формирует имя файла в формате data/{год}/{месяц-день}.zip.
3. Скачивает файл:


`publisher.py`: Этот скрипт считывает данные из RINEX-файла, вычисляет TEC (Total Electron Content), публикует результаты в MQTT-брокер, и запускается как системная служба. 
Основные функции:
1. get_mainpath(): Считывает путь к основному каталогу из файла mainpath.txt.
2. get_rnx_number(): Считывает номер RINEX-файла из файла variables.txt.
3. get_status(receiver_name): Считывает статус обработки для заданного приемника из файла pub_statuses.txt.
4. broker_setup(): Создает подключение к MQTT-брокеру и возвращает объект клиента MQTT.
5. get_begin_work_time(): Вычисляет время начала работы, исходя из текущего времени.
6. publishing(fullpath): Считывает данные из RINEX-файла, вычисляет TEC, публикует результаты в MQTT-брокер.
7. Основная логика:
  - Считывает имя RINEX-файла из аргумента командной строки.
  - Проверяет статус обработки приемника.
  - Если статус "wait" и текущее время до 23:59:21, то скрипт ждет до 23:59:21.
  - В противном случае, запускает функцию publishing() для публикации данных в MQTT-брокер.
Скрипт выполняет следующие задачи:
- Считывает данные из RINEX-файла.
- Вычисляет TEC (Total Electron Content).
- Публикует результаты в MQTT-брокер.
- Запускается как системная служба, автоматически запускается и работает в фоновом режиме. 


#### txt файлы:
`variables.txt`: в этом файле хранятся переменные такие как дата и папка из которой стримятся данные rnx1 и rnx2
`pub_statuses.txt`: хранятся статусы каждого паблишера(демона)


## License

MIT
