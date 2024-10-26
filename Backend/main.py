
import os
import sys
import uuid

from Backend import Commands, Responses, config
# from Backend.Commands import logger
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

    # logger.info(f"Retrieved amount: {amount}, user_id: {user_id}, group_id: {group_id}, category: {category}")

    if amount is None or user_id is None or group_id is None:
        await query.edit_message_text(text="Please enter an amount first.")
        return

    try:
        db.new_expense(user_id, group_id, category, amount)
        await query.edit_message_text(text=f"Added expense: {category}  {amount}")
        # logger.info(f"Expense added: {category} - {amount} for user_id: {user_id}, group_id: {group_id}")
    except Exception as e:
        await query.edit_message_text(text=f"Error: {e}")
        # logger.error(f"Error adding expense: {e}")
        

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
