import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message

from datetime import datetime
#####
from config_plitkanadom import PLITKANADOM_BOT
from database_plitkanadom import create_table, add_user
from filter_params import categories

bot = Bot(token=PLITKANADOM_BOT)
dp = Dispatcher()

# Создаем маршрутизатор (router) для организации хэндлеров
router = Router()
dp.include_router(router)

logging.basicConfig(level=logging.INFO)
set_filter = '&set_filter=Y'


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
async def send_start(message: Message, state: FSMContext):
    user_data = await extract_user_data(message)
    # Меню для основного выбора
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Плитка", callback_data="plitka"))
    builder.add(InlineKeyboardButton(text="Сантехника", callback_data="santechnics"))
    builder.add(InlineKeyboardButton(text="Напольные покрытия", callback_data="floor"))

    # Отправляем сообщение с инлайн-кнопками
    await message.answer("Я чат-бот магазина керамической плитки, сантехники и напольных покрытий www.plitkanadom.ru"
                         "\nЯ могу помочь вам их подобрать:",
                         reply_markup=builder.as_markup())


# Функция для генерации кнопок на основе текущего шага
async def process_step(callback: types.CallbackQuery, state: FSMContext, category_key: str):
    # Получаем данные для текущего шага
    category_data = categories.get(category_key)
    options = category_data['options']

    # Сохраняем текущий шаг как предыдущий
    data = await state.get_data()
    previous_steps = data.get('previous_steps', [])
    previous_steps.append(category_key)
    await state.update_data(previous_steps=previous_steps)

    # Создаём кнопки для каждой опции
    builder = InlineKeyboardBuilder()
    for option, _ in options.items():
        builder.add(InlineKeyboardButton(text=option, callback_data=option))

    # Добавляем кнопку "Пропустить"
    builder.add(InlineKeyboardButton(text="Пропустить", callback_data=f"skip_{category_key}"))

    # Добавляем кнопку "Назад", только если есть предыдущие шаги
    if previous_steps:
        builder.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    builder.adjust(3)  # Расположить кнопки в 3 колонки

    # Обновляем сообщение с новым меню
    await callback.message.edit_text(category_data['text'], reply_markup=builder.as_markup())
    await callback.answer()


# Шаг 1. Обработка нажатий на кнопку "Плитка"
@router.callback_query(F.data == 'plitka')
async def plitka(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/collections/?'
    await state.update_data(url=url)

    # Переходим к первому шагу - выбор назначения плитки
    await process_step(callback, state, 'tile_type')


# Обработка нажатий на конкретные опции для каждой категории
@router.callback_query(F.data.in_(set([opt for category in categories.values() for opt in category['options'].keys()])))
async def handle_selection(callback: types.CallbackQuery, state: FSMContext):
    # Получаем текущий URL из состояния
    data = await state.get_data()
    url = data.get('url')

    # Находим категорию и соответствующий параметр
    for category_key, category_data in categories.items():
        if callback.data in category_data['options']:
            param = category_data['options'][callback.data]
            new_url = url + param
            await state.update_data(url=new_url)

            # Определяем следующий шаг
            next_step = category_data['next_step']
            if next_step:
                # Переход к следующему шагу
                await process_step(callback, state, next_step)
            else:
                # Это последний шаг, выводим финальную ссылку
                await callback.message.edit_text(f"Вы выбрали: {callback.data}.\nСсылка на коллекции: {new_url}")

            await callback.answer()
            return


# Обработка нажатий на "Пропустить"
@router.callback_query(F.data.startswith('skip_'))
async def handle_skip(callback: types.CallbackQuery, state: FSMContext):
    # Извлекаем категорию, которую пользователь пропустил
    category_key = callback.data.split('_')[1]
    # Получаем следующий шаг, если он есть
    category_data = categories.get(category_key)

    if category_data is None:
        # Если категория не найдена, возвращаем ошибку
        await callback.message.edit_text("Ошибка: категория не найдена.")
        await callback.answer()
        return

    next_step = category_data.get('next_step')

    if next_step:
        # Если есть следующий шаг, переходим к нему
        await process_step(callback, state, next_step)
    else:
        # Если это последний шаг, выводим итог
        data = await state.get_data()
        url = data.get('url')
        await callback.message.edit_text(f"Вы пропустили выбор.\nСсылка на коллекции: {url}")

    await callback.answer()


# Обработка команды "Назад"
@router.callback_query(F.data == 'start')
async def back_to_start(callback: types.CallbackQuery):
    # Возвращаемся к начальному меню
    await send_start(callback.message, None)
    await callback.answer()


async def main():
    await on_startup()  # Вызов функции на старте
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())