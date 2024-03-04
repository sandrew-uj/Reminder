from pydantic import BaseModel
from models.Remind import Remind
from models import Remind as remindDb

import os

from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_

from models.UnsortedDeal import UnsortedDeal, UnsortedDealDB


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

    # def to_dict(self):
    #     user_dict = {
    #         'telegram_id': self.telegram_id,
    #         'username': self.username,
    #         'first_name': self.first_name,
    #         'last_name': self.last_name,
    #         'language_code': self.language_code,
    #         'photo': self.photo,
    #         'is_premium': self.is_premium,
    #         'profile_description': self.profile_description
    #     }
    #     return user_dict

    def add_user(self) -> bool:
        return add(self)

    def update(self) -> bool:
        return update(self)

    def delete_user(self) -> bool:
        return delete(self)

    def find_reminds(self) -> [Remind]:
        return remindDb.find_reminds_by_user(self.telegram_id)

    def find_unsorted(self) -> [UnsortedDeal]:
        return UnsortedDealDB.find_deals_by_user(self.telegram_id)

    def find_reminds_by_type(self, remind_type) -> [Remind]:
        return remindDb.find_reminds_by_user_and_type(self.telegram_id, remind_type)

    def get_min_remind(self):
        if self.min_remind_id < 0:
            return None
        return remindDb.find_remind_by_id(self.min_remind_id)

    @staticmethod
    def find_user(search_term):
        return find_user(search_term)


if not os.path.exists('dbs'):
    os.makedirs('dbs')

engine = create_engine('sqlite:///dbs/users.db', echo=False)

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    photo = Column(String)
    is_premium = Column(Integer)
    profile_description = Column(String)
    min_remind_id = Column(Integer)

    def __repr__(self):
        return f"<User(telegram_id='{self.telegram_id}', username='{self.username}', " \
               f"first_name='{self.first_name}', last_name='{self.last_name}', " \
               f"language_code='{self.language_code}', photo='{self.photo}', " \
               f"is_premium='{self.is_premium}', profile_description='{self.profile_description}" \
               f", min_remind_id='{self.min_remind_id}')>"


# создаем таблицу users, если ее не существует
inspector = inspect(engine)
if not inspector.has_table(UserModel.__tablename__):
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# функция проверки наличия пользователя в базе
def exists(user: User):
    return session.query(UserModel).filter_by(telegram_id=user.telegram_id).first() is not None


def get_all_users():
    return session.query(UserModel).all()


# функция добавления пользователя в базу
def add(user: User):
    if not exists(user):
        new_user = UserModel(telegram_id=user.telegram_id, username=user.username, first_name=user.first_name,
                             last_name=user.last_name, language_code=user.language_code, photo=str(user.photo),
                             is_premium=user.is_premium, profile_description=user.profile_description,
                             min_remind_id=user.min_remind_id)
        session.add(new_user)
        session.commit()
        return True
    else:
        return False


# функция удаления пользователя из базы
def delete(user: User):
    if exists(user):
        session.query(UserModel).filter_by(telegram_id=user.telegram_id).delete()
        session.commit()
        return True
    else:
        return False


# функция изменения любого столбца пользователя
def update(user: User):
    if exists(user):
        session.query(UserModel).filter_by(telegram_id=user.telegram_id).update({
            UserModel.username: user.username,
            UserModel.first_name: user.first_name,
            UserModel.last_name: user.last_name,
            UserModel.language_code: user.language_code,
            UserModel.photo: str(user.photo),
            UserModel.is_premium: user.is_premium,
            UserModel.profile_description: user.profile_description,
            UserModel.min_remind_id: user.min_remind_id
        })
        session.commit()
        return True
    else:
        return False


def find_user(search_term):
    user = session.query(UserModel).filter(
        or_(UserModel.telegram_id == search_term,
            UserModel.username == search_term)
    ).first()
    if user:
        user_dict = {'telegram_id': user.telegram_id, 'username': user.username,
                     'first_name': user.first_name, 'last_name': user.last_name,
                     'language_code': user.language_code, 'photo': user.photo,
                     'is_premium': user.is_premium, 'profile_description': user.profile_description,
                     'min_remind_id': user.min_remind_id}
        return User(**user_dict)
    return None
