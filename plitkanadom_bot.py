import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from config_plitkanadom import PLITKANADOM_BOT
from database_plitkanadom import create_table, add_user
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

# Словарь, соответствующий каждому типу плитки и параметрам get_param
tile_params = {
    'Для ванной': '&arrFilter_45_1111111111=Y',
    'Керамогранит': '&arrFilter_45_2225864208=Y',
    'Мозаика': '&arrFilter_45_3333333333=Y',
    'Настенная плитка': '&arrFilter_45_4444444444=Y',
    'Напольная плитка': '&arrFilter_45_5555555555=Y',
    'Для кухни': '&arrFilter_45_6666666666=Y',
    'Ступени (клинкер)': '&arrFilter_45_7777777777=Y'
}

set_filter = '&set_filter=Y'

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

# Определяем состояние для FSM
class TileState(StatesGroup):
    tile_type = State()  # Состояние для типа плитки

@router.message(Command('start'))
async def send_start(message: Message, state: FSMContext):
    user_data = await extract_user_data(message)
    # Меню для основного выбора
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Плитка", callback_data="plitka"))
    builder.add(InlineKeyboardButton(text="Сантехника", callback_data="santechnics"))
    builder.add(InlineKeyboardButton(text="Напольные покрытия", callback_data="floor"))

    # Отправляем сообщение с инлайн-кнопками
    await message.answer("Добрый день! Я чат-бот магазина керамической плитки, сантехники и напольных покрытий www.plitkanadom.ru"
                         "\nЯ могу помочь вам их подобрать:",
                         reply_markup=builder.as_markup())

# Обработка нажатий на кнопку "Плитка"
@router.callback_query(F.data == 'plitka')
async def plitka(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/collections/?'
    # Меню для назначения плитки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Для ванной", callback_data="Для ванной"))
    builder.add(InlineKeyboardButton(text="Керамогранит", callback_data="Керамогранит"))
    builder.add(InlineKeyboardButton(text="Мозаика", callback_data="Мозаика"))
    builder.add(InlineKeyboardButton(text="Настенная плитка", callback_data="Настенная плитка"))
    builder.add(InlineKeyboardButton(text="Напольная плитка", callback_data="Напольная плитка"))
    builder.add(InlineKeyboardButton(text="Для кухни", callback_data="Для кухни"))
    builder.add(InlineKeyboardButton(text="Ступени (клинкер)", callback_data="Ступени (клинкер)"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="start"))
    # Настройка кнопок в две колонки
    builder.adjust(2)  # Каждая строка будет содержать 2 кнопки
    # Сохраняем URL в FSM-состояние (в качестве примера)
    await state.update_data(url=url)

    # Обновляем сообщение с новым меню
    await callback.message.edit_text(
        "Выберите назначение плитки:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка нажатий на конкретные назначения плитки
@router.callback_query(F.data.in_(tile_params.keys()))
async def handle_tile_selection(callback: types.CallbackQuery, state: FSMContext):
    # Получаем данные из FSM

    data = await state.get_data()
    print(data)
    url = data.get('url')
    print(url)
    # Присваиваем переменной значение в зависимости от нажатой кнопки
    tile_type = callback.data  # Здесь мы получаем, какой тип плитки был выбран
    print(tile_type)

    # Извлекаем соответствующий get_param для выбранного типа плитки
    get_param = tile_params.get(tile_type)

    # Формируем новый URL
    new_url = url + get_param + set_filter
    print(new_url)

    # Сохраняем выбранный тип плитки в FSM
    await state.update_data(tile_type=tile_type)
    # Выводим подтверждение выбора
    await callback.message.edit_text(f"Вы выбрали тип плитки: {tile_type}.\n"
                                     f"Ссылка на коллекции: {new_url}")
    await callback.answer()

# Обработка команды "Назад"
@router.callback_query(F.data == 'start')
async def back_to_start(callback: types.CallbackQuery):
    # Возвращаемся к начальному меню
    await send_start(callback.message, None)
    await callback.answer()

# Обработка выбора конкретного типа плитки (например, керамическая плитка)
# @router.callback_query(F.data == 'for_bathroom')
# async def ceramic_tile(callback: types.CallbackQuery):
#     # Создаем новое меню для выбора вариантов плитки
#     builder = InlineKeyboardBuilder()
#     builder.add(InlineKeyboardButton(text="Для ванной", callback_data="for_bathroom"))
#     builder.add(InlineKeyboardButton(text="Для пола", callback_data="for_floor"))
#     builder.add(InlineKeyboardButton(text="Мозаика", callback_data="mosaic"))
#     builder.add(InlineKeyboardButton(text="Назад", callback_data="start"))
#
#     await callback.message.answer("Вы выбрали: Керамическая плитка.")
#     # Обновляем сообщение с новым меню
#     await callback.message.edit_text(
#         "Выберите назначение плитки:",
#         reply_markup=builder.as_markup()
#     )
#     await callback.answer()
#


# Сантехника:
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