
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")


BASE_URL = "https://v6.exchangerate-api.com/v6"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


conn = sqlite3.connect("../Python basic lessons/lessons/users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT
)
""")

conn.commit()

def add_user(user_id, username):
    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    )
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.commit()


# 🔹 Inline tugmalar
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💵 USD → UZS", callback_data="usd"),
        InlineKeyboardButton("💶 EUR → UZS", callback_data="eur"),
        InlineKeyboardButton("🔢 Konvertatsiya", callback_data="convert")
    )
    return kb


# 🔹 Start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "💱 Assalawma aleykum bul valyuta kurs boti !\n\n"
        "Tomendegilerden birewin saylan': ",
        reply_markup=main_menu()
    )


# 🔹 Kurs olish funksiyasi
def get_rate(base, target="UZS"):
    url = f"{BASE_URL}/{API_KEY}/pair/{base}/{target}"
    r = requests.get(url).json()
    return r["conversion_rate"]


# 🔹 Callbacklar
@dp.callback_query_handler(lambda c: c.data in ["usd", "eur"])
async def currency_handler(call: types.CallbackQuery):
    base = "USD" if call.data == "usd" else "EUR"
    rate = get_rate(base)

    await call.message.answer(
        f"📌 1 {base} = {rate:,.2f} UZS"
    )
    await call.answer()


# 🔹 Konvertatsiya boshlash
@dp.callback_query_handler(text= "convert")
async def convert_start(call: types.CallbackQuery):
    await call.message.answer(
        "✍️ Tomendegi koriniste kiritin':\n\n"
        "`100 USD`\n"
        "`250 EUR`",
        parse_mode="Markdown"
    )
    await call.answer()


# 🔹 Konvertatsiya hisoblash
@dp.message_handler(lambda msg: len(msg.text.split()) == 2)
async def convert_calc(message: types.Message):
    try:
        amount, currency = message.text.split()
        amount = float(amount)
        currency = currency.upper()

        rate = get_rate(currency)
        result = amount * rate

        await message.answer(
            f"💰 {amount} {currency} = {result:,.2f} UZS"
        )

    except:
        pass


# 🔹 Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
