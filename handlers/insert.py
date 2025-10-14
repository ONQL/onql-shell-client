import json
import re

class Insert:
    def __init__(self, oc):
        self.oc = oc

    async def handle(self, command):
        # Clean up command
        command = re.sub(r'\s+', ' ', command).strip()
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
