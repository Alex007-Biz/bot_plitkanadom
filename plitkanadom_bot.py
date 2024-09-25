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
#####
from config_plitkanadom import PLITKANADOM_BOT
from database_plitkanadom import create_table, add_user
from filter_params import tile_params, tile_colors
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



# set_filter = '&set_filter=Y'

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
# class TileState(StatesGroup):
#     tile_type = State()  # Состояние для типа плитки

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

# Шаг 1. Обработка нажатий на кнопку "Плитка"
@router.callback_query(F.data == 'plitka')
async def plitka(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/collections/?'
    # Меню для назначения плитки
    builder = InlineKeyboardBuilder()
    for param in tile_params:
        builder.add(InlineKeyboardButton(text=param, callback_data=param))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="start"))
    builder.adjust(2)  # Каждая строка будет содержать 2 кнопки
    # Сохраняем URL в FSM-состояние
    await state.update_data(url=url)

    # Обновляем сообщение с новым меню
    await callback.message.edit_text(
        "Выберите назначение плитки:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Шаг 2. Обработка нажатий на конкретные назначения плитки
@router.callback_query(F.data.in_(tile_params.keys()))
async def handle_tile_selection(callback: types.CallbackQuery, state: FSMContext):
    # Получаем данные из FSM:
    data = await state.get_data()
    url = data.get('url')
    # Присваиваем переменной значение в зависимости от нажатой кнопки
    tile_type = callback.data
    print(tile_type)

    # Извлекаем соответствующий get_param для выбранного типа плитки
    get_param = tile_params.get(tile_type)


    # Сохраняем новый URL с параметром типа плитки
    new_url = url + get_param
    print(new_url)
    await state.update_data(url=new_url)
    print(url)
    # Выводим подтверждение выбора
    # await callback.message.edit_text(f"Назначение плитки: {tile_type}")

    # Переход к выбору цвета плитки
    builder = InlineKeyboardBuilder()
    for color in tile_colors:
        builder.add(InlineKeyboardButton(text=color, callback_data=color))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="plitka"))
    builder.adjust(3)

    # Обновляем сообщение с меню выбора цвета
    await callback.message.edit_text(
        f"Вы выбрали тип плитки: {tile_type}.\nТеперь выберите цвет плитки:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Шаг 3. Обработка нажатий на конкретный цвет плитки
@router.callback_query(F.data.in_(tile_colors.keys()))
async def handle_tile_color_selection(callback: types.CallbackQuery, state: FSMContext):
    # Получаем данные из FSM
    data = await state.get_data()
    url = data.get('url')

    # Присваиваем переменной значение цвета
    tile_color = callback.data
    # Извлекаем соответствующий параметр для выбранного цвета
    color_param = tile_colors.get(tile_color)
    # Формируем новый URL с учетом цвета и типа плитки
    new_url = url + color_param + '&set_filter=Y'

    # Сохраняем выбранный цвет плитки в FSM
    await state.update_data(tile_color=tile_color)

    # Выводим итоговую ссылку на выбранные коллекции
    await callback.message.edit_text(f"Вы выбрали цвет плитки: {tile_color}.\n"
                                     f"Ссылка на коллекции: {new_url}")
    await callback.answer()

# Обработка команды "Назад"
@router.callback_query(F.data == 'start')
async def back_to_start(callback: types.CallbackQuery):
    # Возвращаемся к начальному меню
    await send_start(callback.message, None)
    await callback.answer()




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