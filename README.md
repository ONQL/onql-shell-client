# ONQL Shell Client

This repository contains the source code for the ONQL (Object-Notation-Query-Language) terminal client. This client allows you to connect to an ONQL server and execute commands.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.7+
*   An ONQL server instance running.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ONQL/onql-shell-client.git
    cd onqlclient
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Client

To start the client, run the following command:

```bash
python main.py
```

The client will prompt you to enter the host and port of the ONQL server. The default host is `localhost` and the default port is `5656`.

## Usage

The ONQL shell provides a command-line interface to interact with the ONQL server.

### General Commands

*   `use <keyword>`: Sets the active keyword for the session. This allows you to avoid typing the keyword for every command. For example, after running `use onql`, you can directly type your ONQL queries.
*   `out`: Clears the active keyword.
*   `clear`: Clears the console.
*   `exit`: Exits the ONQL shell.

### Data Manipulation Commands

*   **`onql <query>`**: Executes an ONQL query.
    *   Local commands:
        *   `password`: Prompts for the protocol password.
        *   `context`: Prompts for the context key and values.
*   **`insert <json>`**: Inserts data into a table.
*   **`update <json>`**: Updates data in a table.
*   **`delete <json>`**: Deletes data from a table.

### Schema Management Commands

*   `schema databases`: Lists all databases.
*   `schema tables <db_name>`: Lists all tables in a database.
*   `schema desc <db_name> <table_name>`: Describes the schema of a table.
*   `schema create db <db_name>`: Creates a new database.
*   `schema create table <db_name> <table_name> (columns...)`: Creates a new table.
*   `schema rename db <old_name> <new_name>`: Renames a database.
*   `schema rename table <db_name> <old_name> <new_name>`: Renames a table.
*   `schema alter <db_name> <table_name> <operation>`: Alters a table.
*   `schema drop db <db_name>`: Drops a database.
*   `schema drop table <db_name> <table_name>`: Drops a table.
*   `schema set <json_file_path>`: Sets the schema from a JSON file (for migrations).
*   `schema refresh-indexes`: Refreshes the indexes.

### Protocol Management Commands

*   `protocol desc`: Describes the protocol.
*   `protocol set <json_file_path>`: Sets the protocol from a JSON file.
*   `protocol drop <db_name> <table_name>`: Drops a protocol.

## Project Structure

```
.
├── handlers/
│   ├── __init__.py
│   ├── delete.py
│   ├── insert.py
│   ├── onql.py
│   ├── protocol.py
│   ├── schema.py
│   └── update.py
├── .gitignore
├── main.py
├── manager.py
├── README.md
├── requirements.txt
├── shell.py
└── utils.py
```

*   **`main.py`**: The entry point of the application.
*   **`manager.py`**: The command manager, which routes commands to the appropriate handlers.
*   **`shell.py`**: The command-line shell interface.
*   **`utils.py`**: Utility functions for printing formatted output.
*   **`handlers/`**: Contains the logic for each command.

## How to Contribute

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a pull request.

