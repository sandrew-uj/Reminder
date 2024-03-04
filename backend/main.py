from typing import List

from fastapi import FastAPI, HTTPException

from endpoints.Deals import app_deal
from endpoints.Reminds import app_remind
from endpoints.Unsorted import app_unsorted
from endpoints.Users import app_user

app = FastAPI(
    title="reminder"
)

app.mount("/remind/", app_remind)
app.mount("/user/", app_user)
app.mount("/deal/", app_deal)
app.mount("/unsorted/", app_unsorted)
