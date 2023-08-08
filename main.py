# подключаем модуль для Телеграма
import os

import telebot
import config
import requests
import speech_recognition as sr
from moviepy.editor import VideoFileClip

# указываем токен для доступа к боту
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(content_types=['video_note'])
def circle(message):
    file_info = bot.get_file(message.video_note.file_id)
    file_path = file_info.file_path

    # Сохранение видео на сервере
    video_url = f'https://api.telegram.org/file/bot{config.TOKEN}/{file_path}'
    video_name = f'video_{message.from_user.id}_{message.message_id}.mp4'

    response = requests.get(video_url)
    if response.status_code == 200:
        with open(video_name, 'wb') as video_file:
            video_file.write(response.content)

    # Извлечение аудио из видео
    audio_name = f'audio_{message.from_user.id}_{message.message_id}.wav'
    video_clip = VideoFileClip(video_name)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_name)

    # Закрытие видео и аудио ресурсов
    audio_clip.close()
    video_clip.close()

    # Распознавание речи
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_name) as source:
        audio = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio, language='ru')
            bot.send_message(message.from_user.id, f"{recognized_text}")
        except sr.UnknownValueError:
            bot.send_message(message.from_user.id, "Не смог распознать!")
        except sr.RequestError as e:
            bot.send_message(message.from_user.id, f"Ошибка: {e}")

    # Удаление временных файлов
    os.remove(video_name)
    os.remove(audio_name)



# запускаем бота
if __name__ == '__main__':
    while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            bot.polling(none_stop=True, interval=0)
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e:
            print('❌❌❌❌❌ Сработало исключение! ❌❌❌❌❌')
            print(e)
