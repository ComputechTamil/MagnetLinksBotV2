import asyncio
from main import *
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

dp = Dispatcher()

# Store magnet links globally or in context (simplified demo)
# In production, store this in a per-user/session dict or a database
USER_LINKS = {}

def create_buttons(lst):
    buttons = []
    for idx, (text, url) in enumerate(lst):
        # Use index as callback_data so you know which link to send when pressed
        buttons.append([InlineKeyboardButton(text=text, callback_data=str(idx))])
##    buttons.append([InlineKeyboardButton(text="All Links", callback_data="all")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    username = message.from_user.username or message.from_user.first_name
    await message.answer(
        f"Hello {username}! 👋 Welcome to MagnetLink Bot.\nJust send the movie name, and I will send the magnet links!"
    )

@dp.message()
async def send_magnet_links(message: Message):
    # Get magnet links list: List of (text, url) tuples
    links = await get_magnet_links(message.text)
    links=links[:10]
    if not links:
        await message.answer("Sorry, no magnet links found for your query.")
        return

    # Save links for this user to retrieve later on callback
    USER_LINKS[message.from_user.id] = links

    inline_kb = create_buttons(links)

    await message.answer(
        "Here are the magnet links I found (click a button to get the URL):",
        reply_markup=inline_kb,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    idx = int(callback.data)
    user_links = USER_LINKS.get(user_id)
    if not user_links or idx >= len(user_links):
        await callback.answer("Sorry, link not found or expired.", show_alert=True)
        return

    text, url = user_links[idx]

    # Send magnet link as code
    await callback.message.answer(f"<code>{url}</code>", parse_mode=ParseMode.HTML)

    # Answer callback to remove “loading” animation on button
    await callback.answer()

async def main():
    token = "7854634864:AAHqP2K9l8YzPBnBh_c8kuVwTZQR_gQHDHc"
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
