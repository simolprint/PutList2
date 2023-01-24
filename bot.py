from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, Updater, MessageHandler, filters
import datetime
from geopy.geocoders import Nominatim
from telegram import KeyboardButton

# Define the token for your bot
TOKEN = "5904394121:AAH7nygF6KE_zFsmz0Ac1EAhefSUwHMg7-8"

# Define the function to get the address
async def get_address(location):
    geolocator = Nominatim(user_agent="myGeocoder")
    lat, lon = location.latitude, location.longitude
    address = geolocator.reverse("{}, {}".format(lat, lon), timeout=10)
    return address.address

time_pressed = False
arrival_pressed = False

odometer_reading = None

async def handle_odometer(update, context):
    global odometer_reading
    odometer_reading = update.message.text
    await context.bot.send_message(chat_id=update.message.chat_id, text="Спасибо, теперь делитесь локацией", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="Share location", request_location=True)]]))

async def callback_time(update, context):
    global time_pressed
    time_pressed = True
    query = update.callback_query
    query.answer()
    await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Пожалуйста ведите пробег")

async def callback_arrival(update, context):
    global arrival_pressed
    arrival_pressed = True
    query = update.callback_query
    query.answer()
    await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Пожалуйста ведите пробег")

async def handle_location(update, context):
    location = update.message.location
    if location is None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Локация не указано")
    else:
        global time_pressed, arrival_pressed, odometer_reading
        if time_pressed:
            current_time = datetime.datetime.now().strftime("%m-%d    %H:%M")
            address = await get_address(location)
            message = "При выезде:   " + current_time + "\n\nАдрес: " + address + "\n\nПробег: " + odometer_reading
            await context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=reply_markup)
            time_pressed = False
            odometer_reading = None
        elif arrival_pressed:
            current_time = datetime.datetime.now().strftime("%m-%d    %H:%M")
            address = await get_address(location)
            message = "По прибытии:   " + current_time + "\n\nАдрес: " + address + "\n\nПробег: " + odometer_reading
            await context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=reply_markup)
            arrival_pressed = False
            odometer_reading = None

button = InlineKeyboardButton("Выехал", callback_data="time")
arrival_button = InlineKeyboardButton("Прибыл", callback_data="arrival")

# Create a keyboard with the button
keyboard = [[button, arrival_button]]
reply_markup = InlineKeyboardMarkup(keyboard)

async def start(update, context):
   await context.bot.send_message(chat_id=update.effective_chat.id, text="Ты Выехал или Прибыл?", reply_markup=reply_markup)

# Create the Application and pass it your bot's token.
application = Application.builder().token(TOKEN).build()


# Register the command and callback handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(callback_time, pattern='time'))
application.add_handler(CallbackQueryHandler(callback_arrival, pattern='arrival'))
application.add_handler(MessageHandler(filters.LOCATION, handle_location))
application.add_handler(MessageHandler(filters.TEXT, handle_odometer))

# Run the bot until the user presses Ctrl-C
application.run_polling()