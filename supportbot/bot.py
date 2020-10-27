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

                # Check for new submissions
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
                        print(f"Added Reddit post {submission.id} as record {s.id}")
                        new_requests.append(s)

                # Only post the totals into IRC
                if new_requests:
                    await self.message(room, f"Found {len(new_requests)} new Reddit posts in /r/monerosupport. Use `.list` to see the list and `.request x` to see each one.")

                # Check stored posts to see if they're solved
                posts = SupportRequest.select().where(SupportRequest.solved==False)
                for post in posts:
                    p = r.reddit.submission(post.post_id)
                    if p.link_flair_text:
                        print(f"Marking post {post.id} ({post.post_id}) as solved")
                        post.solved = True
                        post.save()
                    await asyncio.sleep(3)

                await asyncio.sleep(30)

    async def on_message(self, target, source, message):
        if source == self.nickname:
            return
        else:
            print(f"Target: {target} - Source: {source} - Message: {message}")

        if self.nickname in message:
            await self.message(target, f"Sup. I'm not very helpful yet, but getting there.")

        # list command to show series of unsolved/active support requests
        if message in [".list"]:
            s = []
            reqs = SupportRequest.select().where(
                SupportRequest.solved==False
            ).order_by(SupportRequest.timestamp)
            for req in reqs:
                s.append(f"{req.id}")
            await self.message(target, ", ".join(s))

        # request command to view meta about a specific support request
        if message.startswith(".request ") or message in [".request"]:
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
                    _a = f"ASSIGNED ({req.assignee.irc_nick})"
                else:
                    _a = "UNASSIGNED"
                if req.solved:
                    _s = "SOLVED"
                else:
                    _s = "UNSOLVED"
                await self.message(target, f"{req.id}: {req.title} - {arrow.get(req.timestamp).humanize()} - https://reddit.com{req.permalink} - {_a} - {_s}")
            else:
                await self.message(target, "No record with that ID")

        # claim support ticket - you become the assignee/helpers
        if message.startswith(".claim ") or message in [".claim"]:
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
                if not await self.is_registered(source):
                    i = IRCSupportOperator(irc_nick=source)
                    i.save()
                else:
                    i = IRCSupportOperator.select().where(IRCSupportOperator.irc_nick==source)
                req.assigned = True
                req.assignee = i
                req.save()
                await self.message(target, f"Support request {req.id} claimed by {source}")
            else:
                await self.message(target, "No record with that ID")

        # queue command only shows things assigned to you
        if message in [".queue"]:
            req = SupportRequest.select().where(
                IRCSupportOperator.irc_nick==source,
                IRCSupportOperator.solved==False
            ).first()
            if req:
                reqs = []
                for i in req:
                    reqs.append(i)
                await self.message(target, ", ".join(reqs))
            else:
                await self.message(target, "No support requests assigned to you")

        # help command shows available commands
        if message in [".help"]:
            await self.message(target, "`.list`: Show open support tickets on Reddit and synchronized to the database. | `.request x`: Show metadata of support request \"x\". | `.claim x`: Claim support request \"x\" | `.queue`: Show support requests assigned to you")

    async def is_admin(self, nickname):
        admin = False
        if nickname in config.ADMIN_NICKNAMES:
            info = await self.whois(nickname)
            admin = info['identified']
            print("info: ", info)
        return admin

    async def is_registered(self, nickname):
        irc_nick = IRCSupportOperator.select().where(
            IRCSupportOperator.irc_nick==nickname
        ).first()
        if irc_nick:
            return True
        else:
            return False

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
