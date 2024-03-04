import logging
import calendar
import datetime
import time

from aiogram import Bot, Dispatcher, types
import locale
import os
import json

import models
from keyboards import menu_callback, create_remind_or_deal
from loader import dp, bot
from models import User
from models.Deal import Deal
from models.Remind import Remind
from models.UnsortedDeal import UnsortedDeal
from utils.send_message_with_keyboard import sender


# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


# sudo apt-get install language-pack-ru для линукса

# устанавливаем московский часовой пояс


def get_tzinfo(tz: int):
    time_delta = datetime.timedelta(hours=tz)
    tz_info = datetime.timezone(time_delta, name="USER")
    return tz_info


def get_now(tz: int) -> datetime.datetime:
    tz_info = get_tzinfo(tz)
    return datetime.datetime.now(tz=tz_info)


# def default_user_data(user_id: int):
#     user: User = User.get_user_data()
#     now = get_now()
#


def get_user_last_calendar_message(user_id):
    user_data = get_user_data(user_id)
    return user_data.get("last_calendar_message_id", None) if user_data else None


def save_user_last_calendar_message(user_id, message_id):
    user_data = get_user_data(user_id)
    if not user_data:
        user_data = {}
    user_data["last_calendar_message_id"] = message_id
    set_user_data(user_id, user_data)


def get_user_data(user_id):
    now = get_now(3)  # MSK timezone by default
    default_user_data = {
        'year': now.today().year,
        'month': now.today().month,
        'hour': 12,
        'minute': 0,
        'tz': 3,
        'deal': 0
    }

    if os.path.exists("data.json"):
        with open("data.json", "r") as file:
            file_content = file.read()
            if not file_content:
                return None
            try:
                data = json.loads(file_content)
            except json.JSONDecodeError:
                return None
            return data.get(str(user_id), default_user_data)

    return default_user_data


def set_user_data(user_id, user_data):
    data = {}
    if os.path.exists("data.json"):
        with open("data.json", "r") as file:
            data = json.load(file)
    data[str(user_id)] = user_data
    with open("data.json", "w") as file:
        json.dump(data, file)


def create_calendar(user_data: dict = None):
    tz = int(user_data.get('tz'))
    year = user_data.get('year', get_now(tz).today().year)
    month = user_data.get('month', get_now(tz).today().month)
    hour = user_data.get('hour', 12)
    minute = user_data.get('minute', 0)
    deal = user_data.get('deal', 0)
    # print(f"create calendar deal = {deal}")
    selected_date = user_data.get('selected_date')

    if not user_data:
        user_data = {}

    markup = types.InlineKeyboardMarkup()

    if not user_data.get('daily_mode', False) and deal < 2:
        # Отображение года с кнопками для листания
        markup.row(
            types.InlineKeyboardButton("<<", callback_data=f"calendar_year_prev_{year}_{month}"),
            types.InlineKeyboardButton(f"☑️ {year}" if user_data.get('year_selected') else str(year),
                                       callback_data="calendar_year_select"),
            types.InlineKeyboardButton(">>", callback_data=f"calendar_year_next_{year}_{month}")
        )

        # Отображение месяца с кнопками для листания
        month_name = datetime.date(year, month, 1).strftime('%B')
        markup.row(
            types.InlineKeyboardButton("<", callback_data=f"calendar_month_prev_{year}_{month}"),
            types.InlineKeyboardButton(f"☑️ {month_name}" if user_data.get('month_selected') else month_name,
                                       callback_data="calendar_month_select"),
            types.InlineKeyboardButton(">", callback_data=f"calendar_month_next_{year}_{month}")
        )

        # Имена дней недели
        my_calendar = calendar.monthcalendar(year, month)
        selected_day = user_data.get('selected_day')
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вск"]
        row = [types.InlineKeyboardButton(f"☑️ {day}" if i + 1 == selected_day else day, callback_data=f"day_{i + 1}")
               for
               i, day in enumerate(days)]
        markup.row(*row)

        for week in my_calendar:
            row = []
            for day in week:
                if day == 0:
                    row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
                else:
                    date_str = f"{year}-{month:02}-{day:02}"
                    if date_str == selected_date:
                        row.append(types.InlineKeyboardButton(f"☑️ {day}", callback_data=f"calendar_date_{date_str}"))
                    else:
                        row.append(types.InlineKeyboardButton(str(day), callback_data=f"calendar_date_{date_str}"))
            markup.row(*row)

    # Добавляем кнопку "Ежедневное"
    if not user_data.get('daily_mode', False):
        markup.row(types.InlineKeyboardButton("Ежедневное", callback_data="daily_select"))
    else:
        markup.row(types.InlineKeyboardButton("☑️ Ежедневное", callback_data="daily_select"))

    # Добавляем кнопки для управления часами
    markup.row(
        types.InlineKeyboardButton("- час", callback_data=f"time_hour_decrease_{hour}_{minute}"),
        types.InlineKeyboardButton(f"{hour:02}", callback_data="ignore"),
        types.InlineKeyboardButton("+ час", callback_data=f"time_hour_increase_{hour}_{minute}")
    )

    # Добавляем кнопки для управления минутами
    markup.row(
        types.InlineKeyboardButton("- 5 мин", callback_data=f"time_minute_decrease_{hour}_{minute}"),
        types.InlineKeyboardButton(f"{minute:02}", callback_data="ignore"),
        types.InlineKeyboardButton("+ 5 мин", callback_data=f"time_minute_increase_{hour}_{minute}")
    )

    markup.row(
        types.InlineKeyboardButton("Создать", callback_data=create_remind_or_deal.new(action="create", deal=deal)))

    return markup


