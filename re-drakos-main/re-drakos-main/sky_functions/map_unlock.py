from functions.read_resource import ReadResource
from functions.sky_request import SkyRequest

desbloqueables = ReadResource.read_json("desbloqueables.txt")
spirit_shop = ReadResource.read_json("spiritshop.txt")


class MapUnlock:
    @staticmethod
    async def unlock_maps(header):
        payload = await SkyRequest.payload_with_id(header, {"names": []})
        total = [item["name"] for item in desbloqueables if item["type"] not in ['level']]
        payload["names"] = total
        await SkyRequest.make_request(header, '/service/status/api/v1/add_unlocks_batch', payload)

    @staticmethod
    async def unlock_map_hearts(header):
        payload = await SkyRequest.payload_with_id(header, {"unlock_id": 0})
        unlock_ids = [shop["id"] for shop in spirit_shop["spirit_shops"] if shop["typ"] == "ap06unlock"]
        for unlock_id in unlock_ids:
            payload["unlock_id"] = unlock_id
            await SkyRequest.make_request(header, '/account/purchase_spirit_shop_item', payload)
