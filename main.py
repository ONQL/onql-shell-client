import onqlclient
import manager
import shell
import asyncio


async def main():
    try:
        host = input("Enter host (default localhost) :- ") or "localhost"
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        return

    while True:
        try:
            port_input = input("Enter port (default 5656) :- ")
            port = int(port_input) if port_input else 5656
            break
        except ValueError:
            print("Invalid port. Please enter a valid port number.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return

    try:
        oc = await onqlclient.ONQLClient.create(host=host, port=port)
    except Exception as e:
        print(f"\n[!] Connection Error")
        print(f"--------------------------------------------------")
        print(f"Could not connect to ONQL server at {host}:{port}")
        print(f"Reason: {e}")
        print(f"--------------------------------------------------\n")
        return

    m = manager.Manager(oc)

    sh = shell.Shell(m)
    await sh.start()


asyncio.run(main())
# main()

# ipconfig /flushdns
# netsh winsock reset
# netsh int ip reset
