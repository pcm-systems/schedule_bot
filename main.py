import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import csv
import time

#                   Бот запускается с помощью watchdog supervisor
#                   Команда для запуска:
#                   supervisord -c supervisor.conf &
#                   Конфигурация watchdog в файле supervisor.conf

# инициализация бота
bot = telebot.TeleBot(token='111222333:AAAABBBCCC', threaded=False)
group_chat_id = '-111222333444'
owner_chat_id = '111222333'
message_thread_id = 777 # Если чат не поделен на ветки - треды, то необходимо поставить значение "None"

# ссылки для кнопок
url_1 = 'https://google.com/'
url_2 = 'https://google.com/'
url_3 = 'https://google.com/'

# команды

# /start
@bot.message_handler(commands=['start'])
def start_bot(msg):

    """Данная функция запускает ежедневный опрос если он был остановлен командой /pause,
     если id чата = owner_chat_id. В противном случае выводятся ссылки на исходники бота"""

    if str(msg.chat.id) == owner_chat_id:
        scheduler.resume_job(job_id='polling')
    else:
        message_line = ('Информация о боте и исходники лежат на github по ссылке https://github.com/pcm-systems/schedule_bot\n\n'
                        'Для связи с создателями https://t.me/pcm_systems')
        bot.send_message(msg.chat.id, message_line)


# /pause
@bot.message_handler(commands=['pause'])
def pause_bot(msg):

    """Данная функция приостанавливает ежедневный опрос до тех пор, пока его не перезапустят командой /start"""

    if str(msg.chat.id) == owner_chat_id:
        scheduler.pause_job(job_id='polling')


# /tst
@bot.message_handler(commands=['tst'])
def test_bot(msg=None):

    """Данная функция отвечает на команду смайликом робота для проверки работоспособности
    и отправляет сообщение с id чата и его веткой откуда была отправлена команда на владельца бота
    Функция создана для отладки и тестировния"""

    # для определения id нового чата и его треда
    # if msg is None or str(msg.chat.id) == group_chat_id:
    bot.send_message(owner_chat_id, f"🤖")

    # это условие создано для отладки и тестирования планировщика и исключения ошибки id чата
    if msg is not None:
        bot.send_message(owner_chat_id, f"ID чата {msg.chat.id}\nID ветки {msg.message_thread_id}")


# /ping
@bot.message_handler(commands=['ping'])
def ping_bot(msg):

    """Данная функция добавляет расписание с отправкой сообщения раз в минуту до остановки командой /stop_ping"""

    def evil_ping(line_for_send):

        """Функция непосредственной отправки и удаления сообщений"""

        # забираем id сообщения для дальнейшего удаления и отправляем сообщение с текстом
        msg_id = bot.send_message(group_chat_id, text=line_for_send, message_thread_id=message_thread_id).message_id

        time.sleep(10)
        bot.delete_message(group_chat_id, msg_id)

    if str(msg.chat.id) == owner_chat_id:
        # забираем текст после команды /ping
        message_line_list = msg.text.split()
        if len(message_line_list) > 1:
            message_line = ' '.join(message_line_list[1:])
        else:
            message_line = '🤖'

        # запускаем планировщика с аргументом-функцией отправки сообщения
        scheduler.add_job(lambda: evil_ping(message_line),
                          id='ping',
                          trigger='interval',
                          seconds=15)


# /stop_ping
@bot.message_handler(commands=['stop_ping'])
def stop_ping_bot(msg):

    """Данная функция удаляет расписание с отправкой сообщения раз в минуту по команде /ping"""

    if str(msg.chat.id) == owner_chat_id:
        scheduler.remove_job(job_id='ping')


# /help
@bot.message_handler(commands=['help'])
def help_bot(msg):

    """Данная функция отправляет все команды бота в одном сообщение"""

    if str(msg.chat.id) == owner_chat_id:
        message_line = ('Управление:\n'
                        '/start - запустить ежедневный опрос\n'
                        '/pause - остановить ежедневный опрос. Например на праздники.\n'
                        '/pool - отправить ежедневный опрос в чат принудительно\n'
                        '/check_vacation - проверить отпуска, и если они есть в ближайшую неделю, то написать в чат\n'
                        '/check_birthday - проверить дни рождения, и если они есть в ближайшую неделю, то написать в чат\n'
                        '/ping - запуск циклической отправки сообщений. прим. тегирования "/ping @robot @ebobot"\n'
                        '/stop_ping - остановка циклической отправки сообщений\n'
                        '\n'
                        'Информация:\n'
                        '/birthday_list - получить информацию о днях рождения сотрудников\n'
                        '/vacation_list - получить информацию об отпусках сотрудников\n'
                        '/tst - вывести id чата в котором получена команда\n'
                        '/help - получить данное сообщение ещё раз'
                        )
        bot.send_message(owner_chat_id, message_line)


