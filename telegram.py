import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import csv

#                   Бот запускается с помощью watchdog supervisor
#                   Команда для запуска:
#                   supervisord -c supervisor.conf &
#                   Конфигурация watchdog в файле supervisor.conf

# Установка локализации
# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

# Инициализация бота
bot = telebot.TeleBot(token='Ваш:Токен', threaded=False)

# ID чатов
group_chat_id = 'Идентификатор группы куда бот будет слать сообщения'
owner_chat_id = 'Идентификатор владельца бота для управления ботом'
message_thread_id = 999 # Номер ветки в вашем чате, если он разделен по темам


# @bot.message_handler(commands=['start'])
# def start_bot(msg):
#     if str(msg.chat.id) == owner_chat_id:
#         # Отправить сообщение с id чатом на владельца бота
#         bot.send_message(owner_chat_id, f"{msg.chat.id}")


@bot.message_handler()
def message_keeper(msg):
    """Данная функция перехватывает сообщения отправленные боту и позволяет игнорировать их"""

    # Принимаем сообщения только от владельца бота
    if str(msg.chat.id) == owner_chat_id:
        if msg.text == '/pool':
            poll_sender()
        elif msg.text == '/check':
            birthday_and_vacation_ckr()
        elif msg.text == '/tst':
            bot.send_message(owner_chat_id, f"🤖")
        else:
            pass
    else:
        pass
        # Раскомментировать если хотите проверять кто пишет боту
        # bot.send_message(msg.chat.id, f"🤖")
        # bot.send_message(owner_chat_id, f"Мне писал {msg.chat.username}. ID {msg.chat.id}.")


@bot.message_handler()
def birthday_and_vacation_ckr() -> None:
    """Данная функция проверяет в конце каждой недели (воскресенье)
    уходит ли кто-то в отпуск со следующей недели
    и есть ли на следующей неделе дни рождения.
    Информацию получает из файла team.csv
    Разделитель - ";"
    Добавляет информацию в два словаря: словарь дней рождений и словарь отпусков
    Затем отправляет сообщение, если хотя бы один из словарей не пустой"""

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


@bot.message_handler()
def poll_sender() -> None:
    """Данная функция отправляет опрос в чат
    под опросом добавляет две функциональные кнопки для перехода по ссылкам"""
    btn1 = telebot.types.InlineKeyboardButton('Почта✉️',
                                              url='ссылка для перехода в почту')
    btn2 = telebot.types.InlineKeyboardButton('bbb2🎥',
                                              url='ссылка для перехода на корпоративный сайт')
    btn3 = telebot.types.InlineKeyboardButton('В чат🚀',
                                              url='ссылка для перехода в чат ТГ')
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(btn1, btn2, btn3)
    question = f"Где ты планируешь работать {'завтра' if datetime.now().strftime('%w') != str(5) else 'в понедельник'}?"
    options = ["Удаленка🏠",
               "Рабочее место💻",
               "Внешняя встреча🤝",
               "Болею/Отпуск/Пары👀",
               "Напишу свой вариант в чат✏️"]

    bot.send_poll(group_chat_id, question, options, is_anonymous=False, message_thread_id=message_thread_id, protect_content=True, reply_markup=markup)


# Создание планировщика
scheduler = BackgroundScheduler(timezone="Europe/Moscow")
# Отправки опроса
scheduler.add_job(poll_sender,
                  trigger='cron',
                  day_of_week='mon-fri',
                  hour=18,
                  minute=30)

# Проверки отпусков и дней рождений
scheduler.add_job(birthday_and_vacation_ckr,
                  trigger='cron',
                  day_of_week='sun',
                  hour=12,
                  minute=00)
# Запуск планировщика
scheduler.start()

# Запуск бота
bot.infinity_polling(timeout=6000)

