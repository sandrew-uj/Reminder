FROM python:3.9

RUN apt update -y

ADD ./ /backend-bot/

WORKDIR /backend-bot

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app",  "--host", "0.0.0.0", "--port", "8000"]