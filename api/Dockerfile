FROM python:3.7-stretch
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
