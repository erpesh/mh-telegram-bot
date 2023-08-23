import csv
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from messages import get_messages, add_message, remove_message, get_formatted_messages, get_first_message

TOKEN: Final = "6560466673:AAH5JnpF9JJos5bT5BDBCC_4UslF43EDjHY"
BOT_USERNAME: Final = '@uyt_test_bot'

# Admin IDS
ADMIN_IDS: list[int] = [938510955]

# Storage of chats, messages and available admins
active_chats: dict[int:int or None] = {}  # Active chats in {user_id: admin_id} format
active_admin_chats: dict[int:int] = {}  # Active chats in {admin_id: user_id} format
available_admins: list[int] = []  # List of available admins
users_sending_questions: list[int] = []  # List of users sending questions to the database
admins_answering_questions: dict[int:dict or None] = {}  # List of admins answering questions from the database


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет, я тест бот')


def shorten_string(input_string):
    max_length = 50
    if len(input_string) > max_length:
        shortened = input_string[:max_length-3] + '...'
        return shortened
    else:
        return input_string


async def show_stored_message(admin_id: int, update: Update):
    first_message = get_first_message()
    if first_message is None:
        await update.message.reply_text("Нет заданных вопросов.")
        admins_answering_questions.pop(admin_id)
    else:
        admins_answering_questions[admin_id] = first_message
        await update.message.reply_text("Напишите '/ask' когда готовы перейти к следющему вопросу.")
        await update.message.reply_text(f"Сообщение от пользователя {first_message['username']}:\n{first_message['message']}")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in ADMIN_IDS:
        if user_id not in admins_answering_questions:
            admins_answering_questions[user_id] = None

        await show_stored_message(user_id, update)
    else:
        users_sending_questions.append(user_id)
        await update.message.reply_text('Задайте свой вопрос:')


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('О нас')


async def lib_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Наша библиотека - midashall.notion.site')


def get_available_chats() -> list[int]:
    return [key for key, value in active_chats.items() if value is None]


async def connect_admin_to_chat(admin_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_chats = get_available_chats()
    if len(available_chats) > 0:
        first_chat = available_chats[0]

        active_chats[first_chat] = admin_id
        active_admin_chats[admin_id] = first_chat

        await update.message.reply_text(
            f"Вы подключены к чату с пользователем {first_chat}. Напишите '/end' что бы завершить.")
        await context.bot.send_message(
            chat_id=first_chat,
            text="Вы подключены к чату с администратором. Что вас интересует?"
        )
    else:
        if admin_id not in available_admins:
            available_admins.append(admin_id)
        await update.message.reply_text("Ожидайте вопросов от пользователей. Напишите '/leave' если хотите выйти.")


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in ADMIN_IDS:
        await connect_admin_to_chat(user_id, update, context)
    else:
        if len(available_admins) > 0:
            first_admin = available_admins[0]
            active_chats[user_id] = first_admin
            active_admin_chats[first_admin] = user_id
            available_admins.remove(first_admin)
            await context.bot.send_message(
                chat_id=first_admin,
                text=f"Вы подключены к чату с пользователем {user_id}. Напишите '/end' что бы завершить."
            )
            await update.message.reply_text("Вы начали чат с администратором. Пожалуйста, задайте ваш вопрос и ожидайте ответ.")
        else:
            active_chats[user_id] = None
            await update.message.reply_text(f"Пожалуйста подождите, вы {len(get_available_chats())} в очереди.")

    print(active_chats, active_admin_chats, available_admins)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(active_chats)
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    message = update.message.text
    if user_id in active_chats:
        admin_chat_id = active_chats[user_id]
        if admin_chat_id is None:
            await update.message.reply_text("На данный момент нет администраторов онлайн. Попробуйте снова позже.")
        else:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=f"Сообщение от пользователя {update.message.from_user.username}:\n{message}"
            )
    elif user_id in users_sending_questions:
        add_message(user_id, username, message)
        users_sending_questions.remove(user_id)
        await update.message.reply_text("Ваш вопрос сохранен, ожидайте ответа")
    else:
        await update.message.reply_text("Неизвестная команда.")


async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(admins_answering_questions)
    text_message = update.message.text
    admin_id = update.message.from_user.id
    user_id = active_admin_chats.get(admin_id, None)
    if text_message == '/end':
        if admin_id not in active_admin_chats and user_id not in active_chats:
            await update.message.reply_text('Вы не подключены к чату.')
        else:
            active_chats.pop(user_id)
            active_admin_chats.pop(admin_id)
            await update.message.reply_text(f'Чат с {user_id} завершен.')
            await context.bot.send_message(
                chat_id=user_id,
                text="Чат с администратором завершен."
            )

            await connect_admin_to_chat(admin_id, update, context)
            print(active_chats, active_admin_chats, available_admins)
    elif text_message == '/leave':
        if admin_id in available_admins:
            available_admins.remove(admin_id)
            await update.message.reply_text('Вы вышли из режима чатов.')
        else:
            await update.message.reply_text('Вы не в режиме чатов.')
    else:
        if admin_id in admins_answering_questions:
            chat_id = int(admins_answering_questions[admin_id]['user_id'])
            username = admins_answering_questions[admin_id]['username']
            message = shorten_string(admins_answering_questions[admin_id]['message'])
            message_id = admins_answering_questions[admin_id]['message_id']

            answer = f"Ответ на ваш вопрос '{message}':\n{update.message.text}"
            await context.bot.send_message(chat_id=chat_id, text=answer)
            await update.message.reply_text(f'Ваше сообщение отправлено {username}.')

            remove_message(message_id)
            if admin_id in admins_answering_questions:
                admins_answering_questions.pop(admin_id)
        elif user_id is None:
            await update.message.reply_text('Вы не подключены к чату.')
        else:
            await context.bot.send_message(chat_id=user_id, text=update.message.text)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error: {context.error}')


if __name__ == '__main__':
    print('starting bot')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('ask', ask_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('lib', lib_command))
    app.add_handler(CommandHandler("chat", chat_command))

    # Messages
    app.add_handler(MessageHandler(filters.User(ADMIN_IDS), handle_admin_messages))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=1)