# /birthday
@bot.message_handler(commands=['birthday_list'])
def birthday_list_bot(msg):

    """Данная функция проверят и отправляет сообщение с днями рождения коллектива владельцу бота"""

    if str(msg.chat.id) == owner_chat_id:
        # запуск функции проверки дней рождений
        message_line = str()
        with open('team.csv', encoding='utf-8') as team_file:
            rows = csv.DictReader(team_file, delimiter=';', quotechar='"')
            for row in rows:
                message_line += f"{row['name']} - {row['birthday']}\n"
        # отправка сообщения
        bot.send_message(owner_chat_id, message_line)


# /vacation
@bot.message_handler(commands=['vacation_list'])
def vacation_list_bot(msg):

    """Данная функция проверят отпуска и отправляет сообщение с отпусками коллектива владельцу бота"""

    if str(msg.chat.id) == owner_chat_id:
        # запуск функции проверки дней рождений
        message_line = str()
        with open('team.csv', encoding='utf-8') as team_file:
            rows = csv.DictReader(team_file, delimiter=';', quotechar='"')
            for row in rows:
                message_line += f"{row['name']}:\n"
                for vac in row['vacation'].split(', '):
                    message_line += f'{vac}\n'
                message_line += f'\n'

        # отправка сообщения
        bot.send_message(owner_chat_id, message_line)


# /pool
@bot.message_handler(commands=['pool'])
def poll_bot(msg=None):

    """Данная функция отправляет опрос в чат
    под опросом добавляет три функциональные кнопки для перехода по ссылкам"""

    # значение msg = None по умолчанию добавлено для случая, когда эту функцию запустит расписание - scheduler
    if msg is None or str(msg.chat.id) == owner_chat_id:
        # запуск функции опроса
        # добавление кнопок
        # ссылки на кнопки вначале документа
        btn1 = telebot.types.InlineKeyboardButton('Почта✉️', url=url_1)
        btn2 = telebot.types.InlineKeyboardButton('bbb2🎥', url=url_2)
        btn3 = telebot.types.InlineKeyboardButton('В чат🚀', url=url_3)
        markup = telebot.types.InlineKeyboardMarkup()
        # прикрепляем кнопки к сообщению
        markup.row(btn1, btn2, btn3)
        question = f"Где ты планируешь работать {'завтра' if datetime.now().strftime('%w') != str(5) else 'в понедельник'}?"
        options = ["Удаленка🏠",
                   "Офис✏️",
                   "Заказчик👨🏻‍🦳",
                   "Болею/Отпуск/Пары👀",
                   "Напишу свой вариант в чат✏️"]
        # отправка сообщения - опроса
        bot.send_poll(group_chat_id, question, options,
                      is_anonymous=False, message_thread_id=message_thread_id,
                      protect_content=True, reply_markup=markup)


# /check_birthday
@bot.message_handler(commands=['check_birthday'])
def check_birthday_bot(msg=None, num_of_days=7):
    """Данная функция проверяет в конце каждой недели (воскресенье)
    есть ли на следующей неделе дни рождения.
    Функция принимает аргумент сдвига в количествах дней. По умолчанию 7 - неделя.
    Информацию получает из файла team.csv
    Разделителем в файле служит точка с запятой ';'
    Добавляет информацию в словарь, затем отправляет сообщение, если словарь не пустой"""

    # значение msg = None по умолчанию добавлено для случая, когда эту функцию запустит расписание - scheduler
    if msg is None or str(msg.chat.id) == owner_chat_id:
        # формирование списка дней на неделю
        day_roll = [(datetime.now() + timedelta(days=d)).strftime('%d.%m') for d in range(num_of_days - 6, num_of_days + 1)]
        birthday_dct = dict()
        # открытие файла
        with open('team.csv', encoding='utf-8') as team_file:
            rows = csv.DictReader(team_file, delimiter=';', quotechar='"')
            for row in rows:
                # имя в строке
                name = row['name']
                # дата дня рождения в строке
                birthday = datetime.strptime(row['birthday'], '%d.%m').strftime('%d.%m')
                # Если дата дня рождения входит в список дат на неделе, то добавляем в словарь
                if birthday in day_roll:
                    birthday_dct[name] = birthday

        # Если опрос НЕ со значением по умолчанию
        if num_of_days != 7:
            # проверяем есть ли в словаре данные
            if len(birthday_dct.keys()) > 0:
                # проверяем сколько людей уходит в отпуск, что бы правильно прописать склонение
                if len(birthday_dct.keys()) > 1:
                    line_birthday = f'🥳🥳🥳\nЧерез неделю день рождения будут праздновать:\n'
                    for n, b in birthday_dct.items():
                        line_birthday += f'{n} - {b}\n'
                else:
                    line_birthday = f'🥳🥳🥳\nЧерез неделю день рождения будет праздновать:\n'
                    for n, b in birthday_dct.items():
                        line_birthday += f'{n} - {b}\n'

                # отправляем сформированное сообщение
                bot.send_message(group_chat_id, f"{line_birthday}", message_thread_id=message_thread_id)
        else:
            # проверяем есть ли в словаре данные
            if len(birthday_dct.keys()) > 0:
                # проверяем сколько людей уходит в отпуск, что бы правильно прописать склонение
                if len(birthday_dct.keys()) > 1:
                    line_birthday = '🥳🥳🥳\nНа следующей неделе день рождения празднуют:\n'
                    for n, b in birthday_dct.items():
                        line_birthday += f'{n} - {b}\n'
                else:
                    line_birthday = '🥳🥳🥳\nНа следующей неделе день рождения празднует:\n'
                    for n, b in birthday_dct.items():
                        line_birthday += f'{n} - {b}\n'

                # отправляем сформированное сообщение
                bot.send_message(group_chat_id, f"{line_birthday}", message_thread_id=message_thread_id)

