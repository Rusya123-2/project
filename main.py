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
QKASSA_URL = "https://qassa.top/pay/YOUR_SHOP_ID"
OWNER = "username"

bot = Bot(TOKEN)
dp = Dispatcher()

product_photos = {
    "gems": "https://i.imgur.com/4G6N9Gk.jpeg",
    "pass": "https://i.imgur.com/6RL6p9x.jpeg",
    "boost": "https://i.imgur.com/8KZP7kA.jpeg"
}

products = {
    "gems": [
        ("30 Gems", 299),
        ("80 Gems", 499),
        ("170 Gems", 899)
    ],

    "pass": [
        ("Brawl Pass", 799),
        ("Brawl Pass Plus", 1499)
    ],

    "boost": [
        ("Silver -> Gold", 990),
        ("Gold -> Diamond", 1990)
    ]
}


async def create_db():
    async with aiosqlite.connect("shop.db") as db:

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                purchases INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0
            )
            """
        )

        await db.commit()


def menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💎 Gems", callback_data="gems")],
            [InlineKeyboardButton(text="🎟 Pass", callback_data="pass")],
            [InlineKeyboardButton(text="🏆 Boost", callback_data="boost")],
            [InlineKeyboardButton(text="👤 Profile", callback_data="profile")],
            [InlineKeyboardButton(text="⭐ Reviews", callback_data="reviews")],
            [InlineKeyboardButton(text="🎁 Promo", callback_data="promo")],
            [InlineKeyboardButton(text="🛠 Support", url=f"https://t.me/{OWNER}")]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):

    text = (
        "🔥 Brawl Stars Shop"


        "⚡ Fast delivery"

        "💳 Automatic payment"

        "💰 Low prices"

        "🛠 24/7 support"
    )

    await message.answer(text, reply_markup=menu())


@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    async with aiosqlite.connect("shop.db") as db:

        cursor = await db.execute(
            "SELECT purchases, balance FROM users WHERE user_id = ?",
            (callback.from_user.id,)
        )

        user = await cursor.fetchone()

        if not user:
            await db.execute(
                "INSERT INTO users (user_id) VALUES (?)",
                (callback.from_user.id,)
            )

            await db.commit()

            purchases = 0
            balance = 0

        else:
            purchases, balance = user

    text = (
        f"🆔 ID: {callback.from_user.id}"

        f"🛒 Purchases: {purchases}"

        f"💵 Balance: {balance}₽"


        "👑 VIP Levels:"

        "5 purchases -> 5% discount"

        "10 purchases -> VIP"
    )

    await callback.message.edit_text(text, reply_markup=menu())


@dp.callback_query(F.data == "reviews")
async def reviews(callback: CallbackQuery):

    text = (
        "⭐ Reviews:"


        "Good prices"

        "Fast support"

        "Instant payment"
    )

    await callback.message.edit_text(text, reply_markup=menu())


@dp.callback_query(F.data == "promo")
async def promo(callback: CallbackQuery):

    text = (
        "🎁 Promo codes:"


        "START - 5%"

        "VIP - 10%"
    )

    await callback.message.edit_text(text, reply_markup=menu())


@dp.callback_query(F.data.in_(["gems", "pass", "boost"]))
async def show_products(callback: CallbackQuery):

    category = callback.data
    keyboard = []
    text = "🛒 Products:"



    for item, price in products[category]:

        text += f"{item} - {price}₽"


        keyboard.append([
            InlineKeyboardButton(
                text=f"🛒 Buy {item} 🛒",
                callback_data=f"buy:{item}:{price}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="⬅ Back", callback_data="back")
    ])

    await callback.message.answer_photo(
        photo=product_photos[category],
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


async def create_invoice(amount):

    pay_url = f"{QKASSA_URL}?amount={amount}"

    return pay_url


@dp.callback_query(F.data.startswith("buy:"))
async def buy(callback: CallbackQuery):

    _, product, price = callback.data.split(":")

    pay_url = await create_invoice(price)

    if not pay_url:
        await callback.message.delete()

        await callback.message.answer(
            "✅ Test mode: product successfully purchased",
            reply_markup=menu()
        )

        return

    text = (
        f"🎯 Product: {product}"

        f"💰 Price: {price}₽"


        "💳 Payment after clicking button"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Pay", url=pay_url)],
            [InlineKeyboardButton(text="🛠 Support", url=f"https://t.me/{OWNER}")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back")]
        ]
    )

    await callback.message.delete()

    await callback.message.answer_photo(
        photo=product_photos["gems"],
        caption=text,
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):

    await callback.message.delete()

    await callback.message.answer(
        "🏠 Main Menu",
        reply_markup=menu()
    )


async def main():

    await create_db()

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

