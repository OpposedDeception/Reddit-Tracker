import argparse
import praw
from rich.console import Console
from rich.panel import Panel
import pyfiglet
import time
import csv

class Csv:
    @staticmethod
    def save_data(filename, header, data):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for row in data:
                writer.writerow(row)


class RedditTracker:
    def __init__(self):
        self.subreddit = None
        self.user = None
        self.upvotes = False
        self.comments = False
        self.reddit = None

    def authenticate(self, client_id, client_secret):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="User tracker for u/ahstagger",
        )

    def run(self, subreddit, user, upvotes, comments):
        console = Console()
        app_name = Panel("Reddit Tracker", style="bold magenta")
        console.print(app_name)
        self.subreddit = subreddit
        self.user = user
        self.upvotes = upvotes
        self.comments = comments
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

        header = ["Display Name", "Karma Score", "Subreddit Name", "Subreddit Subscribers", "Upvote Count", "Comment Count"]
        data = [[display_name, karma_score, subreddit_name, subreddit_subscribers, upvote_count if self.upvotes else "", comment_count if self.comments else ""]]
        Csv.save_data("reddit_data.csv", header, data)


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

    ver = pyfiglet.figlet_format("V.1.1")
    print(ver)
    client_id = input("Enter your Reddit client ID: ")
    client_secret = input("Enter your Reddit client secret: ")

    parser = argparse.ArgumentParser(description="Reddit Tracker")
    parser.add_argument("--reddit", "-r", help="Specify the subreddit name (e.g., learnpython)", required=False)
    parser.add_argument("--user", "-u", help="Specify the Reddit user (e.g., spez)", required=True)
    parser.add_argument("--upvotes", "-up", action="store_true", help="Get the number of upvotes for the user")
    parser.add_argument("--comments", "-c", action="store_true", help="Get the number of comments for the user")
    args = parser.parse_args()

    reddit_tracker = RedditTracker()
    while True:
        try:
            reddit_tracker.authenticate(client_id, client_secret)
            reddit_tracker.run(args.reddit, args.user, args.upvotes, args.comments)
        except Exception as e:
            print(e)
            continue
        time.sleep(10)