def determine_message_text(user_data):
    if user_data.get('year_selected'):
        if user_data.get('selected_date'):
            date_parts = user_data['selected_date'].split('-')
            day, month = date_parts[2], date_parts[1]
            hour, minute = user_data.get('hour', 12), user_data.get('minute', 0)
            return f"Новое ежегодное напоминание: {day}.{month} в {hour:02}:{minute:02}"
        else:
            return "Новое ежегодное напоминание"
    elif user_data.get('daily_mode', False):
        hour, minute = user_data.get('hour', 12), user_data.get('minute', 0)
        return f"Новое ежедневное напоминание в {hour:02}:{minute:02}"
    elif user_data.get('month_selected'):
        if user_data.get('selected_date'):
            day = user_data['selected_date'].split('-')[2]
            hour, minute = user_data.get('hour', 12), user_data.get('minute', 0)
            return f"Новое ежемесячное напоминание с датой срабатывания: {day} в {hour:02}:{minute:02}"
        else:
            return "Новое ежемесячное напоминание"
    elif user_data.get('selected_day'):
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вск"]
        selected_day_name = day_names[user_data.get('selected_day') - 1]
        days = {
            "Пн": "понедельникам",
            "Вт": "вторникам",
            "Ср": "средам",
            "Чт": "четвергам",
            "Пт": "пятницам",
            "Сб": "субботам",
            "Вск": "воскресеньям"
        }
        hour, minute = user_data.get('hour', 12), user_data.get('minute', 0)
        return f"Новое еженедельное напоминание по {days[selected_day_name]} в {hour:02}:{minute:02}"
    else:
        if user_data.get('selected_date'):
            date_parts = user_data['selected_date'].split('-')
            day, month, year = date_parts[2], date_parts[1], date_parts[0]
            hour, minute = user_data.get('hour', 12), user_data.get('minute', 0)
            return f"Новое напоминание: {day}.{month}.{year} в {hour:02}:{minute:02}"
        else:
            return "Новое напоминание"


@dp.callback_query_handler(lambda c: c.data == 'daily_select')
async def on_daily_select_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    # Переключаем режим "Ежедневное"
    user_data['daily_mode'] = not user_data.get('daily_mode', False)

    set_user_data(user_id, user_data)

    hour = user_data.get('hour', 12)
    minute = user_data.get('minute', 0)

    # Определить текст сообщения
    if user_data['daily_mode']:
        text_message = f"Новое ежедневное напоминание в {hour:02}:{minute:02}"
    else:
        text_message = determine_message_text(user_data)

    markup = create_calendar(user_data=user_data)
    await query.message.edit_text(text=text_message, reply_markup=markup)
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('day_'))
async def on_day_select_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    # Получаем номер выбранного дня недели
    selected_day = int(query.data.split('_')[1])

    # Устанавливаем или сбрасываем выбранный день недели
    if user_data.get('selected_day') == selected_day:
        user_data['selected_day'] = None
    else:
        user_data['selected_day'] = selected_day

    # Сбрасываем выбранный месяц и год
    user_data['month_selected'] = False
    user_data['year_selected'] = False

    # Сбросить выбранную дату
    user_data.pop('selected_date', None)

    set_user_data(user_id, user_data)

    markup = create_calendar(user_data=user_data)
    text_message = determine_message_text(user_data)
    await query.message.edit_text(text=text_message, reply_markup=markup)
    await query.answer()


