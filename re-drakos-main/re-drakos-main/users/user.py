import asyncio
import json

import aiohttp
import bot_context
from functions.fmt import Fmt
from functions.auth import Auth
from functions.sessions import Sessions
from functions.version import Version, FALLBACK_VERSION
from sky_functions.account import Account
from sky_functions.cosmetics import Cosmetics
from sky_functions.currency import Currency, CurrencyMesasge
from sky_functions.eden import Eden
from sky_functions.farm import FarmMessage
from sky_functions.friends import Friends
from sky_functions.iaps import Iap
from sky_functions.map_unlock import MapUnlock
from sky_functions.quests import Quest
from sky_functions.spirit import SpiritMessage
from sky_functions.wings import Wings
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class User:
    def __init__(self, message):
        self.headersu = {
            'Host': 'live.radiance.thatgamecompany.com',
            'User-Agent': 'Sky-Live-com.tgc.sky.android/ (Xiaomi M2012K11AG; android 32.0.0; en)',
            'X-Session-ID': 'aeee648a-ea1f-4700-b970-ebe955750601',
            'user-id': '',
            'session': '',
            'Content-type': 'application/json',
        }
        self.headers = {
            'Host': 'live.radiance.thatgamecompany.com',
            'User-Agent': 'Sky-Live-com.tgc.sky.android/ (Xiaomi M2012K11AG; android 32.0.0; en)',
            'X-Session-ID': 'aeee648a-ea1f-4700-b970-ebe955750601',
            'x-retry': '1',
            'x-sky-install-source': 'com.android.vending',
            'Content-type': 'application/json',
        }
        self.inf_eden = False
        self.inf_seasonal = False
        self.datas = {
            "name": message.from_user.first_name,
            "chatid": f"{message.chat.id}",
        }

    async def send_log(self, data):
        return data

    async def verify_user(self, message):
        bot = bot_context.bot
        t_user_id = message.chat.id
        first_name = message.from_user.first_name

        allowed = await Auth.is_allowed(t_user_id)

        if not allowed:
            # Menyiapkan tombol management untuk dikirim ke Admin log
            admin_markup = InlineKeyboardMarkup()
            admin_markup.row(
                InlineKeyboardButton("ACCEPT", callback_data=f"adm_acc_{t_user_id}"),
                InlineKeyboardButton("DECLINE", callback_data=f"adm_dec_{t_user_id}"),
                InlineKeyboardButton("BAN", callback_data=f"adm_ban_{t_user_id}")
            )

            if bot_context.bot_log:
                await bot_context.bot_log.send_message(
                    bot_context.ADMIN_ID,
                    f"<code>ERROR: {first_name} (ID: {t_user_id}) attempted access but is not validated (not in bypass list).</code>",
                    parse_mode='HTML',
                    reply_markup=admin_markup
                )
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("REQUEST ACCESS", callback_data=f"req_access_{t_user_id}"))
            await bot.send_message(message.chat.id, "<code>ACCESS DENIED: Unauthorized account ID.</code>", parse_mode='HTML', reply_markup=markup)
            await bot.send_message(message.chat.id, "<code>PLEASE REQUEST ACCESS OR CONTACT @diesforcringes</code>", parse_mode='HTML')
            return

        if bot_context.bot_log:
            await bot_context.bot_log.send_message(
                bot_context.ADMIN_ID,
                f"<code>SUCCESS: {first_name} (ID: {t_user_id}) has been validated and granted access.</code>",
                parse_mode='HTML',
            )

        welcome_msg = (
            "SYSTEM: SESSION INITIALIZED\n"
            "----------------------------\n"
            f"USER    : {first_name.upper()}\n"
            "STATUS  : AUTHORIZED\n"
            "VERSION : TrashGC Core v1.0\n"
            "----------------------------"
        )
        await bot.send_message(message.chat.id, f"<code>{welcome_msg}</code>", parse_mode='HTML')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Live', 'Beta', 'Exit')
        await bot.set_state(message.from_user.id, bot_context.MyStates.server)
        await bot.send_message(message.chat.id, "<code>SELECT SERVER:</code>", reply_markup=markup, parse_mode='HTML')

    async def version(self, server_type):
        try:
            modified_version_text = await Version.get_version(server_type)
            if not modified_version_text:
                modified_version_text = FALLBACK_VERSION
            if server_type == "live":
                user_agent = f'Sky-Live-com.tgc.sky.android/{modified_version_text} (Xiaomi M2012K11AG; android 32.0.0; en)'
                host = 'live.radiance.thatgamecompany.com'
            else:
                user_agent = f'Sky-Test-com.tgc.sky.android.test.gold/{modified_version_text} (Apple iPhone 13 Pro Max; android 29.0.0; en)'
                host = 'beta.radiance.thatgamecompany.com'
            self.headersu.update({'User-Agent': user_agent, 'Host': host})
            self.headers.update({'User-Agent': user_agent, 'Host': host})
        except Exception as exc:
            bot_context.console.log(f"[red]Version Error:[/] {exc}")

    async def consulta(self, datos, direccion, headerx=None):
        if headerx is None:
            headerx = self.headersu
        url = f'https://{headerx["Host"]}{direccion}'
        async with aiohttp.TCPConnector(ssl=False) as conn:
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.post(url=url, data=json.dumps(datos), headers=headerx) as request:
                    if request.status == 200:
                        return await request.text()

    def _apply_session(self, user_id, session):
        self.headersu['user-id'] = user_id
        self.headersu['session'] = session
        self.headers['user-id'] = user_id
        self.headers['session'] = session

    async def create_account(self, message):
        user_id, session = await Account.create_account(self.headers, bot_context.bot, message)
        if user_id and session:
            self._apply_session(user_id, session)
        return user_id, session

    async def bind(self, message, platform_type, platform_id, platform_token):
        return await Account.bind(
            self.headersu,
            bot_context.bot,
            message,
            platform_type,
            platform_id,
            platform_token,
        )

    async def get_currency(self, message, send_type=None):
        currency = await Currency.get_currency(self.headersu)
        if send_type == "edit":
            await CurrencyMesasge.edit_currency_mesasge(bot_context.bot, message, currency)
        else:
            await CurrencyMesasge.send_currency_mesasge(bot_context.bot, message, currency)

    async def niveles(self, status_reply, header=None):
        await FarmMessage.send_farm_message(bot_context.bot, status_reply, header or self.headersu)

    async def quest(self):
        await Quest.daily_quest(self.headersu)

    async def todo(self, header=None):
        await Quest.world_quest(header or self.headersu)

    async def todoC(self, header=None):
        await Quest.world_quest_c(header or self.headersu)

    async def eden(self):
        await Eden.eden(self.headersu)
        await Currency.get_currency(self.headersu)

    async def alas(self):
        await Wings.map_wings(self.headersu)

    async def alasall(self):
        await Wings.all_wings(self.headersu)

    async def desbo(self, header=None):
        await MapUnlock.unlock_maps(header or self.headersu)

    async def desboheart(self):
        await MapUnlock.unlock_map_hearts(self.headersu)

    async def coles(self, status_reply):
        await SpiritMessage.send_spirit_message(self.headersu, status_reply, bot_context.bot)

    async def calcular(self):
        await SpiritMessage.send_elder_hair_message(self.headersu, None, bot_context.bot)

    async def eldermask(self):
        await SpiritMessage.send_elder_hair_message(self.headersu, None, bot_context.bot)
        await SpiritMessage.send_elder_mask_message(self.headersu, None, bot_context.bot)

    async def Principe(self):
        await Quest.seasonal_guide_quest(self.headersu)

    async def enviarwax(self):
        await Friends.lit_and_collect(self.headersu)

    async def seasonal_candle(self):
        await Iap.seasonal_candle(self.headersu)

    async def seasonal_candle_300(self, message, uid, session):
        await Iap.seasonal_candle_300(self.headersu)

    async def white_candle(self, message, uid, session):
        await Iap.white_candle(self.headersu)
        await bot_context.bot.edit_message_text(
            chat_id=message.chat.id,
            text="<code>white candle purchase done</code>",
            message_id=message.message_id,
            parse_mode='HTML',
        )

    async def unlock_all(self, message, uid, session):
        await Cosmetics.unlock_all_with_status(bot_context.bot, message, self.headersu)

    async def lock_all(self, message, uid, session):
        await Cosmetics.remove_all_with_status(bot_context.bot, message, self.headersu)

    async def unlock_all_iap(self, message, uid, session):
        await Iap.unlock_all_iap(self.headersu, bot_context.bot, message)

    async def send_error_reply(self, message, error_text):
        markup = types.ReplyKeyboardRemove(selective=False)
        await bot_context.bot.reply_to(
            message,
            f"<code>{error_text}</code>",
            parse_mode='HTML',
            reply_markup=markup,
        )

    async def successful_login_response(self, message, login_type):
        firstname = message.from_user.first_name
        t_user_id = message.chat.id
        self.datas["name"] = firstname
        self.datas["chatid"] = f"{t_user_id}"
        
        reply = "SESSION ESTABLISHED\n"
        reply += "----------------------------\n"
        reply += f"USER ID : {self.headersu['user-id']}\n"
        reply += f"SESSION : {self.headersu['session']}\n"
        reply += "----------------------------"
        
        await bot_context.bot.reply_to(message, f"<code>{reply}</code>", parse_mode='HTML')
        log_message = (
            f"<code>AUTH LOG\nNAME: {firstname}\nID: {t_user_id}\nUID: {self.headersu['user-id']}</code>"
        )
        if bot_context.bot_log:
            await bot_context.bot_log.send_message(bot_context.ADMIN_ID, log_message, parse_mode='HTML')
        await self.get_function(message, login_type)

    async def common_login_handler(self, message, login_type, environment="live"):
        try:
            # Bersihkan input dari spasi atau karakter markdown jika ada
            clean_text = message.text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.strip("`").replace("json", "", 1).strip()

            try:
                code_data = json.loads(clean_text)
            except json.JSONDecodeError:
                return await bot_context.bot.reply_to(message, "<code>ERROR: Format JSON tidak valid. Pastikan kamu copy seluruh kode.</code>", parse_mode='HTML')

            player_id = code_data.get("id")
            signature = code_data.get("token")

            if not player_id or not signature:
                return await bot_context.bot.reply_to(message, "<code>ERROR: Data 'id' atau 'token' tidak ditemukan dalam kode.</code>", parse_mode='HTML')

            payload = Sessions.build_oauth_payload(login_type, player_id, signature, environment.lower())
            await self.version(environment.lower())
            result = await Sessions.login(payload, self.headers)
            
            if result is False:
                # Check if there's a specific error message logged in the console from sessions.py
                # This requires sessions.py to return the error string, not just False.
                # For now, we'll assume the console log is the best place to check.
                # If sessions.py can return the specific error, we can display it here.
                error_detail = "Cek terminal/CMD untuk melihat response code dari TGC."
                # A more robust way would be to modify Sessions.login to return the error string
                # e.g., return data.get("result") if data.get("result") not in ("ok", "not_found", "expired")
                # For now, we rely on the console log.
                return await bot_context.bot.reply_to(
                    message, 
                    "<code>LOGIN FAILED\n"
                    "REASON: Server rejected the request.\n"
                    f"NOTE: {error_detail}</code>",
                    parse_mode='HTML'
                )
            
            user_id, session = result
            if user_id == "not_found":
                await self.send_error_reply(message, "ACCOUNT NOT FOUND: Pastikan akun sudah di-link ke platform tersebut.")
            elif user_id == "expired":
                await self.send_error_reply(message, "CODE EXPIRED: Kode sudah kadaluarsa. Silahkan ambil kode baru.")
            else:
                self._apply_session(user_id, session)
                await self.successful_login_response(message, login_type)
        except Exception as exc:
            bot_context.console.log(f"[bold red]Login Exception:[/] {exc}")

    async def get_function(self, message, server_type):
        server_type = server_type.lower()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        if server_type == "live":
            markup.add(
                'Daily function (farm,quest,lit)', 'Farm', 'Daily quest', 'Unlock all map',
                'Unlock all emotes', 'Eden', 'Unlock all elder hairs', 'Wings',
                'Lit & Collect friends light', 'World Quest', 'Seasonal Quest',
                'Candle info', 'Elder Mask', 'All', 'Exit',
            )
        else:
            markup.add(
                'Daily function (farm,quest,lit)', 'Farm', 'Daily quest', 'Unlock all map',
                'Unlock all emotes', 'Eden', 'Unlock all elder hairs', 'Wings',
                'Lit & Collect friends light', 'World Quest', 'Seasonal Quest',
                'Candle info', 'All Iap', '300 Seasonal Candle', 'Elder Mask', 'All', 'Exit',
            )
        await bot_context.bot.set_state(message.from_user.id, bot_context.MyStates.runfunction)
        await bot_context.bot.send_message(
            message.chat.id,
            "<code>Select function you want to use</code>",
            reply_markup=markup,
            parse_mode='HTML',
        )

    async def ask_login_method(self, message):
        bot = bot_context.bot
        if message.text in ['Live', 'Beta']:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Lua Code', 'Lib Code', 'Nintendo', 'Huawei', 'Steam', 'Google', 'Sony', 'Facebook', 'Exit')
            await bot.set_state(message.from_user.id, bot_context.MyStates.method)
            await bot.reply_to(message, "<code>Select login method</code>", reply_markup=markup, parse_mode='HTML')
        elif message.text == 'Exit':
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, "<code>Bye!</code>", parse_mode='HTML', reply_markup=markup)
            await bot.delete_state(message.from_user.id)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Live', 'Beta', 'Exit')
            await bot.reply_to(message, "<code>Wrong, Select Server</code>", reply_markup=markup, parse_mode='HTML')
            await bot.delete_state(message.from_user.id)

    async def login_method(self, message, server_type):
        bot = bot_context.bot
        server_type = server_type.lower()

        async def send_login_prompt(service_name):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                f"Get {service_name} code",
                url=f"https://{server_type}.radiance.thatgamecompany.com/account/auth/oauth_signin?type={service_name}&token=",
            ))
            await bot.set_state(message.from_user.id, getattr(bot_context.MyStates, f"{service_name.lower()}_code"))
            await bot.send_message(
                message.chat.id,
                f"<code>Click this button, login to your {service_name}, and copy the code it returns.</code>",
                parse_mode='HTML',
                reply_markup=markup,
            )

        if message.text == 'Lua Code':
            await bot.set_state(message.from_user.id, bot_context.MyStates.lua_code)
            await bot.send_message(message.chat.id, "<code>Please input your code from Lua. If you don't have the file, try /lua.</code>", parse_mode='HTML')
            try:
                # Fetching from @Dopaminech ID 300
                await bot.copy_message(message.chat.id, "@Dopaminech", 300)
            except Exception as e:
                bot_context.console.log(f"[red]System Error:[/] Failed to copy Lua file (ID: 300): {e}")

        elif message.text == 'Lib Code':
            await bot.set_state(message.from_user.id, bot_context.MyStates.lib_code)
            await bot.send_message(message.chat.id, "<code>Please input your code from lib canvas. If you don't have the file, try /lib.</code>", parse_mode='HTML')
            try:
                # Mengambil file Lib dari lokal
                with open("files/libAuthPuller.so", "rb") as doc:
                    await bot.send_document(message.chat.id, doc, caption="<code>SYSTEM: Lib file for TrashGC</code>", parse_mode='HTML')
            except FileNotFoundError:
                await bot.send_message(message.chat.id, "<code>ERROR: libAuthPuller.so not found in 'files/' directory.</code>", parse_mode='HTML')
            except Exception as e:
                bot_context.console.log(f"[red]System Error:[/] Failed to send Lib file from local: {e}")

        elif message.text in ['Nintendo', 'Huawei', 'Steam', 'Google', 'Sony', 'Facebook']:
            await send_login_prompt(message.text)
        elif message.text == 'Exit':
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, "<code>Bye!</code>", parse_mode='HTML', reply_markup=markup)
            await bot.delete_state(message.from_user.id)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Lua Code', 'Lib Code', 'Nintendo', 'Huawei', 'Steam', 'Google', 'Sony', 'Facebook', 'Exit')
            await bot.set_state(message.from_user.id, bot_context.MyStates.method)
            await bot.send_message(message.chat.id, "<code>Wrong option. Please select a login method.</code>", reply_markup=markup, parse_mode='HTML')

    async def set_headers_and_respond(self, message, user_id, session, version, server_type):
        host = f"{server_type.lower()}.radiance.thatgamecompany.com"
        if server_type.lower() == "live":
            user_agent = f"Sky-Live-com.tgc.sky.android/{version} (Xiaomi M2012K11AG; android 32.0.0; en)"
        else:
            user_agent = f"Sky-Test-com.tgc.sky.android.test.gold/{version} (Apple iPhone 13 Pro Max; android 29.0.0; en)"
        self.headersu.update({'user-id': user_id, 'session': session, 'User-Agent': user_agent, 'Host': host})
        self.headers.update({'User-Agent': user_agent, 'Host': host})

        reply = "SESSION ESTABLISHED\n"
        reply += "----------------------------\n"
        reply += f"USER ID : {user_id}\n"
        reply += f"SESSION : {session}\n"
        reply += "----------------------------"
        await bot_context.bot.reply_to(message, f"<code>{reply}</code>", parse_mode='HTML')

        if bot_context.bot_log:
            log_message = f"<code>AUTH LOG\nNAME: {message.from_user.first_name}\nID: {message.chat.id}\nUID: {user_id}</code>"
            await bot_context.bot_log.send_message(bot_context.ADMIN_ID, log_message, parse_mode='HTML')

    async def lua_handler(self, message, server_type):
        try:
            import base64
            valor1 = list(base64.b64decode(message.text))

            def decrypt(cadena):
                valor = cadena[::-1]
                valorn = [ord(i) for i in valor if not str(valor[0]).isnumeric()]
                valor = valorn if valorn else valor
                num = int(valor[0] / 2)
                desi = []
                for i in valor[1:]:
                    desi.append(chr(i - num))
                    p = str(i)
                    num = int(p[len(p) - 1])
                return desi

            decrypted = json.loads(''.join(decrypt(decrypt(decrypt(valor1)))))
            user_id = decrypted['uid']
            session = decrypted['session']
            version = decrypted.get('version', await Version.get_version(server_type) or '0.33.7.394009')
            await self.set_headers_and_respond(message, user_id, session, version, server_type)
            await self.get_currency(message)
            await self.get_function(message, server_type)
        except Exception as exc:
            print(f"An exception occurred in lua_handler: {exc}")
            await bot_context.bot.reply_to(message, "<code>Invalid Lua code!</code>", parse_mode='HTML')

    async def lib_handler(self, message, server_type):
        try:
            result = await Sessions.lib(message.text)
            if not result:
                raise ValueError("invalid lib")
            user_id, session = result
            version = await Version.get_version(server_type) or '0.33.7.394009'
            await self.set_headers_and_respond(message, user_id, session, version, server_type)
            await self.get_currency(message)
            await self.get_function(message, server_type)
        except Exception as exc:
            print(f"An exception occurred in lib_handler: {exc}")
            await bot_context.bot.reply_to(message, "<code>Invalid Lib code!</code>", parse_mode='HTML')

    async def select_func(self, message, server_type):
        bot = bot_context.bot
        server_type = server_type.lower()
        func = message.text

        # ─── FARM ────────────────────────────────────────────────────────────────
        if func == "Farm":
            cur_before = await Currency.get_currency(self.headersu)
            status_reply = await bot.reply_to(message, Fmt.working("FARM"), parse_mode='HTML')
            try:
                await self.niveles(status_reply)
                cur_after = await Currency.get_currency(self.headersu)
                await bot.send_message(
                    message.chat.id,
                    Fmt.currency_diff(cur_before, cur_after, "FARM RESULT"),
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"[Farm] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("FARM", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── DAILY QUEST ─────────────────────────────────────────────────────────
        elif func == "Daily quest":
            status_reply = await bot.reply_to(message, Fmt.working("DAILY QUEST"), parse_mode='HTML')
            try:
                await self.quest()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.working("DAILY QUEST  processing"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.quest()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("DAILY QUEST  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Daily quest] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("DAILY QUEST", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── DAILY FUNCTION (farm + quest + lit) ─────────────────────────────────
        elif func == "Daily function (farm,quest,lit)":
            status_reply = await bot.reply_to(message, Fmt.working("DAILY"), parse_mode='HTML')
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(1, 3, "Quest"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.quest()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(1, 3, "Quest  running"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.quest()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("DAILY QUEST  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Daily function] Quest error: {e}")
            try:
                await self.niveles(status_reply)
            except Exception as e:
                print(f"[Daily function] Farm error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(3, 3, "Friends"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.enviarwax()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("DAILY  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Daily function] Lit error: {e}")
            await self.get_function(message, server_type)

        # ─── UNLOCK ALL ELDER HAIRS ───────────────────────────────────────────────
        elif func == "Unlock all elder hairs":
            status_reply = await bot.reply_to(message, Fmt.working("ELDER HAIRS"), parse_mode='HTML')
            try:
                await self.calcular()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("ELDER HAIRS  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Elder hairs] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("ELDER HAIRS", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── INF EDEN ────────────────────────────────────────────────────────────
        elif func == "infeden":
            self.inf_eden = True
            status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
            edc = 0
            er = 0
            current_currency = await bot.send_message(message.chat.id, "<code>Current Currency : </code>", parse_mode='HTML')
            err_count = await bot.send_message(message.chat.id, f"<code>error {er} times </code>", parse_mode='HTML')
            while self.inf_eden:
                try:
                    edc += 1
                    await self.eden()
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=f"<code> Eden : {edc} </code>", message_id=status_reply.message_id, parse_mode='HTML')
                    await self.get_currency(current_currency, "edit")
                except Exception:
                    er += 1
                    await bot.edit_message_text(chat_id=err_count.chat.id, text=f"<code> error : {er} times </code>", message_id=err_count.message_id, parse_mode='HTML')
            await bot.delete_message(status_reply.chat.id, status_reply.message_id)
            await bot.delete_message(current_currency.chat.id, current_currency.message_id)
            await bot.delete_message(err_count.chat.id, err_count.message_id)
            await bot.send_message(message.chat.id, "<code> Eden loop stopped </code>", parse_mode='HTML')

        # ─── INF SEASONAL ────────────────────────────────────────────────────────
        elif func == "infseasonal":
            if server_type == "beta":
                self.inf_seasonal = True
                status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
                scd_total = 0
                er = 0
                current_currency = await bot.send_message(message.chat.id, "<code>Current Currency : </code>", parse_mode='HTML')
                err_count = await bot.send_message(message.chat.id, f"<code>error {er} times </code>", parse_mode='HTML')
                while self.inf_seasonal:
                    try:
                        scd_total += 30
                        await self.seasonal_candle()
                        await bot.edit_message_text(chat_id=status_reply.chat.id, text=f"<code> seasonal candle added : {scd_total} </code>", message_id=status_reply.message_id, parse_mode='HTML')
                        await self.get_currency(current_currency, "edit")
                    except Exception:
                        er += 1
                        await bot.edit_message_text(chat_id=err_count.chat.id, text=f"<code> error : {er} times </code>", message_id=err_count.message_id, parse_mode='HTML')
                await bot.delete_message(status_reply.chat.id, status_reply.message_id)
                await bot.delete_message(current_currency.chat.id, current_currency.message_id)
                await bot.delete_message(err_count.chat.id, err_count.message_id)
                await bot.send_message(message.chat.id, "<code> Seasonal Candle loop stopped </code>", parse_mode='HTML')
            else:
                await bot.reply_to(message, "<code>This only available at beta</code>", parse_mode='HTML')
                await self.get_function(message, server_type)

        # ─── CANCEL ──────────────────────────────────────────────────────────────
        elif func == "cancel":
            await bot.reply_to(message, Fmt.done("EDEN  done"), parse_mode='HTML')
            self.inf_eden = False
            await self.get_function(message, server_type)

        # ─── UNLOCK ALL MAP ───────────────────────────────────────────────────────
        elif func == "Unlock all map":
            status_reply = await bot.reply_to(message, Fmt.working("UNLOCK MAP"), parse_mode='HTML')
            try:
                await self.desboheart()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.working("UNLOCK MAP  sending"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.desbo()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("UNLOCK MAP  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Unlock all map] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("UNLOCK MAP", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── UNLOCK ALL EMOTES ────────────────────────────────────────────────────
        # FIX: hapus edit_message_text setelah coles() karena SpiritMessage
        # sudah melakukan edit sendiri di dalamnya — double edit bisa crash.
        elif func == "Unlock all emotes":
            status_reply = await bot.reply_to(message, Fmt.working("UNLOCK EMOTES"), parse_mode='HTML')
            try:
                await self.coles(status_reply)
                # SpiritMessage sudah update status_reply di dalamnya,
                # jadi kita hanya perlu send pesan selesai terpisah
                await bot.send_message(message.chat.id, Fmt.done("UNLOCK EMOTES  done"), parse_mode='HTML')
            except Exception as e:
                print(f"[Unlock all emotes] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("UNLOCK EMOTES", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── EDEN ─────────────────────────────────────────────────────────────────
        elif func == "Eden":
            status_reply = await bot.reply_to(message, Fmt.working("EDEN"), parse_mode='HTML')
            try:
                await self.eden()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("EDEN  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Eden] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("EDEN", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── WINGS ────────────────────────────────────────────────────────────────
        elif func == "Wings":
            status_reply = await bot.reply_to(message, Fmt.working("WINGS"), parse_mode='HTML')
            try:
                await self.alas()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("WINGS  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Wings] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("WINGS", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── LIT & COLLECT ────────────────────────────────────────────────────────
        elif func == "Lit & Collect friends light":
            status_reply = await bot.reply_to(message, Fmt.working("LIT FRIENDS"), parse_mode='HTML')
            try:
                await self.enviarwax()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("LIT FRIENDS  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Lit & Collect] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("LIT FRIENDS", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── WORLD QUEST ──────────────────────────────────────────────────────────
        elif func == "World Quest":
            status_reply = await bot.reply_to(message, Fmt.working("WORLD QUEST"), parse_mode='HTML')
            try:
                await self.todo()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("WORLD QUEST  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[World Quest] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("WORLD QUEST", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── SEASONAL QUEST ───────────────────────────────────────────────────────
        elif func == "Seasonal Quest":
            status_reply = await bot.reply_to(message, Fmt.working("SEASONAL QUEST"), parse_mode='HTML')
            try:
                await self.Principe()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("SEASONAL QUEST  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Seasonal Quest] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("SEASONAL QUEST", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── ELDER MASK ───────────────────────────────────────────────────────────
        elif func == "Elder Mask":
            status_reply = await bot.reply_to(message, Fmt.working("ELDER MASK"), parse_mode='HTML')
            try:
                await self.eldermask()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("ELDER MASK  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[Elder Mask] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("ELDER MASK", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── ALL ──────────────────────────────────────────────────────────────────
        # FIX: hapus re-assign status_reply di tengah-tengah, pakai satu pesan
        # konsisten dan wrap tiap step dengan try/except agar satu step gagal
        # tidak menghentikan seluruh flow.
        elif func == "All":
            status_reply = await bot.reply_to(message, Fmt.working("ALL"), parse_mode='HTML')
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(1,7,"Unlock Map"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.desboheart()
                await self.desbo()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(1,7,"Unlock Map  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All] Map error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(2,7,"Wings"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.alas()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(2,7,"Wings  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All] Wings error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(3,7,"Eden"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.eden()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("EDEN  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All] Eden error: {e}")
            try:
                await self.niveles(status_reply)
            except Exception as e:
                print(f"[All] Farm error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(4,7,"Daily Quest"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.quest()
                await self.quest()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(4,7,"Daily Quest  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All] Quest error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(5,7,"World Quest"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.todo()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("WORLD QUEST  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All] World Quest error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(6,7,"Seasonal Quest"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.Principe()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("SEASONAL QUEST  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All] Seasonal Quest error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.step(7,7,"Unlock Emotes"), message_id=status_reply.message_id, parse_mode='HTML')
                await self.coles(status_reply)
            except Exception as e:
                print(f"[All] Emotes error: {e}")
            try:
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("ALL  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception:
                await bot.send_message(message.chat.id, Fmt.done("ALL  done"), parse_mode='HTML')
            await self.get_currency(message)
            await self.get_function(message, server_type)

        # ─── CANDLE INFO ──────────────────────────────────────────────────────────
        elif func == "Candle info":
            await self.get_currency(message)
            await self.get_function(message, server_type)

        # ─── ALL WINGS (hidden) ───────────────────────────────────────────────────
        elif func == "allwings":
            status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
            try:
                await self.alasall()
                await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("ALL WINGS  done"), message_id=status_reply.message_id, parse_mode='HTML')
            except Exception as e:
                print(f"[All wings] Error: {e}")
                try:
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("ALL WINGS", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception:
                    pass
            await self.get_function(message, server_type)

        # ─── ALL IAP (beta only) ──────────────────────────────────────────────────
        elif func == "All Iap":
            if server_type == "beta":
                status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
                try:
                    await self.unlock_all_iap(status_reply, self.headersu['user-id'], self.headersu['session'])
                except Exception as e:
                    print(f"[All Iap] Error: {e}")
                await self.get_function(message, server_type)
            else:
                await bot.reply_to(message, "<code>This only available at beta</code>", parse_mode='HTML')
                await self.get_function(message, server_type)

        # ─── 300 SEASONAL CANDLE (beta only) ─────────────────────────────────────
        elif func == "300 Seasonal Candle":
            if server_type == "beta":
                status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
                try:
                    await self.seasonal_candle_300(status_reply, self.headersu['user-id'], self.headersu['session'])
                    await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.done("300 SEASONAL CANDLE  done"), message_id=status_reply.message_id, parse_mode='HTML')
                except Exception as e:
                    print(f"[300 Seasonal Candle] Error: {e}")
                    try:
                        await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("300 SEASONAL CANDLE", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                    except Exception:
                        pass
                await self.get_currency(message)
                await self.get_function(message, server_type)
            else:
                await bot.reply_to(message, "<code>This only available at beta</code>", parse_mode='HTML')
                await self.get_function(message, server_type)

        # ─── WHITE CANDLE (hidden, beta only) ────────────────────────────────────
        elif func == "white_candle":
            if server_type == "beta":
                status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
                try:
                    await self.white_candle(status_reply, self.headersu['user-id'], self.headersu['session'])
                except Exception as e:
                    print(f"[white_candle] Error: {e}")
                    try:
                        await bot.edit_message_text(chat_id=status_reply.chat.id, text=Fmt.error("WHITE CANDLE", str(e)), message_id=status_reply.message_id, parse_mode='HTML')
                    except Exception:
                        pass
                await self.get_currency(message)
                await self.get_function(message, server_type)
            else:
                await bot.reply_to(message, "<code>This only available at beta</code>", parse_mode='HTML')
                await self.get_function(message, server_type)

        # ─── UNLOCK ALL (hidden) ──────────────────────────────────────────────────
        elif func == "unlock_all":
            status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
            try:
                await self.unlock_all(status_reply, self.headersu['user-id'], self.headersu['session'])
            except Exception as e:
                print(f"[unlock_all] Error: {e}")
            await self.get_currency(message)
            await self.get_function(message, server_type)

        # ─── LOCK ALL (hidden) ────────────────────────────────────────────────────
        elif func == "lock_all":
            status_reply = await bot.reply_to(message, Fmt.working(func.upper()), parse_mode='HTML')
            try:
                await self.lock_all(status_reply, self.headersu['user-id'], self.headersu['session'])
            except Exception as e:
                print(f"[lock_all] Error: {e}")
            await self.get_currency(message)
            await self.get_function(message, server_type)

        # ─── EXIT ─────────────────────────────────────────────────────────────────
        elif func == "Exit":
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, "<code>Have a great day, Bye !</code>", parse_mode='HTML', reply_markup=markup)
            await bot.delete_state(message.from_user.id)

        # ─── UNKNOWN ──────────────────────────────────────────────────────────────
        else:
            await bot.send_message(message.chat.id, "<code>Wrong function</code>", parse_mode='HTML')
            await self.get_function(message, server_type)