# /check_vacation
@bot.message_handler(commands=['check_vacation'])
def check_vacation_bot(msg=None, num_of_days=7):
    """Данная функция проверяет в конце каждой недели (воскресенье)
    уходи ли кто-то в отпуск на следующей неделе.
    Функция принимает аргумент сдвига в количествах дней. По умолчанию 7 - неделя.
    Информацию получает из файла team.csv
    Разделителем в файле служит точка с запятой ';'
    Добавляет информацию в словарь, затем отправляет сообщение, если словарь не пустой"""

    # значение msg = None по умолчанию добавлено для случая, когда эту функцию запустит расписание - scheduler
    if msg is None or str(msg.chat.id) == owner_chat_id:
        # формирование списка дней на неделю
        day_roll = [(datetime.now() + timedelta(days=d)).strftime('%d.%m.%Y') for d in range(num_of_days - 6, num_of_days + 1)]
        vacation_dct = dict()
        # открытие файла
        with open('team.csv', encoding='utf-8') as team_file:
            rows = csv.DictReader(team_file, delimiter=';', quotechar='"')
            for row in rows:
                # имя в строке
                name = row['name']

                # перебираем каждый период отпуска
                for vacation_period in row['vacation'].split(', '):
                    # начало отпуска
                    vacation_start = vacation_period.split('-')[0]

                    # Если дата начала отпуска входит в список дат на неделе, то добавляем в словарь
                    if vacation_start in day_roll:
                        vacation_dct[name] = vacation_period

        # Если опрос НЕ со значением по умолчанию
        if num_of_days != 7:
            # проверяем есть ли в словаре данные
            if len(vacation_dct.keys()) > 0:
                if len(vacation_dct.keys()) > 1:
                    line_vacation = f'🍻💤☀️\nЧерез неделю в отпуск уходят:\n'
                    for n, v in vacation_dct.items():
                        line_vacation += f'{n} - {v}\n'
                else:
                    line_vacation = f'🍻💤☀️\nЧерез неделю в отпуск уходит:\n'
                    for n, v in vacation_dct.items():
                        line_vacation += f'{n} - {v}\n'

                # отправляем сформированное сообщение
                bot.send_message(group_chat_id, f"{line_vacation}", message_thread_id=message_thread_id)

        # Если опрос со значением по умолчанию
        else:
            # проверяем есть ли в словаре данные
            if len(vacation_dct.keys()) > 0:
                if len(vacation_dct.keys()) > 1:
                    line_vacation = '🍻💤☀️\nНа следующей неделе в отпуск уходят:\n'
                    for n, v in vacation_dct.items():
                        line_vacation += f'{n} - {v}\n'
                else:
                    line_vacation = '🍻💤☀️\nНа следующей неделе в отпуск уходит\n'
                    for n, v in vacation_dct.items():
                        line_vacation += f'{n} - {v}\n'
                # отправляем сформированное сообщение
                bot.send_message(group_chat_id, f"{line_vacation}", message_thread_id=message_thread_id)


# создание планировщика
scheduler = BackgroundScheduler(timezone="Europe/Moscow")

# отправки опроса
scheduler.add_job(poll_bot, id='polling',
                  trigger='cron',
                  day_of_week='mon-fri',
                  hour=18,
                  minute=30)

# расписание проверки отпусков через две недели
scheduler.add_job(lambda: check_vacation_bot(num_of_days=14),
                  trigger='cron',
                  day_of_week='sun',
                  hour=12,
                  minute=5)

# расписание проверки отпусков на следующей неделе
scheduler.add_job(check_vacation_bot,
                  trigger='cron',
                  day_of_week='sun',
                  hour=12,
                  minute=00)

# расписание проверки дней рождения через две недели
scheduler.add_job(lambda: check_birthday_bot(num_of_days=14),
                  trigger='cron',
                  day_of_week='sun',
                  hour=12,
                  minute=5)

# расписание проверки дней рождения на следующей неделе
scheduler.add_job(check_birthday_bot,
                  trigger='cron',
                  day_of_week='sun',
                  hour=12,
                  minute=00)


# запуск планировщика
scheduler.start()

# запуск бота
bot.infinity_polling(timeout=6000)

