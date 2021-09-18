#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

OPER, PHOTO, LOCATION, BIO, REGISTR = range(5)


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['Registrazione', 'Nuova Segnalazione', 'Modifica Segnalazione', 'Controlla Stato Segnalazione']]

    update.message.reply_text(
        'Ciao sono un Bot di Prova. Proverò ad avere una conversazione con te chiedendoti alcune domande per completare la tua segnalazione. '
        'Scrivi /cancel per interrompere la chiaccherata.\n\n'
        'Che operazione vorresti effettuare?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Selezione un operazione'
        ),
    )

    return OPER


def oper(update: Update, context: CallbackContext) -> int:
    """Stores the selected oper an goes to next question."""
    user = update.message.from_user
    logger.info("Operation of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Capisco! Se ti va mandami una foto da allegare alla segnalazione, '
        'se per caso non ti va scrivi /skip e proseguiamo.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO
    
def oper2(update: Update, context: CallbackContext) -> int:
    """Stores the selected oper an goes to next question."""
    user = update.message.from_user
    logger.info("Operation of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Questa operazione NON è stata ancora implementata, '
        ' CONVERSAZIONE INTERROTTA ',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END

def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    x = ".jpg"
    z = user.first_name + x
    photo_file.download(z)
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Che bella foto! ora, mandami la tua posizione se puoi, o scrivi /skip se non vuoi farlo.'
    )

    return LOCATION


def skip_photo(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Scommetto che comunque stai benissimo! ora, mandami la tua posizione se puoi, o scrivi /skip se non vuoi farlo.'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Scommetto che è un posto da visitare! Per ultima cosa , dimmi qualcosa di te stessa/o.'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'Mamma mia non andare in paranoia! Almeno dimmi qualcosa di te stessa/o.'
    )

    return BIO


def bio(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Grazie! Spero che potremo parlare ancora in futuro.')

    return ConversationHandler.END

def registr(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('REGISTRAZIONE DA IMPLEMENTARE, alla prossima.')

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Ciao ciao! Spero che potremo parlare ancora in futuro.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1830820258:AAFqOmVTWe5YFnKDosW8ihA6SmRk8J0UWGY")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            OPER: [
                MessageHandler(Filters.regex('^(Nuova Segnalazione)$'), oper),
                MessageHandler(Filters.regex('^(Modifica Segnalazione)$'), oper2),
                MessageHandler(Filters.regex('^(Registrazione)$'), registr),
                MessageHandler(Filters.text & ~Filters.command, oper2),
            ],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
             # Sessione in sviluppo
            REGISTR: [MessageHandler(Filters.text & ~Filters.command, registr)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()