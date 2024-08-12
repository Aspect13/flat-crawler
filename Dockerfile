FROM python:3.12-alpine
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN apk del .build-deps

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]