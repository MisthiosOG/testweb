import json

from functions.sky_request import SkyRequest
from sky_functions.map_unlock import MapUnlock
from sky_functions.wings import Wings
from sky_functions.eden import Eden
from sky_functions.farm import FarmMessage
from sky_functions.quests import Quest
from sky_functions.spirit import SpiritMessage
from sky_functions.currency import Currency, CurrencyMesasge


class Account:
    @staticmethod
    async def create_account(header, bot, message):
        account_data = {
            "type": "Local",
            "device_token": (
                "cYngJMuqSCCSZNGDYnA9WL"
                ":APA91bGHNl6vwQD6QQxZ6xCDStoAopU0Q1MbXnyezsHT0xDqtRhHoG2mTGfRMdKOzFh50VprC_mhqeRudXDdQo2axYHTz2G8m1fMQoQH3pJBm7_h5GLNSumxVu1bDqCegkhMw0y3-cop"
            ),
            "production": True,
            "tos_version": 4,
            "device_key": "Ao4zqAlBtPKaaQErCGeDdQKrppSd5iuY/Hli+Rhovvm8",
            "sig_ts": 1624505241,
            "sig": "MEQCIClzltuaMlYbpU4eygo3UIxLbQ4NKQbs0lpPA9ycITvoAiAp+TgeQBHaMLOvn78PtV6LKBBJOMol5JiZ2dnxm6UwNQ==",
            "hashes": [
                1923375798, 122808847, 118657115, 3349695617,
                2905245314, 1246829562, 2625462588, 3062676827,
                2766223387, 4121453246, 2798274008, 3585622646,
                3768441912, 3478312597, 3661381049, 3059530656,
                421587558, 3979675450,
            ],
            "integrity": True,
        }
        response = await SkyRequest.make_request(header, "/account/auth/create", account_data)
        if not response:
            return None, None
        data = json.loads(response)
        user_id = data["authinfo"]["user"]
        session = data["session"]
        await bot.send_message(
            message.chat.id,
            f"<code>Account created with user ID: {user_id} and session: {session}</code>",
            parse_mode='HTML',
        )
        return user_id, session

    @staticmethod
    async def bind(header, bot, message, platform_type, platform_id, platform_token, run_all=True):
        bind_data = {
            "user": header['user-id'],
            "session": header['session'],
            "external_account_type": platform_type,
            "player_id": platform_id,
            "key_url": "",
            "signature": platform_token,
            "salt": "",
            "timestamp": 0,
            "alias": "",
        }
        response = await SkyRequest.make_request(header, "/account/link_external", bind_data)
        await bot.send_message(message.chat.id, f"<code>{response}</code>", parse_mode='HTML')
        if not response:
            return None
        data = json.loads(response)
        if data.get("result") != "ok" or not run_all:
            return response

        status_reply = await bot.reply_to(message, "<code>Starting All : ...</code>", parse_mode='HTML')
        await MapUnlock.unlock_map_hearts(header)
        await bot.reply_to(message, "<code>Unlock all map done</code>", parse_mode='HTML')
        await Wings.map_wings(header)
        await bot.edit_message_text(
            chat_id=status_reply.chat.id,
            text="<code>Unlock wing done</code>",
            message_id=status_reply.message_id,
            parse_mode='HTML',
        )
        await Eden.eden(header)
        await bot.edit_message_text(
            chat_id=status_reply.chat.id,
            text="<code>Eden done</code>",
            message_id=status_reply.message_id,
            parse_mode='HTML',
        )
        await MapUnlock.unlock_maps(header)
        await FarmMessage.send_farm_message(bot, status_reply, header)
        await Quest.daily_quest(header)
        await Quest.daily_quest(header)
        await bot.edit_message_text(
            chat_id=status_reply.chat.id,
            text="<code>Daily Quest done</code>",
            message_id=status_reply.message_id,
            parse_mode='HTML',
        )
        await Quest.world_quest(header)
        await bot.edit_message_text(
            chat_id=status_reply.chat.id,
            text="<code>World Quest done</code>",
            message_id=status_reply.message_id,
            parse_mode='HTML',
        )
        await Quest.seasonal_guide_quest(header)
        await bot.edit_message_text(
            chat_id=status_reply.chat.id,
            text="<code>Seasonal Quest done</code>",
            message_id=status_reply.message_id,
            parse_mode='HTML',
        )
        await SpiritMessage.send_spirit_message(header, status_reply, bot)
        await bot.edit_message_text(
            chat_id=status_reply.chat.id,
            text="<code>All done</code>",
            message_id=status_reply.message_id,
            parse_mode='HTML',
        )
        currency = await Currency.get_currency(header)
        await CurrencyMesasge.send_currency_mesasge(bot, message, currency)
        return response
