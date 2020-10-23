import praw
from supportbot import config


class Reddit(object):
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.PRAW_CLIENT_ID,
            client_secret=config.PRAW_CLIENT_SECRET,
            user_agent=config.PRAW_USER_AGENT,
            username=config.PRAW_USERNAME,
            password=config.PRAW_PASSWORD
        )
        self.subreddit = "monerosupport"

    def post(self, title, url):
        try:
            submission = self.reddit.subreddit(self.subreddit).submit(
                title=title,
                url=url,
                resubmit=False,
            )
            return submission
        except:
            return False

    def comment(self, submission, comment):
        try:
            _comment = submission.reply(comment)
            return _comment
        except:
            return False

if __name__ == '__main__':
    r = Reddit()
    subreddit = r.reddit.subreddit(r.subreddit)
    for submission in subreddit.new():
        print(submission)
        print("author", submission.author)
        print("id", submission.id)
        print("name", submission.name)
        print("permalink", submission.permalink)
        print("title", submission.title)
        print("\n")
