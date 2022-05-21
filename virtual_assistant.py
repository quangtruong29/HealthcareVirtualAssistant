import json
import threading
from pprint import pprint
from tkinter import *

import geocoder
import speech_recognition as sr
import webbrowser
import playsound
import os
import random

from geopy import Nominatim
from gtts import gTTS
import pyttsx3
from datetime import datetime, time

import sensor
from requests_html import HTMLSession
import requests
import pyjokes
import time
import ui

recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # voices[0]: male voice, voices[1]: female voice


def record_audio(ask=False):
    with sr.Microphone() as source:
        if ask:
            speak(ask)
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)  # lúc đang nghe thì tất cả các luồng sẽ dừng
        try:
            voice_data = recognizer.recognize_google(audio, language="en-US")
        except sr.UnknownValueError:
            speak("Sorry, I did not get that.")
            raise sr.UnknownValueError
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            raise sr.RequestError
        return voice_data


def respond(voice_data):
    voice_data = voice_data.lower()
    print(voice_data)
    if "what is your name" in voice_data or "your name" in voice_data:
        ui.name_button.place(relx=0.5, rely=0.0, y=50, anchor=N)
        ui.name_label = Label(ui.window, text=f"My name is Zira", font=("Roboto", 18), padx=10)
        ui.name_label.place(relx=0.5, rely=0.0, anchor=N, y=120)

        speak("My name is Zira")
    elif "what time is it" in voice_data or "what is the time" in voice_data:
        ui.time_button.place(relx=0.5, rely=0.0, y=50, anchor=N)
        ui.name_label = Label(ui.window, text=f"{datetime.now().strftime('%H:%M')}", font=("Roboto", 18), padx=10)
        ui.name_label.place(relx=0.5, rely=0.0, anchor=N, y=120)

        speak(datetime.now().strftime('%H:%M'))
    elif "search" in voice_data:
        search = record_audio("What do you want to search for?")
        url = "https://google.com/search?q=" + search
        webbrowser.get().open(url)
        speak("Here is what I found for " + search)

    elif "find location" in voice_data:
        location = record_audio("What is the location?")
        url = "https://google.nl/maps/place/" + location + "/&amp;"
        webbrowser.get().open(url)
        speak("Here is the location of " + location)

    elif "weather" in voice_data:
        weather()

    elif "heart rate" in voice_data:  # display heart rate of user
        arduino_data = sensor.init_sensor()
        if arduino_data is None:
            speak("This function is not available!")
        else:
            speak("Place your index finger on the sensor with steady pressure.")
            # sensor.measure(arduino_data)
            sensor.measure_max30100(arduino_data)

    elif "temperature" in voice_data:
        sensor.read_temperature()
        pass

    elif "where am i" in voice_data:
        my_location()

    elif "bmi" in voice_data:  # calculate BMI index
        h = record_audio("Please tell me your height")
        w = record_audio("Please tell me your weight")
        height = float(h)
        weight = float(w)
        bmi(height, weight)

    elif "hospital" in voice_data:  # search for hospital nearby
        url = "https://google.com/search?q=hospital-near-me"
        webbrowser.get().open(url)
        speak("I found a few hospitals near you.")

    elif "joke" in voice_data:  # tell s stupid joke
        my_joke = pyjokes.get_joke(language='en', category='all')
        speak(my_joke)

    elif "set alarm" in voice_data:  # set alarm
        time = record_audio("what is the time")


    else:
        speak("Sorry, I'm not able to help with this one.")


def set_alarm(time):
    speak("hello")


def covid_track():
    speak("total case in vietnam is 19000")


def get_address_by_location(latitude, longitude, language="en"):
    app = Nominatim(user_agent="GetLoc")
    """This function returns an address as raw from a location
    will repeat until success"""
    # build coordinates string to pass to reverse() function
    coordinates = f"{latitude}, {longitude}"
    # sleep for a second to respect Usage Policy
    time.sleep(1)
    try:
        return app.reverse(coordinates, language=language).raw
    except:
        return get_address_by_location(latitude, longitude)


def foo():
    key = "YepjuJR2pvYEQrdcXihIvIHOiYWhFFUQ"
    send_url = f"http://api.ipstack.com/check?access_key={key}"
    print(send_url)
    geo_req = requests.get(send_url)
    geo_json = json.loads(geo_req.text)
    latitude = geo_json['latitude']
    longitude = geo_json['longitude']
    city = geo_json['city']
    print(city)


def my_location():
    # loc = Nominatim(user_agent="GetLoc")

    # entering the location name
    # getLoc = loc.geocode("Ho Chi Minh city")
    # geolocator = Nominatim(user_agent="My App")
    latlng = geocoder.ip('me').latlng
    lat = latlng[0]
    lng = latlng[1]

    # print(latlng)
    data = get_address_by_location(lat, lng)
    pprint(data)
    country = data['address']['country']
    road = data['address']['road']
    suburb = data['address']['suburb']
    town = data['address']['town']
    display_name = data['display_name']
    city = display_name.split(",")[3]

    ui.location_button.place(relx=0.5, rely=0.0, y=50, anchor=N)
    ui.location_label = Label(ui.window, text=f"{display_name}", font=("Roboto", 14), padx=10,
                              wraplength=300, justify="center")
    ui.location_label.place(relx=0.5, rely=0.0, anchor=N, y=150)
    speak("Here's your location")


