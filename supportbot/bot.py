import sys, os
import pydle
import asyncio
import arrow
from supportbot.reddit import Reddit
from supportbot.db import SupportRequest, IRCSupportOperator
from supportbot import config


class IRCBot(pydle.Client):

    async def on_connect(self):
        for room in config.ROOMS:
            await self.join(room)
            while True:
                print("Checking reddit for new posts")
                r = Reddit()
                new_requests = []
                subreddit = r.reddit.subreddit(r.subreddit)
                for submission in subreddit.new():
                    if not SupportRequest.select().where(SupportRequest.post_id == submission.id):
                        s = SupportRequest(
                            post_id=submission.id,
                            author=submission.author,
                            title=submission.title,
                            permalink=submission.permalink,
                            timestamp=submission.created_utc
                        )
                        s.save()
                        print(f"Added Reddit post {submission.id} as record #{s.id}")
                        new_requests.append(s)
                if new_requests:
                    await self.message(room, f"Found {len(new_requests)} new Reddit posts in /r/monerosupport. Use `!l` or `!list` to see them.")
                await asyncio.sleep(30)

                #     solved = BooleanField(default=False)
                #     assigned = BooleanField(default=False)
                #     assignee = ForeignKey(IRCSupportOperator, backref='assignee')
                #
                # class IRCSupportOperator(BaseModel):
                #     irc_nick = CharField()
                #     is_a_regular = BooleanField()
                #     is_support_admin = BooleanField()

    async def on_message(self, target, source, message):
        if source == self.nickname:
            return
        else:
            print(f"Target: {target} - Source: {source} - Message: {message}")

        if self.nickname in message:
            await self.message(target, f"Sup. I'm not very helpful yet, but getting there.")

        if message in ["!list"]:
            s = []
            reqs = SupportRequest.select().where(
                SupportRequest.solved==False
            ).order_by(SupportRequest.timestamp.desc())
            for req in reqs:
                s.append(f"{req.id} - {req.author} - {arrow.get(req.timestamp).humanize()}")
            await self.message(target, ", ".join(s[0:9]))

        if message.startswith("!request ") or message in ["!request"]:
            msg = message.split()
            if not len(msg) > 1:
                await self.message(target, "Invalid arguments")
                return

            try:
                post_id = int(msg[1])
            except:
                await self.message(target, "Invalid arguments")
                return

            req = SupportRequest.select().where(
                SupportRequest.id==post_id
            ).first()
            if req:
                if req.assigned:
                    _a = "ASSIGNED"
                else:
                    _a = "UNASSIGNED"
                await self.message(target, f"{req.id} - {req.title} - https://reddit.com/{req.permalink} - {_a}")
            else:
                await self.message(target, "No record with that ID")

        if message in ["!help"]:
            await self.message(target, "not ready")

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
