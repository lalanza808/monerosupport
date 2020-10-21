# monerosupport

An IRC bot for helping people on /r/monerosupport

```
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp supportbot/config.{example.py,py}

# Run
python3 -m supportbot
```

## TODO

- RSS feed https://www.reddit.com/r/monerosupport/new/.rss (track state in DB from posted feeds)
- ACLs / list of user handles for special privileges within DB (potentially IRC modes, 0-100)
- basic queue functionality, list queue, see status
- rudimentary ticket system to "claim" something in the feed
- basic search for past issues

nice to haves:

- reply to comment from IRC
- custom deltabot
