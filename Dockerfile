FROM python:3.13-alpine
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN apk del .build-deps

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]