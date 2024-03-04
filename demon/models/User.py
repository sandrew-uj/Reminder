import json
import logging

from pydantic import BaseModel

from config import BACKEND_URL
from models.Deal import Deal
from models.Remind import Remind
import requests as req

import os


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

    def find_deals(self) -> [Deal]:
        res = req.get(f"{BACKEND_URL}/deal/user/{self.telegram_id}/deals")
        a = []
        for i in res.json():
            a.append(Deal(**i))
        logging.log(20, f"у пользователя с id {self.telegram_id} есть {len(a)} напоминаний")

        return a

    def get_tz(self) -> int:
        res = req.get(f"{BACKEND_URL}/user/{self.telegram_id}/tz")
        # print(res)
        if res == "None":
            return 3
        # print(res.json())
        return int(res.json())
