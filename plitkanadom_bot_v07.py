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
from filter_params import tile_categories, santechnika_categories, floor_categories

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
    # Инициализируем предыдущие шаги и выбранные опции при старте
    await state.update_data(previous_steps=[], selected_options={})

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
    data = await state.get_data()
    current_category = data.get('current_category')
    print(f"current_category: {current_category}")
    # Выбираем правильный словарь категорий
    if current_category == 'tiles':
        categories = tile_categories
    elif current_category == 'santechnika':
        categories = santechnika_categories
    elif current_category == 'floor':
        categories = floor_categories
    else:
        await callback.message.answer("Ошибка: текущая категория не определена.")
        return

    category_data = categories.get(category_key)
    if not category_data:
        await callback.message.answer("Ошибка: категория не найдена.")
        return

    options = category_data['options']

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

    # Обновляем сообщение с новым текстом и клавиатурой
    current_text = category_data['text']
    current_reply_markup = builder.as_markup()
    print(f"current_text: {current_text}")
    if callback.message.text != current_text or callback.message.reply_markup != current_reply_markup:
        # Обновляем сообщение с новым текстом и клавиатурой
        await callback.message.edit_text(current_text, reply_markup=current_reply_markup)
    else:
        # Если текст и разметка не изменились, просто отправляем callback ответ
        await callback.answer()


