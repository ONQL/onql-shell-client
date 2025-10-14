import json
import re

class Delete:
    def __init__(self, oc):
        self.oc = oc
        self.protopass = "default"

    async def handle(self, command):
        # Clean up command
        command = re.sub(r'\s+', ' ', command).strip()
        try:
            payload = self.setupPayload(command)
        except Exception as e:
            print(f"[Delete Error] {e}")
            return
        # Send request with JSON payload
        res = await self.oc.send_request("delete", json.dumps(payload))
        print(res)
        self.handleResponse(res)

    def handleResponse(self, res):
        try:
            data = json.loads(res["payload"])
            print(data)
        except Exception:
            print(res["payload"])

    def setupPayload(self, command):
        payload = json.loads(command)
        payload["protopass"] = self.protopass
        return payload


