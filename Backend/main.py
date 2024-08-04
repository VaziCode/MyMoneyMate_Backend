
import os
import sys
import uuid

from Backend import Commands, Responses, config
from Backend.Commands import logger
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


# def handle_message(text: str) -> str:
#     processed: str = text.lower()
#
#     if 'hello' or 'hi' or 'hey' in text:
#         return 'Hey there!'
#     elif 'how are you' in text:
#         return 'I\'m fine, thanks!'
#     # Add responses ...
#
#     else:# default
#         return 'I don\'t understand...'

# async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     message_type: str = update.message.chat.type
#     text: str = update.message.text
#     print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
#
#     if message_type == 'group':
#         if config.BOT_USERNAME in text:
#             new_text = str = text.replace(config.BOT_USERNAME, '').strip()
#             response = handle_message(new_text)
#         else:
#             return
#     else:
#         response = handle_message(text)
#     print('Bot: ', response)
#     await update.message.reply_text(response)
#
#
#     group_admin_flag = False #flag if the user is group admin
#     group_type = update.message.chat.type
#     if group_type == 'private':
#         group_id = update.message.from_user.id
#         group_name = update.message.from_user.first_name
#         group_admin_flag = True
#     else:
#         group_id = update.message.chat.id
#         group_name = update.message.chat.title
#         chat_admins = await update.effective_chat.get_administrators() #get administrators list
#         if update.effective_user in (admin.user for admin in chat_admins): #if sender is admin
#             group_admin_flag = True
#
#     user_name = update.message.from_user.first_name
#     user_id = update.message.from_user.id
#
#     # check if user and group exists:
#
#     response = db.is_exists(user_id, user_name, group_id, group_name, group_admin_flag, update)
#     if response:
#         await update.message.reply_text(response) #user doesn't exists
#         return
#
#     all_categories = categories_config + get_categories(str(group_id))
#
#     is_invalid_input = validate_input(update.message.text)
#     if is_invalid_input:
#         pass #if invalid input - do nothing for now
#         #await update.message.reply_text(is_invalid_input)
#
#     else:
#         keyboard = [[]]
#         j = 0
#         for i, item in enumerate(all_categories):
#             if i % 3 == 0 and i != 0:
#                 keyboard.append([])
#                 j += 1
#             if item in categories_config:
#                 keyboard[j].append(InlineKeyboardButton(categories_config_dict[item], callback_data=item))
#             else:
#                 keyboard[j].append(InlineKeyboardButton(item, callback_data=item))
#
#         keyboard[j].append(InlineKeyboardButton("Cancel ❌", callback_data="cancel"))
#         reply_markup = InlineKeyboardMarkup(keyboard)
#
#         await update.message.reply_text(update.message.text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    group_id = query.message.chat.id

    # Handle cancel button
    if data.lower() == "cancel":
        await query.edit_message_text(text="Cancelled")
        return

    # Handle /stats responses
    stats_responses = ["This Month", "Last Month", "All Time"]
    if data in stats_responses:
        result = db.total_expenses(group_id, data)
        if not result:
            await query.message.reply_text(f'No expenses found')
            return
        db.piechart(group_id, data)
        db.barchart(group_id, data)
        await query.message.reply_text(f'Total expenses of the group is {result} ')
        await context.bot.send_photo(chat_id=group_id, photo=open('my_plot.png', 'rb'))
        if query.message.chat.type == 'group':
            await context.bot.send_photo(chat_id=group_id, photo=open('my_plot2.png', 'rb'))
        await query.message.delete()
        return

    # Handle expense category selection
    category = data
    amount = context.user_data.get('amount')
    user_id = context.user_data.get('user_id')
    group_id = context.user_data.get('group_id')

    logger.info(f"Retrieved amount: {amount}, user_id: {user_id}, group_id: {group_id}, category: {category}")

    if amount is None or user_id is None or group_id is None:
        await query.edit_message_text(text="Please enter an amount first.")
        return

    try:
        db.new_expense(user_id, group_id, category, amount)
        await query.edit_message_text(text=f"Added expense: {category} - {amount}")
        logger.info(f"Expense added: {category} - {amount} for user_id: {user_id}, group_id: {group_id}")
    except Exception as e:
        await query.edit_message_text(text=f"Error: {e}")
        logger.error(f"Error adding expense: {e}")
        

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')




# Run the program

from Backend import Commands


if __name__ == '__main__':
    #sys.stdout.reconfigure(encoding='utf-8')
    db = Database()
    
    #os.environ["PYTHONIOENCODING"] = "utf-8"
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler(f"{Command.START.value}", Commands.start))
    app.add_handler(CommandHandler(f"{Command.HELP.value}", Commands.help_command))
    app.add_handler(CommandHandler(f"{Command.STATS.value}", Commands.stats))
    app.add_handler(CommandHandler(f"{Command.SIGN_IN.value}", Commands.sign_in))
    app.add_handler(CommandHandler(f"{Command.SET_LOGIN.value}", Commands.set_login))
    app.add_handler(CommandHandler(f"{Command.GET_LOGIN.value}", Commands.get_login))
    app.add_handler(CommandHandler(f"{Command.SET_PASSWORD.value}", Commands.set_password))
    app.add_handler(CommandHandler(f"{Command.GET_PASSWORD.value}", Commands.get_password))
    app.add_handler(CommandHandler(f"{Command.DELETE.value}", Commands.delete))
    app.add_handler(CommandHandler(f"{Command.EXPORT.value}", Commands.export))
    app.add_handler(CommandHandler(f"{Command.BRAKE_EVEN.value}", Commands.brake_even))
    app.add_handler(CommandHandler(f"{Command.ADD_CATEGORY.value}", Commands.add_category))
    app.add_handler(CommandHandler(f"{Command.DELETE_CATEGORY.value}", Commands.delete_category))
    app.add_handler(CommandHandler(f"{Command.DASHBOARD.value}", Commands.dashboard))
    app.add_handler(CommandHandler(f"{Command.DELETE.value}",Commands.db.delete))
    app.add_handler(CommandHandler(f"{Command.SUM.value}",Commands.db.total_expenses))
    app.add_handler(CommandHandler("new", Commands.new_expense_command))

    #click handler
    app.add_handler(CallbackQueryHandler(button))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Commands.handler))
    
    # Log all errors
    app.add_error_handler(error)

    print('Polling...')  # TODO: delete this debug line
    # Run the bot
    app.run_polling(poll_interval=1)
