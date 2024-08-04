import os
import sys
import uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
import logging
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

from Backend import config
from backend import Database as db
from Backend.Responses import responses, get_price, get_category, valid_email, help_response
from Backend.config import (
    TOKEN,
    BOT_USERNAME,
    Category,
    Button,
    Status,
    Command,
    categories_config,
    categories_config_dict,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    LOGIN_NAME_MIN_LENGTH,
    LOGIN_NAME_MAX_LENGTH
)
from Backend.backend import Database, get_categories, write_category, remove_category, validate_input
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from Backend.backend import Database, get_categories, write_category, remove_category, validate_input
db = Database()  # Ensure the database connection is initialized

# # ------------------------------------------------------- #
# # ---------------------- Commands ----------------------- #
# # ------------------------------------------------------- #

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.split()[0][1:].lower()
    if command == Command.STATS.value:
        await stats(update, context)
    elif command == Command.SIGN_IN.value:
        await sign_in(update, context)
    elif command == Command.SET_LOGIN.value:
        await set_login(update, context)
    elif command == Command.GET_LOGIN.value:
        await get_login(update, context)
    elif command == Command.SET_PASSWORD.value:
        await set_password(update, context)
    elif command == Command.GET_PASSWORD.value:
        await get_password(update, context)
    elif command == Command.DELETE.value:
        await delete(update, context)
    elif command == Command.EXPORT.value:
        await export(update, context)
    elif command == Command.BRAKE_EVEN.value:
        await brake_even(update, context)
    elif command == Command.ADD_CATEGORY.value:
        await add_category(update, context)
    elif command == Command.DELETE_CATEGORY.value:
        await delete_category(update, context)
    elif command == Command.DASHBOARD.value:
        await dashboard(update, context)
    elif command == Command.NEW.value:
        await new_expense_command(update, context)
    else:
        await update.message.reply_text("Unknown command")
        
