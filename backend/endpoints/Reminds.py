from fastapi import FastAPI, HTTPException

from models.Remind import Remind, find_remind_by_id, delete_by_id

app_remind = FastAPI(
    title="backend_reminds"
)


@app_remind.post('/')
async def add_remind(remind: Remind) -> bool:
    # print(remind)
    return remind.add_remind()


@app_remind.get('/get/{remind_id}')
async def get_remind(remind_id: int):
    remind = find_remind_by_id(remind_id=remind_id)
    if remind is None:
        raise HTTPException(status_code=404, detail="Remind not found")

    return remind


@app_remind.post('/delete')
async def delete_remind(remind: Remind) -> bool:
    print(remind)
    return remind.delete_remind()


@app_remind.get('/delete/{remind_id}')
async def delete_remind_by_id(remind_id: int):
    # print(remind)
    delete_by_id(remind_id)


@app_remind.post('/update')
async def update_remind(remind: Remind):
    print(remind)
    return remind.update_remind()
