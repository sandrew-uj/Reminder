from pydantic import BaseModel, Field
from typing import Optional

from sqlalchemy import inspect, create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Create a directory for the database if it doesn't exist
if not os.path.exists('dbs'):
    os.makedirs('dbs')

# Create the SQLite database engine
engine = create_engine('sqlite:///dbs/deal.db', echo=False)

# Define the SQLAlchemy Base class
Base = declarative_base()


# Define the DealModel class for the database table
class DealModel(Base):
    __tablename__ = 'deal'
    deal_id = Column(Integer, primary_key=True)
    unsorted_deal_id = Column(Integer)
    date_start = Column(Integer)
    date_end = Column(Integer)
    date_before = Column(Integer)
    deal_type = Column(String)
    user_added_id = Column(Integer)  # Add the user_added_id column

    def __repr__(self):
        return f"<Deal(deal_id='{self.deal_id}', unsorted_deal_id='{self.unsorted_deal_id}', " \
               f"date_start='{self.date_start}', date_end='{self.date_end}', " \
               f"date_before='{self.date_before}', deal_type='{self.deal_type}', " \
               f"user_added_id='{self.user_added_id}'')"


# Initialize the database and create the 'deal' table if it doesn't exist
inspector = inspect(engine)
if not inspector.has_table(DealModel.__tablename__):
    Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


# Define the Deal class with user_added_id
class Deal(BaseModel):
    deal_id: Optional[int]
    unsorted_deal_id: int
    date_start: int
    date_end: int
    date_before: int
    deal_type: str
    user_added_id: int  # Add the user_added_id field

    def add_deal(self) -> bool:
        new_deal = DealModel(unsorted_deal_id=self.unsorted_deal_id,
                             date_start=self.date_start, date_end=self.date_end,
                             date_before=self.date_before, deal_type=self.deal_type,
                             user_added_id=self.user_added_id)  # Add user_added_id
        session.add(new_deal)
        session.commit()
        return True

    def delete_deal(self) -> bool:
        return DealDB.delete_deal(self)

    def update_deal(self):
        return DealDB.deal_update(self)


# Define the DealDB class for database operations
class DealDB:
    @staticmethod
    def add_deal(deal: Deal):
        new_deal = DealModel(unsorted_deal_id=deal.unsorted_deal_id,
                             date_start=deal.date_start, date_end=deal.date_end,
                             date_before=deal.date_before, deal_type=deal.deal_type,
                             user_added_id=deal.user_added_id)  # Add user_added_id
        session.add(new_deal)
        session.commit()
        return True

    @staticmethod
    def deal_update(deal: Deal):
        existing_deal = session.query(DealModel).filter_by(deal_id=deal.deal_id).first()

        if existing_deal:
            existing_deal.unsorted_deal_id = deal.unsorted_deal_id
            existing_deal.date_start = deal.date_start
            existing_deal.date_end = deal.date_end
            existing_deal.date_before = deal.date_before
            existing_deal.deal_type = deal.deal_type
            existing_deal.user_added_id = deal.user_added_id  # Update user_added_id

            session.commit()
            return True
        else:
            return False

    @staticmethod
    def delete_deal(deal):
        return DealDB.delete_deal_by_id(deal.deal_id)

    @staticmethod
    def delete_deal_by_id(deal_id: int):
        session.query(DealModel).filter_by(deal_id=deal_id).delete()
        session.commit()
        return True

    @staticmethod
    def get_all_deals():
        return session.query(DealModel).all()

    @staticmethod
    def find_deals_by_user(telegram_id: int) -> [DealModel]:
        raw = session.query(DealModel).filter_by(user_added_id=telegram_id).all()
        return raw

    @staticmethod
    def find_deals_by_user_and_type(unsorted_deal_id: int, deal_type: str) -> [DealModel]:
        raw = session.query(DealModel).filter_by(unsorted_deal_id=unsorted_deal_id, deal_type=deal_type).all()
        return raw

    @staticmethod
    def find_deal_by_id(deal_id: int):
        deal = session.query(DealModel).filter_by(deal_id=deal_id).first()
        return deal
