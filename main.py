import asyncio
import aiohttp
import aiosqlite

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

TOKEN = "8454016867:AAGFJKrH-itbUs_OqfigmtG6qtneKwKgp4o"
CRYPTO_TOKEN = "CRYPTO_PAY_TOKEN"
OWNER = "your_username"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# DATABASE
# =========================

async def create_db():

    async with aiosqlite.connect("shop.db") as db:

        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            purchases INTEGER DEFAULT 0,
            balance INTEGER DEFAULT 0
        )
        ''')

        await db.commit()


# =========================
# PRODUCTS
# =========================

products = {

    "gems": [
        ("30 Gems", 3),
        ("80 Gems", 6),
        ("170 Gems", 12),
        ("360 Gems", 25),
        ("950 Gems", 60)
    ],

    "battlepass": [
        ("Brawl Pass", 10),
        ("Brawl Pass Plus", 20)
    ],

    "boost": [
        ("Bronze → Silver", 10),
        ("Silver → Gold", 20),
        ("Gold → Diamond", 50),
        ("Diamond → Mythic", 100),
        ("Mythic → Legendary", 250)
    ],

    "quests": [
        ("Daily Quests", 5),
        ("Season Quests", 15),
        ("Mastery", 20)
    ],

    "training": [
        ("1 Hour Training", 15),
        ("Aim Training", 20),
        ("Rank Coaching", 30)
    ]
}


# =========================
# MENUS
# =========================


def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="💎 Gems",
                    callback_data="gems"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎟 Battle Pass",
                    callback_data="battlepass"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏆 Буст ранга",
                    callback_data="boost"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎯 Квесты",
                    callback_data="quests"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎓 Обучение",
                    callback_data="training"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👤 Профиль",
                    callback_data="profile"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛠 Поддержка",
                    url=f"https://t.me/{OWNER}"
                )
            ]
        ]
    )


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    text = f"""
🔥 Добро пожаловать в Brawl Stars Shop!

━━━━━━━━━━━━━━━

Здесь ты можешь:

💎 Купить Gems
🎟 Купить Battle Pass
🏆 Заказать буст ранга
🎯 Выполнить квесты
🎓 Заказать обучение
⚡ Прокачать аккаунт

━━━━━━━━━━━━━━━

📖 Как купить:

1️⃣ Выбери услугу
2️⃣ Нажми купить
3️⃣ Оплати через CryptoBot
4️⃣ Получи товар автоматически

━━━━━━━━━━━━━━━

🎁 Бонусы:

✅ Промокоды
✅ Скидки
✅ Подарки
✅ Бонусы за покупки

━━━━━━━━━━━━━━━

🛠 Поддержка:
@{OWNER}
"""

    await message.answer(
        text,
        reply_markup=main_menu()
    )


# =========================
# PROFILE
# =========================

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    text = f"""
👤 Ваш профиль

🆔 ID: {callback.from_user.id}

💰 Баланс: 0$
🛒 Покупок: 0
🎁 Бонусов: 0

━━━━━━━━━━━━━━━

🔥 VIP бонусы:

5 покупок → скидка 5%
10 покупок → скидка 10%
20 покупок → VIP статус
"""

    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# SHOW PRODUCTS
# =========================

@dp.callback_query(
    F.data.in_([
        "gems",
        "battlepass",
        "boost",
        "quests",
        "training"
    ])
)
async def show_products(callback: CallbackQuery):

    category = callback.data

    text = "🛒 Доступные товары:"



    keyboard = []

    for item, price in products[category]:

        text += f"🎯 {item} — {price}$"


        keyboard.append([
            InlineKeyboardButton(
                text=f"Купить {item}",
                callback_data=f"buy:{item}:{price}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back"
        )
    ])

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )


# =========================
# CREATE PAYMENT
# =========================

async def create_invoice(amount):

    url = "https://pay.crypt.bot/api/createInvoice"

    headers = {
        "Crypto-Pay-API-Token": CRYPTO_TOKEN
    }

    data = {
        "asset": "USDT",
        "amount": amount
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(
            url,
            headers=headers,
            json=data
        ) as response:

            result = await response.json()

            return result["result"]["pay_url"]


# =========================
# BUY
# =========================

@dp.callback_query(F.data.startswith("buy:"))
async def buy(callback: CallbackQuery):

    data = callback.data.split(":")

    product = data[1]
    price = data[2]

    pay_url = await create_invoice(price)

    text = f"""
💳 Оплата товара

🎯 Товар: {product}
💰 Цена: {price}$

━━━━━━━━━━━━━━━

После оплаты товар будет выдан автоматически.
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Оплатить",
                    url=pay_url
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛠 Поддержка",
                    url=f"https://t.me/{OWNER}"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )


# =========================
# BACK
# =========================

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):

    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )


# =========================
# RUN
# =========================

async def main():

    await create_db()

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
