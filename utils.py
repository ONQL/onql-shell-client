from rich.console import Console
from rich.table import Table
import json

console = Console(force_terminal=True, soft_wrap=True)

def printTable(name, data):
    table = Table(title=name)

    # Add columns based on the keys of the first data item
    for key in data[0].keys():
        table.add_column(key)

    # Add rows for each item in the data
    for item in data:
        table.add_row(*[str(value) for value in item.values()])

    console.print(table)


def printJson(data):
    console.print_json(data=data, indent=2, highlight=True, ensure_ascii=False)

def printSchema(data):
    """Print nested schema data in MySQL-style table format"""
    if not isinstance(data, dict):
        console.print("[red]Error: Schema data must be a dictionary[/red]")
        return
    
    for db_name, db_data in data.items():
        # Print database header
        console.print(f"\n[bold cyan]Database: {db_name}[/bold cyan]")
        
        if not isinstance(db_data, dict):
            console.print("[yellow]No tables found[/yellow]")
            continue
            
        for table_name, table_data in db_data.items():
            # Print table header
            console.print(f"\n[bold green]Table: {table_name}[/bold green]")
            
            if not isinstance(table_data, dict):
                console.print("[yellow]No columns found[/yellow]")
                continue
            
            # Create table with MySQL-style formatting
            table = Table(
                title=f"{db_name}.{table_name}",
                show_header=True,
                header_style="bold magenta",
                border_style="blue",
                title_style="bold white"
            )
            
            # Add columns
            table.add_column("Column", style="cyan", width=15)
            table.add_column("Type", style="green", width=10)
            table.add_column("Storage", style="yellow", width=8)
            table.add_column("Blank", style="red", width=6)
            table.add_column("Default", style="white", width=15)
            
            # Add rows for each column
            for col_name, col_info in table_data.items():
                if isinstance(col_info, dict):
                    col_type = col_info.get("type", "")
                    storage = col_info.get("storage", "")
                    blank = col_info.get("blank", "")
                    default = col_info.get("default", "")
                    
                    # Color code blank values
                    blank_colored = "[green]YES[/green]" if blank == "yes" else "[red]NO[/red]"
                    
                    table.add_row(
                        col_name,
                        col_type,
                        storage,
                        blank_colored,
                        f'"{default}"' if default else "[dim]NULL[/dim]"
                    )
            
            console.print(table)

# printJson([{'key': 'value'}])


def read_json_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data