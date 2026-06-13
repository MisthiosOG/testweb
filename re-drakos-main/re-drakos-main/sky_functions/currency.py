import json
from functions.sky_request import SkyRequest
from functions.fmt import Fmt


class Currency:
    @staticmethod
    async def get_currency(header):
        payload = await SkyRequest.payload_with_id(header, {})
        raw = await SkyRequest.make_request(header, '/account/get_currency', payload)
        return json.loads(raw)


class CurrencyMesasge:
    @staticmethod
    async def send_currency_mesasge(bot, message, currency):
        text = Fmt.currency(currency, "BALANCE")
        return await bot.send_message(message.chat.id, text, parse_mode='HTML')

    @staticmethod
    async def edit_currency_mesasge(bot, message, currency):
        text = Fmt.currency(currency, "BALANCE")
        await bot.edit_message_text(
            chat_id=message.chat.id, text=text,
            message_id=message.message_id, parse_mode='HTML'
        )