def weather_scrapping():
    s = HTMLSession()
    query = 'Ho Chi Minh city'
    url = f'https://www.google.com/search?q=weather+{query}'

    r = s.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})

    temp = r.html.find('span#wob_tm', first=True).text
    unit = r.html.find('div.vk_bk.wob-unit span.wob_t', first=True).text
    desc = r.html.find('div.VQF4g', first=True).find('span#wob_dc', first=True).text
    speak(f"The temperature today in {query} is " + temp + " degree celsius")


def weather():
    city = "ho+chi+minh"
    api_key = "832cbe9f134fd35f927eada6c19acf17"
    api = f" http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    json_data = requests.get(api).json()
    city_name = json_data["name"]
    country_name = json_data['sys']['country']
    condition = json_data['weather'][0]['main']
    temp = int(json_data['main']['temp'] - 273.15)
    temp_f = int(json_data['main']['temp'] * 9 / 5 - 459.67)
    min_temp = int(json_data['main']['temp_min'] - 273.15)
    max_temp = int(json_data['main']['temp_max'] - 273.15)
    pressure = json_data['main']['pressure']
    humidity = json_data['main']['humidity']
    wind = int(json_data['wind']['speed'] * 3.6)
    description = json_data['weather'][0]['description']

    # sunrise = time.strftime("%I:%M:%S", time.gmtime(json_data['sys']['sunrise'] - 25200))
    # sunset = time.strftime("%I:%M:%S", time.gmtime(json_data['sys']['sunset'] - 25200))

    final_info = condition + "\n" + str(temp) + "℃"
    final_data = "\n" + "Max Temp: " + str(max_temp) + "\n" + "Min Temp: " + str(min_temp) + "\n" + "Pressure: " + str(
        pressure) + "\n" + "Humidity: " + str(humidity) + "\n"

    print(final_data)
    print(final_info)
    speak("Here's the weather right now")

    ui.city_name_label = Label(ui.window, text=f"{city_name}, {country_name}", font=("Roboto", 18), padx=10)
    ui.temperature_label = Label(ui.window, text=f"{temp} ℃ | {temp_f} °F", font=("Roboto", 16), padx=10)
    ui.weather_label = Label(ui.window, text=f"{condition}, {description}", font=("Roboto Light", 12), padx=10)
    # ui.description_label = Label(ui.window, text=f"", font=("Roboto", 12), padx=10)
    ui.humidity_label = Label(ui.window, text=f"Humidity: {humidity} %", font=("Roboto", 14), padx=10)
    ui.wind_label = Label(ui.window, text=f"Wind: {wind} km/h", font=("Roboto", 14), padx=10)

    ui.sun_button.place(relx=0.5, rely=0.0, y=50, anchor=N)
    ui.city_name_label.place(relx=0.5, rely=0.0, anchor=N, y=120)
    ui.temperature_label.place(relx=0.5, rely=0.0, anchor=N, y=160)
    ui.weather_label.place(relx=0.5, rely=0.0, anchor=N, y=195)
    # ui.description_label.place(relx=0.5, rely=0.0, anchor=N, y=140)
    ui.humidity_label.place(relx=0.5, rely=0.0, anchor=N, y=225)
    ui.wind_label.place(relx=0.5, rely=0.0, anchor=N, y=255)


def speak_thread(audio_string):
    print(audio_string)
    engine.say(audio_string)
    engine.runAndWait()


def speak(audio_string):
    # use gtts
    # tts = gTTS(text=audio_string, lang="en")
    # rand = random.randint(1, 10000000)
    # audio_file = "audio-" + str(rand) + ".mp3"
    # tts.save(audio_file)
    # playsound.playsound(audio_file)
    # print(audio_string)
    # os.remove(audio_file)

    # os.remove(audio_file) is not working so I use pyttsx3 instead
    threading.Thread(target=speak_thread(audio_string), daemon=True).start()


def introduce():
    playsound.playsound('sound/cortana_sound_effect.mp3')
    speak("Hi, I'm your healthcare virtual assistant. What can I do for you?")


def bmi(height, weight):
    result = weight / (height * height)
    if result < 16:
        speak('You are Severe thinness')
    elif result >= 16 & result < 17:
        speak('You are moderate thinness ')
    elif result >= 17 & result < 18.5:
        speak('You are thin')
    elif result >= 18.5 & result < 25:
        speak('You are normal')
    elif result >= 25 & result < 30:
        speak('You are overweight')
    elif result >= 30 & result < 35:
        speak('You are Obese type 1')
    elif result >= 35 & result < 40:
        speak('You are Obese type 2')
    else:
        speak('You are Obese type 3')


if __name__ == "__main__":  # chỉ chạy các chức năng có trong file sensor và không chạy trong các file khác
    # weather()
    # foo()
    my_location()
