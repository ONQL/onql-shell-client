from handlers import schema
from handlers import protocol
from handlers import onql
from handlers import insert
from handlers import delete
from handlers import update

class Manager:
    def __init__(self,onqlclient):
        self.handlers = {
            'schema': schema.Schema(onqlclient),
            'protocol': protocol.Protocol(onqlclient),
            'onql': onql.ONQL(onqlclient),
            'insert': insert.Insert(onqlclient),
            'delete': delete.Delete(onqlclient),
            'update': update.Update(onqlclient)
            # Add more keyword: handler mappings here
        }

    async def handle(self, keyword, data):
        if keyword in self.handlers:
            return await self.handlers[keyword].handle(data)
        else:
            print(f"No handler for keyword: {keyword}")
            # raise ValueError(f"No handler for keyword: {keyword}")

    # def handle_command(self, keyword, command):
    #     if keyword in self.handlers:
    #         return self.handlers[keyword].run_command(command)
    #     else:
    #         raise ValueError(f"No handler for keyword: {keyword}")
