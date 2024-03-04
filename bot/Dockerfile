FROM python:3.9

RUN apt update -y

ADD ./ /bot/

WORKDIR /bot

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "app.py"]