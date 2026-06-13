from functions.read_resource import ReadResource
from functions.sky_request import SkyRequest

wing_list = ReadResource.read_json("wings.json")


class Wings:
    @staticmethod
    async def map_wings(header):
        payload = await SkyRequest.payload_with_id(header, {"names": []})
        wing_payload = [wing for wing in wing_list if wing[0] != "s"]
        payload["names"] = wing_payload
        await SkyRequest.make_request(header, '/account/wing_buffs/collect', payload)

    @staticmethod
    async def all_wings(header):
        payload = await SkyRequest.payload_with_id(header, {"names": wing_list})
        await SkyRequest.make_request(header, '/account/wing_buffs/collect', payload)
