import pyfiglet
# from prompt_toolkit import prompt
# from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit import PromptSession         # <-- change
# from prompt_toolkit.patch_stdout import patch_stdout
import asyncio                                    # <-- add

class Shell:
    def __init__(self, manager):
        self.manager = manager
        self.activeKeyword = None

    async def execute(self, command):
        # This core logic remains unchanged.
        if not command.strip():
            return
        
        # Check for 'use' or 'exit' commands first.
        if self.setKeyword(command):
            return
            
        keyword, data = self.parse_command(command)
        
        # This part would be replaced with your actual manager logic.
        # For demonstration, we'll just print what would be handled.
        # print(f"MANAGER HANDLING: keyword='{keyword}', data='{data}'")
        await self.manager.handle(keyword,data)
        # return self.manager.handle_command(keyword, data)

    def parse_command(self, command):
        # This core logic remains unchanged.
        if self.activeKeyword:
            return self.activeKeyword, command
        parts = command.split(" ", 1)
        keyword = parts[0]
        data = " ".join(parts[1:]) if len(parts) > 1 else ""
        return keyword, data

    def setKeyword(self, command):
        # This core logic remains unchanged.
        # We parse without using the active keyword to catch 'use' or 'exit'.
        parts = command.split(" ", 1)
        keyword = parts[0]
        data = " ".join(parts[1:]) if len(parts) > 1 else ""

        if keyword.lower() == "use":
            if data:
                self.activeKeyword = data
            return True
        elif keyword.lower() == "out":
            self.activeKeyword = None
            return True
        elif keyword.lower() == "exit":
            exit(0)
        elif keyword.lower() == "clear":
            # clear console
            print("\033[H\033[J", end="")
            intro_text = pyfiglet.figlet_format("ONQL", font="slant")
            print(intro_text)
            print("Welcome to the ONQL Shell. Type your commands below.")
            print("Hint: Use 'Ctrl+N' for a new line, 'Enter' to execute.")

            return True
            # self.activeKeyword = None
            # return True
        return False


    # async def start(self):
    #         intro_text = pyfiglet.figlet_format("ONQL", font="slant")
    #         print(intro_text)
    #         print("Welcome to the ONQL Shell. Type your commands below.")
    #         print("Hint: Use 'Ctrl+N' for a new line, 'Enter' to execute.")

    #         key_bindings = KeyBindings()

    #         @key_bindings.add("enter")
    #         def _(event):
    #             event.current_buffer.validate_and_handle()

    #         @key_bindings.add("c-n")   # or use "c-j" if you prefer
    #         def _(event):
    #             event.current_buffer.insert_text("\n")

    #         session = PromptSession(key_bindings=key_bindings, multiline=True)

    #         # Keep prompt intact if other tasks print
    #         with patch_stdout():
    #             while True:
    #                 try:
    #                     prompt_str = f"{self.activeKeyword}> " if self.activeKeyword else "> "
    #                     command = await session.prompt_async(prompt_str)   # <-- async
    #                     if not command.strip():
    #                         continue

    #                     ret = await self.execute(command)
    #                     # If your manager.handle(...) is async, await it:
    #                     if asyncio.iscoroutine(ret):
    #                         await ret

    #                 except (KeyboardInterrupt, EOFError):
    #                     print("\nExiting ONQL Shell.")
    #                     break



    async def start(self):
            intro_text = pyfiglet.figlet_format("ONQL", font="slant")
            print(intro_text)
            print("Welcome to the ONQL Shell. Type your commands below.")
            print("Hint: Use 'Ctrl+N' for a new line, 'Enter' to execute.")

          
            while True:
                    try:
                        prompt_str = f"{self.activeKeyword}> " if self.activeKeyword else "> "
                        command = input(prompt_str)  # Use input() for simplicity
                        if not command.strip():
                            continue

                        ret = await self.execute(command)
                        # If your manager.handle(...) is async, await it:
                        if asyncio.iscoroutine(ret):
                            await ret

                    except (KeyboardInterrupt, EOFError):
                        print("\nExiting ONQL Shell.")
                        break

                    