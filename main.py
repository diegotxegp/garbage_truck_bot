#!/usr/bin/python3

'''
garbagetruckbot.py
Telegram bot which makes typical noises from a garbage truck when collecting garbage at night.

Author: @diegotxegp - diegotxegp(at)outlook.com
'''

import sys
import os
import logging
from time import sleep
from datetime import datetime, date, time
from pytz import timezone
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from random import randint, choice
import threading

start_description = "Garbage truck which makes noises when collecting garbage at night.\nType /help to show all the commands\n\n Author: @diegotxe\t -\t https://github.com/diegotxegp"
command_description = "Commands:\n - /start for initial message\n - /vroom to start garbage truck\n - /no_vroom to stop garbage truck\n - /help to show this help description again"
truck_noise = "Vroom, vroom... psss... rrrrrr... pum... pum... gggg... pssssss... vroom, vroooom, vrooooooooom...\n\nhttps://www.youtube.com/watch?v=alzDsaSYfig"
id_array = [] # Array with the chat_ids of all the chats open to send message

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load enviroment variables
load_dotenv("keys.env")
bot_token = str(os.getenv("TELEGRAM_BOT"))
chat_id = int(os.getenv("CHAT_ID"))
bot = Bot(token=bot_token)

# Initial description
def start(update: Update, context: CallbackContext):
    logging.info("Message start")
    update.message.reply_text(start_description)

# Help description
def help(update: Update, context: CallbackContext):
    logging.info("Help description")
    update.message.reply_text(command_description)

'''
# Select a certain time to collect rubish ("HH:MM:SS")
def schedule(update: Update, context: CallbackContext):
    truck_time = int(context.args[0])
    context.bot.send_message(chat_id=update.effective_chat.id, text=truck_time)
'''

def random_next_time():
    h = choice([0,23])
    m = randint(0,59)
    next_time = time(h, m, 00, 000000)

    logging.info("Next time set at %i:%i",h,m)
    return next_time

def next_sleep(next_time):
    madrid_time = timezone('Europe/Madrid')
    now = datetime.now(madrid_time).time()
    date_one = date(1, 1, 1)
    datetime1 = datetime.combine(date_one, next_time)
    datetime2 = datetime.combine(date_one, now)
    time_elapsed = datetime1 - datetime2
    sleep_time = time_elapsed.total_seconds()

    if sleep_time < 0:
        sleep_time = sleep_time + 86400.0

    logging.info("Sleep time %i", sleep_time)
    return sleep_time

# Makes gargabe truck noises at night
def vroom(update:Update, context: CallbackContext):

    chat_id = update.message.chat.id

    def thread1(update:Update, context: CallbackContext):

        logging.info("chat_id added to array")
        id_array.append(chat_id)

        logging.info("Calculating next time to sound")
        next_time = random_next_time()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ok. Garbage truck working")
        sleep_time = next_sleep(next_time)

        while chat_id in id_array:
            try:
                logging.info("Sleeping for %i seconds", sleep_time)
                sleep(sleep_time)
                logging.info("%s", truck_noise)
                bot.send_message(chat_id=update.effective_chat.id, text=truck_noise)
                sleep(7200)
                next_time = random_next_time()
                sleep_time = next_sleep(next_time)
                
            except Exception:
                logging.info("Bot interrupted")
                sys.exit(0)

    if chat_id not in id_array:
        t1 = threading.Thread(target=thread1, args=(update,context))
        logging.info("Thread started")
        t1.start()
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No effect. Garbage truck was already working before")

# Stops noise
def no_vroom(update: Update, context: CallbackContext):

    chat_id = update.message.chat.id

    if chat_id in id_array:
        logging.info("Cancelling vroom")
        id_array.remove(chat_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Garbage truck stopped working")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Garbage truck wasn't working")

# Echos non-commands
def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    print(update.message)

# Hola Rocio (Easter egg)
def rocio(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola Rocío!")

# Alejandro (Easter egg)
def alejandro(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="¡Mira qué pollón tengo!")

# Message asking for an understable command
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def main():
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    logging.info("Command Start")
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    logging.info("Command Help")
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    logging.info("Command Vroom")
    vroom_handler = CommandHandler('vroom', vroom)
    dispatcher.add_handler(vroom_handler)

    logging.info("Command No_vroom")
    no_vroom_handler = CommandHandler('no_vroom', no_vroom)
    dispatcher.add_handler(no_vroom_handler)

    '''
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    '''

    logging.info("Command Rocio (Easter egg")
    rocio_handler = CommandHandler('rocio', rocio)
    dispatcher.add_handler(rocio_handler)

    logging.info("Command Alejandro (Easter egg")
    alejandro_handler = CommandHandler('alejandro', alejandro)
    dispatcher.add_handler(alejandro_handler)

    logging.info("Unknown command")
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # Start the service
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()