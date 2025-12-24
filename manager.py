from handlers import schema
from handlers import protocol
from handlers import onql
from handlers import insert
from handlers import delete
from handlers import update
from handlers import exporter
from handlers import importer
from handlers import stats
from handlers import sql

class Manager:
    def __init__(self,onqlclient):
        self.handlers = {
            'schema': schema.Schema(onqlclient),
            'protocol': protocol.Protocol(onqlclient),
            'onql': onql.ONQL(onqlclient),
            'insert': insert.Insert(onqlclient),
            'delete': delete.Delete(onqlclient),
            'update': update.Update(onqlclient),
            'export': exporter.Export(onqlclient),
            'import': importer.Import(onqlclient),
            'stats': stats.Stats(onqlclient),
            'sql': sql.SQL(onqlclient)
        }

    async def handle(self, keyword, data):
        if keyword in self.handlers:
            return await self.handlers[keyword].handle(data)
        else:
            print(f"No handler for keyword: {keyword}")
            # raise ValueError(f"No handler for keyword: {keyword}")
