from typing import Optional, Type

from pydantic import BaseModel, Field
# from dbs_controllers import RemindModel as remindDb

import os

from sqlalchemy import create_engine, Column, Integer, String, inspect, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import models
from models import User


# from models.User import find_user


# def find_remind_model():
#     pass


class Remind(BaseModel):
    remind_id: Optional[int]
    user_added_id: int
    title: Optional[str]
    text: str = Field(max_length=500)
    date: int
    remind_type: str
    remind_time: int

    def add_remind(self) -> bool:
        return add(self)

    # def exists(self) -> bool:
    #     return exists(self)

    def delete_remind(self) -> bool:
        # return delete(find_remind_model(self))
        return delete(self)

    def update_remind(self):
        return remind_update(self)


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


if not os.path.exists('dbs'):
    os.makedirs('dbs')

engine = create_engine('sqlite:///dbs/remind.db', echo=False)

Base = declarative_base()


class RemindModel(Base):
    __tablename__ = 'remind'
    remind_id = Column(Integer, primary_key=True)
    user_added_id = Column(Integer)
    title = Column(String)
    text = Column(String)
    date = Column(Integer)
    remind_type = Column(String)
    remind_time = Column(Integer)

    def __repr__(self):
        return f"<Remind(remind_id='{self.remind_id}', user_added_id='{self.user_added_id}', " \
               f"title='{self.title}', text='{self.text}', " \
               f"date='{self.date}', remind_type='{self.remind_type}', " \
               f"remind_time='{self.remind_time}')>"


inspector = inspect(engine)
if not inspector.has_table(RemindModel.__tablename__):
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# def find_remind_model(remind: Remind):
# remind_model = session.query(RemindModel).filter(and_(RemindModel.user_added_id == remind.user_added_id,
#                                                       and_(RemindModel.remind_time == remind.remind_time,
#                                                            and_(
#                                                                RemindModel.date == remind.date,
#                                                                and_(
#                                                                    RemindModel.title == str(remind.title),
#                                                                    RemindModel.text == str(remind.text)
#                                                                )
#                                                            )
#                                                            )
#                                                       )
#                                                  ).first()
# return remind_model


def add(remind: Remind):
    # if not exists(remind):
    new_remind = RemindModel(user_added_id=remind.user_added_id, title=remind.title,
                             text=remind.text, date=remind.date,
                             remind_type=remind.remind_type, remind_time=remind.remind_time)
    session.add(new_remind)
    session.commit()

    user: User = User.find_user(new_remind.user_added_id)
    # print(user)
    min_remind = user.get_min_remind()

    if min_remind is None or min_remind.date > remind.date:
        # print("im here")
        user.min_remind_id = new_remind.remind_id
        # print(new_remind.remind_id)

    # print(user.min_remind_id)

    user.update()

    return True
    # else:
    #     return False


# def exists(remind: RemindModel):
#     return session.query(RemindModel).filter_by(remind_id=remind.remind_id).first() is not None

def remind_update(remind):
    session.query(RemindModel).filter_by(remind_id=remind.remind_id).delete()
    add(remind)


def delete(remind):
    return delete_by_id(remind.remind_id)


def delete_by_id(remind_id: int):
    session.query(RemindModel).filter_by(remind_id=remind_id).delete()
    session.commit()
    return True


def get_all_reminds():
    return session.query(RemindModel).all()


def find_reminds_by_user(user_added_id: int) -> [RemindModel]:
    raw = session.query(RemindModel).filter_by(user_added_id=user_added_id).all()
    return raw


def find_reminds_by_user_and_type(user_added_id: int, remind_type: str) -> [RemindModel]:
    raw = session.query(RemindModel).filter_by(user_added_id=user_added_id, remind_type=remind_type).all()
    return raw


def find_remind_by_id(remind_id: int):
    remind = session.query(RemindModel).filter_by(remind_id=remind_id).first()
    return remind




#
# def check(remind: Remind, i: RemindModel):
#     # remind_id: Optional[int]
#     # user_added_id: int
#     # title: Optional[str]
#     # text: str = Field(max_length=500)
#     # date: int
#     # remind_type: str
#     # remind_time: int
#     if not remind.title == i.title:
#         return False
#     if not remind.text == i.text:
#         return False
#     if not remind.date == i.date:
#         return False
#     if not remind.remind_type == i.remind_type:
#         return False
#     if not remind.remind_time == i.remind_time:
#         return False
#     return True
#
#
# def find_remind_model(remind: Remind):
#     rem = find_reminds_by_user(remind.user_added_id)
#     for i in rem:
#         if check(remind, i):
#             return i
#
#     return None