@dp.callback_query_handler(lambda c: c.data == 'calendar_year_select')
async def on_year_select_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    # Переключаем состояние выбора года
    user_data['year_selected'] = not user_data.get('year_selected', False)
    user_data.pop('selected_day', None)
    # Если год выбран, и месяц также выбран, снимаем выбор месяца
    if user_data['year_selected'] and user_data.get('month_selected', False):
        user_data['month_selected'] = False

    set_user_data(user_id, user_data)

    year = user_data.get('year', datetime.date.today().year)
    month = user_data.get('month', datetime.date.today().month)
    hour = user_data.get('hour', 12)
    minute = user_data.get('minute', 0)

    markup = create_calendar(user_data=user_data)

    # Проверяем, выбран ли год
    if user_data.get('year_selected'):
        # Если дата уже выбрана, обновляем текстовое сообщение
        if user_data.get('selected_date'):
            year, month, day = map(int, user_data.get('selected_date').split('-'))
            await query.message.edit_text(f"Новое ежегодное напоминание: {day:02}.{month:02} в {hour:02}:{minute:02}",
                                          reply_markup=markup)
        else:
            await query.message.edit_text("Новое ежегодное напоминание", reply_markup=markup)
    else:
        # Если дата уже выбрана, обновляем текстовое сообщение
        if user_data.get('selected_date'):
            day, month, year = map(int, user_data.get('selected_date').split('-'))
            await query.message.edit_text(f"Новое напоминание: {day:02}.{month:02}.{year} в {hour:02}:{minute:02}",
                                          reply_markup=markup)
        else:
            await query.message.edit_text("Новое напоминание", reply_markup=markup)

    await query.answer()


@dp.callback_query_handler(lambda c: c.data == 'calendar_month_select')
async def on_month_select_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    # Переключаем состояние выбора месяца
    user_data['month_selected'] = not user_data.get('month_selected', False)

    # Если месяц выбран, и год также выбран, снимаем выбор года
    if user_data['month_selected'] and user_data.get('year_selected', False):
        user_data['year_selected'] = False

    # Если месяц выбран, сбрасываем выбранный день недели
    if user_data['month_selected']:
        user_data.pop('selected_day', None)

    # Если месяц выбран, и дата также выбрана, сохраняем выбранную дату для отображения
    if user_data['month_selected'] and user_data.get('selected_date'):
        selected_date = user_data['selected_date']
        day = selected_date.split('-')[2]
        user_data['day'] = day

    set_user_data(user_id, user_data)

    markup = create_calendar(user_data=user_data)
    await query.message.edit_text(determine_message_text(user_data), reply_markup=markup)
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('time_hour_'))
async def on_hour_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    data_parts = query.data.split('_')
    action = data_parts[2]
    current_hour = int(data_parts[3])
    current_minute = user_data.get('minute', 0)

    if action == "increase":
        current_hour = (current_hour + 1) % 24
    elif action == "decrease":
        current_hour = (current_hour - 1) % 24

    user_data['hour'] = current_hour
    set_user_data(user_id, user_data)

    markup = create_calendar(user_data=user_data)

    text_message = determine_message_text(user_data)
    await query.message.edit_text(text=text_message, reply_markup=markup)
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('time_minute_'))
async def on_minute_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    data_parts = query.data.split('_')
    action = data_parts[2]
    current_minute = int(data_parts[4])
    current_hour = user_data.get('hour', 12)

    if action == "increase":
        current_minute += 5
        if current_minute >= 60:
            current_minute = 0
    elif action == "decrease":
        current_minute -= 5
        if current_minute < 0:
            current_minute = 55

    user_data['minute'] = current_minute
    set_user_data(user_id, user_data)

    markup = create_calendar(user_data=user_data)

    text_message = determine_message_text(user_data)
    await query.message.edit_text(text=text_message, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith('calendar_date_'))
