import asyncio
import json
import os

from dotenv import load_dotenv
from rich.panel import Panel
from rich.text import Text
from telebot import asyncio_filters, types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import FastAPI, Request
import uvicorn

import bot_context
from users.hidden import Hidden
from users.user import User
from functions.auth import Auth

load_dotenv()

app = FastAPI()

bot_context.bot = AsyncTeleBot(
    os.getenv('MAIN_TOKEN') or os.getenv('BOT_TOKEN_MAIN'),
    state_storage=StateMemoryStorage()
)
log_token = os.getenv('BOT_TOKEN_LOG')
bot_context.bot_log = AsyncTeleBot(log_token) if log_token else None
bot = bot_context.bot
obj = {}


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    markup = InlineKeyboardMarkup()
    # Ganti URL ini dengan URL tempat kamu meng-host file main.html (harus HTTPS)
    web_app = types.WebAppInfo(url="https://your-domain.com/main.html")
    markup.add(InlineKeyboardButton("OPEN SKYNET DASHBOARD", web_app=web_app))
    
    await bot.send_message(
        message.chat.id, 
        "<code>SYSTEM: Web Interface Ready.\nClick button below to manage your Sky session.</code>", 
        parse_mode='HTML', 
        reply_markup=markup
    )


@bot.message_handler(commands=['cancel'])
async def cancel_handler(message):
    try:
        user = obj[message.from_user.id]
        user.inf_eden = False
        user.inf_seasonal = False
    except KeyError:
        await bot.send_message(message.chat.id, "Go start first bruh")


@bot.message_handler(state=bot_context.MyStates.server)
async def server_get(message):
    async with bot.retrieve_data(message.from_user.id) as data:
        data['server'] = message
        await obj[message.from_user.id].ask_login_method(data['server'])


@bot.message_handler(state=bot_context.MyStates.method)
async def method_get(message):
    async with bot.retrieve_data(message.from_user.id) as data:
        data['method'] = message
        await obj[message.from_user.id].login_method(data['method'], data['server'].text)


@bot.message_handler(state=bot_context.MyStates.lua_code)
async def lua_code(message):
    async with bot.retrieve_data(message.from_user.id) as data:
        data['lua_code'] = message
        await obj[message.from_user.id].lua_handler(data['lua_code'], data['server'].text)


@bot.message_handler(state=bot_context.MyStates.lib_code)
async def lib_login(message):
    async with bot.retrieve_data(message.from_user.id) as data:
        data['lib_code'] = message
        await obj[message.from_user.id].lib_handler(data['lib_code'], data['server'].text)


async def common_login(message, login_type):
    async with bot.retrieve_data(message.from_user.id) as data:
        server_type = data['server'].text
        await obj[message.from_user.id].common_login_handler(message, login_type, environment=server_type.lower())


@bot.message_handler(state=bot_context.MyStates.nintendo_code)
async def nintendo_login(message):
    await common_login(message, "Nintendo")


@bot.message_handler(state=bot_context.MyStates.huawei_code)
async def huawei_login(message):
    await common_login(message, "Huawei")


@bot.message_handler(state=bot_context.MyStates.steam_code)
async def steam_login(message):
    await common_login(message, "Steam")


@bot.message_handler(state=bot_context.MyStates.google_code)
async def google_login(message):
    await common_login(message, "Google")


@bot.message_handler(state=bot_context.MyStates.sony_code)
async def sony_login(message):
    await common_login(message, "Sony")


@bot.message_handler(state=bot_context.MyStates.facebook_code)
async def facebook_login(message):
    await common_login(message, "Facebook")


@bot.message_handler(state=bot_context.MyStates.runfunction)
async def run_function(message):
    async with bot.retrieve_data(message.from_user.id) as data:
        await obj[message.from_user.id].select_func(message, data['server'].text)


@bot.message_handler(commands=['help'])
async def send_help(message):
    replyx = """
        <code>User friendly astral body projection (TrashGC) in Telegram. Listed features:
        - Daily Function (farm, quest, light and collect light from constellation)
        - Unlock all map, spirit/emote
        - Seasonal Quest
        - World Quest
        - Eden [repeatable]
        - Wings (Location only, not spirit buff; it won't make your wing go 194)
        - Unlock all IAPs (beta only)
        - 300 seasonal candles (beta only) [repeatable]

        Be sure to ask the bot owner's permission before using it.
        </code> -iPowfuVM
            """
    await bot.send_message(message.chat.id, replyx, parse_mode='HTML')


@bot.message_handler(commands=['changelog'])
async def send_changelog(message):
    replyx = """
        <code>Changelog
        - Beta login fix
        - Add hidden unlock all cosmetic, lock all cosmetic, and buy white candle as testing hidden beta</code>
        """
    await bot.send_message(message.chat.id, replyx, parse_mode='HTML')


