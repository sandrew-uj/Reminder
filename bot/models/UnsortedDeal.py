import json
from typing import Optional
import requests as req
from pydantic import BaseModel, Field

from config import BACKEND_URL


class UnsortedDeal(BaseModel):
    deal_id: Optional[int]
    user_added_id: int
    title: Optional[str]
    text: str = Field(max_length=500)
    deal_time: int

    def to_dict(self):
        return self.__dict__

    def add_deal(self) -> int:
        res = req.post(f'{BACKEND_URL}/unsorted/', json.dumps(self.to_dict()))
        return res.status_code

    def delete_deal(self) -> int:
        res = req.post(f'{BACKEND_URL}/unsorted/delete', json.dumps(self.to_dict()))
        return res.status_code

    @staticmethod
    def delete_deal_by_id(deal_id: int) -> int:
        try:
            res = req.get(f'{BACKEND_URL}/unsorted/delete/{deal_id}')
            return res.status_code
        except Exception:
            pass

    @staticmethod
    def get_deal(deal_id: int):
        res = req.get(f"{BACKEND_URL}/unsorted/get/{deal_id}")
        return UnsortedDeal(**res.json())