async def on_date_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    data_parts = query.data.split('_')
    selected_date = data_parts[2]  # Получаем полную дату в формате "YYYY-MM-DD"

    if selected_date == user_data.get('selected_date', None):
        user_data['selected_date'] = None
    else:
        user_data['selected_date'] = selected_date

    # Сбросить значение выбранного дня недели
    user_data.pop('selected_day', None)

    set_user_data(user_id, user_data)

    year, month, _ = map(int, selected_date.split('-'))
    hour = user_data.get('hour', 12)
    minute = user_data.get('minute', 0)
    markup = create_calendar(user_data=user_data)

    text_message = determine_message_text(user_data)
    await query.message.edit_text(text=text_message, reply_markup=markup)
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('calendar_month_'))
async def on_month_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    data_parts = query.data.split('_')
    action = data_parts[2]
    current_year = int(data_parts[3])
    current_month = int(data_parts[4])

    if action == "prev":
        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1
    elif action == "next":
        current_month += 1
        if current_month == 13:
            current_month = 1
            current_year += 1

    user_data['year'] = current_year
    user_data['month'] = current_month
    set_user_data(user_id, user_data)

    hour = user_data.get('hour', 12)  # Используем значение по умолчанию, если ключ отсутствует
    minute = user_data.get('minute', 0)  # Используем значение по умолчанию, если ключ отсутствует

    markup = create_calendar(user_data=user_data)
    await query.message.edit_reply_markup(reply_markup=markup)
    await query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('calendar_year_'))
async def on_year_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    data_parts = query.data.split('_')
    action = data_parts[2]
    current_year = int(data_parts[3])
    current_month = int(data_parts[4])

    if action == "prev":
        current_year -= 1
    elif action == "next":
        current_year += 1

    user_data['year'] = current_year
    set_user_data(user_id, user_data)

    hour = user_data.get('hour', 12)  # Используем значение по умолчанию, если ключ отсутствует
    minute = user_data.get('minute', 0)  # Используем значение по умолчанию, если ключ отсутствует

    markup = create_calendar(user_data=user_data)
    await query.message.edit_reply_markup(reply_markup=markup)
    await query.answer()


# @dp.message_handler(commands=["calendar"])
# @dp.callback_query_handler(menu_callback.filter(cbtype='1'), state='*')
async def on_show_calendar(message: types.Message, deal: int = 0, call: types.CallbackQuery = None):
    # print("Command /calendar received.")
    user_id = message.from_user.id
    if call:
        user_id = call.from_user.id

    user_data = get_user_data(user_id)
    # print(user_id)
    tz = int(user_data.get('tz'))

    # Удалить старые данные пользователя
    if os.path.exists("data.json"):
        with open("data.json", "r+") as file:
            data = json.load(file)
            if str(user_id) in data:
                del data[str(user_id)]
                file.seek(0)
                json.dump(data, file)
                file.truncate()

    # Если у вас сохранена ссылка на старое сообщение с календарем, удаляем его
    last_calendar_message_id = get_user_last_calendar_message(user_id)
    if last_calendar_message_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=last_calendar_message_id)
        except Exception as e:
            logging.error(f"Error deleting the old calendar: {e}")

    today = get_now(tz).today()

    print(f"on show deal = {deal}")
    user_data = {
        'year': today.year,
        'month': today.month,
        'hour': 12,
        'minute': 0,
        'tz': tz,
        'deal': deal
    }
    if deal >= 2:
        user_data['hour'] = 0
    set_user_data(user_id, user_data)

    markup = create_calendar(user_data=user_data)

    selected_date = user_data.get('selected_date')

    deal_to_str = {
        0: "напоминание",
        1: "дело (начало)",
        2: "дело (продолжительность)",
        3: "За сколько напомнить?"
    }

    if selected_date:
        day, month, year = map(int, selected_date.split('-'))
        time_str = f"{user_data['hour']:02}:{user_data['minute']:02}"
        text_message = f"Новое ежегодное {deal_to_str[deal]}: {day:02}.{month:02} в {time_str}"
    else:
        text_message = f"Новое {deal_to_str[deal]}"

    sent_message = await message.answer(text=text_message, reply_markup=markup)

    # Сохраняем ID нового сообщения с календарем
    save_user_last_calendar_message(user_id, sent_message.message_id)


