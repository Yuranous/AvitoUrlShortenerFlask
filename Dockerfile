FROM python:3.6.5-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV STATIC_URL /static/
ENV STATIC_PATH /app/static
ENV FLASK_ENV development
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run"]