import base64
import json

import bot_context
from functions.version_live import get_version as sky_version
from functions.version import Version
from sky_functions.farm import FarmMessage
from sky_functions.quests import Quest


class Hidden:
    @staticmethod
    async def lua_handler(message):
        bot = bot_context.bot
        try:
            code = message.text.split(' ')[1]
            valor1 = list(base64.b64decode(code))

            def des(cadena):
                valor = cadena[::-1]
                valorn = []
                if not str(valor[0]).isnumeric():
                    for i in valor:
                        valorn.append(ord(i))
                    valor = valorn
                num = int(valor[0] / 2)
                desi = []
                for i in valor[1:]:
                    desi.append(chr(i - num))
                    p = str(i)
                    num = int(p[len(p) - 1])
                return desi

            var = json.loads(''.join(des(des(des(valor1))))) # This is a very specific decryption logic
            version = var.get('version', await Version.get_version('live') or '0.33.7.394009')
            headersu = {
                'Host': 'live.radiance.thatgamecompany.com',
                'User-Agent': f'Sky-Live-com.tgc.sky.android/{version} (Xiaomi M2012K11AG; android 32.0.0; en)',
                'X-Session-ID': 'aeee648a-ea1f-4700-b970-ebe955750601',
                'user-id': var['uid'],
                'session': var['session'],
                'Content-type': 'application/json',
            }
            await bot.reply_to(
                message,
                f"<code>user-id :{headersu['user-id']}\nsession :{headersu['session']}</code>",
                parse_mode='HTML',
            )
            currency = await Currency.get_currency(headersu)
            candle_rep = await CurrencyMesasge.send_currency_mesasge(bot, message, currency)
            status_reply = await bot.send_message(message.chat.id, "<code>The status</code>", parse_mode='HTML')
            await FarmMessage.send_farm_message(bot, status_reply, headersu)
            await Quest.daily_quest(headersu)
            await bot.edit_message_text(chat_id=status_reply.chat.id, text="<code>Doing Quest ...</code>", message_id=status_reply.message_id, parse_mode='HTML')
            await Quest.daily_quest(headersu)
            await bot.edit_message_text(chat_id=status_reply.chat.id, text="<code>Daily Quest done</code>", message_id=status_reply.message_id, parse_mode='HTML')
            await bot.delete_message(candle_rep.chat.id, candle_rep.message_id)
            currency = await Currency.get_currency(headersu)
            await bot.send_message(message.chat.id, f"<code>All done \n{''.join(f'{k} : {v}\n' for k,v in currency['currency'].items())}</code>", parse_mode='HTML')
        except Exception as exc:
            print(f"Hidden lua handler failed: {exc}")
            await bot.reply_to(message, "<code>Code not valid</code>", parse_mode='HTML')
