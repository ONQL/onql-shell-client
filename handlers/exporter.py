import json
import re

class Export:
    def __init__(self, oc):
        self.oc = oc

    async def handle(self, command):
        """
        Command format received (args only):
        all [filename]
        db <dbname> [filename]
        table <dbname> <tablename> [filename]
        """
        parts = command.split()
        if len(parts) < 1:
            print("Usage: export [all|db|table] ...")
            return

        target = parts[0]
        filename = "backup.json"  # Default filename

        result_data = []

        try:
            if target == "all":
                if len(parts) > 1:
                    filename = parts[1]
                result_data = await self.exportAll()
            
            elif target == "db":
                if len(parts) < 2:
                    print("Usage: export db <dbname> [filename]")
                    return
                dbname = parts[1]
                if len(parts) > 2:
                    filename = parts[2]
                result_data = await self.exportDb(dbname)
            
            elif target == "table":
                if len(parts) < 3:
                    print("Usage: export table <dbname> <tablename> [filename]")
                    return
                dbname = parts[1]
                tablename = parts[2]
                if len(parts) > 3:
                    filename = parts[3]
                result_data = await self.exportTable(dbname, tablename)
            
            else:
                print(f"Unknown export target: {target}")
                return

            if result_data:
                # Ensure the filename ends with .json
                if not filename.endswith('.json'):
                    filename += '.json'
                
                with open(filename, 'w') as f:
                    json.dump(result_data, f, indent=2)
                print(f"Export completed successfully to {filename}")
            else:
                print("Nothing to export or empty result.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Export failed: {e}")

    async def exportAll(self):
        dbs_res = await self.oc.send_request("schema", json.dumps(["databases"]))
        dbs_payload = json.loads(dbs_res["payload"])
        
        databases = []
        if isinstance(dbs_payload, dict) and "data" in dbs_payload:
             for row in dbs_payload["data"]:
                 databases.append(row[0]) 
        elif isinstance(dbs_payload, list):
             databases = dbs_payload 
        
        full_export = []
        for db in databases:
            if db == "system": continue # Skip system db if needed
            db_export = await self.fetchDatabaseExport(db)
            full_export.append(db_export)
            
        protocols_export = await self.fetchProtocolsExport()
        full_export.append({"protocols": protocols_export})
            
        return full_export

    async def fetchProtocolsExport(self):
        try:
            res = await self.oc.send_request("protocol", json.dumps(["desc"]))
            data = json.loads(res["payload"])
            
            # User specified: "you will get all with first key is its password"
            # Assuming data is a Dict {password: definition}
            protocols = []
            if isinstance(data, dict):
                for password, definition in data.items():
                   protocols.append({
                       "password": password,
                       "definition": definition
                   })
            return protocols
        except Exception as e:
            print(f"Error exporting protocols: {e}")
            return []

    async def exportDb(self, dbname):
        db_export = await self.fetchDatabaseExport(dbname)
        return [db_export]

    async def exportTable(self, dbname, tablename):
        table_schema_res = await self.oc.send_request("schema", json.dumps(["desc", dbname, tablename]))
        table_schema = json.loads(table_schema_res["payload"])
        
        table_data_res = await self.oc.send_request("onql", json.dumps({
            "query": f"{dbname}.{tablename}",
            "protopass": "default",
            "ctxkey": "",
            "ctxvalues": []
        }))
        
        table_data_payload = json.loads(table_data_res["payload"])
        rows = []
        if isinstance(table_data_payload, list):
             rows = table_data_payload
        elif isinstance(table_data_payload, dict):
             if "data" in table_data_payload and table_data_payload["data"]:
                  # Check if it's double nested (grid) or single nested (list of dicts)
                  sub_data = table_data_payload["data"]
                  if isinstance(sub_data, dict) and "data" in sub_data:
                       rows = sub_data["data"]
                  else:
                       rows = sub_data
        
        return [{
            "database": dbname,
            "tables": [{
                "name": tablename,
                "schema": table_schema,
                "data": rows
            }]
        }]

    async def fetchDatabaseExport(self, dbname):
        # Get Tables
        tables_res = await self.oc.send_request("schema", json.dumps(["tables", dbname]))
        tables_payload = json.loads(tables_res["payload"])
        
        table_names = []
        if isinstance(tables_payload, dict) and "data" in tables_payload:
            for row in tables_payload["data"]:
                table_names.append(row[0])
        elif isinstance(tables_payload, list):
            table_names = tables_payload

        tables_export = []
        for tbl in table_names:
            # DESC table
            desc_res = await self.oc.send_request("schema", json.dumps(["desc", dbname, tbl]))
            desc_payload = json.loads(desc_res["payload"])
            
            # GET Data
            data_res = await self.oc.send_request("onql", json.dumps({
                "query": f"{dbname}.{tbl}",
                "protopass": "default",
                "ctxkey": "",
                "ctxvalues": []
            }))
            data_payload = json.loads(data_res["payload"])
            
            rows = []
            if isinstance(data_payload, list):
                 rows = data_payload
            elif isinstance(data_payload, dict):
                 if 'error' in data_payload and data_payload['error']:
                     print(f"Error fetching data for {dbname}.{tbl}: {data_payload['error']}")
                 elif "data" in data_payload and data_payload["data"] is not None:
                      # Check if it's double nested (grid) or single nested (list of dicts)
                      sub_data = data_payload["data"]
                      if isinstance(sub_data, dict) and "data" in sub_data:
                           rows = sub_data["data"]
                      else:
                           rows = sub_data
            
            tables_export.append({
                "name": tbl,
                "schema": desc_payload,
                "data": rows
            })
            
        return {
            "database": dbname,
            "tables": tables_export
        }
