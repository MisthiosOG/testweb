import base64
import json

from functions.license import License
from functions.sky_request import SkyRequest
import bot_context


class Sessions:
    @staticmethod
    async def lua(code):
        try:
            valor1 = list(base64.b64decode(code))

            def des(cadena):
                valor = cadena[::-1]
                valorn = []
                if not str(valor[0]).isnumeric():
                    for i in valor:
                        valorn.append(ord(i))
                    valor = valorn
                num = int(valor[0] / 2)
                desi = []
                for i in valor[1:]:
                    desi.append(chr(i - num))
                    p = str(i)
                    num = int(p[len(p) - 1])
                return desi

            valuer = ''.join(des(des(des(valor1))))
            var = json.loads(valuer)
            return var['uid'], var['session']
        except Exception as exc:
            print(f"Error at lua code extraction: {exc}")
            return False

    @staticmethod
    async def lib(code):
        try:
            data = json.loads(code)
            return data['user'], data['session']
        except Exception as exc:
            print(f"Error at lib code extraction: {exc}")
            return False

    @staticmethod
    def build_oauth_payload(login_type, player_id, signature, environment):
        normalized = login_type.capitalize()
        if environment == "live":
            return License.build_live_payload(normalized, player_id, signature)
        return License.build_beta_payload(normalized, player_id, signature)

    @staticmethod
    async def login(payload, headers):
        try:
            response_data = await SkyRequest.make_request(headers, '/account/auth/login', payload)
            if not response_data:
                return False
            data = json.loads(response_data)
            if "result" in data and data["result"] not in ("ok", "not_found", "expired"):
                bot_context.console.log(f"[yellow]Login Server Response:[/] {data['result']}")
                
            if data.get("result") in ("not_found", "expired"):
                return data["result"], None
            user_id = data.get("result", data.get("authinfo", {}).get("user"))
            session = data.get("session", data.get("result"))
            return user_id, session
        except Exception as exc:
            print(f"Error at login: {exc}")
            return False
