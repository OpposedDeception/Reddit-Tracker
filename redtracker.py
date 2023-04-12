#!/usr/bin/env python3


from __future__ import absolute_import
from json import dump
from pytz import UTC
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from rich.console import Console
from rich.panel import Panel
from time import sleep
from argparse import ArgumentParser
from praw import Reddit
from pyfiglet import figlet_format
from datetime import datetime
from requests import get
from textblob import TextBlob
import nltk
import csv


def get_current_utc_time():
    response = get('https://worldtimeapi.org/api/timezone/Etc/UTC')
    data = response.json()
    utc_time_str = data['datetime']
    utc_time = datetime.fromisoformat(utc_time_str).replace(tzinfo=UTC)
    c = Console()
    c.print(f"[bold]The current time is: [\bold]" + str(utc_time))


class Csv(object):
     def __init__(self, filename=None):
        self.filename = filename
        self.headers = []
        self.data = []

     def csvread(self):
        with open(self.filename, "r") as f:
            lines = f.readlines()

        self.headers = lines[0].strip().split(",")
        self.data = [line.strip().split(",") for line in lines[1:]]

     def csvwrite(self):
        with open(self.filename, "w") as f:
            f.write(",".join(self.headers) + "\n")
            for row in self.data:
                f.write(",".join(row) + "\n")

     def csvsort(self, column, reverse=False):
        if column not in self.headers:
            raise ValueError("Invalid column name")

        index = self.headers.index(column)
        self.data.sort(key=lambda x: x[index], reverse=reverse)
        self.headers = [self.headers[index]] + [h for h in self.headers if h != self.headers[index]]

     def __str__(self):
        rows = [self.headers] + self.data
        return "\n".join([",".join(row) for row in rows])

     @classmethod
     def from_file(cls, filename):
        instance = cls(filename)
        instance.csvread()
        return instance
    
     @staticmethod
     def save_data(filename, header, data):
        with open(filename, mode='w', newline='') as file:
            write = csv.writer(file)
            write.writerow(header)
            for row in data:
                write.writerow(row)
                
class KeyWords(object):
    @staticmethod
    def extract_keywords(text, *args, **kwargs):
        nltk.download('punkt')
        nltk.download('stopwords')
        stop_words = set(kwargs.get('stopwords', stopwords.words('english')))
        min_len = kwargs.get('min_len', 4)
        min_count = kwargs.get('min_count', 3)
        
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if t not in stop_words]
        tr = nltk.Text(tokens)
        keywords = tr.vocab()
        keywords = [k for k in keywords.keys() if len(k) >= min_len and keywords[k] >= min_count]
        return keywords
 
                 
    @staticmethod
    def save_keywords(keywords, filename):
         with open(filename, 'w') as f:
            dump(keywords, f)
            print(f"Keywords have been saved to {filename}.")                


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
        #c.print(f"\n[bold]Comment:[/bold] {comment.body} ({comment.score})")
        comment_text = ' '.join([comment['body'] for comment in comment_data])
        header = ["Body", "Score", "Created UTC", "Submission ID"]
        data = [[comment['body'], comment['score'], comment['created'], comment['submission_id']] for comment in comment_data]
        Csv.save_data("reddit_comments.csv", header, data)
        return comment_text

        
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
                      
    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        return sentiment                                           
                    

    def get_influential_users(self, username, keyword, limit=10):
        user = self.reddit.redditor(username)
        users = {}
    
        for submission in user.submissions.new(limit=limit):
            if keyword.lower() in submission.title.lower():
                author = submission.author
                if author not in users:
                    users[author] = {
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'followers': author.subreddit['subscribers'],
                    'posts': 1
                }
                else:
                    users[author]['score'] += submission.score
                    users[author]['num_comments'] += submission.num_comments
                    users[author]['posts'] += 1

                for comment in user.comments.new(limit=limit):
                    if keyword.lower() in comment.body.lower():
                        author = comment.author
                        if author not in users:
                            users[author] = {
                    'score': comment.score,
                    'num_comments': 1,
                    'followers': author.subreddit['subscribers'],
                    'posts': 0
                }
                        else:
                            users[author]['score'] += comment.score
                            users[author]['num_comments'] += 1
    
                        influential_users = sorted(users.items(), key=lambda x: x[1]['followers'], reverse=True)[:10]
                        c = Console()
                        c.print(f"[bold]Influential users: [\bold] ({influential_users})")

                    
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

    ver = figlet_format("V.1.5")
    print(ver)
    get_current_utc_time()
    client_id = input("Enter your Reddit client ID: ")
    client_secret = input("Enter your Reddit client secret: ")

    parser = ArgumentParser(description="Reddit Tracker")
    parser.add_argument("--reddit", "-r", help="Specify the subreddit name (e.g., learnpython)", required=False)
    parser.add_argument("--user", "-u", help="Specify the Reddit user (e.g., spez)", required=True)
    parser.add_argument("--upvotes", "-up", action="store_true", help="Get the number of upvotes for the user")
    parser.add_argument("--comments", "-c", action="store_true", help="Get the number of comments for the user")
    parser.add_argument('--index', "-i", type=int, help='The index of the comment to retrieve. Only for comments now')
    parser.add_argument("--post", "-p", help="Shows last post from the selected subreddit")
    parser.add_argument("--keywords", "-kw", help="Allows you to write keywords you want to save. All words are saved in a .json file", required=False)
    args = parser.parse_args()

    reddit_tracker = RedditTracker()
    while True:
        try:
            reddit_tracker.authenticate(client_id, client_secret)
            reddit_tracker.run(args.reddit, args.user, args.upvotes, args.comments)
            if args.index:
                reddit_tracker.get_comments(args.user, args.index)
                if args.index:
                    comments = reddit_tracker.get_comments(args.user, 10)
                    for comment in comments:
                        sentiment = reddit_tracker.analyze_sentiment(reddit_tracker.get_comments(args.user, args.index))
                        c = Console()
                        c.print(f"Sentiment: {sentiment}")
                        c.print(f"The number represents the sentiment score of the text. In this case, the sentiment score is {sentiment} which indicates a slightly negative sentiment. The sentiment score is usually a value between -1 and 1, with negative values indicating negative sentiment, positive values indicating positive sentiment, and zero indicating a neutral sentiment. The closer the value is to -1 or 1, the stronger the sentiment.")
                        break
                        if args.keywords:
                           reddit_tracker.get_influential_users(args.user, args.keywords)
                
                if args.post:
                   
                   reddit_tracker.get_posts(args.post)
                   print("\033[1;35m" + r"""
 /\_/\
( o   o )
=(  Y  )=
  \~(*)~/
   - ^ -
""" + "\033[0m")

                   if input("Do you want to save the keywords to a file? (Y/N): ").lower() == 'y':
                    keywords = KeyWords.extract_keywords(reddit_tracker.get_comments(args.user, args.index), stopwords={'is', 'some', 'that', 'US'})

                    filename = f"reddit_keywords.json"
                    KeyWords.save_keywords(keywords, filename)                   
                else:
                    exit()
            else:
                print("\033[1;35m" + r"""
 /\_/\
( o   o )
=(  Y  )=
  \~(*)~/
   - ^ -
""" + "\033[0m")

                c = Console()
                c.print(f'[bold]Under the maintainment![\bold]')
                exit()
        except Exception as e:
            print("An error has occured! Please double check your Client ID/Client Secret. Make sure you typed correct username/subreddit without u/ or r/" + e)        
            break            
            sleep(10)
            exit()
        sleep(30)
