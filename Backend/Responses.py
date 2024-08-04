import re

from telegram import Update
from telegram.ext import CallbackContext

from Backend import config




# async def handle_message(update: Update, context: CallbackContext):
#     message_type: str = update.message.chat.type
#     text: str = update.message.text
#     print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
#
#     if message_type == 'group':
#         if config.BOT_USERNAME in text:
#             new_text = str = text.replace(config.BOT_USERNAME, '').strip()
#             response = handle_response(new_text)
#         else:
#             return
#     else:
#         response = handle_response(text)
#     print('Bot: ', response)
#     await update.message.reply_text(response)
        
    
    

def responses(input_text):
    user_message = str(input_text).lower()

    msg = user_message.split()
    return user_message

def get_price(input_text):
    msg = input_text.split()
    for s in msg:
        if s.isnumeric():
            return s

def get_category(input_text):
    msg = input_text.split()
    for s in msg:
        if not s.isnumeric():
            return s

def valid_email(email):
    if len(email) > 7:
        if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) != None:
            return True
        

help_response = "Initial setup\nAdd the bot to a group and then you can start writing expenses.\nFor example, type 50 to add an expense and then select category.\nfor more commands, type '/' and you will see the entire commands list\n"