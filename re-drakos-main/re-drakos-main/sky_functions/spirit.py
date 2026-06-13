from functions.read_resource import ReadResource
from functions.sky_request import SkyRequest

spirit_list = ReadResource.read_json("CollectibleDefs.json")


class SpiritMessage:
    @staticmethod
    async def send_spirit_message(header, message, bot):
        food = await SkyRequest.payload_with_id(header, {"name": '', "carrying": False})
        await bot.edit_message_text(
            chat_id=message.chat.id,
            text="<code>[SYSTEM] STATUS: RETRIEVING EMOTES</code>",
            message_id=message.message_id,
            parse_mode='HTML'
        )
        total_loop = len(spirit_list)
        for index, spirit in enumerate(spirit_list, start=1):
            food["name"] = spirit["name"]
            if index % 8 == 0:
                bar_len = 10
                filled = int((index / total_loop) * bar_len)
                bar = "=" * filled + "-" * (bar_len - filled)
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    text=f"<code>PROGRESS: {index}/{total_loop} [{bar}]</code>",
                    message_id=message.message_id,
                    parse_mode='HTML'
                )
            await SkyRequest.make_request(header, '/account/collect_collectible', food)

    @staticmethod
    async def send_elder_hair_message(header, message, bot):
        elder_hair_ids = [
            416680174, 2432602294, 1078517906, 3381405437,
            777821397, 2681369749, 3721236258
        ]
        payload = await SkyRequest.payload_with_id(header, {"unlock_id": 0})
        for unlock_id in elder_hair_ids:
            payload["unlock_id"] = unlock_id
            await SkyRequest.make_request(header, '/account/purchase_spirit_shop_item', payload)

    @staticmethod
    async def send_elder_mask_message(header, message, bot):
        elder_mask_ids = [850155893, 776944197, 4247878009]
        payload = await SkyRequest.payload_with_id(header, {"unlock_id": 0})
        for unlock_id in elder_mask_ids:
            payload["unlock_id"] = unlock_id
            await SkyRequest.make_request(header, '/account/purchase_spirit_shop_item', payload)
