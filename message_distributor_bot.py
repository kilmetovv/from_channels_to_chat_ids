from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup, Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
import re
import asyncio


# Путь к файлу со списком менеджеров
MANAGERS_FILE = 'managers.txt'
# Токен вашего бота
BOT_TOKEN = "8167525848:AAGdwk5IKoJNcQRfIsZ695-hWGluSBRWrWk"
# ID нужного канала (можно получить, добавив бота в канал и отправив сообщение)
TARGET_CHANNEL_ID = "-1002203249461"  # Замените на ID или юзернейм вашего канала

application = None

# Список менеджеров (загружаем его при старте бота)
managers_list = {}

# Функция для загрузки менеджеров из файла +++
def load_managers():
    global managers_list
    if os.path.exists(MANAGERS_FILE):
        with open(MANAGERS_FILE, 'r') as file:
            for line in file:
                phone_number, chat_id = line.strip().split()
                phone_number = phone_number.lstrip("+")  # Убираем символ "+" в начале номера, если есть
                managers_list[phone_number] = chat_id

# Функция для сохранения нового менеджера в файл +++
def save_manager(phone_number, chat_id):
    with open(MANAGERS_FILE, 'a') as file:
        file.write(f"{phone_number} {chat_id}\n")

# Функция для обработки команды /manager +++
async def manager_command(update: Update, context):
    print('manager_command')
    # Создаем кнопку для запроса контакта
    contact_button = InlineKeyboardButton(text="Поделиться контактом", request_contact=True)
    reply_markup = InlineKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

    # Отправляем сообщение с кнопкой для запроса контакта
    await update.message.reply_text("Пожалуйста, поделитесь вашим контактом, чтобы добавить вас как менеджера.", reply_markup=reply_markup)

""" async def start(update: Update, context: CallbackContext):
    print('start')
    # Проверка, что сообщение пришло из канала (где есть channel_chat)
    if update.channel_post.sender_chat.type == 'channel':
        channel_id = update.channel_post.chat.id
        await update.message.reply_text(f"ID этого канала: {channel_id}")
    else:
        await update.message.reply_text("Эта команда должна быть запущена в канале.") """

# Функция для обработки сообщений из канала +++
async def handle_channel_message(update: Update, context):
    print('handle_channel_message')
    # Проверяем, что сообщение пришло из нужного канала
    """ if update.channel_post.chat.id != TARGET_CHANNEL_ID:
        return  # Игнорируем сообщения из других каналов """
    if update.channel_post.sender_chat.type == 'channel':
        message_text = update.channel_post.text

        # Ищем номер телефона в сообщении между символами ">" и ":"
        match = re.search(r'>\s*(\+?\d+)\s*:', message_text)
        if match:
            phone_number = match.group(1).lstrip("+")  # Убираем символ "+" в начале, если есть
            if phone_number in managers_list:
                chat_id = managers_list[phone_number]
                # Отправляем текст сообщения в чат с менеджером
                await application.bot.send_message(chat_id, message_text)

# Функция для обработки контакта, который прислал пользователь +++
async def handle_contact(update: Update, context):
    print('handle_contact')
    contact = update.message.contact
    phone_number = contact.phone_number.lstrip("+")  # Убираем "+" в начале, если есть
    chat_id = update.message.chat.id
    
    if phone_number not in managers_list:
        # Добавляем нового менеджера в список
        managers_list[phone_number] = chat_id
        save_manager(phone_number, chat_id)
        await update.message.reply_text(f"Вы добавлены как менеджер с номером: {phone_number}")
    else:
        await update.message.reply_text(f"Номер {phone_number} уже есть в списке менеджеров.")

""" # Функция для игнорирования всех остальных сообщений
async def ignore_message(update: Update, context):
    print('ignore_message')
    # Игнорируем все сообщения, которые не являются командой /manager или не содержат контакт
    #pass """

# Основная функция инициализации бота
def main():
    global application
    # Загружаем менеджеров из файла
    load_managers()

    # Создаем приложение с токеном вашего бота
    application = Application.builder().token(BOT_TOKEN).build()
    # Запускаем бота
    #await application.initialize()
    #await application.start()

    # Регистрируем обработчик команды /start
    #application.add_handler(CommandHandler("start", start))

    # Обработчик команды /manager для запроса контакта
    application.add_handler(CommandHandler('manager', manager_command))

    # Обработчик контакта
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Обработчик сообщений из каналов
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, handle_channel_message))

    # Игнорируем все остальные команды и сообщения
    #application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.CONTACT, ignore_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    #try:
    main()
"""     except KeyboardInterrupt:
        application.updater.stop()
        application.stop()
        application.shutdown()
        print("Interrupted by user")
    finally:
        print("Shutting down") """
