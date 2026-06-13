from functions.read_resource import ReadResource
from functions.sky_request import SkyRequest
from sky_functions.wings import Wings

wing_list = ReadResource.read_json("wings.json")


class Eden:
    @staticmethod
    async def eden(header):
        payload = await SkyRequest.payload_with_id(header, {"name_deposit_id_pairs": []})
        wing_payload = [[wing_list[i], i + 1] for i in range(len(wing_list))]
        payload["name_deposit_id_pairs"] = wing_payload
        await SkyRequest.make_request(header, '/account/wing_buffs/deposit', payload)
        await SkyRequest.make_request(header, '/account/wing_buffs/convert', await SkyRequest.payload_with_id(header, {}))
        await SkyRequest.make_request(header, '/account/rebirth', await SkyRequest.payload_with_id(header, {}))
        await Wings.map_wings(header)
