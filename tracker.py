import requests
from bs4 import BeautifulSoup
import argparse
from rich.console import Console
from rich.panel import Panel
import pyfiglet


class RedditTracker:
    def __init__(self, subreddit, user, upvotes, comments):
        self.subreddit = subreddit
        self.user = user
        self.upvotes = upvotes
        self.comments = comments

    def run(self):
        console = Console()
        app_name = Panel("Reddit Tracker", style="bold magenta")
        console.print(app_name)
        url = f"https://www.reddit.com/user/{self.user}"
        response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, "lxml")
        display_name = soup.find("span", class_="_2BMnT8pWnIhEjqIWuJHYYa").text
        karma_score = soup.find("span", class_="_1hNyZs13xy-JWvaI8OZ-3k").text
        console.print(f"\n[bold]{display_name}[/bold] ({karma_score} karma)")
        subreddit_url = f"https://www.reddit.com/{self.subreddit}"
        subreddit_response = requests.get(subreddit_url, headers={'User-agent': 'Mozilla/5.0'})
        subreddit_soup = BeautifulSoup(subreddit_response.content, "lxml")
        subreddit_name = subreddit_soup.find("span", class_="_2yYKzH1JjpzT3TENaSMSUz").text
        subreddit_subscribers = subreddit_soup.find("span", class_="_1a4ZBXR9fNz5ttm8hpYvO4").text
        console.print(f"\n[bold]Subreddit:[/bold] {subreddit_name} ({subreddit_subscribers} subscribers)")

        if self.upvotes:
            upvote_count = soup.find("span", class_="_2KJtLbLCZJ0x2HsENFS8Da").text
            console.print(f"\n[bold]{display_name}[/bold] has [bold]{upvote_count}[/bold] upvotes.")

        if self.comments:
            comment_count = soup.find("span", class_="_2KJtLbLCZJ0x2HsENFS8Da", title="comment karma").text
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

    ver = pyfiglet.figlet_format("V.0.3")
    print(ver)
    parser = argparse.ArgumentParser(description="Reddit Tracker")
    parser.add_argument("--reddit", "-r", help="Specify the subreddit name (e.g., r/learnpython)", required=True)
    parser.add_argument("--user", "-u", help="Specify the Reddit user (e.g., u/Spez)", required=True)
    parser.add_argument("--upvotes", "-up", action="store_true", help="Get the number of upvotes for the user")
    parser.add_argument("--comments", "-c", action="store_true", help="Get the number of comments for the user")
    args = parser.parse_args()
    reddit_tracker = RedditTracker(args.reddit, args.user, args.upvotes, args.comments)
    reddit_tracker.run()
