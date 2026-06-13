import json
from functions.sky_request import SkyRequest


class Friends:
    @staticmethod
    async def lit_and_collect(header):
        food = await SkyRequest.payload_with_id(header, {"max": 86, "sort_ver": 1})
        claim = await SkyRequest.payload_with_id(header, {"msg_id": 2513664012})
        gift = await SkyRequest.payload_with_id(header, {
            "target": "02501d44-53b8-4206-964d-042004f0f6f3",
            "gift_type": "gift_heart_wax"
        })
        paths = [
            "/account/get_friend_statues",
            "/account/send_message",
            "/account/get_pending_messages",
            "/account/claim_message_gift"
        ]
        today = await SkyRequest.make_request(header, paths[0], food)
        pending = await SkyRequest.make_request(header, paths[2], await SkyRequest.payload_with_id(header, {}))
        friends = json.loads(today)["set_friend_statues"]
        pending_messages = json.loads(pending)["set_recvd_messages"]
        for friend in friends:
            gift["target"] = friend["friend_id"]
            await SkyRequest.make_request(header, paths[1], gift)
        for message in pending_messages:
            claim["msg_id"] = message["msg_id"]
            await SkyRequest.make_request(header, paths[3], claim)
