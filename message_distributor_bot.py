from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import re

# Путь к файлу со списком менеджеров
MANAGERS_FILE = 'managers.txt'
# Токен вашего бота
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# ID нужного канала (можно получить, добавив бота в канал и отправив сообщение)
TARGET_CHANNEL_ID = "@your_channel_id"  # Замените на ID или юзернейм вашего канала

# Список менеджеров (загружаем его при старте бота)
managers_list = {}

# Функция для загрузки менеджеров из файла
def load_managers():
    global managers_list
    if os.path.exists(MANAGERS_FILE):
        with open(MANAGERS_FILE, 'r') as file:
            for line in file:
                phone_number, chat_id = line.strip().split()
                phone_number = phone_number.lstrip("+")  # Убираем символ "+" в начале номера, если есть
                managers_list[phone_number] = chat_id

# Функция для сохранения нового менеджера в файл
def save_manager(phone_number, chat_id):
    with open(MANAGERS_FILE, 'a') as file:
        file.write(f"{phone_number} {chat_id}\n")

# Функция для обработки команды /manager
async def manager_command(update: Update, context):
    # Создаем кнопку для запроса контакта
    contact_button = KeyboardButton(text="Поделиться контактом", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

    # Отправляем сообщение с кнопкой для запроса контакта
    await update.message.reply_text("Пожалуйста, поделитесь вашим контактом, чтобы добавить вас как менеджера.", reply_markup=reply_markup)

# Функция для обработки контакта, который прислал пользователь
async def handle_contact(update: Update, context):
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

# Функция для обработки сообщений из канала
async def handle_channel_message(update: Update, context):
    # Проверяем, что сообщение пришло из нужного канала
    if update.message.chat.username != TARGET_CHANNEL_ID.lstrip('@'):
        return  # Игнорируем сообщения из других каналов

    message_text = update.message.text

    # Ищем номер телефона в сообщении между символами ">" и ":"
    match = re.search(r'>\s*(\+?\d+)\s*:', message_text)
    if match:
        phone_number = match.group(1).lstrip("+")  # Убираем символ "+" в начале, если есть
        if phone_number in managers_list:
            chat_id = managers_list[phone_number]
            # Отправляем текст сообщения в чат с менеджером
            await context.bot.send_message(chat_id, message_text)

# Функция для игнорирования всех остальных сообщений
async def ignore_message(update: Update, context):
    # Игнорируем все сообщения, которые не являются командой /manager или не содержат контакт
    pass

# Основная функция инициализации бота
async def main():
    # Загружаем менеджеров из файла
    load_managers()

    # Создаем приложение с токеном вашего бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик команды /manager для запроса контакта
    application.add_handler(CommandHandler('manager', manager_command))

    # Обработчик контакта
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Обработчик сообщений из каналов
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.CHANNEL, handle_channel_message))

    # Игнорируем все остальные команды и сообщения
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.CONTACT, ignore_message))

    # Запускаем бота
    await application.start_polling()
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
