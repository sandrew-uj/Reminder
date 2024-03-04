from typing import Optional

from pydantic import BaseModel, Field
import requests as req

from config import BACKEND_URL
import json


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

    def get_deal_text(self) -> str:
        res = req.get(f"{BACKEND_URL}/unsorted/get/{self.unsorted_deal_id}")
        return res.json()["text"]

    def delete_deal(self) -> int:
        res = req.post(f'{BACKEND_URL}/deal/delete', json.dumps(self.to_dict()))
        return res.status_code

    def update_deal(self):
        try:
            res = req.post(f'{BACKEND_URL}/deal/update', json.dumps(self.to_dict()))
            return res.status_code
        except Exception:
            pass
