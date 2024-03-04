from typing import Any

from pydantic import BaseModel
from models.Remind import Remind
from models import Remind as remindDb

import os

from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_


class Timezone(BaseModel):
    telegram_id: int
    tz: int

    def __init__(self, **data: Any) -> None:
        # super().__init__(**data)
        super().__init__(**data)
        # self.telegram_id = telegram_id
        # self.tz = tz

    class Config:
        arbitrary_types_allowed = True

    def add(self):
        return add(self)

    def update(self):
        return update(self)


if not os.path.exists('dbs'):
    os.makedirs('dbs')

engine = create_engine('sqlite:///dbs/timezones.db', echo=False)

Base = declarative_base()


class TimezoneModel(Base):
    __tablename__ = 'timezones'
    timezone_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    tz = Column(Integer)

    # def __repr__(self):
    #     return f"<User(telegram_id='{self.telegram_id}', username='{self.username}', " \
    #            f"first_name='{self.first_name}', last_name='{self.last_name}', " \
    #            f"language_code='{self.language_code}', photo='{self.photo}', " \
    #            f"is_premium='{self.is_premium}', profile_description='{self.profile_description}" \
    #            f", min_remind_id='{self.min_remind_id}', tz='{self.tz}')>"


# создаем таблицу users, если ее не существует
inspector = inspect(engine)
if not inspector.has_table(TimezoneModel.__tablename__):
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def exists(timezone: Timezone):
    return session.query(TimezoneModel).filter_by(telegram_id=timezone.telegram_id).first() is not None


def get_timezone(telegram_id: int):
    res = session.query(TimezoneModel).filter_by(telegram_id=telegram_id).first()
    if res:
        tz_dict = {'telegram_id': res.telegram_id, 'tz': res.tz}
        return Timezone(**tz_dict)
    return None


def update(timezone: Timezone):
    if exists(timezone):
        session.query(TimezoneModel).filter_by(telegram_id=timezone.telegram_id).update({
            TimezoneModel.telegram_id: timezone.telegram_id,
            TimezoneModel.tz: timezone.tz
        })
        session.commit()
        return True
    else:
        return False


def add(timezone: Timezone):
    if not exists(timezone):
        new_timezone = TimezoneModel(telegram_id=timezone.telegram_id, tz=timezone.tz)
        session.add(new_timezone)
        session.commit()
        return True
    else:
        return False