import json
import re

class Insert:
    def __init__(self, oc):
        self.oc = oc

    async def handle(self, command):
        # Clean up command
        command = re.sub(r'\s+', ' ', command).strip()

        # Sub-command: file <filepath> [db <dbname>] table <tablename>
        if command.lower().startswith("file "):
            await self.handleFile(command[5:].strip())
            return

        try:
            # payload = self.setupPayload(command)
            pass
        except Exception as e:
            print(f"[Insert Error] {e}")
            return
        # Send request with JSON payload
        # res = await self.oc.send_request("insert", json.dumps(payload))
        res = await self.oc.send_request("insert", command)
        print(res)
        self.handleResponse(res)

    async def handleFile(self, args):
        """
        Syntax: insert file <filepath> <dbname> <tablename>
        Example: insert file data/forex_assets.json mydb instruments
        """
        import os
        tokens = args.split()
        if len(tokens) < 3:
            print("Usage: insert file <filepath> <dbname> <tablename>")
            return

        filepath  = tokens[0]
        dbname    = tokens[1]
        tablename = tokens[2]

        # Resolve file path
        if not os.path.exists(filepath):
            if os.path.exists(filepath + ".json"):
                filepath += ".json"
            else:
                print(f"File not found: {filepath}")
                return

        # Load JSON
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read file: {e}")
            return

        if not isinstance(data, list):
            print("Error: JSON file must contain a top-level array of objects.")
            return

        total = len(data)
        print(f"Inserting {total} records into '{dbname}.{tablename}'...")
        success = 0
        failed  = 0

        for i, row in enumerate(data):
            if not isinstance(row, dict):
                print(f"  [{i+1}/{total}] Skipping: not an object.")
                failed += 1
                continue

            payload = {"db": dbname, "table": tablename, "records": row}
            try:
                res = await self.oc.send_request("insert", json.dumps(payload))

                # Check server-side error in response payload
                try:
                    res_data = json.loads(res.get("payload", "{}"))
                    err = res_data.get("error", "")
                except Exception:
                    err = ""

                if err:
                    print(f"  [{i+1}/{total}] Error ({row.get('name', i)}): {err}")
                    failed += 1
                else:
                    success += 1
                    print(f"  [{i+1}/{total}] OK: {row.get('name', i)}")

            except (TimeoutError, ConnectionError) as e:
                print(f"  [{i+1}/{total}] Connection error: {e}")
                failed += 1
            except Exception as e:
                # Catch CancelledError and anything else without crashing the shell
                print(f"  [{i+1}/{total}] Failed: {type(e).__name__}: {e}")
                failed += 1

        print(f"\nDone. {success} inserted, {failed} failed.")

    def handleResponse(self, res):
        try:
            data = json.loads(res["payload"])
            print(data)
        except Exception:
            print(res["payload"])

    def setupPayload(self, command):
        # Expected: db table (columns) (values)
        # Example: mydb users (name,age) ("John",25)
        parts = re.split(r'\s+', command, maxsplit=2)
        if len(parts) < 3:
            raise ValueError("Command must start with: db table (columns) (values)")
        db = parts[0]
        table = parts[1]
        rest = parts[2]
        groups = re.findall(r'\((.*?)\)', rest)
        if len(groups) != 2:
            raise ValueError("Command must have two groups: (columns)(values)")
        columns = [col.strip() for col in groups[0].split(',')]
        values = [val.strip() for val in groups[1].split(',')]
        if len(columns) != len(values):
            raise ValueError("Number of columns and values must match")
        records = {}
        for col, val in zip(columns, values):
            # Try to parse value as JSON, fallback to string
            try:
                parsed_val = json.loads(val)
            except Exception:
                parsed_val = val.strip('"').strip("'")
            records[col] = parsed_val
        return {"db": db, "table": table, "records": records}
