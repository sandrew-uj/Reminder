import datetime
import time

from aiogram import types
from pdf2image import convert_from_path

from handlers.user.with_menu import get_now
from keyboards import menu_callback
from loader import dp
from fpdf import FPDF
import os
from ironpdf import *

from models import User
from models.Deal import Deal
from models.UnsortedDeal import UnsortedDeal
from utils.send_message_with_keyboard import sender


def append_deal(start: int, end: int, text: str, data):
    date_start = datetime.datetime.fromtimestamp(start)
    date_end = datetime.datetime.fromtimestamp(end)
    data.append([f"{date_start.strftime('%H:%M')} -\n{date_end.strftime('%H:%M')}",
                 text[0:30]])
    # print(data[-1])


def fill_from_current(current_time: int, end: int, data):
    while current_time < end:
        current_datetime = datetime.datetime.fromtimestamp(current_time)
        current_datetime = current_datetime.replace(minute=0 if current_datetime.minute < 30 else 30)
        # print(current_datetime.minute)
        current_start = int(time.mktime(current_datetime.timetuple()))

        maybe = current_start + int(datetime.timedelta(hours=1.5).total_seconds())
        current_end = min(maybe, end)
        append_deal(current_time, current_end, "Нет дела", data)
        current_time = current_end


@dp.callback_query_handler(menu_callback.filter(cbtype='4'), state='*')
async def add_deal_start(call: types.CallbackQuery):
    spacing = 1
    data = [['Время', 'Дело'],
            ]

    user: User = await User.get_user_data(call)

    tz = user.get_tz()

    user_id: int = call.from_user.id

    deals = Deal.get_deals_by_user(user_id)

    now = get_now(tz)

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=1)
    start = time.mktime(start.timetuple())
    end = time.mktime(end.timetuple())

    current_time = int(start)

    # print(deals)

    for deal in deals:
        if deal.date_start >= start and deal.date_end <= end:
            fill_from_current(current_time, deal.date_start, data)
            current_time = deal.date_end
            append_deal(deal.date_start, deal.date_end, UnsortedDeal.get_deal(deal.unsorted_deal_id).text, data)

    # print("deals ended")
    fill_from_current(current_time, int(end), data)
    # print("fill ended")

    pdf = FPDF()
    pdf.add_font("Russian", style="", fname="src/font.ttf", uni=True)
    pdf.set_font("Russian", size=20)
    pdf.add_page()

    col_width1 = pdf.w / 4
    col_width2 = pdf.w / 1.5
    col_width = [col_width1, col_width2]

    row_height = pdf.h / (len(data) + 5)
    # print("table started")
    for row in data:
        for width, item in zip(col_width, row):
            pdf.cell(width, row_height,
                     txt=item, border=1, align='C')
        pdf.ln(row_height * spacing)

    # print("table ended")

    if not os.path.exists('src'):
        os.makedirs('src')
    pdf.output(f'src/table{user_id}.pdf')

    images = convert_from_path(f'src/table{user_id}.pdf')
    images[0].save(f'src/schedule{user_id}.jpg', 'JPEG')

    await call.message.answer_photo(photo=open(f'src/schedule{user_id}.jpg', 'rb'), caption="Ваше расписание")
