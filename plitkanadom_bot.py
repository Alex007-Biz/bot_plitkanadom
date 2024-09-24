import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database_plitkanadom import create_table, add_user
from datetime import datetime
from aiogram import Router
from config_plitkanadom import PLITKANADOM_BOT
# from telegram import Update
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# from openai import OpenAI
# client = OpenAI()


bot = Bot(token=PLITKANADOM_BOT)
dp = Dispatcher()

# Создаем маршрутизатор (router) для организации хэндлеров
router = Router()
dp.include_router(router)

logging.basicConfig(level=logging.INFO)

# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {
#             "role": "user",
#             "content": "Write a haiku about recursion in programming."
#         }
#     ]
# )
#
# print(completion.choices[0].message)

async def on_startup():
    await create_table()

async def extract_user_data(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    last_access = datetime.now().isoformat()
    # Сохраняем данные о пользователе
    await add_user(user_id, username, first_name, last_name, last_access)


@router.message(Command('start'))
async def send_start(message: Message):
    user_data = await extract_user_data(message)

    # Создаем инлайн-клавиатуру с основным меню
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Плитка", callback_data="plitka"))
    builder.add(InlineKeyboardButton(text="Сантехника", callback_data="santechnics"))
    builder.add(InlineKeyboardButton(text="Напольные покрытия", callback_data="floor"))

    # Отправляем сообщение с инлайн-кнопками
    await message.answer("Добрый день! Я чат-бот магазина керамической плитки, сантехники и напольных покрытий www.plitkanadom.ru"
                         "\nЯ могу помочь вам их подобрать:",
                         reply_markup=builder.as_markup())

# Обработка нажатий на инлайн-кнопки
@router.callback_query(F.data == 'plitka')
async def plitka(callback: types.CallbackQuery):
    # Создаем новое меню для выбора вариантов плитки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Керамическая плитка", callback_data="ceramic"))
    builder.add(InlineKeyboardButton(text="Керамогранит", callback_data="porcelain"))
    builder.add(InlineKeyboardButton(text="Мозаика", callback_data="mosaic"))

    # Обновляем сообщение с новым меню
    await callback.message.edit_text(
        "Выберите тип плитки:",
        reply_markup=builder.as_markup()
    )
    # Подтверждаем обработку callback
    await callback.answer()

# Обработка выбора конкретного типа плитки (например, керамическая плитка)
@router.callback_query(F.data == 'ceramic')
async def ceramic_tile(callback: types.CallbackQuery):
    await callback.message.answer("Вы выбрали: Керамическая плитка.")
    await callback.answer()


@router.callback_query(F.data == 'santechnics')
async def santechnics(callback: types.CallbackQuery):
    await callback.message.answer("Сантехника:")
    await callback.answer()

@router.callback_query(F.data == 'floor')
async def floor(callback: types.CallbackQuery):
    await callback.message.answer("Напольные покрытия:")
    await callback.answer()

async def main():
    await on_startup()  # Вызов функции на старте
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())