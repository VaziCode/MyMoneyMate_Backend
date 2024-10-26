import os
from sys import exit
from enum import Enum
from dotenv import load_dotenv
from typing import \
    Final  # A special typing construct to indicate to type checkers that a name cannot be re-assigned or overridden in a subclass

# load .env file
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

#DB info
DB_HOST = os.environ.get("DB_HOST")
DB_DATABASE_NAME = os.environ.get("DB_DATABASE_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")



# telegram info
# TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Commands
class Command(Enum):
    START = "start"  # start conversation
    HELP = "help"  # get information to how to use the bot
    STATS = "stats"  # show stats of the group
    NEW = "new"  # add a new expense
    DELETE = "delete"  # delete a new expenses
    SUM = "sum"  # get the total expenses in a specific month or year in a pie chart histogram
    LIST = "list"  # get a list of all your expenses in a specific month or year
    EXPORT = "export"  # export the expenses of a given month as excel file
    STOP = "stop"  # stops a recurring expense
    LINK = "link"  # send fast UI link (NICE TO HAVE)
    BRAKE_EVEN = "brakeeven"
    ADD_CATEGORY = "addcategory"
    DELETE_CATEGORY = "deletecategory"
    DASHBOARD = "dashboard"
    GET_PASSWORD = "getpassword" # sends user's password in a private chat
    SET_PASSWORD = "setpassword" # give the user the option to change his password
    GET_LOGIN = "getlogin"
    SET_LOGIN = "setlogin"
    SIGN_IN = "signin" # create user in 'users' table


# buttons:
class Button(Enum):
    APPROVE = "Approve ✅"
    CANCEL = "Cancel ❌"

# status:
class Status(Enum):
    APPROVED = "Approved ✅"
    CANCELLED = "Cancelled ❌"


# categories:
class Category(Enum):
    FOOD = "food"
    GAS = "gas"
    GROCERIES = "groceries"
    SHOPPING = "shopping"
    CLOTHES = "clothes"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"
    # TODO: verify categories

# categories_config = ["food", "gas", "groceries", "shopping", "clothes", "pleasure", "other"]
# categories_config_dict = {"food": "Food 🍔", "gas": "Gas ⛽", "groceries": "Groceries🍎", "shopping": "Shopping🛒", "clothes": "Clothes👕", "pleasure": "Pleasure🎦", "other": "Other"}

categories_config = {
    'Food': '🍔',
    'Groceries': '🛒',
    'Transport': '🚗',
    'Rent': '🏠',
    'Insurance': '🛡️',
    'Health': '💊',
    'Education': '📚',
    'Entertainment': '🎬',
    'Travel': '✈️',
    'Pet': '🐾',
    'Childcare': '👶',
    'Gas': '⛽',
    'Shopping': '🛍️',
    'Clothing': '👚',
    'Other': '🗃️',
    'Cancel': '❌'
}

categories_config_dict = {
    'Food': 'Food 🍔',
    'Groceries': 'Groceries 🛒',
    'Transport': 'Transport 🚗',
    'Rent': 'Rent 🏠',
    'Insurance': 'Insurance 🛡️',
    'Health': 'Health 💊',
    'Education': 'Education 📚',
    'Entertainment': 'Entertainment 🎬',
    'Travel': 'Travel ✈️',
    'Pet': 'Pet 🐾',
    'Childcare': 'Childcare 👶',
    'Gas': 'Gas ⛽',
    'Shopping': 'Shopping 🛍️',
    'Clothing': 'Clothing 👚',
    'Other': 'Other 🗃️',
    'Cancel': 'Cancel ❌'
}
#GLOBAL VALUES:
PASSWORD_MAX_LENGTH = 40
PASSWORD_MIN_LENGTH = 6
LOGIN_NAME_MAX_LENGTH = 12
LOGIN_NAME_MIN_LENGTH = 6
TOKEN: Final = '6982655062:AAG94hat5MKd7QX7y8id6FM7qyp_B5B2nm4'
BOT_USERNAME: Final = '@My_Money_Mate_bot'

