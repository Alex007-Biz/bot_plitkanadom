categories = {
    # Категория "Назначение" для плитки
    'Назначение': {
        'options': {
            'Для ванной': '&arrFilter_45_2367533627=Y',
            'Керамогранит': '&arrFilter_45_2225864208=Y',
            'Мозаика': '&arrFilter_45_336913281=Y',
            'Настенная плитка': '&arrFilter_45_326707096=Y',
            'Напольная плитка': '&arrFilter_45_1662243607=Y',
            'Для кухни': '&arrFilter_45_4196041389=Y',
            'Ступени (клинкер)': '&arrFilter_45_4088188550=Y'
        },
        'text': 'Выберите назначение плитки:',
        'next_step': 'Цвет'
    },
    # Категория "Цвет" для плитки
    'Цвет': {
        'options': {
            'Белый': '&arrFilter_44_734540143=Y',
            'Бежевый': '&arrFilter_44_1557070329=Y',
            'Желтый': '&arrFilter_44_1161005205=Y',
            'Голубой': '&arrFilter_44_895056922=Y',
            'Красный': '&arrFilter_44_3694844207=Y',
            'Розовый': '&arrFilter_44_842315779=Y',
            'Зеленый': '&arrFilter_44_1113476236=Y',
            'Коричневый': '&arrFilter_44_3429899368=Y',
            'Мультиколор': '&arrFilter_44_3795085693=Y',
            'Оранжевый': '&arrFilter_44_3145149694=Y',
            'Серый': '&arrFilter_44_3679919414=Y',
            'Синий': '&arrFilter_44_2890935712=Y',
            'Фиолетовый': '&arrFilter_44_2872961465=Y',
            'Черно-белый': '&arrFilter_44_2651089905=Y',
            'Черный': '&arrFilter_44_1273495719=Y',
        },
        'text': 'Выберите цвет плитки:',
        'next_step': 'Поверхность'  # Переход к следующему шагу - выбор поверхности
    },
    # Добавление "Поверхность" для плитки
    'Поверхность': {
        'options': {
            'Гладкая': '&surface=smooth',
            'Матовая': '&surface=matt',
            'Глянцевая': '&surface=glossy',
        },
        'text': 'Выберите поверхность плитки:',
        'next_step': 'Рисунок'
    },
    # Добавление "Рисунок" для плитки
    'Рисунок': {
        'options': {
            'Однотонная': '&pattern=solid',
            'С рисунком': '&pattern=patterned',
        },
        'text': 'Выберите рисунок плитки:',
        'next_step': 'Цена'
    },
    # Добавление "Цена" для плитки
    'Цена': {
        'options': {
            'До 1000 рублей': '&price=low',
            '1000-2000 рублей': '&price=medium',
            'Более 2000 рублей': '&price=high',
        },
        'text': 'Выберите диапазон цены:',
        'next_step': None  # Это последний шаг
    },
    # Новая категория "Тип сантехники"
    'Тип сантехники': {
        'options': {
            'Ванны': '&arrFilter_51_436075299=Y',
            'Унитазы': '&arrFilter_51_234612522=Y',
            'Раковины': '&arrFilter_51_1637612205=Y',
            'Душевые кабины': '&arrFilter_51_3910412085=Y',
            'Смесители': '&arrFilter_51_341297207=Y',
            'Биде': '&arrFilter_51_4243672784=Y',
        },
        'text': 'Выберите тип сантехники:',
        'next_step': 'Бренд сантехники'
    },
    # Добавление "Бренд сантехники"
    'Бренд сантехники': {
        'options': {
            'Roca': '&arrFilter_52_3420982455=Y',
            'Grohe': '&arrFilter_52_1320975589=Y',
            'Hansgrohe': '&arrFilter_52_278352087=Y',
            'Villeroy & Boch': '&arrFilter_52_2898127547=Y',
        },
        'text': 'Выберите бренд сантехники:',
        'next_step': 'Цена сантехники'
    },
    # Добавление "Цена сантехники"
    'Цена сантехники': {
        'options': {
            'До 5000 рублей': '&price=low',
            '5000-10000 рублей': '&price=medium',
            'Более 10000 рублей': '&price=high',
        },
        'text': 'Выберите диапазон цены сантехники:',
        'next_step': None  # Это последний шаг
    },
    # Новая категория "Тип покрытия"
    'Тип покрытия': {
        'options': {
            'Ламинат': '&arrFilter_53_213090400=Y',
            'Паркетная доска': '&arrFilter_53_4089585740=Y',
            'Ковролин': '&arrFilter_53_136758936=Y',
            'Виниловая плитка': '&arrFilter_53_273526781=Y',
            'Линолеум': '&arrFilter_53_378617391=Y',
        },
        'text': 'Выберите тип напольного покрытия:',
        'next_step': 'Цвет покрытия'
    },
    # Добавление "Цвет покрытия"
    'Цвет покрытия': {
        'options': {
            'Светлый': '&arrFilter_54_123349847=Y',
            'Темный': '&arrFilter_54_834960847=Y',
            'Серый': '&arrFilter_54_2323418937=Y',
            'Деревянный оттенок': '&arrFilter_54_121432134=Y',
        },
        'text': 'Выберите цвет покрытия:',
        'next_step': 'Цена покрытия'
    },
    # Добавление "Цена покрытия"
    'Цена покрытия': {
        'options': {
            'До 500 рублей': '&price=low',
            '500-1000 рублей': '&price=medium',
            'Более 1000 рублей': '&price=high',
        },
        'text': 'Выберите диапазон цены напольного покрытия:',
        'next_step': None  # Это последний шаг
    }
}