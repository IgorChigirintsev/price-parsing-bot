import os
import pandas as pd
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InputFile
from aiogram.filters import Command
from parser import get_product_price
from database import init_db, save_to_permanent_storage, save_to_temp_storage, get_temp_data
import asyncio
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем токен из переменных окружения
API_TOKEN = os.getenv('API_TOKEN')

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация базы данных
init_db()

# Обработчик команды /start
async def send_welcome(message: Message):
    await message.answer("Привет! Отправь мне Excel-файл с данными (title, url, xpath).")


# Обработчик файлов
async def handle_file(message: Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "temp.xlsx")

    # Чтение файла
    df = pd.read_excel("temp.xlsx")
    data = df.to_dict('records')

    # Сохранение данных в базу
    save_to_temp_storage([(d['title'], d['url'], d['xpath']) for d in data])
    save_to_permanent_storage([(d['title'], d['url'], d['xpath']) for d in data])

    # Вывод данных пользователю
    response = "Данные из файла:\n"
    for i, d in enumerate(data, 1):
        response += f"{i}. {d['title']} - {d['url']} - {d['xpath']}\n"

    await message.answer(response)

    # Парсинг цен и расчет среднего
    prices = []
    temp_data = get_temp_data()
    for title, url, xpath in temp_data:
        price = await get_product_price(url, xpath)
        if price:
            prices.append(price)

    if prices:
        average_price = sum(prices) / len(prices)
        await message.answer(f"Средняя цена: {average_price}")
    else:
        await message.answer("Не удалось получить цены.")

    await message.answer("Можешь отправить новый файл!")

# Регистрация хэндлеров
dp.message.register(send_welcome, Command(commands=['start']))
dp.message.register(handle_file, F.content_type == "document")

# Асинхронный запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
