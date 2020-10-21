import sys, os
import pydle
from supportbot import config
from supportbot import db


class IRCBot(pydle.Client):
    async def on_connect(self):
        for room in config.ROOMS:
            await self.join(room)

    async def on_message(self, target, source, message):
        if source == self.nickname:
            return
        else:
            print(f"Target: {target} - Source: {source} - Message: {message}")

        if self.nickname in message:
            await self.message(target, f"Sup. I'm not very helpful yet, but getting there."

    async def is_admin(self, nickname):
        admin = False
        if nickname in config.ADMIN_NICKNAMES:
            info = await self.whois(nickname)
            admin = info['identified']
            print("info: ", info)
        return admin



def run_bot():
    try:
        print(f"[+] Starting IRC bot connecting to {config.IRC_HOST}...\n")
        client = IRCBot(nickname=config.BOT_NICKNAME)
        client.run(config.IRC_HOST, tls=True, tls_verify=False)
    except KeyboardInterrupt:
        print(' - Adios')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
