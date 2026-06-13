import copy

LIVE_LOGIN_BASE = {
    "external_credentials": {
        "key_url": "",
        "salt": "",
        "timestamp": 0,
        "alias": "",
    },
    "user": "00000000-0000-0000-0000-000000000000",
    "device": "00000000-0000-0000-0000-000000000000",
    "key": "0000000000000000000000000000000000000000000000000000000000000000",
    "device_name": "M2012K11AI",
    "device_token": "cKN45n7UTSKHNoyzdugWNE:APA91bFg8MGDK26uj-RjRrRSANDGST4AqE29kh3ygCzN0IZWLgGis2K16aD9JoYXnaRBD2LgghA18Bc0ZG76AuWEzr3eAMTSRen8SsBPjtPftUVnuXECrjVfhd9z_WeDbx9MaHUO7GS9",
    "production": True,
    "tos_version": 4,
    "device_key": "AzsVI0WrO7ogCD1XQc4x7UP8NFvWkgprHKr9Dy3EldUs",
    "sig_ts": 1654180945,
    "sig": "MEQCIAMQ36cVdxjL+/jCGsfKmjhtEQVZFMIW2ICzHzhuADhbAiAlDdhjLkrxVTPer/EPmeIOqrU8f5yJyBCmsBaqw6pFxQ==",
    "hashes": [
        1135420871, 4291554428, 1662465570, 2939294528, 2864712656, 784335679,
        1246829562, 4147059363, 191933768, 3062676827, 3931787622, 2766223387,
        576746911, 2275726205, 1729690551, 2495669098, 2669125820, 495611257,
        1810499009, 3661381049, 943977965, 3914553296, 2198427157, 1330181820,
    ],
    "integrity": True,
}

BETA_LOGIN_BASE = {
    **LIVE_LOGIN_BASE,
    "install_license": (
        "0:0|-2142255415|com.tgc.sky.android.test.gold|222967|"
        "ANlOHQMLwncNA9HE4mh7c6SJ0JDrC4TLnQ==|1687414134937:VT=9223372036854775807|"
        "O94CEx0HXJ6o3STD3aVWGJd3uwGfxsFQDP1S4A7zIhkNvb0ceoYQVV2ppb6V92fst9fBYhZ8h7/"
        "C2gsFQLkISBKBjFuWW3Z2wbW/9wBFUHzAFuklOEPNKovsgGrAXjKb06GhcPSxGxaeAwT+p+NiFiVZXFKx3KQid8U31VIBErS6rY73d/8+os8kTTol2DyAb0F0kQAr1YUd38OkJeEkicjetToo8LevSGoOeIxaWSF6c8+HxwCpfB9Scb1p62eSuvWFodzJjUT15L5lnUo4LPPpulM7V+Wjm/y1gJ5BywMNfDgBgIr2XZIpdr+dAUOxKUzExcNaZMCIOLuR3UTESQ=="
    ),
    "device_name": "iPowfuVM",
    "device_token": "c3uV1qAGR36I14La_WtJ54:APA91bEdgzKA3lHDWm7wGsWggctStiN3vr2ZC5nM9NzQSw5xgivzzSYl6i_VqJV5eXfv6svZfA9Js8rBGMYHpOhEYP5vdo7AC2xs20JAddmcqgDz4Njoeu4p37y8uraKLtjG1MofdUNY",
    "device_key": "AolSPZZss3FFT3xE2oJoJ66+pmOWNZgzL1ae4EDvznYN",
    "sig_ts": 1687414135,
    "sig": "MEUCIQD/wiQOXihHF92/I0W6pFhcbxla15I+mioRxYNUHB3I8wIgQJvzlkNrzLkZu07/euTE1qv00m7lY8DEyHFLp0IrFMQ=",
    "hashes": [
        1135420871, 1754241469, 2776773758, 4255068017, 157546658, 1597970967,
        2862836767, 2538641935, 3062676827, 3714531524, 2766223387, 2624082062,
        793936230, 4289683175, 472200357, 2553099186, 884461435, 1017506911,
        3203138559, 1810499009, 3661381049, 3736026542, 2830814215, 3312396323,
        3071829575, 2398773561, 1507229735,
    ],
}


class License:
    @staticmethod
    def build_live_payload(login_type, player_id, signature):
        payload = copy.deepcopy(LIVE_LOGIN_BASE)
        payload["type"] = login_type
        payload["external_credentials"] = {
            **payload["external_credentials"],
            "external_account_type": login_type,
            "player_id": player_id,
            "signature": signature,
        }
        return payload

    @staticmethod
    def build_beta_payload(login_type, player_id, signature):
        payload = copy.deepcopy(BETA_LOGIN_BASE)
        payload["type"] = login_type
        payload["external_credentials"] = {
            **payload["external_credentials"],
            "external_account_type": login_type,
            "player_id": player_id,
            "signature": signature,
        }
        return payload

    @staticmethod
    async def get_license(login_type):
        """Backward-compatible helper used by sessions module."""
        normalized = login_type.capitalize()
        return License.build_beta_payload(normalized, "", "")
