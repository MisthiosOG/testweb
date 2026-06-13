import os

BYPASS_FILE = os.path.join(os.path.dirname(__file__), '..', 'bypass.txt')


class Auth:
    @staticmethod
    def _path():
        return os.path.abspath(BYPASS_FILE)

    @staticmethod
    async def fetch_bypass_ids():
        path = Auth._path()
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            ids = []
            for line in f.read().splitlines():
                line = line.strip()
                if line.isdigit():
                    ids.append(int(line))
            return ids

    @staticmethod
    async def is_allowed(telegram_id):
        bypass = await Auth.fetch_bypass_ids()
        return int(telegram_id) in bypass

    @staticmethod
    async def add_to_bypass(telegram_id):
        try:
            ids = await Auth.fetch_bypass_ids()
            if int(telegram_id) not in ids:
                ids.append(int(telegram_id))
                with open(Auth._path(), 'w') as f:
                    f.write("\n".join(map(str, ids)))
            return True
        except Exception as e:
            print(f"[Auth] Failed to write bypass.txt: {e}")
            return False
