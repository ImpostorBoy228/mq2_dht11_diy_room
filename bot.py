import asyncio
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Telegram bot token
TELEGRAM_BOT_TOKEN = "***********"

# Firebase setup
cred = credentials.Certificate("./google-services.json")  # Файл в той же папке, что и этот скрипт
firebase_admin.initialize_app(cred, {
    'databaseURL': "*************************"
})

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# FSM для установки порогов
class ThresholdState(StatesGroup):
    waiting_for_min_threshold = State()
    waiting_for_max_threshold = State()

# Кнопки для основного меню
main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[ 
        [InlineKeyboardButton(text="Узнать данные 💾", callback_data="get_data")],
        [InlineKeyboardButton(text="🥒Включить ручное управление", callback_data="enable_manual")],
        [InlineKeyboardButton(text="⚙️Установить пороги", callback_data="set_thresholds")]
    ]
)

# Кнопки для ручного управления
manual_control_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💦Включить увлажнитель", callback_data="enable_humidifier")],
        [InlineKeyboardButton(text="☔Выключить увлажнитель", callback_data="disable_humidifier")],
        [InlineKeyboardButton(text="🍺Перейти в автоматический режим", callback_data="disable_manual")]
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

# Обновление значений в Firebase
def update_firebase(ref_path, value):
    ref = db.reference(ref_path)
    ref.set(value)

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Нажмите на кнопку ниже, чтобы взаимодействовать с системой:", reply_markup=main_menu_keyboard)

# Обработчик кнопки "Узнать данные 💾"
@dp.callback_query(lambda c: c.data == "get_data")
async def get_data(callback_query: CallbackQuery):
    # Обновление данных без необходимости повторного нажатия
    data = await fetch_data()
    await callback_query.message.edit_text(data, reply_markup=main_menu_keyboard)

    # Запускаем задачу по обновлению данных каждую секунду
    asyncio.create_task(auto_update_data(callback_query.message))

# Автоматическое обновление данных
async def auto_update_data(message):
    while True:
        await asyncio.sleep(10)  # Задержка в 10 секунд для получения актуальных данных
        data = await fetch_data()
        await message.edit_text(data, reply_markup=main_menu_keyboard)

# Обработчик кнопки "🥒Включить ручное управление"
@dp.callback_query(lambda c: c.data == "enable_manual")
async def enable_manual(callback_query: CallbackQuery):
    update_firebase('house/is_manual', True)
    update_firebase('house/manual', False)
    await callback_query.message.edit_text("Ручное управление включено. Выберите действие:", reply_markup=manual_control_keyboard)

# Обработчик кнопки "💦Включить увлажнитель"
@dp.callback_query(lambda c: c.data == "enable_humidifier")
async def enable_humidifier(callback_query: CallbackQuery):
    update_firebase('house/manual', True)
    await callback_query.message.edit_text("Увлажнитель включён.", reply_markup=manual_control_keyboard)

# Обработчик кнопки "☔Выключить увлажнитель"
@dp.callback_query(lambda c: c.data == "disable_humidifier")
async def disable_humidifier(callback_query: CallbackQuery):
    update_firebase('house/manual', False)
    await callback_query.message.edit_text("Увлажнитель выключен.", reply_markup=manual_control_keyboard)

# Обработчик кнопки "🍺Перейти в автоматический режим"
@dp.callback_query(lambda c: c.data == "disable_manual")
async def disable_manual(callback_query: CallbackQuery):
    update_firebase('house/is_manual', False)
    await callback_query.message.edit_text("Автоматический режим включён.", reply_markup=main_menu_keyboard)

# Обработчик кнопки "⚙️Установить пороги"
@dp.callback_query(lambda c: c.data == "set_thresholds")
async def start_threshold_setting(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ThresholdState.waiting_for_min_threshold)
    await callback_query.message.answer("Введите минимальный порог:")

# Обработчик ввода минимального порога
@dp.message(ThresholdState.waiting_for_min_threshold)
async def process_min_threshold(message: Message, state: FSMContext):
    try:
        min_threshold = int(message.text)
        await state.update_data(min_threshold=min_threshold)
        await state.set_state(ThresholdState.waiting_for_max_threshold)
        await message.answer("Введите максимальный порог:")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")

# Обработчик ввода максимального порога
@dp.message(ThresholdState.waiting_for_max_threshold)
async def process_max_threshold(message: Message, state: FSMContext):
    try:
        max_threshold = int(message.text)
        user_data = await state.get_data()
        min_threshold = user_data.get("min_threshold")

        if max_threshold <= min_threshold:
            await message.answer("Максимальный порог должен быть больше минимального. Попробуйте снова.")
            return

        # Обновляем Firebase
        update_firebase("/house/humidity_low", min_threshold)
        update_firebase("/house/humidity_high", max_threshold)

        await message.answer(
            f"Пороги успешно установлены!\n"
            f"Минимальный порог: {min_threshold}\n"
            f"Максимальный порог: {max_threshold}"
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")

# Главная функция
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
