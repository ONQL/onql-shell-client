import json
import re

class Update:
    def __init__(self, oc):
        self.oc = oc
        self.protopass = "default"

    async def handle(self, command):
        # Clean up command
        command = re.sub(r'\s+', ' ', command).strip()
        try:
            payload = self.setupPayload(command)
        except Exception as e:
            print(f"[Update Error] {e}")
            return
        # Send request with JSON payload
        res = await self.oc.send_request("update", json.dumps(payload))
        print(res)
        self.handleResponse(res)

    def handleResponse(self, res):
        try:
            data = json.loads(res["payload"])
            print(data)
        except Exception:
            print(res["payload"])

    def setupPayload(self, command):
        payload = {}
        try:
            payload = json.loads(command)
        except:
            cmd = command.split(" ")
            db,table = cmd[0].split(".")
            command = command.lstrip(cmd[0])
            cmd = command.split(" on ")
            data = cmd [0]
            query = cmd[1]
            payload = {
                "db":db,
                "table":table,
                "records":data,
                "query":query
            }
        payload["protopass"] = self.protopass
        return payload
