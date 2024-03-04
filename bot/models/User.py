import json

from pydantic import BaseModel
from models.Remind import Remind
from config import BACKEND_URL
from aiogram import types
import requests as req
from loader import bot
import logging

from models.UnsortedDeal import UnsortedDeal


class User(BaseModel):
    telegram_id: int
    username: str
    first_name: str
    last_name: str
    language_code: str
    is_premium: bool
    profile_description: str

    min_remind_id: int

    photo: str  # List[types.UserProfilePhotos]

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self):
        return self.__dict__

    def add_user(self) -> int:
        res = req.post(f"{BACKEND_URL}/user/", json.dumps(self.to_dict()))
        logging.log(20, f"пользователь с id {self.telegram_id} был добавлен в базу данных")
        return res.status_code

    def exists(self) -> int:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}")

        logging.log(20, f"пользователь с id {self.telegram_id} уже существует в базе данных")
        return res.json()

    # def update(self) -> bool:
    #     return update(self)

    # def delete_user(self) -> bool:
    #     return delete(self)

    def find_reminds(self) -> [Remind]:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/reminds")
        a = []
        for i in res.json():
            a.append(Remind(**i))
        logging.log(20, f"у пользователя с id {self.telegram_id} есть {len(a)} напоминаний")

        return a

    def find_reminds_by_type(self, remind_type: str) -> [Remind]:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/reminds/{remind_type}")
        a = []
        if res.json():
            for i in res.json():
                a.append(Remind(**i))

        return a

    def find_unsorted(self) -> [UnsortedDeal]:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/unsorted")
        a = []
        if res.json():
            for i in res.json():
                a.append(UnsortedDeal(**i))

        return a

    def get_min_remind(self):
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/min_remind")
        # print(res)
        if res == "None":
            return None
        return Remind(**res.json())

    def get_tz(self) -> int:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/tz")
        # print(res)
        if res == "None":
            return 3
        return int(res.json())

    def update_tz(self, tz: int) -> int:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/update_tz/{tz}")
        return res.status_code

    @staticmethod
    async def get_user_data(message):
        telegram_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        language_code = message.from_user.language_code
        try:
            is_premium = message.from_user.is_premium or False
        except AttributeError:
            is_premium = False

        profile_photos = []
        # Get profile photos
        photos = await bot.get_user_profile_photos(telegram_id)
        for i, photo in enumerate(photos.photos):
            try:
                file_id = photo[-1].file_id
                profile_photos.append(types.InputMediaPhoto(media=file_id))
            except (IndexError, TypeError):
                logging.error(f"Failed to get profile photo for user {telegram_id}")

        # Get profile description
        profile_description = ""
        profile = await bot.get_chat(telegram_id)
        if profile.bio:
            profile_description = f"Profile description: {profile.bio}\n"

        user_dict = {'telegram_id': telegram_id, 'username': username,
                     'first_name': first_name, 'last_name': last_name,
                     'language_code': language_code, 'photo': str(profile_photos),
                     'is_premium': is_premium, 'profile_description': profile_description,
                     'min_remind_id': -1, }  # setting msk timezone by default
        return User(**user_dict)
