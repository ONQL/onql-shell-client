import utils
import json
import re

class Schema():
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
        # res = await self.oc.send_request("schema", json.dumps(["desc"]))
        res = await self.oc.send_request("schema", json.dumps(payload))
        self.handleResponse(res)

    def handleResponse(self,res):
        try:
            data = json.loads(res["payload"])
            utils.printJson(data)
            # utils.printSchema(data)
        except:
            print(res["payload"])

    def setupPayload(self, command):
        cmd = command.split(" ")
        
        if cmd[0] == "databases":
            return ["databases"]
            
        elif cmd[0] == "tables":
            if len(cmd) < 2:
                raise ValueError("tables command requires database name")
            return ["tables", cmd[1]]
            
        elif cmd[0] == "desc":
            return cmd
        
        elif cmd[0] == "create":
            if cmd[1] == "db":
                if len(cmd) < 3:
                    raise ValueError("create db requires database name")
                return ["create", "db", cmd[2]]
                
            elif cmd[1] == "table":
                # Parse: create table dbname tablename (name,string,disk,no,"")(age,number,ram,yes,18)
                return self.parseCreateTable(command)
                
        elif cmd[0] == "rename":
            if cmd[1] == "db":
                if len(cmd) < 4:
                    raise ValueError("rename db requires old_name new_name")
                return ["rename", "db", cmd[2], cmd[3]]
            elif cmd[1] == "table":
                if len(cmd) < 5:
                    raise ValueError("rename table requires dbname old_name new_name")
                return ["rename", "table", cmd[2], cmd[3], cmd[4]]
                
        elif cmd[0] == "alter":
            if len(cmd) < 4:
                raise ValueError("alter requires dbname tablename operation")
            return ["alter", cmd[1], cmd[2], json.loads(command.lstrip(cmd[0] + " " + cmd[1] + " " + cmd[2]))]
        
        elif cmd[0] == "drop":
            if cmd[1] == "db":
                if len(cmd) < 3:
                    raise ValueError("drop db requires database name")
                return ["drop", "db", cmd[2]]
            elif cmd[1] == "table":
                if len(cmd) < 4:
                    raise ValueError("drop table requires dbname tablename")
                return ["drop", "table", cmd[2], cmd[3]]
        elif cmd[0] == "set":
            return ["set", utils.read_json_file(cmd[1])]
        elif cmd[0] == "refresh-indexes":
            return ["refresh-indexes"]

        else:
            raise ValueError(f"Unknown command: {cmd[0]}")


    def parseCreateTable(self, command):
        # Extract table name and columns from: create table dbname tablename (col1,type1,storage1,blank1,default1)(col2,type2,storage2,blank2,default2)
        parts = command.split("(")
        if len(parts) < 2:
            raise ValueError("create table requires column definitions in parentheses")
            
        # Get dbname and tablename
        header = parts[0].strip().split()
        if len(header) < 4:
            raise ValueError("create table syntax: create table dbname tablename (columns...)")
        dbname = header[2]
        tablename = header[3]
        
        # Parse column definitions
        columns = {}
        for i in range(1, len(parts)):
            col_def = parts[i].split(")")[0]  # Remove closing parenthesis
            if not col_def.strip():
                continue
                
            # Parse column: name,type,storage,blank,default
            col_parts = [p.strip().strip('"').strip("'") for p in col_def.split(",")]
            if len(col_parts) < 2:
                raise ValueError("Column definition requires at least name and type")
                
            col_name = col_parts[0]
            col_type = col_parts[1]
            
            # Set defaults
            storage = col_parts[2] if len(col_parts) > 2 else "disk"
            blank = col_parts[3] if len(col_parts) > 3 else "no"
            default = col_parts[4] if len(col_parts) > 4 else ""
            
            columns[col_name] = {
                "type": col_type,
                "storage": storage,
                "blank": blank,
                "default": default
            }
        
        return ["create", "table", dbname, tablename, columns]

