import utils
import json
import re

class Protocol():
    def __init__(self,oc):
        self.oc = oc
    
    async def handle(self,command):
        # Clean up command and prepare payload
        command = re.sub(r'\s+', ' ', command).strip()
        try:
            payload = self.setupPayload(command)
        except Exception as e:
            print(e)
            return

        # Send request with JSON payload
        res = await self.oc.send_request("protocol", json.dumps(payload))
        print(res)
        self.handleResponse(res)

    def handleResponse(self,res):
        try:
            data = json.loads(res["payload"])
            # utils.printJson(data)
            utils.printJson(data)
        except:
            print(res["payload"])

    def setupPayload(self, command):
        cmd = command.split(" ")    
        if cmd[0] == "desc":
            return cmd
        elif cmd[0] == "set":
            if len(cmd) < 2:
                raise ValueError("set command requires keyword and value")
            password = input("Enter password: ")
            return ["set", password, utils.read_json_file(cmd[1])]
        
        elif cmd[0] == "drop":
            if len(cmd) != 2:
                raise ValueError("drop command: use 'drop dbname tablename'")
            return ["drop", cmd[1]]