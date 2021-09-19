#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.
import flask
from convbot5 import location
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import requests
import base64
import logging

from flask import Flask
from flask import send_from_directory
app = Flask(__name__)



#Botpress API URL
botpress_url = "https://tranquil-ridge-44045.herokuapp.com/api/v1/bots/report-handling/converse/"

#Configura il logger (poi in realtà non lo uso lmao)
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger("botpress_middleman")

@app.route('/handle_message')
#Inoltra a Botpress il messaggio dell' utente e gestisce la risposta
def handle_message(update, context):
    result = forward(update, context)
    chat_id = update.effective_chat.id
    
    for response in result["responses"]:
        #type == custom significa che si tratta di un nodo scelta
        if response["type"] == "custom":
            keyboard = []
            #quick_replies contiene tutte le opzioni tra cui l' utente può scegliere
            for reply in response["quick_replies"]:
                keyboard.append([KeyboardButton(reply["title"])])

            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True)
            context.bot.send_message(chat_id = chat_id,
                                     text = response["wrapped"]["text"],
                                     reply_markup = reply_markup)

        #type == text significa che si tratta di un semplice messaggio di testo
        if response["type"] == "text":
            context.bot.send_message(chat_id = chat_id,
                                     text = response["text"])

@app.route('/forward', methods=['GET', 'POST', 'PUT'])
#Inoltra a Botpress il messaggio dell' utente
def forward(update, context):
    text = update.message.text #None se il messaggio non è solo testo
    photos = update.message.photo #None se il messaggio non è una foto
    location = update.message.location #None se il messaggio non è una posizione

    user_id = update.message.from_user.id #Id dell' utente che ha inviato il messaggio (necessario per autenticazione)

    #Costruisco opportunamente il payload in base al tipo di messaggio mandato dall' utente
    if(text):
        payload = {"type":"text", "text":"{0}".format(update.message.text)}
    elif(photos):
        photo_id = photos[-1].file_id
        file = context.bot.get_file(photo_id)
        payload = {"type":"text", "text":"[PHOTO]{0}".format(file["file_path"])}
    elif(location):
        payload = {"type":"text", "text":"[COORDS]{0}|{1}".format(location["longitude"], location["latitude"])}

    return requests.post(botpress_url + str(user_id), payload).json() #Invio il messaggio a Botpress e restituisco la risposta

@app.route('/')
@app.route('/main')    
def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1830820258:AAFqOmVTWe5YFnKDosW8ihA6SmRk8J0UWGY")
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    forward_handler = MessageHandler(Filters.all, handle_message)
    dispatcher.add_handler(forward_handler)
    
    updater.start_polling()
    updater.idle() #Almeno non si chiude di colpo quando fai ctrl-c
    
if __name__ == '__main__':
    main()