@bot.message_handler(commands=['version'])
async def send_version(message):
    await bot.send_message(message.chat.id, "1.0.0", parse_mode='HTML')


@bot.message_handler(commands=['sauto'])
async def send_sauto(message):
    await Hidden.lua_handler(message)


@bot.message_handler(commands=['lua'])
async def send_lua(message):
    try:
        # Source: https://t.me/Dopaminech/300
        await bot.copy_message(message.chat.id, "@Dopaminech", 300)
    except Exception:
        await bot.send_message(message.chat.id, "<code>ERROR: Could not retrieve Lua file from repository.</code>", parse_mode='HTML')


@bot.message_handler(commands=['lib'])
async def send_lib(message):
    try:
        with open("files/libAuthPuller.so", "rb") as doc:
            await bot.send_document(message.chat.id, doc, caption="<code>SYSTEM: Lib file for TrashGC</code>", parse_mode='HTML')
    except FileNotFoundError:
        await bot.send_message(message.chat.id, "<code>ERROR: libAuthPuller.so not found in 'files/' directory.</code>", parse_mode='HTML')
    except Exception as e:
        await bot.send_message(message.chat.id, f"<code>ERROR: {str(e)}</code>", parse_mode='HTML')


@bot.message_handler(commands=['donate'])
async def send_donate(message):
    markup = InlineKeyboardMarkup(row_width=2)
    donation_links = {
        "Paypal": "https://www.paypal.me/FRozy531",
        "Saweria": "https://saweria.co/AntisWaterflai",
        "Ko-fi": "https://ko-fi.com/antis",
    }
    for label, url in donation_links.items():
        markup.add(InlineKeyboardButton(label, url=url))
    await bot.reply_to(message, '<code>Some donation will help me to buy some milk</code>', parse_mode='HTML', reply_markup=markup)


PLATFORMS = ["Nintendo", "Huawei", "Steam", "Sony", "Facebook", "Google"]


@bot.message_handler(commands=['create-account'])
async def create_account_handler(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await bot.send_message(message.chat.id, "<code>Usage: /create-account {platform} {code_json}</code>", parse_mode='HTML')
            return

        platform = args[1].capitalize()
        if platform not in PLATFORMS:
            supported = ", ".join(PLATFORMS)
            await bot.send_message(message.chat.id, f"<code>Unsupported platform '{platform}'. Supported: {supported}.</code>", parse_mode='HTML')
            return

        code_data = json.loads(args[2])
        platform_id = code_data.get("id")
        platform_token = code_data.get("token")
        if not platform_id or not platform_token:
            await bot.send_message(message.chat.id, "<code>Invalid code format! JSON must include 'id' and 'token'.</code>", parse_mode='HTML')
            return

        obj[message.from_user.id] = User(message)
        await obj[message.from_user.id].version('live')
        user_id, session = await obj[message.from_user.id].create_account(message)
        if not user_id or not session:
            await bot.send_message(message.chat.id, "<code>Account creation failed. Please try again later.</code>", parse_mode='HTML')
            return

        bind_response = await obj[message.from_user.id].bind(message, platform, platform_id, platform_token)
        if not bind_response:
            await bot.send_message(message.chat.id, "<code>Binding failed. Please check the platform code and try again.</code>", parse_mode='HTML')
    except json.JSONDecodeError:
        await bot.send_message(message.chat.id, "<code>Error: Invalid JSON format for the code.</code>", parse_mode='HTML')
    except Exception as exc:
        print(f"Error in create_account_handler: {exc}")
        await bot.send_message(message.chat.id, "<code>An error occurred while processing the command.</code>", parse_mode='HTML')


@bot.message_handler(func=lambda message: True, content_types=['text'])
async def command_default(message):
    await bot.send_message(message.chat.id, "<code>I don't understand, try with</code> /start", parse_mode='HTML')
    if bot_context.bot_log:
        replyx = f"""
        <code>firstname: {message.from_user.first_name}
        telegram_id: {message.chat.id}
        message: {message.text}</code>
        """
        await bot_context.bot_log.send_message(bot_context.ADMIN_ID, replyx, parse_mode='HTML')


# --- CALLBACK HANDLERS FOR ACCESS MANAGEMENT ---

# req_access_ di-handle main bot (karena pesan REQUEST ACCESS dikirim main bot ke user)
@bot.callback_query_handler(func=lambda call: call.data.startswith('req_access_'))
async def handle_request_access(call):
    user_id = call.data.split('_')[2]
    user_name = call.from_user.first_name

    admin_msg = (
        "ACCESS REQUEST\n"
        "----------------------------\n"
        f"NAME: {user_name}\n"
        f"ID  : {user_id}\n"
        "----------------------------"
    )
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("ACCEPT", callback_data=f"adm_acc_{user_id}"),
        InlineKeyboardButton("DECLINE", callback_data=f"adm_dec_{user_id}"),
        InlineKeyboardButton("BAN", callback_data=f"adm_ban_{user_id}")
    )

    # Kirim button via bot_log ke ADMIN_ID — callback akan ditangkap bot_log handler
    # Kalau bot_log tidak ada, fallback ke main bot
    if bot_context.bot_log:
        await bot_context.bot_log.send_message(
            bot_context.ADMIN_ID, f"<code>{admin_msg}</code>", parse_mode='HTML', reply_markup=markup
        )
    else:
        await bot.send_message(
            bot_context.ADMIN_ID, f"<code>{admin_msg}</code>", parse_mode='HTML', reply_markup=markup
        )

    await bot.answer_callback_query(call.id, "Request sent to Admin.")
    await bot.edit_message_text(
        "<code>REQUEST SENT: Please wait for admin approval.</code>",
        call.message.chat.id, call.message.message_id, parse_mode='HTML'
    )


