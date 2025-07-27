import os
import asyncio
from aiohttp import web
from main import get_magnet_links  # Your magnet link scraper
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set this in Render environment variables!
WEBHOOK_URL = f"https://magnetlinksbotv2.onrender.com"

# --- Bot & Dispatcher ---
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# --- In-Memory Storage ---
USER_LINKS = {}

def create_buttons(lst):
    buttons = []
    for idx, (text, url) in enumerate(lst):
        buttons.append([InlineKeyboardButton(text=text, callback_data=str(idx))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    username = message.from_user.username or message.from_user.first_name
    await message.answer(
        f"Hello {username}! 👋 Welcome to MagnetLink Bot.\nJust send the movie name, and I will send the magnet links!"
    )

@dp.message()
async def send_magnet_links(message: Message):
    links = await get_magnet_links(message.text)
    links = links[:10]
    if not links:
        await message.answer("Sorry, no magnet links found for your query.")
        return

    USER_LINKS[message.from_user.id] = links
    inline_kb = create_buttons(links)

    await message.answer(
        "Here are the magnet links I found (click a button to get the URL):",
        reply_markup=inline_kb
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
    await callback.message.answer(f"<code>{url}</code>")
    await callback.answer()

# --- Startup Hook ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

# --- Shutdown Hook (Optional) ---
async def on_shutdown(app):
    await bot.delete_webhook()

# --- App Factory ---
def create_app():
    app = web.Application()

    # Register Telegram Webhook Handler
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)

    # Set up middleware/hooks
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Add health check route
    async def health_check(request):
        return web.Response(text="OK")
    app.router.add_get("/", health_check)

    return app

# --- Entry ---
if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
