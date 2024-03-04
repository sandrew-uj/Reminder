import json
from typing import Optional

import requests as req
from pydantic import BaseModel, Field

import os

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
        try:
            res = req.post(f'{BACKEND_URL}/remind/', json.dumps(self.to_dict()))
            print(20, self.to_dict())
            return res.status_code

        except Exception:
            pass

    def delete_remind(self) -> int:
        try:
            res = req.post(f'{BACKEND_URL}/remind/delete', json.dumps(self.to_dict()))
            return res.status_code
        except Exception:
            pass

    def update_remind(self):
        try:
            res = req.post(f'{BACKEND_URL}/remind/update', json.dumps(self.to_dict()))
            return res.status_code
        except Exception:
            pass
