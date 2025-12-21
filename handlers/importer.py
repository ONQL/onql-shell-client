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
        if len(parts) < 2:
            print("Usage: import <filename>")
            return
        
        filename = parts[1]
        
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
        # schema is the payload from "desc" command.
        # Expected structure: {"headers": ["Field", "Type", ...], "data": [[name, type, storage, blank, default], ...]}
        
        if "data" not in schema:
            print(f"    Skipping table {tablename}: Invalid schema definition")
            return

        columns_def = ""
        # iterate over rows in the desc grid
        # The schema grid usually has: Name, Type, Storage, Blank, Default
        # We need to map these back to create table command: (name,type,storage,blank,default)
        
        # We assume the order of columns in "data" matches the create syntax or check headers
        # Headers usually: ["Field", "Type", "Null", "Key", "Default", "Extra"] in SQL, but for ONQL?
        # Let's assume onql desc output maps closely to the create params.
        # Based on schema.py parseCreateTable: name,type,storage,blank,default
        
        # Let's verify headers if available, otherwise assume index 0,1,2,3,4
        
        grid_data = schema["data"]
        # If schema["data"] is a dict with "data", unpack it
        if isinstance(grid_data, dict) and "data" in grid_data:
            grid_data = grid_data["data"]
            
        for col_row in grid_data:
            # col_row is [name, type, storage, blank, default]
            if len(col_row) >= 2:
                name = col_row[0]
                ctype = col_row[1]
                storage = col_row[2] if len(col_row) > 2 else "disk"
                blank = col_row[3] if len(col_row) > 3 else "no"
                default = col_row[4] if len(col_row) > 4 else ""
                
                # Enclose default in quotes if it's empty string or string?
                # The generic create parser splits by comma.
                # If default is empty string, we should explicitly pass something? 
                # parseCreateTable does: default = col_parts[4] if len > 4 else ""
                
                # Check for empty string representation
                if default == "":
                   default = '""'
                
                columns_def += f"({name},{ctype},{storage},{blank},{default})"

        create_cmd = f"create table {dbname} {tablename} {columns_def}"
        # Schema handler `create table` logic expects the full command string to parse it manually?
        # No, schema.py `handle` calls `setupPayload`. `setupPayload` calls `parseCreateTable`.
        # `parseCreateTable` takes the `command` string.
        # So we can't send JSON to `parseCreateTable`. We need to simulate the CLI command or construct the payload manually!
        
        # `parseCreateTable` returns `["create", "table", dbname, tablename, columns_dict]`
        # We can construct this list directly and send it to "schema" endpoint!
        # This bypasses the string parsing and is safer.
        
        columns_dict = {}
        for col_row in grid_data:
            if len(col_row) >= 2:
                 columns_dict[col_row[0]] = {
                     "type": col_row[1],
                     "storage": col_row[2] if len(col_row) > 2 else "disk",
                     "blank": col_row[3] if len(col_row) > 3 else "no",
                     "default": col_row[4] if len(col_row) > 4 else ""
                 }

        payload = ["create", "table", dbname, tablename, columns_dict]
        await self.oc.send_request("schema", json.dumps(payload))

    async def insertData(self, dbname, tablename, schema, rows):
        if not rows:
            return

        # We need column names to construct the insert command
        # insert command: db table (col1,col2) (val1,val2)
        # OR we can send direct JSON payload to insert if we knew the format?
        # insert.py sends raw command to server: `res = await self.oc.send_request("insert", command)`
        # It does NOT use JSON payload.
        # So we must construct the command string.
        
        # Get column names from schema
        col_names = []
        grid_data = schema["data"]
        if isinstance(grid_data, dict) and "data" in grid_data:
            grid_data = grid_data["data"]
            
        for col_row in grid_data:
            col_names.append(col_row[0])
            
        cols_str = ",".join(col_names)
        
        # Batching might be good, but let's do row by row for safety first
        # row is a list of values? Or dict?
        # export.py uses `table_data_payload["data"]["data"]` which is typically list of lists (rows) matching headers.
        
        # Wait, if export.py exports list of lists, we need to map values to columns by index.
        # Assuming Data rows order matches Schema column order.
        
        for row in rows:
            # Row is a list of values.
            # Convert values to string representations
            
            vals = []
            for v in row:
                if isinstance(v, str):
                    vals.append(f"\"{v}\"") # Quote strings
                elif v is None:
                    vals.append("null")
                else:
                    vals.append(str(v))
            
            vals_str = ",".join(vals)
            
            # Construct command
            # db table (cols) (vals)
            cmd = f"{dbname} {tablename} ({cols_str}) ({vals_str})"
            
            # Send insert
            await self.oc.send_request("insert", cmd)
