import asyncio
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

# Telegram bot token
TELEGRAM_BOT_TOKEN = "*********"

# Firebase setup
cred = credentials.Certificate("./google-services.json")  # Файл в той же папке, что и этот скрипт
firebase_admin.initialize_app(cred, {
    'databaseURL': "************"
})

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Кнопка "Узнать данные"
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Узнать данные 💾", callback_data="get_data")]
    ]
)

# Получение данных из Firebase
async def fetch_data():
    humidity_ref = db.reference('house/humidity')
    temp_ref = db.reference('house/temp')
    gas_ref = db.reference('house/raw_value')

    humidity = humidity_ref.get()
    temp = temp_ref.get()
    gas = gas_ref.get()

    if humidity is None or temp is None or gas is None:
        return "Не удалось получить данные."

    return f"💧 Влажность: {humidity}%\n🌡 Температура: {temp}°C\n☣ Газ: {gas}"

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Нажмите на кнопку ниже, чтобы узнать данные:", reply_markup=keyboard)

# Обработчик нажатия на кнопку
@dp.callback_query(lambda c: c.data == "get_data")
async def get_data(callback_query: CallbackQuery):
    # Извлекаем данные и отправляем сообщение
    data = await fetch_data()
    sent_message = await callback_query.message.answer(data, reply_markup=keyboard)
    
    # Обновляем сообщение каждые 0.1 секунды
    while True:
        await asyncio.sleep(0.1)  # Ждём 0.1 секунды
        new_data = await fetch_data()

        # Попытаться отредактировать сообщение, если данные изменились
        if sent_message.text != new_data:
            await bot.edit_message_text(new_data, chat_id=sent_message.chat.id, message_id=sent_message.message_id, reply_markup=keyboard)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
