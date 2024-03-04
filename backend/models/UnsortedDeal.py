from pydantic import BaseModel, Field
from typing import Optional

from sqlalchemy import inspect, engine, Column, Integer, String, create_engine
import os

from sqlalchemy.orm import declarative_base, sessionmaker

from models import User


class UnsortedDeal(BaseModel):
    deal_id: Optional[int]
    user_added_id: int
    title: Optional[str]
    text: str = Field(max_length=500)
    deal_time: int

    def add_deal(self) -> bool:
        return UnsortedDealDB.add_deal(self)

    def delete_deal(self) -> bool:
        return UnsortedDealDB.delete_deal(self)

    def update_deal(self):
        return UnsortedDealDB.deal_update(self)


if not os.path.exists('dbs'):
    os.makedirs('dbs')

engine = create_engine('sqlite:///dbs/unsorted_deal.db', echo=False)

Base = declarative_base()


class UnsortedDealModel(Base):
    __tablename__ = 'unsorted_deal'
    deal_id = Column(Integer, primary_key=True)
    user_added_id = Column(Integer)
    title = Column(String)
    text = Column(String)
    deal_time = Column(Integer)

    def __repr__(self):
        return f"<Deal(deal_id='{self.deal_id}', user_added_id='{self.user_added_id}', " \
               f"title='{self.title}', text='{self.text}', " \
               f"deal_time='{self.deal_time}')>"


inspector = inspect(engine)
if not inspector.has_table(UnsortedDealModel.__tablename__):
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class UnsortedDealDB:

    @staticmethod
    def add_deal(deal: UnsortedDeal):
        new_deal = UnsortedDealModel(user_added_id=deal.user_added_id, title=deal.title,
                                     text=deal.text, deal_time=deal.deal_time)
        session.add(new_deal)
        session.commit()

        return True

    @staticmethod
    def deal_update(deal: UnsortedDeal):
        existing_deal = session.query(UnsortedDealModel).filter_by(deal_id=deal.deal_id).first()

        if existing_deal:
            existing_deal.user_added_id = deal.user_added_id
            existing_deal.title = deal.title
            existing_deal.text = deal.text
            existing_deal.deal_time = deal.deal_time

            session.commit()
            return True
        else:
            return False

    # The rest of your code for delete, delete_by_id, get_all_deals, find_deals_by_user, find_deals_by_user_and_type,
    # and find_deal_by_id should be similar to what you've already implemented for reminders.
    @staticmethod
    def delete_deal(deal):
        return UnsortedDealDB.delete_deal_by_id(deal.deal_id)

    @staticmethod
    def delete_deal_by_id(deal_id: int):
        session.query(UnsortedDealModel).filter_by(deal_id=deal_id).delete()
        session.commit()
        return True

    @staticmethod
    def get_all_deals():
        return session.query(UnsortedDealModel).all()

    @staticmethod
    def find_deals_by_user(user_added_id: int) -> [UnsortedDealModel]:
        raw = session.query(UnsortedDealModel).filter_by(user_added_id=user_added_id).all()
        return raw

    @staticmethod
    def find_deal_by_id(deal_id: int):
        deal = session.query(UnsortedDealModel).filter_by(deal_id=deal_id).first()
        return deal

    @staticmethod
    def find_unsorted_by_user(user_added_id: int) -> [UnsortedDealModel]:
        raw = session.query(UnsortedDealModel).filter_by(user_added_id=user_added_id).all()
        return raw
