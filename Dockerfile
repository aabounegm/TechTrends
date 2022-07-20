FROM python:3.8-slim-buster

WORKDIR /app

COPY techtrends/requirements.txt ./

RUN pip install -r requirements.txt

ADD techtrends ./

RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]
