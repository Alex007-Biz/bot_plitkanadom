import asyncio
import logging
import re
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
    # print(f"category_data: {category_data}")
    options = category_data['options']
    # print(f"options: {options}")

    # Получаем данные о предыдущих шагах
    data = await state.get_data()
    # print(f"data: {data}")
    previous_steps = data.get('previous_steps', [])
    # print(f"previous_steps: {previous_steps}")

    # Если selected_options еще не существует, инициализируем его как пустой словарь
    selected_options = data.get('selected_options', {})

    # Обработка нажатия кнопки "Назад"
    if callback.data == "back" and len(previous_steps) > 1:
        print(f"Before popping: {previous_steps}")
        # previous_steps.pop()  # НЕ удаляем последний шаг!!!
        category_key = previous_steps[-1]  # Берем предыдущий шаг (последний в списке)
        print(f"category_key: {category_key}")
        category_data = categories.get(category_key)
        options = category_data['options']
        # print(f"options: {options}")
    else:
        if category_key not in previous_steps:
            previous_steps.append(category_key)  # Добавляем текущий шаг, только если это не "Назад"

    # Сохраняем обновленные шаги и выбранные опции
    await state.update_data(previous_steps=previous_steps, selected_options=selected_options)

    # Создаём кнопки для каждой опции
    builder = InlineKeyboardBuilder()
    for option, _ in options.items():
        builder.add(InlineKeyboardButton(text=option, callback_data=option))

    # Добавляем кнопку "Пропустить"
    builder.add(InlineKeyboardButton(text="Пропустить", callback_data=f"skip_{category_key}"))

    # Добавляем кнопку "Назад", если есть предыдущие шаги
    print(f"len(previous_steps): {len(previous_steps)}")
    if len(previous_steps) > 1:
        builder.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    builder.adjust(3)  # Расположить кнопки в 3 колонки

    # Проверяем, изменилось ли сообщение
    current_text = category_data['text']
    current_reply_markup = builder.as_markup()
    print(f"current_text: {current_text}")

    # Обновляем сообщение с новым текстом и клавиатурой
    if callback.message.text != current_text or callback.message.reply_markup != current_reply_markup:
        # Обновляем сообщение с новым текстом и клавиатурой
        await callback.message.edit_text(current_text, reply_markup=current_reply_markup)
    else:
        # Если текст и разметка не изменились, просто отправляем callback ответ
        await callback.answer()


# Шаг 1. Обработка нажатий на кнопку "Плитка"
@router.callback_query(F.data == 'plitka')
async def plitka(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/collections/?'
    await state.update_data(url=url)

    # Переходим к первому шагу - выбор назначения плитки
    await process_step(callback, state, 'Назначение')


# Обработка нажатий на конкретные опции для каждой категории
@router.callback_query(F.data.in_(set([opt for category in categories.values() for opt in category['options'].keys()])))
async def handle_selection(callback: types.CallbackQuery, state: FSMContext):
    # Получаем текущий URL из состояния
    data = await state.get_data()
    # print(f"data: {data}")
    # url = data.get('url')
    # print(f"url: {url}")
    previous_steps = data.get('previous_steps', [])
    selected_options = data.get('selected_options', {})

    # Находим категорию и соответствующий параметр
    for category_key, category_data in categories.items():
        if callback.data in category_data['options']:
            # Сохраняем выбранную опцию в состоянии
            selected_options[category_key] = category_data['options'][callback.data]
            print(f"selected_options: {selected_options}")
            await state.update_data(selected_options=selected_options)

            # Сообщение пользователю с выбранной опцией
            category_name = category_data.get('name', category_key)
            option_name = callback.data
            await callback.message.answer(f"{category_name}: {option_name}")

            # Определяем следующий шаг
            next_step = category_data['next_step']
            if next_step:
                # Переход к следующему шагу
                await process_step(callback, state, next_step)
            else:
                # Это последний шаг, формируем и выводим финальную ссылку на основании selected_options
                base_url = 'https://www.plitkanadom.ru/collections/?'
                # Формируем URL на основе выбранных опций
                params = '&'.join(selected_options.values())
                print(f"params: {params}")
                final_url = base_url + params + set_filter
                print(f"final_url: {final_url}")

                # Вывод финальной ссылки
                await callback.message.answer(f"Ссылка на выбранные товары: {final_url}")

            await callback.answer()
            return


# Обработка нажатий на "Пропустить"
@router.callback_query(F.data.startswith('skip_'))
async def handle_skip(callback: types.CallbackQuery, state: FSMContext):
    category_key = callback.data[len('skip_'):]
    data = await state.get_data()

    # Получаем выбранные опции из состояния
    selected_options = data.get('selected_options', {})  # Инициализируем selected_options, если его нет
    previous_steps = data.get('previous_steps', [])

    print(f"selected_options до пропуска: {selected_options}")

    # Получаем следующий шаг, если он есть
    category_data = categories.get(category_key)

    # Добавляем пропущенный шаг в selected_options как пустой (или с другим специальным значением)
    selected_options[category_key] = ''  # Пропуск шага

    # Обновляем состояние
    await state.update_data(selected_options=selected_options)

    # Добавляем текущий шаг в previous_steps
    previous_steps.append(category_key)
    await state.update_data(previous_steps=previous_steps)

    next_step = category_data.get('next_step')
    print(f"next_step: {next_step}")

    if next_step:
        # Если есть следующий шаг, переходим к нему
        await process_step(callback, state, next_step)
    else:
        # Это последний шаг, формируем и выводим финальную ссылку на основании selected_options
        base_url = 'https://www.plitkanadom.ru/collections/?'
        # Формируем URL на основе выбранных опций
        params = '&'.join(filter(None, selected_options.values()))  # Исключаем пустые значения из URL
        print(f"params: {params}")
        final_url = base_url + params + set_filter
        print(f"final_url: {final_url}")

        # Вывод финальной ссылки
        await callback.message.answer(f"Ссылка на выбранные товары: {final_url}")

    await callback.answer()

# Обработка кнопки "Назад"
@router.callback_query(F.data == 'back')
async def handle_back(callback: types.CallbackQuery, state: FSMContext):
    print(f"Нажатие Назад")

    # Получаем данные из состояния
    data = await state.get_data()
    previous_steps = data.get('previous_steps', [])
    selected_options = data.get('selected_options', {})  # Инициализируем selected_options, если его нет
    # url = data.get('url', '')

    # print(f"url после previous_steps: {url}")
    print(f"previous_steps: {previous_steps}")
    print(f"selected_options: {selected_options}")

    # Удаляем текущий шаг и откатываем URL
    if len(previous_steps) > 1:
        current_step = previous_steps.pop()  # Удаляем текущий шаг
        previous_step = previous_steps[-1]  # Получаем предыдущий шаг
        print(f"Текущий шаг (current_step): {current_step}")
        print(f"Предыдущий шаг (previous_step): {previous_step}")

        # Удаляем последний выбранный параметр, если он был сохранён
        selected_options.pop(current_step, None)
        print(f"selected_options после удаления текущего шага: {selected_options}")

        # Обновляем состояние с откорректированными предыдущими шагами, выбранными опциями и URL
        await state.update_data(previous_steps=previous_steps, selected_options=selected_options)

        # Переходим на предыдущий шаг
        await process_step(callback, state, previous_step)
    else:
        # Если шагов для возврата нет, отправляем сообщение о невозможности вернуться назад
        await callback.answer("Вы не можете вернуться назад с текущего шага.", show_alert=True)

    await callback.answer()


async def main():
    await on_startup()  # Вызов функции на старте
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())