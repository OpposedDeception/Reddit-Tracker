#!/usr/bin/env python3

from rich.console import Console
from rich.panel import Panel
from time import sleep
from argparse import ArgumentParser
from praw import Reddit
from pyfiglet import figlet_format
import csv


class Csv:
    @staticmethod
    def save_data(filename, header, data):
        with open(filename, mode='w', newline='') as file:
            write = csv.writer(file)
            write.writerow(header)
            for row in data:
                write.writerow(row)


class RedditTracker:
    def __init__(self):
        self.subreddit = None
        self.user = None
        self.upvotes = False
        self.comments = False
        self.reddit = None
        self.index = None

    def authenticate(self, client_id, client_secret):
        self.reddit = Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="User tracker for u/Reddit",
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
        
    def get_comments(self, username, limit):
        redditor = self.reddit.redditor(username)
        comments = redditor.comments.new(limit=limit)
        comment_data = []
        for comment in comments:
            comment_data.append({
                'body': comment.body,
                'score': comment.score,
                'created': comment.created_utc,
                'submission_id': comment.submission.id
            })
        c = Console()
        c.print(f"\n[bold]Comment:[/bold] {comment.body} ({comment.score})")
        header = ["Body", "Score", "Created UTC", "Submission ID"]
        data = [[comment['body'], comment['score'], comment['created'], comment['submission_id']] for comment in comment_data]
        Csv.save_data("reddit_comments.csv", header, data)
        
    def get_posts(self, subreddit, limit=1):
            subreddit = self.reddit.subreddit(subreddit)
            latest_post = subreddit.new(limit=1).__next__()
            data = [[latest_post.title, latest_post.shortlink, latest_post.selftext]]
            post_comments = []
            for comment in latest_post.comments:
                if len(post_comments) < 4:
                    post_comments.append(f"{comment.author.name}: {comment.body}")                    
                    c = Console()
                    csv = Csv()
                    header = ["Post Title", "Post URL", "Post Text"]
                    c.print(f"\n[bold]Post:[/bold] {latest_post.title} ({latest_post.selftext})")
                    c.print(f"\n[bold]Post comments:[/bold] {comment.body} ({comment.author.name})")
                    csv.save_data("reddit_post_comments.csv", header, data)                    
                else:
                    break                                      
                    
                    
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

    ver = figlet_format("V.1.3")
    print(ver)
    client_id = input("Enter your Reddit client ID: ")
    client_secret = input("Enter your Reddit client secret: ")

    parser = ArgumentParser(description="Reddit Tracker")
    parser.add_argument("--reddit", "-r", help="Specify the subreddit name (e.g., learnpython)", required=False)
    parser.add_argument("--user", "-u", help="Specify the Reddit user (e.g., spez)", required=True)
    parser.add_argument("--upvotes", "-up", action="store_true", help="Get the number of upvotes for the user")
    parser.add_argument("--comments", "-c", action="store_true", help="Get the number of comments for the user")
    parser.add_argument('--index', "-i", type=int, help='The index of the comment to retrieve. Only for comments now')
    parser.add_argument("--post", "-p", help="Shows last post from the selected subreddit")
    args = parser.parse_args()

    reddit_tracker = RedditTracker()
    while True:
        try:
            reddit_tracker.authenticate(client_id, client_secret)
            reddit_tracker.run(args.reddit, args.user, args.upvotes, args.comments)
            if args.index:
                reddit_tracker.get_comments(args.user, args.index)
                if args.post:
                   reddit_tracker.get_posts(args.post)
                else:
                    pass
            else:
                 pass
        except Exception as e:
            print("An error has occured! Please double check your Client ID/Client Secret. Make sure you typed correct username/subreddit without u/ or r/" + e)        
            break            
            sleep(10)
            exit()
        sleep(30)
