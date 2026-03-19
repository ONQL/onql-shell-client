import onqlclient
import manager
import shell
import asyncio

async def main():
    # oc = await onqlclient.ONQLClient.create(host="localhost", port=5656)
    # oc = await onqlclient.ONQLClient.create(host="192.46.213.87", port=int(input("Enter port :- ")))
    oc = await onqlclient.ONQLClient.create(host=input("Enter host :- ") or "localhost", port=int(input("Enter port :- ") or 5656), data_limit=16 * 1024 * 1024 * 1024,  default_timeout=300)

    m = manager.Manager(oc)

    sh = shell.Shell(m)
    await sh.start()

asyncio.run(main())
# main()

# ipconfig /flushdns
# netsh winsock reset
# netsh int ip reset
