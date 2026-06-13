from functions.sky_request import SkyRequest
from functions.read_resource import ReadResource
import bot_context

try:
    candle_list = ReadResource.read_json("levels.json")
    bot_context.console.log(f"[green]Farm:[/] Loaded {len(candle_list)} levels from levels.json")
except Exception as e:
    bot_context.console.log(f"[red]Farm ERROR:[/] Failed to load levels.json: {e}")
    candle_list = {}


class Farm:
    @staticmethod
    async def farm(header):
        if not candle_list:
            print("[Farm] candle_list is empty, skipping farm")
            return

        payload_collect = await SkyRequest.payload_with_id(header, {
            "level_id": 0,
            "pickup_ids": [],
            "emitters": []
        })
        payload_forge = await SkyRequest.payload_with_id(header, {
            "currency": "candles",
            "forge_currency": "wax",
            "count": 19,
            "cost": 150
        })
        for level_id in candle_list.keys():
            for candlelist in candle_list[level_id]:
                payload_collect["level_id"] = int(level_id)
                payload_collect["pickup_ids"] = candlelist
                try:
                    await SkyRequest.make_request(header, '/account/collect_pickup_batch', payload_collect)
                except Exception as e:
                    print(f"[Farm] Error collecting level {level_id}: {e}")
        try:
            await SkyRequest.make_request(header, '/account/buy_candle_wax', payload_forge)
        except Exception as e:
            print(f"[Farm] Error forging wax: {e}")


class FarmMessage:
    @staticmethod
    async def send_farm_message(bot, message, header):
        if not candle_list:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                text="<code>Farm error: levels.json not loaded or empty</code>",
                message_id=message.message_id,
                parse_mode='HTML'
            )
            print("[FarmMessage] candle_list is empty, aborting")
            return

        payload_collect = await SkyRequest.payload_with_id(header, {
            "level_id": 0,
            "pickup_ids": [],
            "emitters": []
        })
        payload_forge = await SkyRequest.payload_with_id(header, {
            "currency": "candles",
            "forge_currency": "wax",
            "count": 19,
            "cost": 150
        })

        await bot.edit_message_text(
            chat_id=message.chat.id,
            text="<code>[SYSTEM] STATUS: FARMING IN PROGRESS</code>",
            message_id=message.message_id,
            parse_mode='HTML'
        )

        progress = 0
        total = len(candle_list)
        for level_id in candle_list.keys():
            progress += 1
            for candlelist in candle_list[level_id]:
                payload_collect["level_id"] = int(level_id)
                payload_collect["pickup_ids"] = candlelist
                try:
                    await SkyRequest.make_request(header, '/account/collect_pickup_batch', payload_collect)
                except Exception as e:
                    print(f"[FarmMessage] Error collecting level {level_id}: {e}")
            bar_len = 10
            filled = int((progress / total) * bar_len)
            bar = "=" * filled + "-" * (bar_len - filled)
            try:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    text=f"<code>PROGRESS: {progress}/{total} [{bar}]</code>",
                    message_id=message.message_id,
                    parse_mode='HTML'
                )
            except Exception:
                pass  # Ignore edit errors during progress update

        try:
            await SkyRequest.make_request(header, '/account/buy_candle_wax', payload_forge)
        except Exception as e:
            print(f"[FarmMessage] Error forging wax: {e}")

        await bot.edit_message_text(
            chat_id=message.chat.id,
            text="<code>STATUS: Farm sequence completed</code>",
            message_id=message.message_id,
            parse_mode='HTML'
        )