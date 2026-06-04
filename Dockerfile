FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.py

EXPOSE 8080

ENTRYPOINT ["python", "entrypoint.py"]
