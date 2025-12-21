import json
import utils

class Stats:
    def __init__(self, oc):
        self.oc = oc

    async def handle(self, command):
        """
        Command format:
        stats
        """
        try:
            res = await self.oc.send_request("stats", json.dumps([]))
            data = json.loads(res["payload"])
            utils.printJson(data)
        except Exception as e:
            print(f"Stats failed: {e}")