async def read_json(file):
    json_text = ""
    while True:
        json_line = file.readline()
        if json_line is None or json_line == "":
            break
        json_text += json_line

    return json_text


def get_reminder_time(year, month, day, hour, minute, tz: int):
    return datetime.datetime(year, month, day, hour, minute, tzinfo=get_tzinfo(tz))


def get_time_delta(hours, minutes):
    return datetime.timedelta(hours=hours, minutes=minutes)


def check_crossings(start: float, end: float, user_id: int):
    deals = Deal.get_deals_by_user(user_id)
    for deal in deals:
        if deal.date_start < start < deal.date_end:
            return False
        if deal.date_start < end < deal.date_end:
            return False
        if start < deal.date_start < end:
            return False
        if start < deal.date_end < end:
            return False
    return True


def convert_timedelta(needed_time) -> str:
    hours, seconds = divmod(needed_time, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours} часов {minutes} минут"


@dp.callback_query_handler(create_remind_or_deal.filter(action="create"))
async def on_create_reminder_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    user_data = get_user_data(user_id)

    if int(user_data['deal']) >= 2:
        # Определяем тип напоминания
        if user_data.get('year_selected'):
            reminder_type = 'yearly'
        elif user_data.get('month_selected'):
            reminder_type = 'monthly'
        elif user_data.get('selected_day'):
            reminder_type = 'weekly'
        elif user_data.get('daily_mode', False):
            reminder_type = 'daily'
        else:
            reminder_type = 'single'

        hour = user_data.get('hour', 0)
        minute = user_data.get('minute', 0)
        reminder_time = get_time_delta(hour, minute)

    # Если режим "Ежедневное" активирован
    elif user_data.get('daily_mode', False):
        hour = user_data.get('hour', 12)
        minute = user_data.get('minute', 0)

        # Получаем текущую дату и время
        tz = int(user_data.get('tz'))
        now = get_now(tz)
        reminder_time = get_reminder_time(now.year, now.month, now.day, hour, minute, tz)

        # Если указанное время уже прошло, устанавливаем напоминание на следующий день
        if reminder_time < now:
            reminder_time += datetime.timedelta(days=1)

        reminder_type = "daily"

    else:
        # Определяем тип напоминания
        if user_data.get('year_selected'):
            reminder_type = 'yearly'
        elif user_data.get('month_selected'):
            reminder_type = 'monthly'
        elif user_data.get('selected_day'):
            reminder_type = 'weekly'
        else:
            reminder_type = 'single'

        # Получаем дату и время напоминания
        selected_date = user_data.get('selected_date')
        selected_day_of_week = user_data.get('selected_day')  # выбранный день недели (1-7)

        tz = int(user_data.get('tz'))
        if selected_date:
            year, month, day = map(int, selected_date.split('-'))
        elif selected_day_of_week:  # если выбран день недели
            today = get_now(tz).today()
            while today.weekday() + 1 != selected_day_of_week:  # weekday() возвращает 0-6, поэтому добавляем 1
                today += datetime.timedelta(days=1)
            year, month, day = today.year, today.month, today.day
        else:
            year, month, day = get_now(tz).today().year, get_now(tz).today().month, get_now(tz).today().day

        hour = user_data.get('hour', 12)
        minute = user_data.get('minute', 0)
        tz = int(user_data.get('tz'))
        reminder_time = get_reminder_time(year, month, day, hour, minute, tz)

        # Если напоминание не "ежедневное" и дата напоминания в прошлом
        if reminder_type != 'daily' and reminder_time.date() < get_now(tz).date():
            if reminder_type == 'single':
                await query.answer("Невозможно создать напоминание в прошлом!")
                return
            elif reminder_type == 'monthly':
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                # Проверяем, не превышает ли день последний день следующего месяца
                last_day_of_next_month = calendar.monthrange(year, month)[1]
                if day > last_day_of_next_month:
                    day = last_day_of_next_month
                reminder_time = get_reminder_time(year, month, day, hour, minute, tz)
            elif reminder_type == 'yearly':
                year += 1
                reminder_time = get_reminder_time(year, month, day, hour, minute, tz)

    # unix_time = int(reminder_time.timestamp())

    # reminder_time = reminder_time.astimezone(tz=msk_tz)

    deal = int(create_remind_or_deal.parse(query.data)["deal"])
    if deal < 2:
        needed_time = time.mktime(reminder_time.timetuple())  # запихать в date
    else:
        needed_time = reminder_time.total_seconds()

    print(deal)

    if deal == 0:
        file = open(f"data/{query.from_user.id}/user_remind.json", 'r')
        json_text = await read_json(file)
        file.close()

        user_deal = Remind(**json.loads(json_text))
        user_deal.remind_type = reminder_type
        user_deal.date = needed_time

        # user_remind.remind_time = diff

        # print(user_remind)

        user_deal.add_remind()

        curr_user: User = await User.get_user_data(query)
        min_remind = curr_user.get_min_remind()

        if not min_remind:
            return await query.answer("Ошибка!")

        # import shutil
        # shutil.rmtree(f'data/{query.from_user.id}/')
        # min_remind_datetime = datetime.datetime.fromtimestamp(min_remind.date)
        min_remind_datetime = datetime.datetime.fromtimestamp(user_deal.date)
        await query.message.edit_text(f"Добавил напоминание.\n"
                                      f"Ближайшее напоминание: "
                                      f"{time.strftime('%Y.%m.%d в %H:%M', min_remind_datetime.timetuple())}")
        #   f"{user_remind.}")

        # Формируем и печатаем JSON
        reminder_data = {
            "user": user_id,
            "type": reminder_type,
            "time": needed_time
        }
    elif deal == 1:
        file = open(f"data/{query.from_user.id}/user_deal.json", 'r')
        json_text = await read_json(file)
        file.close()

        user_deal = UnsortedDeal(**json.loads(json_text))

        if not check_crossings(needed_time, needed_time + user_deal.deal_time, user_id):
            return await query.answer("Имеются пересечения в расписании, выберите другое время")

        data = {
            "deal_id": 1,
            "unsorted_deal_id": user_deal.deal_id,
            "user_added_id": user_deal.user_added_id,
            "title": "",
            "date_start": needed_time,
            "date_end": needed_time + user_deal.deal_time,
            "date_before": 0,
            "deal_type": reminder_type
        }

        with open(f"data/{query.from_user.id}/user_deal.json", 'w') as file:
            file.write(json.dumps(data))

        await sender(call=query, message_text="Теперь выберите за какое время напомнить: ")
        await on_show_calendar(message=query.message, deal=3, call=query)
    elif deal == 2:
        file = open(f"data/{query.from_user.id}/user_deal.json", 'r')
        json_text = await read_json(file)
        file.close()
        user_deal = UnsortedDeal(**json.loads(json_text))
        # user_deal.date_end = needed_time

        # date_start = datetime.datetime.fromtimestamp(user_deal.date_start)
        user_deal.deal_time = needed_time
        # user_deal.date_end = time.mktime((date_start + reminder_time).timetuple())
        user_deal.add_deal()

        await query.message.edit_text(f"Добавил дело.\n"
                                      f"Продолжительность дела: {convert_timedelta(needed_time)}")
    elif deal == 3:
        file = open(f"data/{query.from_user.id}/user_deal.json", 'r')
        json_text = await read_json(file)
        file.close()
        user_deal = Deal(**json.loads(json_text))
        user_deal.date_before = user_deal.date_start - needed_time

        user_deal.add_deal()

        date_start = datetime.datetime.fromtimestamp(user_deal.date_start)
        date_end = datetime.datetime.fromtimestamp(user_deal.date_end)
        date_before = datetime.datetime.fromtimestamp(user_deal.date_before)
        await query.message.edit_text(f"Запланировал дело.\n"
                                      f"Ближайшее дело:\n"
                                      f"{time.strftime('с %Y.%m.%d в %H:%M ', date_start.timetuple())}"
                                      f"{time.strftime('до %Y.%m.%d в %H:%M', date_end.timetuple())}\n"
                                      f"{time.strftime('напомнить %Y.%m.%d в %H:%M', date_before.timetuple())}")
    # print(json.dumps(reminder_data))

    # Отправляем ответ пользователю
    await query.answer()
