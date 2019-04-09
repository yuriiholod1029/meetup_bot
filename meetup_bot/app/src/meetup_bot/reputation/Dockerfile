FROM python:3-alpine

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../../../.. /app

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["app.py"]
