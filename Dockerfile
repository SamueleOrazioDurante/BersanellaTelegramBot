FROM python:3.10.12
WORKDIR /usr/src/app
COPY . .
RUN mkdir ./images
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install telebot pytube
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg
CMD ["python", "-u", "./bot.py"]
