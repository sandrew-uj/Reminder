from fastapi import FastAPI, HTTPException

from models.Deal import DealDB
from models.Timezone import get_timezone, Timezone
from models.User import find_user, User, get_all_users

app_user = FastAPI(
    title="backend_users"
)


@app_user.get('/{telegram_id}/reminds')
async def list_reminds(telegram_id: int):
    user = find_user(telegram_id)
    if user is not None:
        a = user.find_reminds()
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return a


@app_user.get('/{telegram_id}/reminds/{remind_type}')
async def list_reminds_by_type(telegram_id: int, remind_type: str):
    user = find_user(telegram_id)
    if user is not None:
        a = user.find_reminds_by_type(remind_type)
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return a


@app_user.get('/{telegram_id}/min_remind')
async def get_min_remind(telegram_id: int):
    user = find_user(telegram_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user.get_min_remind()


@app_user.get('/{telegram_id}/tz')
async def get_tz(telegram_id: int):
    timezone = get_timezone(telegram_id)
    if timezone is None:
        timezone = Timezone(telegram_id=telegram_id, tz=3)
        timezone.add()
    return timezone.tz


@app_user.get('/{telegram_id}/update_tz/{tz}')
async def update_tz(telegram_id: int, tz: int):
    timezone = get_timezone(telegram_id)
    if timezone is None:
        timezone = Timezone(telegram_id=telegram_id, tz=tz)
        return timezone.add()
    timezone.tz = tz

    return timezone.update()


@app_user.get('/{telegram_id}/reminds/count')
async def count_reminds(telegram_id: int) -> int:
    user = find_user(telegram_id)
    if user is not None:
        a = user.find_reminds()
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return len(a)


@app_user.post('/')
async def add_user(user: User) -> bool:
    if not user.add_user():
        raise HTTPException(status_code=500, detail="error")
    return True


@app_user.get('/{telegram_id}')
async def exists(telegram_id: int) -> bool:
    return find_user(telegram_id) is not None


# get all users
@app_user.get('/users/all')
async def all_users():
    a = get_all_users()
    return a


# Route to list deals by type for a user
@app_user.get('/{telegram_id}/deals/{deal_type}')
async def list_deals_by_type(telegram_id: int, deal_type: str):
    deals = DealDB.find_deals_by_user_and_type(telegram_id, deal_type)
    if not deals:
        raise HTTPException(status_code=404, detail="User not found")
    return deals


# Route to get the minimum deal for a user
@app_user.get('/{telegram_id}/min_deal')
async def get_min_deal(telegram_id: int):
    user_deals = DealDB.find_deals_by_user(telegram_id)
    if not user_deals:
        raise HTTPException(status_code=404, detail="User not found")

    min_deal = min(user_deals, key=lambda x: x.date_start, default=None)

    if min_deal:
        return min_deal
    else:
        raise HTTPException(status_code=404, detail="No deals found for the user")


@app_user.get('/{telegram_id}/unsorted')
async def list_unsorted(telegram_id: int):
    user = find_user(telegram_id)
    if user is not None:
        a = user.find_unsorted()
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return a