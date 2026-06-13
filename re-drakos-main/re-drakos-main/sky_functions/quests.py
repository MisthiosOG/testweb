import json
from functions.sky_request import SkyRequest
from functions.read_resource import ReadResource

daily_quest = ReadResource.read_json("DailyQuestDefs.json")
world_quest = ReadResource.read_json("WorldQuestDefs.json")
world_quest_c = ReadResource.read_json("WorldQuestDefsC.json")


class Quest:
    @staticmethod
    async def daily_quest(header):
        payload = await SkyRequest.payload_with_id(header, {
            "quest_id": "",
            "achievement_stats": [{"type": "", "value": 0}]
        })
        paths = [
            "/account/get_season_quests",
            "/account/activate_season_quest",
            "/account/set_achievement_stats",
            "/account/claim_season_quest_reward"
        ]
        today_quest = await SkyRequest.make_request(header, paths[0], payload)
        quest_data = json.loads(today_quest)
        has_season_quests_reward = quest_data["has_season_quests_rewards"]
        season_quests = quest_data["season_quests"]
        for i in range(len(has_season_quests_reward)):
            payload["quest_id"] = season_quests[i]["daily_quest_def_id"]
            await SkyRequest.make_request(header, paths[1], payload)
        for i in range(len(has_season_quests_reward)):
            if has_season_quests_reward[i]["rewarded"]:
                continue
            aumenta = season_quests[i]["start_value"]
            payload["quest_id"] = season_quests[i]["daily_quest_def_id"]
            payload["achievement_stats"][0]["type"] = season_quests[i]["stat_type"]
            for quest_def in daily_quest:
                if quest_def["id"] == payload["quest_id"]:
                    aumenta += quest_def["stat_delta"]
                    payload["achievement_stats"][0]["value"] = aumenta
                    break
            await SkyRequest.make_request(header, paths[2], payload)
            await SkyRequest.make_request(header, paths[3], payload)

    @staticmethod
    async def seasonal_guide_quest(header):
        payload = await SkyRequest.payload_with_id(header, {"names": []})
        for season in range(4, 24):
            season_code = f"0{season}" if season < 10 else str(season)
            total = [f'ap06unlock_ap{season_code}_fetch_0{i}_quest_done' for i in range(1, 9)]
            payload["names"] = total
            await SkyRequest.make_request(header, '/service/status/api/v1/add_unlocks_batch', payload)

    @staticmethod
    async def world_quest(header):
        payload = await SkyRequest.payload_with_id(header, {"name": "", "bonus_percent": 1})
        for quest in world_quest:
            payload["name"] = quest["id"]
            await SkyRequest.make_request(header, '/account/claim_quest_reward', payload)

    @staticmethod
    async def world_quest_c(header):
        payload = await SkyRequest.payload_with_id(header, {"name": "", "bonus_percent": 1})
        for quest in world_quest_c:
            payload["name"] = quest["id"]
            await SkyRequest.make_request(header, '/account/wing_buffs/collect', payload)
