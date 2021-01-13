# Performing the necessary imports 
import re
import requests
from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name,URL 
from time import sleep

global bot
global TOKEN #from BotFather
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

# start the flask app
app = Flask(__name__)

#Function to access API 
def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

#RandomDog API generates videos and GIFs as well. This will result in an error and the bot won't send anything. To handle this, 
#we use regex to match the extension and call the API again if video/GIF is received. 
def get_image_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url


#Bind function to route - telling flask what to do when a URL is called
#This is the URL Tele will call to get responses 
@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id

   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()
   # for debugging purposes only
   print("got text message :", text)
   # the first time you chat with the bot AKA the welcoming message
   if text == "/start":
       # print the welcoming message
       bot_welcome = """
       Welcome to DoggoBot, this bot brightens your day by showing you 
       a cute dog! Send any message to see a doggo.
       """
       #show 'typing' under bot name
       bot.sendChatAction(chat_id=chat_id, action="typing")
       sleep(1.5)
       # send the welcoming message
       bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)


   else:
       try:
           # clear the message we got from any non alphabets
           text = re.sub(r"W", "_", text)
           # create the api link for the avatar based on
           photo_url = get_image_url()
           #show 'sending photo' under bot name 
           bot.sendChatAction(chat_id=chat_id, action="upload_photo")
           sleep(2)
           # reply with a photo to the name the user sent,
           # note that you can send photos by url and telegram will fetch it for you
           bot.sendPhoto(chat_id=chat_id, photo=photo_url, reply_to_message_id=msg_id)
       except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="There was a problem, please try again.", reply_to_message_id=msg_id)

   return 'ok'

#Webhooks help alter the behaviour of webpages using custom callbacks. So the server is called by webhook only when the bot receoves a message.
@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'
if __name__ == '__main__':
    # note the threaded arg which allow
    # your app to have more than one thread
    app.run(threaded=True)