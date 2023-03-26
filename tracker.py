import argparse
import praw
from rich.console import Console
from rich.panel import Panel
import pyfiglet


class RedditTracker:
    def __init__(self, subreddit, user, upvotes, comments):
        self.subreddit = subreddit
        self.user = user
        self.upvotes = upvotes
        self.comments = comments
        self.reddit = None

    def authenticate(self, client_id, client_secret):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="RedditTracker"
        )

    def run(self):
        console = Console()
        app_name = Panel("Reddit Tracker", style="bold magenta")
        console.print(app_name)
        
        user = self.reddit.redditor(self.user)
        display_name = user.name
        karma_score = user.link_karma + user.comment_karma
        console.print(f"\n[bold]{display_name}[/bold] ({karma_score} karma)")
        
        subreddit = self.reddit.subreddit(self.subreddit)
        subreddit_name = subreddit.display_name
        subreddit_subscribers = subreddit.subscribers
        console.print(f"\n[bold]Subreddit:[/bold] {subreddit_name} ({subreddit_subscribers} subscribers)")

        if self.upvotes:
            upvote_count = user.link_karma
            console.print(f"\n[bold]{display_name}[/bold] has [bold]{upvote_count}[/bold] upvotes.")

        if self.comments:
            comment_count = user.comment_karma
            console.print(f"\n[bold]{display_name}[/bold] has [bold]{comment_count}[/bold] comments.")


if __name__ == '__main__':
    print("\033[1;31m" + r"""
        _____.-~"   "~-.____
     ~~~"   __         __    ~~~
           /'__`\     /'__`\
          | /oo\ \   | /oo\ \
          | \()\/_/   \ \/()/
          \ \ \/      \/ / /
           \/         \/\/
           /            \
          (      /       )
           \____/\/\/\___/
            \ _ /    \ _ /
             ' V        V'
""" + "\033[0m")

    ver = pyfiglet.figlet_format("V1.0")
    print(ver)

    print("""
          Provide these information to continue. To get necessary data
          go to old Reddit and go to your account and click Developers settings.
    """)
    client_id = input("Enter your Reddit client ID: ")
    client_secret = input("Enter your Reddit client secret: ")
    
    parser = argparse.ArgumentParser(description="Reddit Tracker")
    parser.add_argument("--reddit", "-r", help="Specify the subreddit name (e.g., learnpython)", required=True)
    parser.add_argument("--user", "-u", help="Specify the Reddit user (e.g., spez)", required=True)
    parser.add_argument("--upvotes", "-up", action="store_true", help="Get the number of upvotes for the user")
    parser.add_argument("--comments", "-c", action="store_true", help="Get the number of comments for the user")
    args = parser.parse_args()

    reddit_tracker = RedditTracker(args.reddit, args.user, args.upvotes, args.comments)
    reddit_tracker.authenticate(client_id, client_secret)
    reddit_tracker.run()
