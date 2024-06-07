import telebot
from pytube import YouTube
import os
import requests
import re
import subprocess

file = open("key", "r") 
key = file.read()
file.close()

bot = telebot.TeleBot(key)

def markup_typo(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    video = telebot.types.InlineKeyboardButton("Video", callback_data="video")
    audio = telebot.types.InlineKeyboardButton("Audio", callback_data="audio")
    markup.add(video, audio)
    bot.send_message(message.chat.id, "Seleziona la tipologia:", reply_markup=markup)
    return markup

def markup_format(message,typo):

    # video
    mp4 = telebot.types.InlineKeyboardButton(".mp4", callback_data="mp4")
    mov = telebot.types.InlineKeyboardButton(".mov", callback_data="mov")

    #audio  
    mp3 = telebot.types.InlineKeyboardButton(".mp3", callback_data="mp3")
    wav = telebot.types.InlineKeyboardButton(".wav", callback_data="wav")
    webm = telebot.types.InlineKeyboardButton(".webm", callback_data="webm")

    #error
    error = telebot.types.InlineKeyboardButton("Errore", callback_data="errore")

    if typo == "video":
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(mp4, mov)
    elif typo == "audio":
        markup = telebot.types.InlineKeyboardMarkup(row_width=3)
        markup.add(mp3,wav,webm)
    else:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(error)

    bot.send_message(message.chat.id, "Seleziona il formato:", reply_markup=markup)
    return markup

# comandi

@bot.message_handler(commands=['bersanella'])
def you(message):
    bot.send_message(message.chat.id, 'La donna piú bella!')

@bot.message_handler(commands=['mov'])
def you(message):
    bot.send_message(message.chat.id, 'File troppo grandi :(((')
    
# inizio

@bot.message_handler(func=lambda message: True)
def default_reply(message):
    if check_video_url(message):
        process_url(message)
    elif message.text != "/start":
        bot.send_message(message.chat.id, 'Link non valido.')   

def check_video_url(message):

    video_url = message.text
    
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, video_url)
    if youtube_regex_match:
        request = requests.get(video_url)
        return request.status_code == 200
    else:
        return False

def process_url(message):
    global url
    url = message.text
    print(url)
    markup_typo(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_data(call):
    if call.message:
        # typo
        if call.data == "video":
            markup_format(call.message,"video")
        elif call.data == "audio":
            markup_format(call.message,"audio")
        # video
        elif call.data == "mp4":
            download_video(call.message, 'mp4')
        elif call.data == "mov":
            download_video(call.message, 'mov')
        # audio
        elif call.data == "mp3":
            download_audio(call.message, 'mp3')
        elif call.data == "wav":
            download_audio(call.message, 'wav')
        elif call.data == "webm":
            download_audio(call.message, 'webm')

def download_video(message,format):

    yt = YouTube(url)
    video_title = yt.title
    bot.send_message(message.chat.id, f"Download in corso: {video_title} | Formato: {format} ...")
    
    stream = yt.streams.filter(mime_type="video/mp4",progressive=True).get_highest_resolution()
    
    if stream:
        stream.download()

        if format == "mp4":
            sendVideo(message,stream.default_filename,stream.title)
        elif format == "mov":
            mov_path = stream.default_filename.replace(".mp4", ".mov")

            mp4_path_ffmpeg = "\""+stream.default_filename+"\""
            mov_path_ffmpeg = "\""+mov_path+"\""

            os.system(f"ffmpeg -i {mp4_path_ffmpeg} -vcodec mjpeg -q:v 2 -acodec pcm_s16be -q:a 0 -f mov {mov_path_ffmpeg}")

            os.remove(stream.default_filename)
            sendVideo(message,mov_path,stream.title)
        else:
            bot.send_message(message.chat.id,"Formato non esistente")
            print("Formato errato!");
        
    else:
        bot.send_message(message.chat.id, "Nessun video trovato")

def sendVideo(message,file,title):
    with open(file, 'rb') as video:
        bot.send_video(message.chat.id, video, caption=f"Download completato: {title}")
    os.remove(file)

def download_audio(message,format):

    yt = YouTube(url)
    video_title = yt.title
    bot.send_message(message.chat.id, f"Download in corso: {video_title} | Formato: {format} ...")
    
    stream = yt.streams.filter(only_audio=True,mime_type="audio/webm").first()
    
    if stream:
        
        stream.download()
        
        if format == "webm":
            sendAudio(message,stream.default_filename,stream.title)
        elif format == "mp3":
            mp3_path = stream.default_filename.replace(".webm", ".mp3")

            webm_path_ffmpeg = "\""+stream.default_filename+"\""
            mp3_path_ffmpeg = "\""+mp3_path+"\""

            os.system(f"ffmpeg -i {webm_path_ffmpeg} {mp3_path_ffmpeg}")

            os.remove(stream.default_filename)
            sendAudio(message,mp3_path,stream.title)
        elif format == "wav":
            wav_path = stream.default_filename.replace(".webm", ".wav")

            webm_path_ffmpeg = "\""+stream.default_filename+"\""
            wav_path_ffmpeg = "\""+wav_path+"\""

            os.system(f"ffmpeg -i {webm_path_ffmpeg} {wav_path_ffmpeg}")

            os.remove(stream.default_filename)
            sendAudio(message,wav_path,stream.title)
        else:
            bot.send_message(message.chat.id,"Formato non esistente")
            print("Formato errato!");
    else:
        bot.send_message(message.chat.id, "Nessun video trovato")
        
def sendAudio(message,file,title):
    with open(file, 'rb') as audio:
        bot.send_audio(message.chat.id, audio, caption=f"Download completato: {title}")
    os.remove(file)

bot.polling()
