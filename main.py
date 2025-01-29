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

    # для определения id нового чата и треда
    if msg is None or str(msg.chat.id) == group_chat_id:
        bot.send_message(owner_chat_id, f"🤖")
        # это условие создано для отладки и тестирования планировщика и исключения ошибки id чата
        if msg is not None:
            bot.send_message(owner_chat_id, f"ID чата {msg.chat.id}\n ID ветки {msg.message_thread_id}")


# /ping
@bot.message_handler(commands=['ping'])
def ping_bot(msg):

    """Данная функция добавляет расписание с отправкой сообщения раз в минуту до остановки командой /stop_ping"""

    def evil_ping(line_for_send):

        """Функция непосредственной отправки и удаления сообщений"""

        # забираем id сообщения для дальнейшего удаления и отправляем сообщение с текстом
        msg_id = bot.send_message(group_chat_id, text=line_for_send, message_thread_id=message_thread_id).message_id

        # print(line_for_send)
        time.sleep(10)
        bot.delete_message(group_chat_id, msg_id)

    if str(msg.chat.id) == owner_chat_id:

        # забираем текст после команды /fire
        message_line = ' '.join(msg.text.split()[1:])

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
        message_line = ('/start - запустить ежедневный опрос\n'
                        '/pause - остановить ежедневный опрос\n'
                        '/birthday - получить информацию о днях рождения сотрудников\n'
                        '/vacation - получить информацию об отпусках сотрудников\n'
                        '/pool - отправить ежедневный опрос в чат принудительно\n'
                        '/check - проверить дни рождения и отпуска, и если они есть в ближайшую неделю, то написать в чат\n'
                        '/tst - вывести id чата в котором получена команда\n'
                        '/ping - запуск циклической отправки сообщений. прим. тегирования "/ping @robot @ebobot"\n'
                        '/stop_ping - остановка циклической отправки сообщений\n'
                        '/help - получить данное сообщение ещё раз'
                        )
        bot.send_message(owner_chat_id, message_line)


# /birthday
@bot.message_handler(commands=['birthday'])
def birthday_bot(msg):

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
@bot.message_handler(commands=['vacation'])
def vacation_bot(msg):

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
                   "Офис🖥️",
                   "Заказчик👨🏻‍🦳",
                   "Болею/Отпуск/Пары👀",
                   "Напишу свой вариант в чат✏️"]
        # отправка сообщения - опроса
        bot.send_poll(group_chat_id, question, options,
                      is_anonymous=False, message_thread_id=message_thread_id,
                      protect_content=True, reply_markup=markup)


# /check
@bot.message_handler(commands=['check'])
def check_bot(msg=None):

    """Данная функция проверяет в конце каждой недели (воскресенье)
       уходит ли кто-то в отпуск со следующей недели
       и есть ли на следующей неделе дни рождения.
       Информацию получает из файла team.csv
       Разделителем в файле служит точка с запятой ';'
       Добавляет информацию в два словаря: словарь дней рождений и словарь отпусков
       Затем отправляет сообщение, если хотя бы один из словарей не пустой"""

    # значение msg = None по умолчанию добавлено для случая, когда эту функцию запустит расписание - scheduler
    if msg is None or str(msg.chat.id) == owner_chat_id:
        # запуск функции проверки дней рождений и отпусков
        day_roll = [(datetime.now() + timedelta(days=d)).strftime('%d.%m.%y') for d in range(1, 8)]
        birthday_dct = dict()
        vacation_dct = dict()
        with open('team.csv', encoding='utf-8') as team_file:
            rows = csv.DictReader(team_file, delimiter=';', quotechar='"')
            for row in rows:
                name = row['name']
                b_d = datetime.strptime(row['birthday'], '%d.%m').strftime('%d.%m')
                if b_d in [d[:5] for d in day_roll]:
                    birthday_dct[name] = b_d
                # Перебор отпусков (начало-конец)
                for vac in row['vacation'].split(', '):
                    # Инициализация начало-конец каждого отпуска
                    vac_from_to = [
                        datetime.strptime(v, '%d.%m.%Y').strftime('%d.%m.%y')
                        for v in vac.split('-')
                    ]
                    if vac_from_to[0] in day_roll:
                        vacation_dct.setdefault(name, [])
                        vacation_dct[name].append(vac)

        line_bd, line_vac, full_line = str(), str(), str()
        if len(birthday_dct.keys()) > 0:
            if len(birthday_dct.keys()) > 1:
                line_bd = ('🥳🥳🥳На следующей неделе день рождения празднуют:\n' +
                           '\n'.join([f"{name} - {date}" for name, date in birthday_dct.items()]))
            else:
                line_bd = ('🥳🥳🥳На следующей неделе день рождения празднует ' +
                           '\n'.join([f"{name} - {date}" for name, date in birthday_dct.items()]))
        if len(vacation_dct.keys()) > 0:
            if len(vacation_dct.keys()) > 1:
                line_vac = ('🍻💤☀️На следующей неделе в отпуск уходят:\n' +
                            '\n'.join([f"{name} - {', '.join(dates)}" for name, dates in vacation_dct.items()]))
            else:
                line_vac = ('🍻💤☀️На следующей неделе в отпуск уходит\n' +
                            '\n'.join([f"{name} - {', '.join(dates)}" for name, dates in vacation_dct.items()]))
        if len(line_bd) > 0:
            if len(line_vac) > 0:
                line_bd += '\n'
                line_bd += f"🍻💤☀️В{line_vac[25:]}"
            bot.send_message(group_chat_id, f"Привет!\n{line_bd}", message_thread_id=message_thread_id)
        else:
            if len(line_vac) > 0:
                bot.send_message(group_chat_id, f"Привет!\n{line_vac}", message_thread_id=message_thread_id)


# создание планировщика
scheduler = BackgroundScheduler(timezone="Europe/Moscow")

# отправки опроса
scheduler.add_job(poll_bot,
                  trigger='cron',
                  day_of_week='mon-fri',
                  hour=18,
                  minute=30)

# проверки отпусков и дней рождений
scheduler.add_job(check_bot, id='polling',
                  trigger='cron',
                  day_of_week='sun',
                  hour=12,
                  minute=00)

# запуск планировщика
scheduler.start()

# запуск бота
bot.infinity_polling(timeout=6000)
