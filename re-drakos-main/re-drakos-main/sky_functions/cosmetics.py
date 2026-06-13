import asyncio
import math
from functions.read_resource import ReadResource
from functions.sky_request import SkyRequest

cosmetic_list = ReadResource.read_json("CosmeticAll.json")


class Cosmetics:
    @staticmethod
    async def _batched_request(header, names, endpoint):
        total_batches = 10
        batch_size = math.ceil(len(names) / total_batches)
        batches = [names[i:i + batch_size] for i in range(0, len(names), batch_size)][:total_batches]
        for batch in batches:
            payload = await SkyRequest.payload_with_id(header, {"names": batch})
            await SkyRequest.make_request(header, endpoint, payload)
            await asyncio.sleep(0.5)

    @staticmethod
    async def unlock_all_cosmetics(header):
        await Cosmetics._batched_request(header, cosmetic_list, '/service/status/api/v1/add_unlocks_batch')

    @staticmethod
    async def remove_all_cosmetics(header):
        await Cosmetics._batched_request(header, cosmetic_list, '/service/status/api/v1/delete_unlocks_batch')

    @staticmethod
    async def unlock_all_with_status(bot, message, header):
        await Cosmetics.unlock_all_cosmetics(header)
        await bot.edit_message_text(
            chat_id=message.chat.id,
            text="<code>done unlock all cosmetics</code>",
            message_id=message.message_id,
            parse_mode='HTML',
        )

    @staticmethod
    async def remove_all_with_status(bot, message, header):
        await Cosmetics.remove_all_cosmetics(header)
        await bot.edit_message_text(
            chat_id=message.chat.id,
            text="<code>done lock all cosmetics</code>",
            message_id=message.message_id,
            parse_mode='HTML',
        )