def handle_message(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed or 'hi' in processed or 'hey' in processed:
        return 'Hey there!'
    elif 'how are you' in processed:
        return 'I\'m fine, thanks!'
    else:  # default
        return 'Sorry 😢 I don\'t understand...'
    
# def handle_message(text: str) -> str:
#     processed: str = text.lower()
#
#     if 'hello' or 'hi' or 'hey' in text:
#         return 'Hey there!'
#     elif 'how are you' in text:
#         return 'I\'m fine, thanks!'
#     # Add responses ...
#
#     else:  # default
#         return 'Sorry 😢 I don\'t understand...'
    
# async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     message_type: str = update.message.chat.type
#     text: str = update.message.text
#     user_id = update.message.from_user.id
#     group_id = update.message.chat.id
#
#     logger.info(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
#
#     if message_type == 'group' and config.BOT_USERNAME in text:
#         new_text = text.replace(config.BOT_USERNAME, '').strip()
#         response = handle_message(new_text)
#         await update.message.reply_text(response)
#         return
#
#     if text.startswith('/'):
#         await handle_command(update, context)
#     else:
#         try:
#             amount = float(text)
#             context.user_data['amount'] = amount
#             context.user_data['user_id'] = user_id
#             context.user_data['group_id'] = group_id
#
#             logger.info(f"Stored amount: {amount}, user_id: {user_id}, group_id: {group_id}")
#
#             categories = config.categories_config_dict
#             keyboard = [
#                 [InlineKeyboardButton(categories[cat], callback_data=cat) for cat in row]
#                 for row in [
#                     ['Food', 'Groceries', 'Transport'],
#                     ['Rent', 'Insurance', 'Health'],
#                     ['Education', 'Entertainment', 'Travel'],
#                     ['Pet', 'Childcare', 'Gas'],
#                     ['Shopping', 'Clothing', 'Other'],
#                     ['Cancel']
#                 ]
#             ]
#             reply_markup = InlineKeyboardMarkup(keyboard)
#             await update.message.reply_text("Select a category for the expense:", reply_markup=reply_markup)
#         except ValueError:
#             await update.message.reply_text("Please enter a valid amount.")
#             logger.error("Invalid amount entered")



async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        message_type: str = update.message.chat.type
        text: str = update.message.text
        user_id = update.message.from_user.id
        group_id = update.message.chat.id

        logger.info(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

        if message_type == 'group' and config.BOT_USERNAME in text:
            new_text = text.replace(config.BOT_USERNAME, '').strip()
            response = handle_message(new_text)
            await update.message.reply_text(response)
            return

        if text.startswith('/'):
            await handle_command(update, context)
        else:
            try:
                amount = float(text)
                context.user_data['amount'] = amount
                context.user_data['user_id'] = user_id
                context.user_data['group_id'] = group_id

                logger.info(f"Stored amount: {amount}, user_id: {user_id}, group_id: {group_id}")

                categories = config.categories_config_dict
                keyboard = [
                    [InlineKeyboardButton(categories[cat], callback_data=cat) for cat in row]
                    for row in [
                        ['Food', 'Groceries', 'Transport'],
                        ['Rent', 'Insurance', 'Health'],
                        ['Education', 'Entertainment', 'Travel'],
                        ['Pet', 'Childcare', 'Gas'],
                        ['Shopping', 'Clothing', 'Other'],
                        ['Cancel']
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Select a category for the expense:", reply_markup=reply_markup)
            except ValueError:
                response = handle_message(text)
                await update.message.reply_text(response)
                logger.error("Invalid amount entered")



async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        amount = float(update.message.text)
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        
        # Save the amount and other details to the context for later use
        context.user_data['amount'] = amount
        context.user_data['user_id'] = user_id
        context.user_data['group_id'] = group_id
        
        # Log the stored context data
        logger.info(f"Stored amount: {amount}, user_id: {user_id}, group_id: {group_id}")
        
        # Create category selection buttons with icons
        categories = config.categories_config_dict  # Use the dictionary with combined text and icons
        keyboard = [
            [
                InlineKeyboardButton(categories[cat], callback_data=cat)
                for cat in row
            ]
            for row in [
                ['Food', 'Groceries', 'Transport'],
                ['Rent', 'Insurance', 'Health'],
                ['Education', 'Entertainment', 'Travel'],
                ['Pet', 'Childcare', 'Gas'],
                ['Shopping', 'Clothing', 'Other'],
                ['Cancel']
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("Select a category for the expense:", reply_markup=reply_markup)
    except ValueError:
        await update.message.reply_text("Please enter a valid amount.")
        logger.error("Invalid amount entered")
        




        
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# ------------------------------------------------------- #
# ---------------------- Commands ----------------------- #
# ------------------------------------------------------- #
async def new_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /new command to add a new expense."""
    try:
        if update.message is None:
            await update.callback_query.answer()
            return
        
        args = update.message.text.split()
        if len(args) < 3:
            await update.message.reply_text("Usage: /new <category> <price>")
            return
        
        category = args[1]
        price = float(args[2])
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        
        db.new_expense(user_id, group_id, category, price)
        await update.message.reply_text(f"Added expense: {category} - {price}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do and create group for them in DB."""

    group_id = update.message.chat.id
    group_type = update.message.chat.type
    if group_type == 'group':
        group_name = update.message.chat.title
    else:
        group_name = update.message.chat.first_name

    user_name = update.message.from_user.first_name
    user_id = update.message.from_user.id

    # Check if user and group exist and create if not
    db.is_exists(user_id, user_name, group_id, group_name, group_admin_flag=(group_type == 'private'))

    await update.message.reply_text("Thank you for adding me, I will help you to track your expenses.")
    if group_type == 'group':
        await update.message.reply_text(
            f"Please each of you provide me your username for login permissions to our website, e.g:\n'/{Command.SIGN_IN.value} TalVazana'")
    else:
        await update.message.reply_text(
            f"Please provide me your username for login permissions to our website, e.g:\n'/{Command.SIGN_IN.value} TalVazana'")



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(help_response)


async def sign_in(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/signin LOGIN_NAME' sign-in the user with given login_name into DB (for permissions to website) """
    # get parameters of sender for new row in 'users' table
    sender_user_id = update.message.from_user.id
    sender_user_name = update.message.from_user.name
    sender_loginname = (update.message.text).split(Command.SIGN_IN.value)[1].strip()  # get text (the loginname)
    group_id = update.message.chat.id  # get group_id = chat_id
    last_message_flag = False  # to cut messages early
    
    # check if user exists and get his user's info from DB
    is_user_exists, user_info = db.is_user_exists(user_id=sender_user_id)
    
    # if user is exists
    if is_user_exists:
        signed_loginname = user_info[0][2]  # get loginname from user_info
        if signed_loginname != sender_loginname:  # and if he sent different loginname -> ask for changes
            await update.message.reply_text(
                f'hey {update.message.from_user.first_name}, your user is already signed-in with the login name:\n{signed_loginname}')
            await update.message.reply_text(
                f"To change the login name please use the next command: '/{Command.SET_LOGIN.value} YOUR_NEW_LOGIN_NAME'")
            last_message_flag = True
        # TODO: !NICE TO HAVE! would you like to change the loginname? (button of (Accept / Decline))
        # TODO: !NICE TO HAVE! NOAM - how to add button to accept changes
        
        if db.get_password(sender_user_id) == None:  # if password not exists
            db.set_password(user_id=sender_user_id, password=f"{uuid.uuid4()}")
            await update.message.reply_text(
                f"hey {update.message.from_user.first_name}, I have generated you a new password.\nPlease use '/{Command.GET_PASSWORD.value}' command in a private chat with me.")
    
    # if user is NOT exists
    else:
        temp_password = f"{uuid.uuid4()}"  # generate new password
        succeed = db.create_user(user_id=sender_user_id, user_name=sender_user_name, login_name=sender_loginname,
                                 password=temp_password, is_admin=0)
        if not succeed:
            await update.message.reply_text(
                f"hey {update.message.from_user.first_name}, your login_name should be between [{LOGIN_NAME_MIN_LENGTH}-{LOGIN_NAME_MAX_LENGTH}] charatcers")
        else:
            await update.message.reply_text(
                f"hey {update.message.from_user.first_name}, I have generated you a new password for our website.\nPlease use '/{Command.GET_PASSWORD.value}' command in a private chat with me.")
            await update.message.reply_text(
                f"To change the password please use the next command in a private chat with me: '/{Command.SET_PASSWORD.value} YOUR_NEW_PASSWORD'")
    
    # CREATE connection between user and group in 'usergroups' table
    connection = db.is_usergroups_row_exists(user_id=sender_user_id,
                                             group_id=group_id)  # check if connection already exists
    if not connection:  # if connection NOT exists
        
        # on group chat
        group_type = update.message.chat.type
        if group_type == 'group':
            chat_admins = await update.effective_chat.get_administrators()  # get administrators list
            if update.effective_user in (admin.user for admin in chat_admins):  # if sender is admin
                db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=1)
                await update.message.reply_text(
                    f"hey {update.message.from_user.first_name}, I have added your account admin permissions for this group")
            else:  # user is not admin
                db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=0)
                await update.message.reply_text(
                    f"hey {update.message.from_user.first_name}, I have added your account viewer permissions for this group")
        
        # on private chat
        else:
            db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=1)
            await update.message.reply_text(
                f"hey {update.message.from_user.first_name}, I have added your account admin permissions for this chat")
    
    else:
        if last_message_flag == False:
            await update.message.reply_text(
                f"hey {update.message.from_user.first_name}, you already signed-in and have permissions to our website")
    
    return


async def set_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/setLogin ....' - set a new login_name for the user """
    
    # set the new login_name for this user
    sender_user_id = update.message.from_user.id
    try:
        sender_loginname = (update.message.text).split(Command.SET_LOGIN.value)[
            1].strip()  # get the text after the command (the loginname)
    except:
        await update.message.reply_text(
            f"hey {update.message.from_user.first_name}, please send this command in the format of '/{Command.SET_LOGIN.value} YOUR_LOGIN_NAME'")
    succeed = db.set_login_name(sender_user_id, login_name=sender_loginname)  # get None if failed
    if succeed == None:
        await update.message.reply_text(
            f'hey {update.message.from_user.first_name}, your new login_name should be between [{LOGIN_NAME_MIN_LENGTH}-{LOGIN_NAME_MAX_LENGTH}] charatcers')
    else:
        await update.message.reply_text(
            f"hey {update.message.from_user.first_name}, your new login_name has been updated to: '{succeed}'")


async def get_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/getLogin' - send the user his login_name """
    
    # get the login_name from db
    sender_user_id = update.message.from_user.id
    login = db.get_login(sender_user_id)
    
    # send login_name
    if login:
        await update.message.reply_text(f"Hello, your login name for our website is: {login}")
    else:
        await update.message.reply_text(
            f"hey {update.message.from_user.first_name}, please sign-in first using the next command: '/{Command.SIGN_IN.value} YOUR_LOGIN_NAME''")


async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/setPassword ....' - set a new password for the user """
    
    # verify it is private chat
    group_type = update.message.chat.type
    if group_type == 'group':  # get group_name = chat_name / user name (in private chat)
        await update.message.reply_text(
            f'hey {update.message.from_user.first_name}, this command can only be used in a private chat with me')
        return
    
    # set the new password for this user
    sender_user_id = update.message.from_user.id
    try:
        sender_password = (update.message.text).split(Command.SET_PASSWORD.value)[
            1].strip()  # get the text after the command (the password)
    except:
        await update.message.reply_text(
            f"hey {update.message.from_user.first_name}, please send this command in the format of '/{Command.SET_PASSWORD.value} YOUR_PASSWORD'")
    succeed = db.set_password(sender_user_id, password=sender_password)  # get None if failed
    if succeed == None:
        await update.message.reply_text(
            f'hey {update.message.from_user.first_name}, your new password should be between [{PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH}] charatcers')
    else:
        await update.message.reply_text(
            f"hey {update.message.from_user.first_name}, your new password has been updated to: '{succeed}'")


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/getPassword' - send the user his password in private chat """
    
    # verify it is private chat
    group_type = update.message.chat.type
    if group_type == 'group':  # get group_name = chat_name / user name (in private chat)
        await update.message.reply_text(
            f'hey {update.message.from_user.first_name}, this command can only be used in a private chat with me')
        return
    
    # get the password from db
    sender_user_id = update.message.from_user.id
    password = db.get_password(sender_user_id)
    
    # send password in private chat
    if password:
        await update.message.reply_text(f"Hello, your password for our website is: {password}")
    else:
        await update.message.reply_text(
            f"hey {update.message.from_user.first_name}, please sign-in first using the next command: '/{Command.SIGN_IN.value} YOUR_LOGIN_NAME''")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("This Month", callback_data="This Month"),
            InlineKeyboardButton("Last Month", callback_data="Last Month"),
            InlineKeyboardButton("All Time", callback_data="All Time")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a period of time", reply_markup=reply_markup)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        group_id = update.message.from_user.id
    else:
        group_id = update.message.chat.id
    
    user_id = update.message.from_user.id
    msg = update.message.text.split()
    if len(msg) == 2:
        delete_time = msg[1]
    elif len(msg) == 1:
        delete_time = 'latest'
    else:
        await update.message.reply_text("could not procces this command")
        return
    
    deleted = db.delete(group_id, user_id, delete_time)
    await update.message.reply_text(deleted)


async def export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        print(update.message.chat.id)
    else:
        db.toExcel(update.message.chat.id)
        await context.bot.send_document(chat_id=update.message['chat']['id'], document=open('expenses.xlsx', 'rb'))


async def brake_even(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot is available only for groups')
        return
    
    response = db.brake_even(update.message.chat.id)
    if not response:
        response = "There is no breakeven for this group"
    await update.message.reply_text(response)


# async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# 	if update.message.chat.type == 'private':
# 		group_id = update.message.from_user.id
# 	else:
# 		group_id = update.message.chat.id
#
# 	try:
# 		new_category = update.message.text.split()
# 		added = write_category(group_id, new_category[1])
# 		await update.message.reply_text(added)
# 	except:
# 		await update.message.reply_text("an error has occured")
async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /add_category command to add a new expense category."""
    try:
        args = update.edited_message.text.split()
        if len(args) < 2:
            await update.message.reply_text("Usage: /add_category <category_name>")
            return
        
        category_name = args[1]
        
        # Add category to the database (you'll need a method in your backend to handle this)
        db.add_category(category_name)
        await update.edited_message.reply_text(f"Added new category: {category_name}")
    except Exception as e:
        await update.edited_message.reply_text(f"Error: {e}")

async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        group_id = update.message.from_user.id
    else:
        group_id = update.message.chat.id
    
    try:
        new_category = update.message.text.split()
        deleted = remove_category(group_id, new_category[1])
        await update.message.reply_text(deleted)
    except:
        await update.message.reply_text("an error has occured")


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return
    
    group_id = str(update.message.chat.id)
    link = "www.google.com"
    await update.message.reply_text(text=f"<a href='{link}'>dashboard</a>", parse_mode="html")



# ------------------------------------------------------- #
# ---------------------- End Commands ------------------- #
# ------------------------------------------------------- #

