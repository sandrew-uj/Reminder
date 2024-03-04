import json
import logging
from typing import Optional
import requests as req
from pydantic import BaseModel, Field

from config import BACKEND_URL


class Remind(BaseModel):
    remind_id: Optional[int]
    user_added_id: int
    title: Optional[str]
    text: str = Field(max_length=500)
    date: int
    remind_type: str
    remind_time: int

    def to_dict(self):
        return self.__dict__

    def add_remind(self) -> int:
        res = req.post(f'{BACKEND_URL}/remind/', json.dumps(self.to_dict()))
        # print(20, self.to_dict())
        return res.status_code

    def delete_remind(self) -> int:
        res = req.post(f'{BACKEND_URL}/remind/delete', json.dumps(self.to_dict()))
        return res.status_code

    @staticmethod
    def delete_remind_by_id(remind_id: int) -> int:
        try:
            res = req.get(f'{BACKEND_URL}/remind/delete/{remind_id}')
            return res.status_code
        except Exception:
            pass

    @staticmethod
    def get_remind(remind_id: int):
        res = req.get(f"{BACKEND_URL}/remind/get/{remind_id}")
        return Remind(**res.json())

#
# data = {
#     "remind_id": 0,
#     "user_added_id": 0,
#     "text": "some text",
#     "date": 0,
#     "remind_type": "once",
#     "remind_time": 6
# }
#
# remind = Remind(**data)
