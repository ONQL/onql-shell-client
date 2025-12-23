import json
import os
import re

class Import:
    def __init__(self, oc):
        self.oc = oc

    async def handle(self, command):
        """
        Command format:
        import <filename>
        """
        parts = command.split()
        if len(parts) < 1:
            print("Usage: import <filename>")
            return
        
        filename = parts[0]
        
        if not os.path.exists(filename):
            # Try adding .json
            if os.path.exists(filename + ".json"):
                filename += ".json"
            else:
                print(f"File not found: {filename}")
                return

        try:
            print(f"Reading backup from {filename}...")
            with open(filename, 'r') as f:
                data = json.load(f)
            
            await self.processImport(data)
            print("Import completed successfully.")
        except Exception as e:
            print(f"Import failed: {e}")
            import traceback
            traceback.print_exc()

    async def processImport(self, data):
        for item in data:
            if "protocols" in item:
                print("Restoring protocols...")
                await self.importProtocols(item["protocols"])
                continue

            if "database" in item:
                dbname = item["database"]
                # Create Database
                # We blindly try to create it. If it exists, server might complain or ignore.
                # Schema handler expects: create db <name> -> ["create", "db", name]
                print(f"Restoring database: {dbname}")
                await self.oc.send_request("schema", json.dumps(["create", "db", dbname]))
                
                if "tables" in item:
                    for table_obj in item["tables"]:
                        tablename = table_obj["name"]
                        schema = table_obj["schema"]
                        rows = table_obj["data"]
                        
                        print(f"  Restoring table: {tablename}")
                        await self.createTable(dbname, tablename, schema)
                        await self.insertData(dbname, tablename, schema, rows)

    async def importProtocols(self, protocols):
        for p in protocols:
            password = p["password"]
            definition = p["definition"]
             # Send request to protocol endpoint
             # payload: ["set", password, definition]
            try:
                await self.oc.send_request("protocol", json.dumps(["set", password, definition]))
                print(f"  Restored protocol with password: {password}")
            except Exception as e:
                print(f"  Failed to restore protocol {password}: {e}")

    async def createTable(self, dbname, tablename, schema):
        # schema corresponds to the JSON object in backup.json (which is the output of 'desc table')
        # Structure: {"Columns": { "colname": {"Name":..., "Type":..., ...}, ... }}

        if "Columns" not in schema:
            print(f"    Skipping table {tablename}: Invalid schema definition (missing 'Columns')")
            return

        columns_dict = {}
        for col_name, col_def in schema["Columns"].items():
             # Map keys to what schema handler expects in "create table" payload
             # schema.py parseCreateTable expects: type, storage, blank, default, index?
             # Actually, schema.py `handle` -> `setupPayload` -> `parseCreateTable` 
             # -> returns params.
             # BUT here we are sending ["create", "table", dbname, tablename, columns_dict] DIRECTLY.
             # So we need to match the structure that `schema.py` USES when it receives this payload.
             # Looking at schema.py `processCreate`, it iterates over `columns` dict.
             # It expects keys: type, storage, blank, default, validator, formatter, index.
             
             columns_dict[col_name] = {
                 "type": col_def.get("Type", "string"),
                 "storage": col_def.get("Storage", "disk"), # Default to disk? backup doesn't show storage
                 "blank": "yes" if col_def.get("Validator") != "required" else "no", # Infer blank from validator?
                 "default": col_def.get("DefaultValue", ""),
                 "validator": col_def.get("Validator", ""),
                 "formatter": col_def.get("Formatter", ""),
                 "index": col_def.get("Indexed", False)
             }

        payload = ["create", "table", dbname, tablename, columns_dict]
        await self.oc.send_request("schema", json.dumps(payload))

    async def insertData(self, dbname, tablename, schema, rows):
        if not rows:
            return

        # Get column names from schema
        if "Columns" in schema:
             col_names = list(schema["Columns"].keys())
        else:
             print(f"Skipping insert for {tablename}: Missing Columns definition")
             return
        
        # Insert row by row using JSON format
        for row in rows:
            # Row can be a list of values or a dict
            records = {}
            if isinstance(row, dict):
                 records = row
            else:
                # Map list values to column names
                for col, val in zip(col_names, row):
                    records[col] = val
            
            # Create insert payload: {"db":"dbname","table":"tablename","records":{...}}
            payload = {
                "db": dbname,
                "table": tablename,
                "records": records
            }
            
            # Send insert request with JSON payload
            await self.oc.send_request("insert", json.dumps(payload))
