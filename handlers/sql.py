import json
from rich.console import Console
from rich.table import Table
from rich import box

class SQL:
    def __init__(self, oc):
        self.oc = oc
        self.console = Console()

    async def handle(self, command):
        """
        Command format:
        sql <query>
        or if active keyword is sql: <query>
        """
        if not command.strip():
            return

        payload = {"query": command}
        
        try:
            # Send request to sql endpoint
            response_str = await self.oc.send_request("sql", json.dumps(payload))
            response = json.loads(response_str)

            if response.get("error"):
                self.console.print(f"[bold red]Error:[/bold red] {response['error']}")
                return

            data = response.get("data")
            
            if data is None:
                self.console.print("Query executed successfully, no data returned.")
            elif isinstance(data, list):
                if not data:
                    self.console.print("Empty set")
                else:
                    self.print_table(data)
            elif isinstance(data, str):
                self.console.print(data)
            else:
                self.console.print(f"Unknown response format: {data}")

        except Exception as e:
            self.console.print(f"[bold red]Exception:[/bold red] {e}")
            import traceback
            traceback.print_exc()

    def print_table(self, data):
        if not data:
            return

        # Infer columns from the first row, or collect from all if variable
        # But SQL results usually have consistent columns.
        # However, JSON decoding might produce arbitrary dicts if some fields are missing.
        # But from evalSelect implementation, all rows have same keys (projections).
        
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Create a table
        table = Table(box=box.ASCII, show_header=True, header_style="bold cyan")
        
        for col in columns:
            table.add_column(col)

        for row in data:
            row_data = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    row_data.append("NULL")
                else:
                    row_data.append(str(val))
            table.add_row(*row_data)

        self.console.print(table)
