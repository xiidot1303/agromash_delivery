class Strings:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def __getattribute__(self, key: str):
        if result := object.__getattribute__(self, key):
            if isinstance(result, list):
                from bot.services.redis_service import get_user_lang
                user_id = object.__getattribute__(self, "user_id")
                user_lang_code = get_user_lang(user_id)
                return result[user_lang_code]
            else:
                return result
        else:
            return key

    hello = """🤖 Xush kelibsiz!\n Bot tilini tanlang  🌎 \n\n ➖➖➖➖➖➖➖➖➖➖➖➖\n
    👋 Добро пожаловать \n \U0001F1FA\U0001F1FF Выберите язык бота \U0001F1F7\U0001F1FA"""
    added_group = "Чат успешно добавлена ✅"
    uz_ru = ["UZ 🇺🇿", "RU 🇷🇺"]
    main_menu = ["Asosiy menyu 🏠", "Главное меню 🏠"]
    change_lang = [
        "\U0001F1FA\U0001F1FF Tilni o'zgartirish \U0001F1F7\U0001F1FA",
        "\U0001F1FA\U0001F1FF Сменить язык \U0001F1F7\U0001F1FA",
    ]
    select_lang = [""" Tilni tanlang """, """Выберите язык бота """]
    type_name = ["""Ismingizni kiriting """, """Введите ваше имя """]
    send_number = [
        """Telefon raqamingizni yuboring """,
        """Оставьте свой номер телефона """,
    ]
    leave_number = ["Telefon raqamni yuborish", "Оставить номер телефона"]
    back = ["""🔙 Ortga""", """🔙 Назад"""]
    next_step = ["""Davom etish ➡️""", """Далее ➡️"""]
    seller = ["""Sotuvchi 🛍""", """Продавцам 🛍"""]
    buyer = ["""Xaridor 💵""", """Покупателям 💵"""]
    settings = ["""Sozlamalar ⚙️""", """Настройки ⚙️"""]
    language_change = ["""Tilni o\'zgartirish 🇺🇿🇷🇺""", """Смена языка 🇺🇿🇷🇺"""]
    change_phone_number = [
        """Telefon raqamni o\'zgartirish 📞""",
        """Смена номера телефона 📞""",
    ]
    change_name = ["""Ismni o\'zgartirish 👤""", """Смени имени 👤"""]
    settings_desc = ["""Sozlamalar ⚙️""", """Настройки ⚙️"""]
    your_phone_number = [
        """📌 Sizning telefon raqamingiz: [] 📌""",
        """📌 Ваш номер телефона: [] 📌""",
    ]
    send_new_phone_number = [
        """Yangi telefon raqamingizni yuboring!\n<i>Jarayonni bekor qilish uchun "🔙 Ortga" tugmasini bosing.</i>""",
        """Отправьте свой новый номер телефона!\n<i>Нажмите кнопку "🔙 Назад", чтобы отменить процесс.</i>""",
    ]
    number_is_logged = [
        "Bunday raqam bilan ro'yxatdan o'tilgan, boshqa telefon raqam kiriting",
        "Этот номер уже зарегистрирован. Введите другой номер",
    ]
    changed_your_phone_number = [
        """Sizning telefon raqamingiz muvaffaqiyatli o\'zgartirildi! ♻️""",
        """Ваш номер телефона успешно изменен! ♻️""",
    ]
    your_name = ["""Sizning ismingiz: """, """Ваше имя: """]
    send_new_name = [
        """Ismingizni o'zgartirish uchun, yangi ism kiriting:\n<i>Jarayonni bekor qilish uchun "🔙 Ortga" tugmasini bosing.</i>""",
        """Чтобы изменить свое имя, введите новое:\n<i>Нажмите кнопку "🔙 Назад", чтобы отменить процесс.</i>""",
    ]
    changed_your_name = [
        """Sizning ismingiz muvaffaqiyatli o'zgartirildi!""",
        """Ваше имя успешно изменено!""",
    ]
    select_region = ["""Hududingizni tanlang""", """Выберите ваш регион"""]
    select_car_brand = ["Mashina brendini tanlang", "Выберите марку машины"]
    select_product_type = ["Mahsulot turini tanlang", "Выберите тип продукта"]
    select_product_size = ["Mahsulot o'lchamini tanlang", "Выберите размер продукта"]
    select_product = [
        "Qidiruv tugmasini bosgan holda, mahsulotni tanlang 🔖",
        "Выберите продукт, нажав кнопку поиска 🔖"
    ]

    regions = [
        [
            "Toshkent", "Samarkand", "Buxoro", "Andijon", "Farg'ona", "Namangan",
            "Qashqadaryo", "Surxondaryo", "Xorazm", "Navoiy", "Jizzax", "Sirdaryo", "Qoraqalpog'iston"

        ],
        [
            "Ташкент", "Самарканд", "Бухара", "Андижан", "Фергана", "Наманган",
            "Кашкадарья", "Сурхандарья", "Хорезм", "Навои", "Джизак", "Сырдарья", "Каракалпакстан"
        ]
    ]

    cart = [
        "🛒 Savatcha",
        "🛒 Корзина"
    ]

    added_to_cart = [
        "Savatga qo'shildi. Siz savatga boshqa mahsulotlarni qo'shishingiz yoki buyurtmani rasmiylashtirishingiz mumkin.",
        "Добавлен в корзину. Вы можете добавить другие продукты в корзину или оформить заказ."
    ]

    price = [
        "Narxi",
        "Цена"
    ]

    confirm_order = [
        "☑️ Buyurtma berish",
        "☑️ Оформить заказ"
    ]

    your_order_accepted = [
        "Sizning buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        "Ваш заказ принят! Мы свяжемся с вами в ближайшее время."
    ]
    
    add_to_cart = [
        "➕ Savatga qo'shish",
        "➕ Добавить в корзину"
    ]
    
    get_location = ["🗺 Manzilingizni yuboring", "🗺 Отправьте ваш адрес"]

    send_location = [
        "📍 Lokatsiya yuborish",
        "📍 Отправить местоположение"
        ]

    get_delivery_time = ["Yetkazib berish vaqtini kiriting", "Введите время доставки"]

    get_payment_type = ["To'lov turini tanlang", "Выберите тип оплаты"]

    get_comment = ["Izoh qoldiring", "Оставьте комментарий"]

    payment_types = [
        ["Naqd", "Kartadan karta", "Bank o'tkazmasi"], 
        ["Наличные", "С карты на карту", "Банковский перевод"]
    ]
    
    order = [
        "🛒 Buyurtma berish",
        "🛒 Заказать"
    ]
    
    search_products = [
        "🔍 Mahsulotlarni qidirish",
        "🔍 Поиск продуктов"
    ]
    
    continue_shopping = [
        "🔄 Xaridlarni davom ettirish",
        "🔄 Продолжить покупки"
    ]
    
    cart_empty = [
        "Savatchangiz bo'sh",
        "Ваша корзина пуста"
    ]

    total_price = [
        "Umumiy narx",
        "Общая цена"
    ]

    search_sizes = [
        "🔎 O'lchamlarni qidirish",
        "🔎 Поиск размеров"
    ]

    search = [
        "🔎 Qidirish",
        "🔎 Поиск"
    ]
    
    enter_at_least_3_characters = [
        "📝 Kamida 3 ta belgini kiriting",
        "📝 Введите минимум 3 символа"
    ]
    
    no_products_found = [
        "✖️ Mahsulot topilmadi",
        "✖️ Продукты не найдены"
    ]
    
    to_empty_cart = [
        "🧹 Savatchani bo'shatish",
        "🧹 Очистить корзину"
    ]
    
    cart_cleared = [
        "✔️ Savatchangiz bo'shatildi.",
        "✔️ Ваша корзина очищена."
    ]
    
    result_of_the_search = [
        "🔍 Qidiruv natijalari",
        "🔍 Результаты поиска"
    ]
    
    _ = [
        "",
        ""
    ]
    
    _ = [
        "",
        ""
    ]
