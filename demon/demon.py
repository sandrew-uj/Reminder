import asyncio
import json

import config
from loader import bot
import requests
import datetime
import time

from models import User
from models.Deal import Deal
from models.Remind import Remind


def get_time(user: User):
    tz: int = user.get_tz()
    time_delta = datetime.timedelta(hours=tz)
    user_tz = datetime.timezone(time_delta, name="USER")
    return int(time.mktime(datetime.datetime.now(tz=user_tz).timetuple()))


async def remind_user(remind: Remind):
    await bot.send_message(chat_id=remind.user_added_id, text=f"Напоминание: \n"
                                                              f"{remind.text}")


async def remind_deal_user(deal: Deal):
    date_start = datetime.datetime.fromtimestamp(deal.date_start)
    date_end = datetime.datetime.fromtimestamp(deal.date_end)
    await bot.send_message(chat_id=deal.user_added_id, text=f"Дело: \n"
                                                            f"{deal.get_deal_text()}\n"
                                                            f"{time.strftime('с %Y.%m.%d в %H:%M ', date_start.timetuple())}"
                                                            f"{time.strftime('до %Y.%m.%d в %H:%M', date_end.timetuple())}")


def get_delta(remind_type):
    if remind_type == "daily":
        return datetime.timedelta(days=1)
    elif remind_type == "weekly":
        return datetime.timedelta(days=7)
    elif remind_type == "monthly":
        return datetime.timedelta(days=30)
    elif remind_type == "yearly":
        return datetime.timedelta(days=365)
    return datetime.timedelta(days=0)


async def demon():
    while True:
        res = None
        try:
            res = requests.get(f"{config.BACKEND_URL}/user/users/all")
        except Exception:
            print("Связь потеряна")
            await asyncio.sleep(5)
            continue
        for i in res.json():
            # print(i)
            user = User(**i)
            if user.telegram_id == 0:
                continue
            user_reminds: list[Remind] = user.find_reminds()
            for j in user_reminds:
                if j.date <= get_time(user):
                    await remind_user(j)
                    if j.remind_type != "single":
                        time_delta = get_delta(j.remind_type)
                        reminder_time = datetime.datetime.fromtimestamp(j.date)
                        j.date = time.mktime((reminder_time + time_delta).timetuple())

                        j.update_remind()
                    else:
                        j.delete_remind()

            user_deals: list[Deal] = user.find_deals()
            for j in user_deals:
                user_time = get_time(user)
                if j.date_start <= user_time or j.date_end <= user_time or j.date_before <= user_time:
                    await remind_deal_user(j)
                    if j.deal_type != "single":
                        time_delta = get_delta(j.deal_type)

                        date_start = datetime.datetime.fromtimestamp(j.date_start)
                        date_end = datetime.datetime.fromtimestamp(j.date_end)
                        date_before = datetime.datetime.fromtimestamp(j.date_before)
                        j.date_start = time.mktime((date_start + time_delta).timetuple())
                        j.date_end = time.mktime((date_end + time_delta).timetuple())
                        j.date_before = time.mktime((date_before + time_delta).timetuple())

                        j.update_deal()
                    else:
                        j.delete_deal()

        await asyncio.sleep(5)