# Обработка выбора "Плитка"
@router.callback_query(F.data == 'plitka')
async def plitka(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/collections/?'
    await state.update_data(url=url, current_category='tiles')
    await process_step(callback, state, 'Назначение плитки')

# Обработка выбора "Сантехника"
@router.callback_query(F.data == 'santechnics')
async def santechnics(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/santekhnika?'
    await state.update_data(url=url, current_category='santechnika')
    await process_step(callback, state, 'Тип сантехники')

# Обработка выбора категории "Напольные покрытия"
@router.callback_query(F.data == 'floor')
async def floor(callback: types.CallbackQuery, state: FSMContext):
    url = 'https://www.plitkanadom.ru/napolnye-pokrytiya/?'
    await state.update_data(url=url, current_category='floor')

    # Переходим к первому шагу - выбор типа покрытия
    await process_step(callback, state, 'Тип покрытия')


# Собираем все опции из обоих словарей
tile_options = set(opt for cat in tile_categories.values() for opt in cat['options'])
santechnika_options = set(opt for cat in santechnika_categories.values() for opt in cat['options'])
all_options = tile_options.union(santechnika_options)


# Обработка нажатий на конкретные опции для каждой категории
@router.callback_query(F.data)
async def handle_selection(callback: types.CallbackQuery, state: FSMContext):
    # Проверяем, если данные начинаются с "skip_", то перенаправляем их в handle_skip
    if callback.data.startswith('skip_'):
        await handle_skip(callback, state)
        return

    # Проверяем, если нажата кнопка "Назад"
    if callback.data == 'back':
        await handle_back(callback, state)  # Перенаправляем в обработчик кнопки "Назад"
        return

    # Получаем текущий URL из состояния
    data = await state.get_data()
    print(f"data: {data}")
    current_category = data.get('current_category')
    print(f"current_category: {current_category}")
    previous_steps = data.get('previous_steps', [])
    print(f"previous_steps: {previous_steps}")
    selected_options = data.get('selected_options', {})
    print(f"selected_options: {selected_options}")

    # Выбираем правильный словарь категорий
    if current_category == 'tiles':
        categories = tile_categories
        print(f"current_category == 'tiles'")
    elif current_category == 'santechnika':
        categories = santechnika_categories
    elif current_category == 'floor':
        categories = floor_categories
    else:
        await callback.message.answer("Ошибка: текущая категория не определена.")
        return
    # Выводим callback.data для отладки
    print(f"Callback data: {callback.data}")

    # Проверяем, существует ли выбранная опция в текущей категории
    for category_key, category_data in categories.items():
        option_value = category_data['options'].get(callback.data)
        print(f"option_value: {option_value}")
        if option_value:
            selected_options[category_key] = option_value
            await state.update_data(selected_options=selected_options)

            # Сообщение пользователю с выбранной опцией
            category_name = category_data.get('name', category_key)
            print(f"category_name: {category_name}")
            option_name = callback.data
            print(f"option_name: {option_name}")
            await callback.message.answer(f"{category_name}: {option_name}")

            # Определяем следующий шаг
            next_step = category_data.get('next_step')
            print(f"next_step: {next_step}")

            if next_step:
                # Переход к следующему шагу
                await process_step(callback, state, next_step)
            else:
                # Это последний шаг, формируем финальную ссылку
                url = data.get('url')
                # Исключаем шаги, где значение 'skipped'
                params = ''.join(value for key, value in selected_options.items() if value != 'skipped')

                final_url = url + params + set_filter
                # Удаляем все лишние символы "?", оставляя только один
                final_url = final_url.replace('?', '', final_url.count('?') - 1)
                print(f"final_url: {final_url}")
                await callback.message.answer(f"Ссылка на выбранные товары: {final_url}")

            await callback.answer()
            return

    # Если опция не найдена
    await callback.message.answer("Ошибка: выбранная опция не найдена.")
    


# Обработка нажатий на "Пропустить"
@router.callback_query(F.data.startswith('skip_'))
async def handle_skip(callback: types.CallbackQuery, state: FSMContext):
    category_key = callback.data[len('skip_'):]
    data = await state.get_data()

    # Получаем выбранные опции из состояния
    selected_options = data.get('selected_options', {})  # Инициализируем selected_options, если его нет
    previous_steps = data.get('previous_steps', [])

    # Определяем текущие категории для обработки
    current_category = data.get('current_category')
    if current_category == 'tiles':
        categories = tile_categories
    elif current_category == 'santechnika':
        categories = santechnika_categories
    elif current_category == 'floor':
        categories = floor_categories
    else:
        await callback.message.answer("Ошибка: текущая категория не определена.")
        return

    # Проверка на существование категории
    category_data = categories.get(category_key)
    if not category_data:
        await callback.message.answer("Ошибка: категория для пропуска не найдена.")
        return

    # Обновляем выбранную категорию с пометкой "skipped"
    selected_options[category_key] = 'skipped'  # Пропуск шага

    # Обновляем состояние
    await state.update_data(selected_options=selected_options)

    # Добавляем текущий шаг в previous_steps
    if category_key not in previous_steps:
        previous_steps.append(category_key)
    await state.update_data(previous_steps=previous_steps)

    # Получаем следующий шаг
    next_step = category_data.get('next_step')
    if next_step:
        # Если есть следующий шаг, переходим к нему
        await process_step(callback, state, next_step)
    else:
        # Это последний шаг, формируем финальную ссылку
        url = data.get('url')  # Извлекаем значение 'url' из состояния
        # Исключаем шаги, где значение 'skipped'
        params = ''.join(value for key, value in selected_options.items() if value != 'skipped')
        final_url = url + params + set_filter
        # Удаляем все лишние символы "?", оставляя только один
        final_url = final_url.replace('?', '', final_url.count('?') - 1)
        await callback.message.answer(f"Ссылка на выбранные товары: {final_url}")

    await callback.answer()

# Обработка кнопки "Назад"
@router.callback_query(F.data == 'back')
async def handle_back(callback: types.CallbackQuery, state: FSMContext):
    print("Нажатие Назад")

    # Получаем данные из состояния
    data = await state.get_data()
    previous_steps = data.get('previous_steps', [])
    selected_options = data.get('selected_options', {})

    # Проверка на наличие шагов для возврата
    if len(previous_steps) > 1:
        current_step = previous_steps.pop()  # Удаляем текущий шаг
        previous_step = previous_steps[-1]  # Получаем предыдущий шаг

        # Удаляем последний выбранный параметр, если он был сохранён
        if current_step in selected_options:
            selected_options.pop(current_step)

        # Обновляем состояние с откорректированными предыдущими шагами и выбранными опциями
        await state.update_data(previous_steps=previous_steps, selected_options=selected_options)

        # Определяем текущие категории для обработки
        current_category = data.get('current_category')
        if current_category == 'tiles':
            categories = tile_categories
        elif current_category == 'santechnika':
            categories = santechnika_categories
        elif current_category == 'floor':
            categories = floor_categories
        else:
            await callback.message.answer("Ошибка: текущая категория не определена.")
            return

        # Проверяем, существует ли предыдущий шаг в текущей категории
        category_data = categories.get(previous_step)
        if category_data:
            # Переходим на предыдущий шаг
            await process_step(callback, state, previous_step)
        else:
            await callback.message.answer("Ошибка: предыдущий шаг не найден.")
    else:
        # Если шагов для возврата нет
        await callback.answer("Вы не можете вернуться назад с текущего шага.", show_alert=True)

    await callback.answer()


async def main():
    await on_startup()  # Вызов функции на старте
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())