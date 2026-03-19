import json
import re
import utils

class Stats:
    def __init__(self, oc):
        self.oc = oc

    async def handle(self, command):
        """
        Command format:
        stats                    - show system stats (connections, memory, goroutines)
        stats queries [limit]    - show recent query history (default limit: 100)
        stats summary            - show aggregated query statistics
        stats clear              - clear query history
        """
        command = re.sub(r'\s+', ' ', command).strip()
        try:
            payload = self.setupPayload(command)
        except Exception as e:
            print(f"Stats failed: {e}")
            return

        try:
            res = await self.oc.send_request("stats", json.dumps(payload))
            data = json.loads(res["payload"])
            utils.printJson(data)
        except Exception as e:
            print(f"Stats failed: {e}")

    def setupPayload(self, command):
        if not command:
            return {}

        parts = command.split(" ")
        action = parts[0]

        if action == "queries":
            payload = {"action": "queries"}
            if len(parts) > 1:
                payload["limit"] = int(parts[1])
            return payload

        elif action == "summary":
            return {"action": "queries_summary"}

        elif action == "clear":
            return {"action": "clear_queries"}

        else:
            raise ValueError(f"Unknown stats action: {action}\nUsage: stats [queries [limit] | summary | clear]")