def setup_log_bot_handlers(log_bot):
    """Register adm_ callback di bot_log — karena button dikirim bot_log,
    Telegram routing callback-nya kembali ke bot_log."""

    @log_bot.callback_query_handler(func=lambda call: call.data.startswith('adm_'))
    async def handle_admin_action(call):
        if call.from_user.id != bot_context.ADMIN_ID:
            return await log_bot.answer_callback_query(call.id, "Unauthorized.")

        parts = call.data.split('_')
        action = parts[1]
        target_id = int(parts[2])

        if action == "acc":
            success = await Auth.add_to_bypass(target_id)
            if success:
                await bot.send_message(target_id, "<code>ACCESS GRANTED: You can now use /start</code>", parse_mode='HTML')
                status = "ACCEPTED"
            else:
                await log_bot.answer_callback_query(call.id, "Failed to write bypass file.")
                return
        elif action == "dec":
            await bot.send_message(target_id, "<code>ACCESS DECLINED: Contact owner for details.</code>", parse_mode='HTML')
            status = "DECLINED"
        else:  # ban
            status = "BANNED"

        new_text = call.message.text + f"\n\nACTION: {status} BY ADMIN"
        await log_bot.edit_message_text(
            f"<code>{new_text}</code>",
            call.message.chat.id, call.message.message_id,
            parse_mode='HTML', reply_markup=None
        )
        await log_bot.answer_callback_query(call.id, f"User {status}")


# Fallback adm_ handler di main bot (kalau bot_log tidak ada)
@bot.callback_query_handler(func=lambda call: call.data.startswith('adm_'))
async def handle_admin_action_fallback(call):
    if bot_context.bot_log:
        return  # bot_log yang handle, abaikan di main bot
    if call.from_user.id != bot_context.ADMIN_ID:
        return await bot.answer_callback_query(call.id, "Unauthorized.")

    parts = call.data.split('_')
    action = parts[1]
    target_id = int(parts[2])

    if action == "acc":
        success = await Auth.add_to_bypass(target_id)
        if success:
            await bot.send_message(target_id, "<code>ACCESS GRANTED: You can now use /start</code>", parse_mode='HTML')
            status = "ACCEPTED"
        else:
            await bot.answer_callback_query(call.id, "Failed to write bypass file.")
            return
    elif action == "dec":
        await bot.send_message(target_id, "<code>ACCESS DECLINED: Contact owner for details.</code>", parse_mode='HTML')
        status = "DECLINED"
    else:
        status = "BANNED"

    new_text = call.message.text + f"\n\nACTION: {status} BY ADMIN"
    await bot.edit_message_text(
        f"<code>{new_text}</code>",
        call.message.chat.id, call.message.message_id,
        parse_mode='HTML', reply_markup=None
    )
    await bot.answer_callback_query(call.id, f"User {status}")


bot.add_custom_filter(asyncio_filters.StateFilter(bot))


async def main():
    # Jalankan API server di background
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    
    if bot_context.bot_log:
        setup_log_bot_handlers(bot_context.bot_log)
        bot_context.console.log("[green]System: Log bot handlers registered.[/]")
        await asyncio.gather(
            bot.infinity_polling(skip_pending=True),
            server.serve(),
            bot_context.bot_log.infinity_polling(skip_pending=True)
        )
    else:
        await bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    bot_context.console.clear()
    banner = Text("TRASHGC TELEGRAM BOT", style="bold cyan")
    banner.append("\nModular Sky: CotL Automation", style="italic white")
    bot_context.console.print(Panel(banner, border_style="blue", expand=False))

    bot_context.console.log("[green]System: Initializing polling...[/]")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("")
        bot_context.console.log("[yellow]System: KeyboardInterrupt detected. Shutting down gracefully...[/]")