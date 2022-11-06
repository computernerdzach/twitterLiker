import time
import datetime
import requests
import tweepy

from random import randint
from typing import TextIO


# pick this exact moment right now (at any given moment)
def right_now() -> str:
    return datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def report(message: str, logfile: TextIO):
    print(message)
    logfile.write(f"{message}\n")


# set now and write heading
def set_sub_heading(tweet_run: int, logfile: TextIO) -> str:
    message = f"[TWEET RETRIEVAL] -- # {tweet_run} (asks to continue after 4 runs) -- {right_now()}"
    report(message=message, logfile=logfile)
    return message


def follow_and_report(logfile: TextIO, client: requests.session, author_id: int, author: str):
    # follow tweet author and report
    client.follow_user(author_id)
    message = f"[RANDOMLY FOLLOWED AUTHOR] -- author: {author} -- {right_now()}"
    report(message=message, logfile=logfile)


# randomly select accounts to follow
def random_follow(tweet: tweepy.Tweet, logfile: TextIO, client: requests.session, api: tweepy.API):
    try:
        random_number = randint(1, 20)
        # capture the author_id and screen_name of the tweet's author
        author_id = tweet.data['author_id']
        author = api.get_user(user_id=author_id).screen_name
        # randomly follow authors of 5% of liked tweets
        if random_number == 15:
            follow_and_report(logfile=logfile, client=client, author_id=author_id, author=author)
            return
    # report oopsies
    except Exception as oops:
        message = f"[OOPS] -- {oops} -- {right_now()}"
        report(message=message, logfile=logfile)


# follow back all followers
def follow_back(followers: list, following: list, logfile: TextIO, client: requests.session, api: tweepy.API):
    for follower in followers:
        if follower not in following:
            try:
                client.follow_user(follower)
                message = f"[FOLLOW BACK] -- now following: {api.get_user(follower).screen_name} -- {right_now()}"
                report(message=message, logfile=logfile)
            except Exception as oops:
                message = f"[OOPS] -- {oops} -- {right_now()}"
                report(message=message, logfile=logfile)
        else:
            message = f"[FOLLOW BACK] -- already following {api.get_user(user_id=follower).screen_name}"
            report(message=message, logfile=logfile)


def like_and_report(client: requests.session, tweet: tweepy.Tweet, logfile: TextIO):
    # like each tweet that is found and report
    client.like(tweet.id)
    message = f"[LIKED TWEET] -- # {tweet.text[0:50]}... -- {right_now()}"
    report(message=message, logfile=logfile)


# like each tweet
def like_tweet_random_follow(tweets: {requests.Response}, logfile: TextIO,
                             client: requests.session, api: tweepy.API, tweet_run: int):
    tweet_count = 1
    for tweet in tweets.data:
        try:
            message = f"[CURRENT TWEET] -- {tweet_count} of 100 tweets -- run # {tweet_run + 1}"
            report(message=message, logfile=logfile)
            # like and report
            like_and_report(client=client, tweet=tweet, logfile=logfile)
            # randomly follow (or not) the tweet author
            random_follow(tweet=tweet, logfile=logfile, client=client, api=api)
            # increment tweet
            tweet_count += 1
            # chill for a bit
            time.sleep(randint(20, 45))
        # report oopsies
        except Exception as e:
            message = f"[OOPS] -- {e} --- {right_now()}"
            report(message=message, logfile=logfile)
            time.sleep(10)


# report that the next run is starting
def log_next_run(logfile: TextIO, tweet_run: int):
    message = f"[INITIATE TWEET RETRIEVAL] {tweet_run}-- of 100 tweets (asks to continue after 4 runs) -- {right_now()}"
    report(message=message, logfile=logfile)


def go_again(logfile: TextIO) -> bool:
    question = "Continue? [y] or [n]\n> "
    user_answer = input(question).lower()
    while (user_answer != "y") and (user_answer != "n"):
        user_answer = input('Please enter "y" or "n" and press enter.')
    if user_answer == "n":
        message = f"C{question} -- {user_answer}"
        report(message=message, logfile=logfile)
        logfile.close()
        return False
    elif user_answer == "y":
        message = f"C{question} -- {user_answer}"
        report(message=message, logfile=logfile)
        return True
    else:
        message = "[ERROR] -- beginning next run"
        report(message=message, logfile=logfile)


def main(followers: list[int], following: list[int], logfile: TextIO,
         client: requests.session, api: tweepy.API, tweet_run: int, query: str):
    # follow back all followers
    follow_back(followers=followers, following=following, logfile=logfile, client=client, api=api)
    # set log sub-heading
    logfile.write(set_sub_heading(tweet_run=tweet_run, logfile=logfile))
    for i in range(0, 3):
        # get 100 tweets matching hashtags, and returning desired data
        tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'],
                                             expansions=['entities.mentions.username', 'author_id'],
                                             user_fields=['username'], max_results=100)
        # like the tweets and randomly select a few authors to follow
        like_tweet_random_follow(tweets=tweets, logfile=logfile,
                                 client=client, api=api, tweet_run=i+1)
