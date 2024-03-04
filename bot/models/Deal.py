import json
from typing import Optional
import requests as req
from pydantic import BaseModel, Field

from config import BACKEND_URL


class Deal(BaseModel):
    deal_id: Optional[int]
    unsorted_deal_id: int
    date_start: int
    date_end: int
    date_before: int
    deal_type: str
    user_added_id: int

    def to_dict(self):
        return self.__dict__

    def add_deal(self) -> int:
        res = req.post(f'{BACKEND_URL}/deal/', json.dumps(self.to_dict()))
        return res.status_code

    def delete_deal(self) -> int:
        res = req.post(f'{BACKEND_URL}/deal/delete', json.dumps(self.to_dict()))
        return res.status_code

    @staticmethod
    def delete_deal_by_id(deal_id: int) -> int:
        try:
            res = req.get(f'{BACKEND_URL}/deal/delete/{deal_id}')
            return res.status_code
        except Exception:
            pass

    @staticmethod
    def get_deal(deal_id: int):
        res = req.get(f"{BACKEND_URL}/deal/get/{deal_id}")
        return Deal(**res.json())

    @staticmethod
    def get_deals_by_user(telegram_id: int):
        res = req.get(f"{BACKEND_URL}/deal/user/{telegram_id}/deals")

        a = []
        # print(res.json())
        if res.json():
            for i in res.json():
                a.append(Deal(**i))

        return a
