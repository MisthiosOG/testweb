import aiohttp
import json
import bot_context


class SkyRequest:
    @staticmethod
    async def make_request(header, path, payload):
        host = header.get("Host") or header.get("host")
        url = f"https://{host}{path}"
        async with aiohttp.TCPConnector(ssl=False) as conn:
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.post(url=url, data=json.dumps(payload), headers=header) as request:
                    if request.status == 200:
                        data = await request.text()
                        bot_context.console.log(f"[bold green]200[/] POST [cyan]{path}[/]")
                        return data
                    bot_context.console.log(f"[bold red]{request.status}[/] POST [cyan]{path}[/]", style="yellow")

    @staticmethod
    async def payload_with_id(header, payload):
        new_payload = {
            "user": f"{header['user-id']}",
            "session": f"{header['session']}",
        }
        new_payload.update(payload)
        return new_payload
