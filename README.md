# discord_bot

Discord бот для автоматизированного администрирования Discord сервера онлайн игры. Был разработан строго для использования на одном сервере, не является универсальным!

## Используемые технологии<a id="technologies-project"></a>:

![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg?style=flat&logo=python&logoColor=white)
![Pycord-2.6.0](https://img.shields.io/badge/Pycord-2.6.0-brightgreen.svg?style=flat)

## Для чего создан бот:

1. Принятие и обработка запросов на выдачу роли на сервере.
   - Для новых пользователей доступна кнпока для подачи заявки. При нажатии на кнпоку пользователь видит форму для ввода игрового никнейма.
   - Далее работает парсер. Выполняется POST запрос на [API ресурс](https://api.allodswiki.ru/api/v1/armory/avatars) с данными о никнейме игрока.
   - После этого собирается информация об игроке путем GET запроса с получением ифнормации в формате json.
   - В конечном итоге администратор получает сообщение в канале со встроенным embed и информацией об игроке в данном embed, а также 2 кнопки с разрешением выдачи роли или отказе.

2. Проведение автоматического аукциона внутриигровых ценностей.
   - Команда /go_auc позволяет запустить аукцион после ввода параметров в появившейся форме.
   - Аукцион автоматически принимает и обрабатывает ставки.
   - Аукцион автоматически завершает работу в установленную дату и время.

3. Сбор заявок на внутриигровую активность (РЧД).
   - Функция позволяет для всех пользователей пользоваться кнопкой для сбора заявок.
   - Для администратора в закрытом канале появляется полный функционал по обработке заявок и созданию списка игроков для активности.
   - После созадния списка есть функция оповещения пользователей. Бот отправляет сообщения в ЛС с информацией об активности.

4. Рандомайзер.
   - Простая функция, помогающая выявить победителя из списка, или путём выбранного диапазона чисел использовав встроенный модуль random.

## Как развернуть проект

1. Вам необходимо создать самого бота и получить TOKEN на [ПОРТАЛЕ](https://discord.com/developers/applications/) разработчике Discord ботов
2. Клонировать репозиторий, создать виртуальное окружение, установить зависимости:
```
git clone git@github.com:MihailKirzhakov/discord_bot.git
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
3. Заполнить файл .env
```
TOKEN = ВАШ ТОКЕН
DEBUG_SERVER_ID = ID сервера на котором будет работать бот
APPLICATION_CHANNEL_ID = ID канала для приёма заявок
RCD_APPLICATION_CHANNEL_ID = ID канала для приёма заявок на активность РЧД
```
4. Настроить файл variables.py, тк некоторые параметры относятся напрямую к серверу, в котором будет работать бот, в основном ID.
5. Запустить бота можно с помощью запуска исполняемого файла bot_run.py.
