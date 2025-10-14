import utils
import json
import re

class ONQL():
    def __init__(self,oc):
        self.oc = oc
        self.password = "default"
        self.contextKey = ""
        self.values = ""
    
    async def handle(self,command):
        if self.runLocalCommands(command):
            return
        # Send request with JSON payload
        payload = {
            "query":command,
            "protopass":self.password,
            "ctxkey":self.contextKey,
            "ctxvalues":self.values
        }
        res = await self.oc.send_request("onql", json.dumps(payload))
        # print(res)
        try:
            res = json.loads(res["payload"])
            if res['error']:
                print(res["error"])
            else:
                utils.printJson(json.loads(res["data"]))
        except:
            print(res["payload"])
        # self.handleResponse(res)

    def runLocalCommands(self,command):
        if command == "password":
            self.password = input("enter protocol password :- ")
            return True
        
        if command == "context":
            self.contextKey = input("enter context key :- ")
            self.values = input("enter context values ',' saparated :- ")
            return True
        
        return False