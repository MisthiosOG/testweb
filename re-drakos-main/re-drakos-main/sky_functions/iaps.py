import asyncio
from functions.sky_request import SkyRequest


class Iap:
    @staticmethod
    async def _receipt(header, product_id):
        payload = await SkyRequest.payload_with_id(header, {
            "platform": "fake",
            "receipt": f"com.tgc.sky.android.test.gold.{product_id}",
            "target_pid": product_id,
            "target_uid": header['user-id'],
        })
        return await SkyRequest.make_request(header, '/account/commerce/receipt', payload)

    @staticmethod
    async def seasonal_candle(header):
        return await Iap._receipt(header, "SPASSP3")

    @staticmethod
    async def white_candle(header):
        return await Iap._receipt(header, "CDL50")

    @staticmethod
    async def seasonal_candle_300(header):
        tasks = [Iap.seasonal_candle(header) for _ in range(10)]
        await asyncio.gather(*tasks)

    @staticmethod
    async def unlock_all_iap(header, bot=None, message=None):
        for iap_number in range(80):
            product_id = f"SNC{iap_number:02d}"
            await Iap._receipt(header, product_id)
            if bot and message:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    text=f"<code>[SYSTEM] PROCESSING: {product_id}</code>",
                    message_id=message.message_id,
                    parse_mode='HTML',
                )
