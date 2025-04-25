from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
import requests

API_TOKEN = '7660079395:AAHg9ydMSJfJn80Ok0V00cDanMJyTiMpGWk'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# زر الجودة
quality_keyboard = InlineKeyboardMarkup(row_width=2)
quality_keyboard.add(
    InlineKeyboardButton("جودة عالية", callback_data="high"),
    InlineKeyboardButton("جودة متوسطة", callback_data="medium"),
    InlineKeyboardButton("صوت فقط", callback_data="audio")
)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("أهلًا بك في بوت فصيح لتحميل الفيديوهات!\n\nأرسل الرابط من أي منصة (يوتيوب، إنستجرام، فيسبوك، واتساب، تيك توك...) وسنقوم بالباقي!", reply_markup=quality_keyboard)

user_links = {}

@dp.message_handler()
async def handle_link(message: types.Message):
    url = message.text.strip()
    if url.startswith("http"):
        user_links[message.from_user.id] = url
        await message.reply("من فضلك اختر الجودة المطلوبة:", reply_markup=quality_keyboard)
    else:
        await message.reply("من فضلك أرسل رابط صحيح للفيديو.")

@dp.callback_query_handler(lambda c: c.data in ["high", "medium", "audio"])
async def process_quality(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    quality = callback_query.data
    url = user_links.get(callback_query.from_user.id)

    if not url:
        await bot.send_message(callback_query.from_user.id, "من فضلك أرسل رابط أولاً.")
        return

    await bot.send_message(callback_query.from_user.id, "جارٍ تحميل الفيديو... برجاء الانتظار.")

    try:
        response = requests.get(f"https://api.savethevideo.com/download?url={url}")
        if response.ok:
            result = response.json()
            video_url = result.get("url")
            if video_url:
                await bot.send_message(callback_query.from_user.id, f"ها هو رابط التحميل:\n{video_url}")
            else:
                await bot.send_message(callback_query.from_user.id, "عذرًا، لم نتمكن من استخراج الفيديو.")
        else:
            await bot.send_message(callback_query.from_user.id, "حدث خطأ أثناء محاولة تحميل الفيديو.")
    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"حدث خطأ: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)